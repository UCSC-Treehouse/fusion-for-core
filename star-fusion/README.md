
STAR-Fusion for Treehouse RNA-seq analysis
====================


### Overview

Gene fusions play a major role in tumorigenesis, so it is crucial that Treehouse has a pipeline for detecting them. We have built a docker container that runs [STAR-Fusion](https://github.com/STAR-Fusion/STAR-Fusion/wiki) and filters the output against a list of known cancer fusion genes. There is also an option to run additional filters and generate *de novo* assembled fusion transcripts using the [FusionInspector](https://github.com/FusionInspector/FusionInspector/wiki/Home/5fb0116687e9f80a7e926e55657b46392b781f64) program.

### Docker and usage

##### Image located on hub.docker.com

REPOSITORY: jpfeil/star-fusion

TAG: 0.1.0

IMAGE ID: bb0c8be35574


##### Input files

The pipeline requires paired-end fastq files, the output directory, and the genome library directory. The genelist is already baked into the docker container, but there is an option to include a different genelist. Please refer to the STAR-Fusion documentation for creating a genome library. You can also find a prebuilt genome library here: `http://ceph-gw-01.pod/references/STARFusion-GRCh38gencode23.tar.gz` 

```
usage: star_fusion_pipeline.py [-h] --left_fq R1 --right_fq R2 --output_dir
                               OUTPUT_DIR --genome_lib_dir GENOME_LIB_DIR
                               [--CPU CPU] [--genelist GENELIST]
                               [--skip_filter] [-F] [--test]

Wraps STAR-Fusion program and filters output using FusionInspector.

optional arguments:
  -h, --help            show this help message and exit
  --left_fq R1          Fastq 1
  --right_fq R2         Fastq 2
  --output_dir OUTPUT_DIR
                        Output directory
  --genome_lib_dir GENOME_LIB_DIR
                        Genome library directory
  --CPU CPU             Number of cores
  --genelist GENELIST
  --skip_filter
  -F, --run_fusion_inspector
                        Runs FusionInspector on output
  --test
```


##### Run command
```
docker run -it --rm -v `pwd`:/data jpfeil/star-fusion:0.1.0 \
                                   --left_fq 1.fq.gz \
                                   --right_fq 2.fq.gz \
                                   --output_dir fusion_output \
                                   --CPU `nproc` \
                                   --genome_lib_dir STARFusion-GRCh38gencode23
                                   --run_fusion_inspector
```

### **Output**

There will be many files in the output directory, but you can find the fusion calls here:

- `star-fusion.fusion_candidates.final.abridged.FFPM`
- `star-fusion.fusion_candidates.final.in_genelist.abridged.FFPM`

The second file contains fusion calls where both fusion partners are in the gene-list. If the pipeline is run with the --run_fusion_inspector flag, then there will also be a separate FusionInspector directory that contains fusion calls that passed the FusionInspector filter. FusionInspector is also configured to *de novo* assemble fusion transcripts using Trinity and to create IGV input files for viewing fusion sequences.

* FusionInspector predictions 
  * `FusionInspector/FusionInspector.fusion_predictions.final.abridged.FFPM`
* *de novo* assembled transcripts
  * `FusionInspector/FusionInspector.gmap_trinity_GG.fusions.fasta`
* IGV input files
  * `FusionInspector/FusionInspector.fa`
  * `FusionInspector/FusionInspector.gtf`
  * `FusionInspector/FusionInspector.junction_reads.bam`
  * `FusionInspector/FusionInspector.spanning_reads.bam`

FusionInspector predictions with a combined FFPM > 0.1 are considered significant.
