
STAR-Fusion for Treehouse RNA-seq analysis
====================


### Overview

Gene fusions play a major role in tumorigenesis, so it is crucial that Treehouse has a pipeline for detecting them. We have built a docker container that runs [STAR-Fusion](https://github.com/STAR-Fusion/STAR-Fusion/wiki) and filters the output against a list of known cancer fusion genes. 

### Docker and usage

##### Image located on hub.docker.com

REPOSITORY: jpfeil/star-fusion

TAG: 0.0.1

IMAGE ID: 520e7a15847b


##### Input files

The pipeline requires paired-end fastq files, the output directory, and the genome library directory. The genelist is already baked into the docker container, but there is an option to include a different genelist. Please refer to the STAR-Fusion documentation for creating a genome library. You can also find a prebuilt genome library here: `http://ceph-gw-01.pod/references/STARFusion-GRCh38gencode23.tar.gz` 

```
usage: star_fusion_pipeline.py [-h] --left_fq R1 --right_fq R2 --output_dir
                               OUTPUT_DIR --genome_lib_dir GENOME_LIB_DIR
                               [--CPU CPU] [--genelist GENELIST]
                               [--skip_filter] [--test]

Wraps STAR-Fusion program and filters output.

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
  --test

```


##### Run command
```
docker run -it --rm -v `pwd`:/data jpfeil/star-fusion:0.0.1 \
                                   --left_fq 1.fq.gz \
                                   --right_fq 2.fq.gz \
                                   --output_dir fusion_output \
                                   --CPU `nproc` \
                                   --genome_lib_dir STARFusion-GRCh38gencode23
```

### **Output**

There will be many files in the output directory, but you can find the fusion calls in these files:

- `star-fusion.fusion_candidates.final.abridged`
- `star-fusion.fusion_candidates.final.in_genelist.abridged`

The second file contains fusion calls were both fusion partners are in the genelist.
