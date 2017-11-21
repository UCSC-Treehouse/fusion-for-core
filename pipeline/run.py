#!/usr/bin/env python2.7

from __future__ import print_function
import argparse
import csv
import glob
import multiprocessing
import os
import shutil
import subprocess
import sys
import tarfile

from library.utils import untargz


def pipeline(args):
    """
    STAR-Fusion and FusionInspector pipeline

    :param args: Argparse object containing command line arguments
    :return: None
    """
    # Run STAR-Fusion
    cmd = ['STAR-Fusion',
           '--genome_lib_dir', args.genome_lib_dir,
           '--output_dir', args.output_dir,
           '--left_fq', args.r1,
           '--right_fq', args.r2,
           '--CPU', args.CPU]

    output = os.path.abspath('%s/star-fusion.fusion_candidates.final.abridged.FFPM' % args.output_dir)

    if args.test:
        cmd = ['echo'] + cmd
        shutil.copy('/home/star-fusion.fusion_candidates.final.abridged.FFPM',
                    output)

    if args.debug:
        print(cmd, file=sys.stderr)

    print('Beginning STAR-Fusion Run.', file=sys.stderr)
    subprocess.check_call(cmd)

    # Check that local output exists
    if not os.path.exists(output):
        raise ValueError('Could not find output from STAR-Fusion')

    results = os.path.abspath('%s/star-fusion-non-filtered.final' % args.output_dir)
    os.rename(output, results)

    if args.skip_filter:
        print('Skipping filter.', file=sys.stderr)

    else:
        print('Filtering results with gene-list.', file=sys.stderr)

        # Load genelist fusions. Each gene must be on a separate line.
        genelist = set()
        with open(args.genelist, 'r') as f:
            for line in f:
                genelist.add(line.strip())

        # Parse results and filter
        gl_results = os.path.abspath('%s/star-fusion-gene-list-filtered.final' % args.output_dir)
        with open(results, 'r') as in_f, open(gl_results, 'w') as out_f:
            reader = csv.reader(in_f, delimiter='\t')
            writer = csv.writer(out_f, delimiter='\t')
            header = reader.next()
            writer.writerow(header)

            for line in reader:
                gene1, gene2 = line[0].split('--')
                if gene1 not in genelist or gene2 not in genelist:
                    print('Fusion %s--%s not in gene-list.' % (gene1, gene2), file=sys.stderr)

                # If fusion call passed filter, then write it to the output
                else:
                    writer.writerow(line)

        # Update results file
        results = out_f.name

    if args.run_fusion_inspector:
        # Check input file for at least one fusion prediction
        with open(results, 'r') as f:

            # Header line
            f.next()
            try:
                f.next()

            except StopIteration:
                print("Stopping: no fusions were found.", file=sys.stderr)
                return

        fusion_inspector(results, args)


def fusion_inspector(results, args):

    fi_path = os.path.abspath(os.path.join(args.output_dir, 'FI-output'))

    cmd = ['FusionInspector',
           '--fusions', os.path.abspath(results),
           '--genome_lib', os.path.abspath(args.genome_lib_dir),
           '--left_fq', os.path.abspath(args.r1),
           '--right_fq', os.path.abspath(args.r2),
           '--out_dir', fi_path,
           '--out_prefix', 'FusionInspector',
           '--prep_for_IGV',
           '--CPU', args.CPU]

    fi_output = os.path.join(fi_path, 'FusionInspector.fusion_predictions.final.abridged.FFPM')

    if args.test:
        cmd = ['echo'] + cmd
        os.mkdir(os.path.join(args.output_dir, 'FI-output'))
        shutil.copy('/home/FusionInspector.fusion_predictions.final.abridged.FFPM',
                    os.path.join(fi_path, fi_output))

    if args.debug:
        print(cmd, file=sys.stderr)

    print('Beginning FusionInspector run.', file=sys.stderr)
    subprocess.check_call(cmd)

    # Rename the output so it is a little clearer
    fi_rename = os.path.join(fi_path, 'fusion-inspector-results.final')
    os.rename(fi_output, fi_rename)


def main():
    """
    Wraps STAR-Fusion program and filters output using FusionInspector.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('--left-fq',
                        dest='r1',
                        required=True,
                        help='Fastq 1')
    parser.add_argument('--right-fq',
                        dest='r2',
                        required=True,
                        help='Fastq 2')
    parser.add_argument('--output-dir',
                        dest='output_dir',
                        required=True,
                        help='Output directory')
    parser.add_argument('--tar-gz',
                        dest='tar_gz',
                        action='store_true',
                        default=False,
                        help='Compresses output directory to tar.gz file')
    parser.add_argument('--genome-lib-dir',
                        dest='genome_lib_dir',
                        required=True,
                        help='Reference genome directory (can be tarfile)')
    parser.add_argument('--CPU',
                        default=str(multiprocessing.cpu_count()),
                        help='Number of jobs to run in parallel')
    parser.add_argument('--genelist',
                        default='/home/gene-list')
    parser.add_argument('--skip-filter',
                        help='Skips gene-list filter',
                        dest='skip_filter',
                        action='store_true')
    parser.add_argument('-F', '--run-fusion-inspector',
                        dest='run_fusion_inspector',
                        action='store_true',
                        help='Runs FusionInspector on STAR-Fusion output')
    parser.add_argument('--untargz-ref',
                        dest='untargz_ref',
                        action='store_true',
                        help='Expands tar/gzipped reference file')
    parser.add_argument('--star-fusion-results',
                        dest='star_fusion_results',
                        help='Skips STAR-Fusion and runs FusionInspector')
    parser.add_argument('--save-intermediates',
                        dest='save_intermediates',
                        action='store_true',
                        default=False,
                        help='Does not delete intermediate files')
    parser.add_argument('--root-ownership',
                        dest='run_as_root',
                        action='store_true',
                        default=False,
                        help='Does not change file ownership to user')
    parser.add_argument('--test',
                        help='Runs the pipeline with dummy files',
                        action='store_true',
                        default=False)
    parser.add_argument('--debug',
                        help='Prints tool command line arguments',
                        action='store_true',
                        default=False)
    args = parser.parse_args()

    # Check if output directory already exists. The final permissions are set
    # to the permissions of the output directory if run_as_root is not set.
    if not os.path.exists(args.output_dir):
        if args.run_as_root:
            os.mkdir(args.output_dir)
        else:
            raise ValueError('Stopping: output directory does not exist and run_as_root is not set.')

    # Check that output is not owned by root
    stat = os.stat(args.output_dir)
    # Note that the flag is root-ownership
    if not args.run_as_root and stat.st_uid == 0:
        raise ValueError('Stopping: output directory owned by root user.')

    # Untar the genome directory if necessary
    if args.untargz_ref and os.path.isfile(args.genome_lib_dir):
        args.genome_lib_dir = untargz(args.genome_lib_dir, '/tmp')

    # This is based on the Toil RNA-seq pipeline:
    # https://github.com/BD2KGenomics/toil-rnaseq/blob/master/docker/wrapper.py#L51
    try:
        if args.star_fusion_results:
            print("Starting FusionInspector run.", file=sys.stderr)
            fusion_inspector(args.star_fusion_results, args)

        else:
            print("Starting Treehouse fusion pipeline.", file=sys.stderr)
            pipeline(args)

    except subprocess.CalledProcessError as e:
        print(e.message, file=sys.stderr)

    finally:
        # Check if FusionInspector directory still exists
        fi_path = os.path.abspath(os.path.join(args.output_dir, 'FI-output'))
        if os.path.exists(fi_path):
            # FusionInspector requires a sub-directory to run correctly
            # Here, I move the FI-output files into the parent directory
            for f in os.listdir(fi_path):
                shutil.move(os.path.join(fi_path, f),
                            os.path.join(args.output_dir, f))

            # Remove intermediate directory
            shutil.rmtree(fi_path)

        # Note that the flag is root-ownership
        if not args.run_as_root:
            print('Changing file ownership to user.', file=sys.stderr)
            subprocess.check_call(['chown', '-R', '{}:{}'.format(stat.st_uid, stat.st_gid), args.output_dir])

        if not args.save_intermediates:
            print('Cleaning output directory.', file=sys.stderr)

            delete = set()
            with open('/home/delete-list') as f:
                for line in f:
                    delete.add(line.strip())

            # https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
            for d in delete:
                # Need to add a relative path within docker
                d = os.path.join(args.output_dir, d)

                # Skip files or directories that do not exist
                if not os.path.exists(d):
                    continue

                # Remove file
                try:
                    os.remove(d)

                # Remove directory
                except OSError:
                    shutil.rmtree(d)

        # https://gist.github.com/dreikanter/2835292
        if args.tar_gz:
            tarname = '%s.tar.gz' % args.output_dir
            print('Compressing files to %s' % tarname)
            tar = tarfile.open(tarname, "w:gz")
            for fname in glob.glob(args.output_dir):
                tar.add(fname, os.path.basename(fname))
            tar.close()


if __name__ == '__main__':
    main()
