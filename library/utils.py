import os
import sys
import tarfile


def untargz(input_targz_file, untar_to_dir):
    """
    This module accepts a tar.gz archive and untars it.

    :param input_targz_file: Input targz file
    :param untar_to_dir: Output directory
    :returns: Path to the untar-ed directory/file

    Copied from the ProTECT common library
    NOTE: this module expects the multiple files to be in a directory before
          being tar-ed.
    """
    print('Extracting STAR index.', file=sys.stderr)
    assert tarfile.is_tarfile(input_targz_file), 'Not a tar file.'
    tarball = tarfile.open(input_targz_file)
    return_value = os.path.join(untar_to_dir, tarball.getmembers()[0].name)
    tarball.extractall(path=untar_to_dir)
    tarball.close()
    return return_value

def star_to_bedpe(input_pth, output_pth):
    """
    Converts STAR-Fusion output to BEDPE format.

    :param input_pth: Path to STAR-Fusion output
    :param output_pth: Path for BEDPE-formatted output

    Copied from https://github.com/brianjohnhaas/Winterfell_SMC_RNA_DREAM2016/blob/master/STAR_Fusion/docker/convert_star_to_bedpe.py
    KKD for Sage Bionetworks
    June 13, 2016
    Convert star-fusion output to BEDPE

    http://bedtools.readthedocs.io/en/latest/content/general-usage.html
    """

    with open(input_pth, 'r') as f, open(output_pth, 'w') as g:
        header = ['chrom1', 'start1', 'end1',
                  'chrom2', 'start2', 'end2',
                  'name', 'score',
                  'strand1', 'strand2']

        g.write('\t'.join(header) + '\n')
        for line in f:
            if not line.startswith('#'):
                vals = line.strip().split()
                valsL = vals[5].split(':')
                valsR = vals[7].split(':')
                chrL = valsL[0]
                posL = valsL[1]
                geneL = vals[4].split('^')[1]
                strandL = valsL[2]
                chrR = valsR[0]
                posR = valsR[1]
                geneR = vals[6].split('^')[1]
                strandR = valsR[2]
                bedpe = '\t'.join([chrL, str(int(posL)-1), posL,
                                   chrR, str(int(posR)-1), posR,
                                   '-'.join([geneL, geneR]), '0',
                                   strandL, strandR])
                g.write(bedpe + '\n')
