from __future__ import print_function
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
