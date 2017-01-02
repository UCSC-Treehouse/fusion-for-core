#!/usr/bin/env python2.7
from __future__ import print_function
import argparse
import csv
import os
import subprocess
import sys


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
    parser.add_argument('--CPU', default='1', help='Number of cores')
    parser.add_argument('--genelist', default='/home/genelist.txt')
    parser.add_argument('--skip_filter', action='store_true')
    parser.add_argument('-F', '--run_fusion_inspector', action='store_true', help='Runs FusionInspector on output')
    parser.add_argument('--test', action='store_true', default=False)
    args = parser.parse_args()

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

        print("The gene-list filtered output is located here:\n%s" % out_f.name, file=sys.stderr)

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
                print("There are no fusions to filter with FusionInspector", file=sys.stderr)
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
               '--CPU', args.CPU]

        print('Beginning FusionInspector Run', file=sys.stderr)
        subprocess.check_call(cmd)


if __name__ == '__main__':
    main()
