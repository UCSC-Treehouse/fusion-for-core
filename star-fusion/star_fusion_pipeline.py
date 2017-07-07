#!/usr/bin/env python2.7

from __future__ import print_function
import argparse
import csv
import os
import shutil
import subprocess
import sys

def pipeline(args):
    """
    STAR-Fusion and FusionInspector pipeline

    :param args: Argparse object containing command line arguments
    :return: None
    """
    # Run STAR-Fusion
    cmd = ['STAR-Fusion',
           '--genome_lib_dir', '/data/%s' % args.genome_lib_dir,
           '--output_dir', '/data/%s' % args.output_dir,
           '--left_fq', '/data/%s' % args.r1,
           '--right_fq', '/data/%s' % args.r2,
           '--CPU', args.CPU]

    if args.test:
        cmd = ['echo'] + cmd

    print('Beginning STAR-Fusion Run', file=sys.stderr)
    subprocess.check_call(cmd)

    results = os.path.abspath('%s/star-fusion.fusion_candidates.final.abridged' % args.output_dir)

    # Check that local output exists
    if not os.path.exists(results):
        raise ValueError('Could not find output from STAR-Fusion')

    if args.skip_filter:
        print('Skipping filter...', file=sys.stderr)

    else:
        print('Filtering results with gene-list...', file=sys.stderr)

        # Load genelist fusions. Each gene must be on a separate line.
        genelist = set()
        with open(args.genelist, 'r') as f:
            for line in f:
                genelist.add(line.strip())

        # Parse results and filter
        base, ext = os.path.splitext(results)
        gene_list_results = ''.join([base, '.in_genelist', ext])
        with open(results, 'r') as in_f, open(gene_list_results, 'w') as out_f:
            reader = csv.reader(in_f, delimiter='\t')
            writer = csv.writer(out_f, delimiter='\t')
            header = reader.next()
            writer.writerow(header)

            for line in reader:
                save = True
                gene1, gene2 = line[0].split('--')
                if gene1 not in genelist or gene2 not in genelist:
                    print('Fusion %s--%s not in genelist' % (gene1, gene2), file=sys.stderr)
                    save = False

                # If fusion call passed filter, then write it to the output
                if save:
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
                print("No gene-list fusions were found, so stopping.", file=sys.stderr)
                exit()

        cmd = ['FusionInspector',
               '--fusions', results,
               '--genome_lib', '/data/%s' % args.genome_lib_dir,
               '--left_fq', '/data/%s' % args.r1,
               '--right_fq', '/data/%s' % args.r2,
               '--out_dir', os.path.join('/data/', args.output_dir, 'FusionInspector'),
               '--out_prefix', 'FusionInspector',
               '--prep_for_IGV',
               '--include_Trinity',
               '--CPU', args.CPU,
               '--cleanup']

        print('Beginning FusionInspector Run', file=sys.stderr)
        subprocess.check_call(cmd)

    os.mkdir('fusion')
    with open('/home/save-list') as f:
        for line in f:
            line = line.strip()

            # Check that output file exists
            if not os.path.exists(line):
                raise ValueError('Expected file %s not found' % line)

            else:
                shutil.move(line, os.path.join('fusion', os.path.basename(line)))


def main():
    """
    Wraps STAR-Fusion program and filters output using FusionInspector.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('--left_fq', 
                        dest='r1', 
                        required=True, 
                        help='Fastq 1')
    parser.add_argument('--right_fq', 
                        dest='r2', 
                        required=True, 
                        help='Fastq 2')
    parser.add_argument('--output_dir',
                        required=True,
                        help='Output directory')
    parser.add_argument('--genome_lib_dir',
                        required=True,
                        help='Reference genome directory')
    parser.add_argument('--CPU',
                        default='1',
                        help='Number of jobs to run in parallel')
    parser.add_argument('--genelist',
                        default='/home/gene-list')
    parser.add_argument('--skip-filter',
                        action='store_true')
    parser.add_argument('-F',
                        '--run_fusion_inspector',
                        action='store_true',
                        help='Runs FusionInspector on STAR-Fusion output')
    parser.add_argument('--clean',
                        action='store_true',
                        default=False,
                        help='Cleans output directory')
    parser.add_argument('--test',
                        action='store_true',
                        default=False)
    args = parser.parse_args()

    # Check if output directory already exists. The final permissions are set
    # to the permissions of the output directory.
    if not os.path.exists(args.output_dir):
        raise ValueError('Output directory does not exist!')

    # This is based on the Toil RNA-seq pipeline:
    # https://github.com/BD2KGenomics/toil-rnaseq/blob/master/docker/wrapper.py#L51
    try:
        print("Starting STAR-Fusion Pipeline", file=sys.stderr)
        pipeline(args)

    except subprocess.CalledProcessError as e:
        print(e.message, file=sys.stderr)
        exit(e.returncode)

    finally:
        print('Changing file ownership to user.', file=sys.stderr)
        stat = os.stat(args.output_dir)
        subprocess.check_call(['chown', '-R', '{}:{}'.format(stat.st_uid, stat.st_gid), args.output_dir])

        if args.clean:
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

                try:
                    os.remove(d)

                except OSError:
                    shutil.rmtree(d)

def main():
    """
    Wraps STAR-Fusion program and filters output using FusionInspector.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('--left_fq', 
                        dest='r1', 
                        required=True, 
                        help='Fastq 1')
    parser.add_argument('--right_fq', 
                        dest='r2', 
                        required=True, 
                        help='Fastq 2')
    parser.add_argument('--output_dir',
                        required=True,
                        help='Output directory')
    parser.add_argument('--genome_lib_dir',
                        required=True,
                        help='Genome library directory')
    parser.add_argument('--CPU',
                        default='1',
                        help='Number of cores')
    parser.add_argument('--genelist',
                        default='/home/genelist.txt')
    parser.add_argument('--skip-filter',
                        action='store_true')
    parser.add_argument('-F',
                        '--run_fusion_inspector',
                        action='store_true',
                        help='Runs FusionInspector on output')
    parser.add_argument('--clean',
                        action='store_true',
                        default=False,
                        help='Cleans directory of intermediate files.')
    parser.add_argument('--test',
                        action='store_true',
                        default=False)
    args = parser.parse_args()

    # Check if output directory already exists. The final permissions are set
    # to the permissions of the output directory.
    if not os.path.exists(args.output_dir):
        raise ValueError('Output directory does not exist!')

    # This is based on the Toil RNA-seq pipeline:
    # https://github.com/BD2KGenomics/toil-rnaseq/blob/master/docker/wrapper.py#L51
    try:
        print("Starting STAR-Fusion Pipeline", file=sys.stderr)
        pipeline(args)

    except subprocess.CalledProcessError as e:
        print(e.message, file=sys.stderr)
        exit(e.returncode)

    finally:
        print('Changing file ownership to user.', file=sys.stderr)
        stat = os.stat(args.output_dir)
        subprocess.check_call(['chown', '-R', '{}:{}'.format(stat.st_uid, stat.st_gid), args.output_dir])

        if args.clean:
            print('Cleaning output directory.', file=sys.stderr)

            delete = set()
            with open('/home/delete-list') as f:
                for line in f:
                    delete.add( line.strip() )

            # https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
            for d in delete:
                # Need to add a relative path within the docker instance
                d = os.path.join(args.output_dir, d)

                # Skip files or directories that do not exist
                if not os.path.exists(d):
                    continue

                try:
                    os.remove(d)

                except OSError:
                    shutil.rmtree(d)

if __name__ == '__main__':
    main()
