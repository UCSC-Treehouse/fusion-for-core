
STAR-Fusion for Treehouse RNA-seq analysis
====================


### Overview

Gene fusions play a major role in tumorigenesis, so it is crucial that Treehouse has a pipeline for detecting them. We have built a docker container that runs [STAR-Fusion](https://github.com/STAR-Fusion/STAR-Fusion/wiki) and filters the output against a list of known cancer fusion genes. There is also an option to run additional filters and generate *de novo* assembled fusion transcripts using the [FusionInspector](https://github.com/FusionInspector/FusionInspector/wiki/Home/5fb0116687e9f80a7e926e55657b46392b781f64) program.

### Docker and usage

##### Image located on hub.docker.com

REPOSITORY: ucsctreehouse/fusion

TAG: 0.3.0


##### Input files

The pipeline requires paired-end fastq files, the output directory, and the genome library directory. The genelist is already baked into the docker container, but there is an option to include a different genelist. Please refer to the STAR-Fusion documentation for creating a genome library. 

```
Wraps STAR-Fusion program and filters output using FusionInspector.

optional arguments:
  -h, --help            show this help message and exit
  --left-fq R1          Fastq 1
  --right-fq R2         Fastq 2
  --output-dir OUTPUT_DIR
                        Output directory
  --tar-gz              Compresses output directory to tar.gz file
  --genome-lib-dir GENOME_LIB_DIR
                        Reference genome directory (can be tarfile)
  --CPU CPU             Number of jobs to run in parallel
  --genelist GENELIST
  --skip-filter         Skips gene-list filter
  -F, --run-fusion-inspector
                        Runs FusionInspector on STAR-Fusion output
  --star-fusion-results STAR_FUSION_RESULTS
                        Skips STAR-Fusion and runs FusionInspector
  --save-intermediates  Does not delete intermediate files
  --root-ownership      Does not change file ownership to user
  --test                Runs the pipeline with dummy files
  --debug               Prints tool command line arguments
```


##### Run command
```
docker run -it --rm -v `pwd`:/data ucsctreehouse/fusion:0.3.0 \
                                   --left-fq 1.fq.gz \
                                   --right-fq 2.fq.gz \
                                   --output-dir fusion_output \
                                   --genome-lib-dir STARFusion-GRCh38gencode23 \
                                   --run-fusion-inspector
```

### **Output**
STAR-Fusion Output
* STAR-Fusion candidates and fusion fragments per million mapped read values
    * star-fusion-non-filtered.final
* Fusions where donor and acceptor genes passed the gene-list filter
    * star-fusion-gene-list-filtered.final

FusionInspector Output
* FusionInspector candidates and fusion fragments per million mapped read values where donor and acceptor passed gene-list filter
    * fusion-inspector-results.final
* IGV input files for visualization
    * FusionInspector.fa
    * FusionInspector.gtf
    * FusionInspector.junction_reads.bam
    * FusionInspector.spanning_reads.bam

Fusion predictions with a large anchor support (YES_LDAS) and total FFPM > 0.1 are considered significant.
