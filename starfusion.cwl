#!/usr/bin/env cwl-runner

class: CommandLineTool
label: "STAR-fusion workflow by Jacob Pfeil; CWL by Jeltje van Baren"
cwlVersion: v1.0

requirements:
  - class: DockerRequirement
    dockerPull: "ucsctreehouse/fusion:0.2.0"

baseCommand: []

inputs:

  fastq1:
    type: File
    inputBinding:
      prefix: --left-fq

  fastq2:
    type: File
    inputBinding:
      prefix: --right-fq

  outputdir:
    type: string
    default: starfusion_out 
    inputBinding:
      prefix: --output-dir

  index:
    type: File
    inputBinding:
      prefix: --genome-lib-dir

  cpu:
    type: int
    default: 8
    inputBinding:
      prefix: --CPU

  genelist:
    type: File?
    inputBinding:
      prefix: --genelist

  skip_filter:
    type: boolean
    default: False
    inputBinding:
      prefix: --skip-filter

  inspect:
    type: boolean
    default: False
    inputBinding:
      prefix: --run-fusion-inspector

  save_intermediates:
    type: boolean
    default: False
    inputBinding:
      prefix: --save-intermediates

  root-ownership:
    type: boolean
    default: False
    inputBinding:
      prefix: --root-ownership

  test:
    type: boolean
    default: False
    inputBinding:
      prefix: --test

outputs:

  output:
    type: Directory
    outputBinding:
       glob: $(inputs.outputdir)




