
import os
from cmmodule import ireader
from cmmodule import bgrMerge
import pyBigWig
from cmmodule.utils import map_coordinates, wiggleReader
from cmmodule.utils import bigwigReader, update_chromID
import logging


def crossmap_wig_file(mapping, in_file, out_prefix,
                      taget_chrom_size, in_format, binSize=100000, cstyle='a'):
    '''
    Description
    -----------
    Convert genome coordinates (in wiggle/bigwig format) between assemblies.
    wiggle format: http://genome.ucsc.edu/goldenPath/help/wiggle.html
    bigwig format: http://genome.ucsc.edu/goldenPath/help/bigWig.html

    Parameters
    ----------
    mapping : dict
        Dictionary with source chrom name as key, IntervalTree object as value.

    in_file : file
        Input file in wig or bigwig format. Both "variableStep" and
        "fixedStep" wiggle lines are supported.

    out_prefix : str
        Prefix of output files.

    taget_chrom_size : dict
        Chromosome size of the target genome assembly. Key is chromosome ID,
        value is the length of the chromosome. Note, the chromosome ID and
        length information were extracted from the chain file, therefore,
        the chrom_IDs can be with or without the leading "chr".

    in_format : str
        Either "wiggle" or "bigwig"

    binSize : int
        The chunk size when reading bigwig file in each iteration.

    cstyle : str, optional
        Chromosome ID style. Must be one of ['a', 's', 'l'], where
        'a' : as-is. The chromosome ID of the output file is in the same
            style of the input file.
        's' : short ID, such as "1", "2", "X.
        'l' : long ID, such as "chr1", "chr2", "chrX.
    '''

    OUT_FILE1 = open(out_prefix + '.bgr', 'w')  # original bgr file
    OUT_FILE2 = open(out_prefix + '.sorted.bgr', 'w')  # sorted bgr file
    OUT_FILE3 = pyBigWig.open(out_prefix + '.bw', "w")  # bigwig file

    chrom_style = 'chr1'

    if in_format.upper() == "WIGGLE":
        logging.info(
            "Liftover wiggle file \"%s\" to bedGraph file \"%s\""
            % (in_file, out_prefix + '.bgr'))

        for chrom, start, end, strand, score in wiggleReader(in_file):
            chrom_style = chrom
            maps = map_coordinates(
                mapping, chrom, start, end, '+',  chrom_style=cstyle)
            if maps is None:
                continue
            if len(maps) == 2:
                print('\t'.join([str(i) for i in [
                    maps[1][0],
                    maps[1][1],
                    maps[1][2],
                    score]]), file=OUT_FILE1)
            else:
                continue
            maps[:] = []
        OUT_FILE1.close()

        logging.info("Merging overlapped entries in bedGraph file")
        for (chrom, start, end, score) in bgrMerge.merge(out_prefix + '.bgr'):
            print('\t'.join([str(i) for i in (chrom, start, end, score)]),
                  file=OUT_FILE2)
        OUT_FILE2.close()

        os.remove(out_prefix + '.bgr')  # remove .bgr, keep .sorted.bgr

        # make bigwig header
        target_chroms_sorted = []
        for k in sorted(taget_chrom_size.keys()):
            i_chrom = update_chromID(chrom_style, k)
            i_value = taget_chrom_size[k]
            target_chroms_sorted.append((i_chrom, i_value))

        # add bigwig header
        logging.info("Writing header to \"%s\" ..." % (out_prefix + '.bw'))
        OUT_FILE3.addHeader(target_chroms_sorted)

        # add entries to bigwig file
        logging.info("Writing entries to \"%s\" ..." % (out_prefix + '.bw'))
        for line in ireader.reader(out_prefix + '.sorted.bgr'):
            r_chr, r_st, r_end, r_value = line.split()
            OUT_FILE3.addEntries(
                [r_chr],
                [int(r_st)],
                ends=[int(r_end)],
                values=[float(r_value)])

        OUT_FILE3.close()

    elif in_format.upper() == "BIGWIG":
        logging.info(
            "Liftover bigwig file %s to bedGraph file %s:"
            % (in_file, out_prefix + '.bgr'))
        for chrom, start, end, score in bigwigReader(in_file):
            chrom_style = chrom
            maps = map_coordinates(
                mapping, chrom, start, end, '+',  chrom_style=cstyle)
            try:
                if maps is None:
                    continue
                if len(maps) == 2:
                    print('\t'.join([str(i) for i in [
                        maps[1][0],
                        maps[1][1],
                        maps[1][2],
                        score]]),
                        file=OUT_FILE1)
                else:
                    continue
            except:
                continue
            maps[:] = []
        OUT_FILE1.close()

        logging.info("Merging overlapped entries in bedGraph file")
        for (chrom, start, end, score) in bgrMerge.merge(out_prefix + '.bgr'):
            print(
                '\t'.join([str(i) for i in (chrom, start, end, score)]),
                file=OUT_FILE2)
        OUT_FILE2.close()
        os.remove(out_prefix + '.bgr')  # remove .bgr, keep .sorted.bgr

        logging.info("Writing header to \"%s\" ..." % (out_prefix + '.bw'))

        # make bigwig header
        target_chroms_sorted = []
        for k in sorted(taget_chrom_size.keys()):
            i_chrom = update_chromID(chrom_style, k)
            i_value = taget_chrom_size[k]
            target_chroms_sorted.append((i_chrom, i_value))

        # add bigwig header
        OUT_FILE3.addHeader(target_chroms_sorted)

        # add entries to bigwig file
        logging.info("Writing entries to \"%s\" ..." % (out_prefix + '.bw'))
        for line in ireader.reader(out_prefix + '.sorted.bgr'):
            r_chr, r_st, r_end, r_value = line.split()
            OUT_FILE3.addEntries(
                [r_chr], [int(r_st)], [int(r_end)], [float(r_value)])
        OUT_FILE3.close()
    else:
        raise Exception("Unknown foramt. Must be 'wiggle' or 'bigwig'")
