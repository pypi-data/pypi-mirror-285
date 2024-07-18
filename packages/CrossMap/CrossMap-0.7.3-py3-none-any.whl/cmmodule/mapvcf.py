import os
import pysam
import re
import datetime
import subprocess
import logging
from cmmodule import ireader
from cmmodule.utils import update_chromID, revcomp_DNA, map_coordinates, is_dna
from cmmodule.meta_data import __version__


def crossmap_vcf_file(mapping, infile, outfile,
                      liftoverfile, refgenome, noCompAllele=False,
                      compress=False, cstyle='a'):
    '''
    Convert genome coordinates in VCF format.

    Parameters
    ----------
    mapping : dict
        Dictionary with source chrom name as key, IntervalTree object as value.

    infile : file
        Input file in VCF format. Can be a regular or compressed
        (*.gz, *.Z,*.z, *.bz, *.bz2, *.bzip2) file, local file or URL
        (http://, https://, ftp://) pointing to remote file.

    outfile : str
        prefix of output files.

    liftoverfile : file
        Chain (https://genome.ucsc.edu/goldenPath/help/chain.html) format file.
        Can be a regular or compressed (*.gz, *.Z,*.z, *.bz, *.bz2, *.bzip2)
        file, local file or URL (http://, https://, ftp://) pointing to remote
        file.
    refgenome : file
        The genome sequence file of 'target' assembly in FASTA format.
    noCompAllele : bool
        A logical value indicates whether to compare ref_allele to alt_allele
        after liftover. If True, the variant will be marked as "unmap" if
        ref_allele == alt_allele.

    cstyle : str, optional
        Chromosome ID style. Must be one of ['a', 's', 'l'], where
        'a' : as-is. The chromosome ID of the output file is in the same
            style of the input file.
        's' : short ID, such as "1", "2", "X.
        'l' : long ID, such as "chr1", "chr2", "chrX.
    '''

    if noCompAllele:
        logging.info(
            "Keep variants [reference_allele == alternative_allele] ...")
    else:
        logging.info(
            "Filter out variants [reference_allele == alternative_allele] ...")

    # index the *original* refegenome file if it hasn't been done
    if not os.path.exists(refgenome + '.fai'):
        logging.info("Creating index for: %s" % refgenome)
        pysam.faidx(refgenome)
    if os.path.getmtime(refgenome + '.fai') < os.path.getmtime(refgenome):
        logging.info(
            "Index file is outdated. Re-creating index for: %s" % refgenome)
        pysam.faidx(refgenome)

    # index the *target* refegenome file if it hasn't been done
    # if not os.path.exists(refgenome1 + '.fai'):
    #    logging.info("Creating index for: %s" % refgenome1)
    #    pysam.faidx(refgenome1)
    # if os.path.getmtime(refgenome1 + '.fai') < os.path.getmtime(refgenome1):
    #    logging.info(
    #        "Index file is outdated. Re-creating index for: %s" % refgenome1)
    #    pysam.faidx(refgenome1)

    refFasta = pysam.Fastafile(refgenome)

    FILE_OUT = open(outfile, 'w')
    UNMAP = open(outfile + '.unmap', 'w')

    total = 0
    fail = 0

    # if there is no contig field, use this chrom ID style.
    chr_template = 'chr1'

    for line in ireader.reader(infile):
        if not line.strip():
            continue
        line = line.strip()

        # deal with meta-information lines.
        # meta-information lines needed in both mapped and unmapped files
        if line.startswith('##fileformat'):
            print(line, file=FILE_OUT)
            print(line, file=UNMAP)
        elif line.startswith('##INFO'):
            print(line, file=FILE_OUT)
            print(line, file=UNMAP)
        elif line.startswith('##FILTER'):
            print(line, file=FILE_OUT)
            print(line, file=UNMAP)
        elif line.startswith('##FORMAT'):
            print(line, file=FILE_OUT)
            print(line, file=UNMAP)
        elif line.startswith('##ALT'):
            print(line, file=FILE_OUT)
            print(line, file=UNMAP)
        elif line.startswith('##SAMPLE'):
            print(line, file=FILE_OUT)
            print(line, file=UNMAP)
        elif line.startswith('##PEDIGREE'):
            print(line, file=FILE_OUT)
            print(line, file=UNMAP)

        # meta-information lines needed in unmapped files
        elif line.startswith('##assembly'):
            print(line, file=UNMAP)
        elif line.startswith('##contig'):
            print(line, file=UNMAP)
            if 'ID=chr' in line:
                chr_template = 'chr1'
            else:
                chr_template = '1'

        # update contig information
        elif line.startswith('#CHROM'):
            logging.info("Updating contig field ... ")
            target_gsize = dict(
                list(zip(refFasta.references, refFasta.lengths)))
            for chr_id in sorted(target_gsize):
                print("##contig=<ID=%s,length=%d,assembly=%s>"
                      % (update_chromID(chr_template,
                         chr_id, cstyle),
                         target_gsize[chr_id],
                         os.path.basename(refgenome)),
                      file=FILE_OUT)

            print("##liftOverProgram=CrossMap,version=%s"
                  % __version__, file=FILE_OUT)
            print("##liftOverChainFile=%s"
                  % liftoverfile, file=FILE_OUT)
            print("##originalFile=%s"
                  % infile, file=FILE_OUT)
            print("##targetRefGenome=%s"
                  % refgenome, file=FILE_OUT)
            print("##liftOverDate=%s"
                  % datetime.date.today().strftime("%B%d,%Y"), file=FILE_OUT)
            print(line, file=FILE_OUT)
            print(line, file=UNMAP)
            logging.info("Lifting over ... ")

        else:
            if line.startswith('#'):
                continue
            fields = str.split(line, maxsplit=7)
            total += 1
            # original coordinates of variants
            chrom = fields[0]
            start = int(fields[1])-1     # 0 based
            end = start + 1  # liftover the **First position** of REF
            ref_allele_size = len(fields[3])
            alt_allele_size = len(fields[4])
            # allele_diff is used to tell the variant type:
            # substitution, insertion or deletion
            allele_diff = alt_allele_size - ref_allele_size
            if allele_diff == 0:
                v_type = 'sub'
            elif allele_diff > 0:
                v_type = 'ins'
            else:
                v_type = 'del'
            # Note, only convert the first position of REF allele
            a = map_coordinates(
                mapping, chrom, start, end, '+', chrom_style=cstyle)
            if a is None:
                print(line + "\tFail(Unmap)", file=UNMAP)
                fail += 1
                continue

            # one to one match
            if len(a) == 2:
                target_chr = a[1][0]
                target_start = a[1][1]
                target_end = a[1][2]
                target_strand = a[1][3]

                # update fields[0]: chrom
                fields[0] = target_chr

                # map to reverse strand
                if target_strand == '-':
                    # For substitution (SNP), the REF allele is 1 nucleotide
                    if v_type == 'sub':
                        ref_allele_start = target_start
                        ref_allele_end = target_end
                    # For insertion, the REF allele is 1 also nucleotide
                    elif v_type == 'ins':
                        ref_allele_start = target_start
                        ref_allele_end = target_end
                    # For deletion, the REF allele is longer than 1 nucleotide
                    elif v_type == 'del':
                        ref_allele_start = target_start - ref_allele_size
                        ref_allele_end = ref_allele_start + ref_allele_size
                # map to forward strand
                elif target_strand == '+':
                    if v_type == 'sub':
                        ref_allele_start = target_start
                        ref_allele_end = target_end
                    elif v_type == 'ins':
                        ref_allele_start = target_start
                        ref_allele_end = target_end
                    elif v_type == 'del':
                        ref_allele_start = target_start
                        ref_allele_end = ref_allele_start + ref_allele_size

                # update field[3] (REF)
                target_chr = update_chromID(
                    refFasta.references[0], target_chr)
                try:
                    fields[3] = refFasta.fetch(
                        target_chr, ref_allele_start, ref_allele_end).upper()
                except:
                    print(line + "\tFail(KeyError)", file=UNMAP)
                    fail += 1
                    continue
                # update fields[1]: postion of the REF
                fields[1] = ref_allele_start + 1

                if len(fields[3]) == 0:
                    print(line + "\tFail(KeyError)", file=UNMAP)
                    fail += 1
                    continue

                # for insertions and deletions in a VCF file,
                # the first nucleotide in REF and ALT
                # fields correspond to the nucleotide at POS in the
                # *reference genome*
                ref_allele = fields[3]
                alt_alleles = fields[4].split(',')
                alt_alleles_updated = []
                for alt_allele in alt_alleles:
                    if is_dna(alt_allele):
                        # indels
                        if len(ref_allele) != len(alt_allele):
                            # replace the 1st nucleotide of ALT
                            if a[1][3] == '-':
                                tmp = ref_allele[0] + revcomp_DNA(
                                   alt_allele[1:], True)
                            else:
                                tmp = ref_allele[0] + alt_allele[1:]
                            alt_alleles_updated.append(tmp)
                        # substitutions
                        else:
                            if a[1][3] == '-':
                                alt_alleles_updated.append(
                                    revcomp_DNA(alt_allele, True))
                            else:
                                alt_alleles_updated.append(alt_allele)
                    else:
                        alt_alleles_updated.append(alt_allele)
                # remove alt_allele if it is equal to ref_allele
                alt_alleles_updated = [i for i in alt_alleles_updated if i != ref_allele]
                fields[4] = ','.join(alt_alleles_updated)

                # update END if any
                fields[7] = re.sub(
                    r'END\=\d+', 'END=' + str(target_end), fields[7])

                # check if ref_allele is the same as alt_allele
                if noCompAllele:
                    print('\t'.join(map(str, fields)), file=FILE_OUT)
                else:
                    if fields[3] != fields[4]:
                        print('\t'.join(map(str, fields)), file=FILE_OUT)
                    else:
                        print(line + "\tFail(REF==ALT)", file=UNMAP)
                        fail += 1
            else:
                print(line + "\tFail(Multiple_hits)", file=UNMAP)
                fail += 1
                continue
    FILE_OUT.close()
    UNMAP.close()

    logging.info("Total entries: %d" % total)
    logging.info("Failed to map: %d" % fail)

    if compress:
        try:
            logging.info("Compressing \"%s\" ..." % outfile)
            subprocess.call("gzip " + outfile, shell=True)
        except:
            pass
