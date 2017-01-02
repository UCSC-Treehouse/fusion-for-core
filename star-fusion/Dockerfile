# STAR-Fusion Dockerfile 
# https://github.com/STAR-Fusion/STAR-Fusion/wiki

FROM ubuntu:16.04

MAINTAINER Jacob Pfeil, jpfeil@ucsc.edu

# Update and install required software
RUN apt-get update --fix-missing && \
    apt-get install -y python zlib1g-dev gzip perl libdb-dev build-essential wget make git \ 
                       samtools default-jre && \
    cpan App::cpanminus && cpanm Set::IntervalTree && cpanm DB_File && cpanm URI 

WORKDIR /home

# Install bgzip, STAR, STAR-Fusion, FusionInspector, and Trinity
RUN wget -qO- https://github.com/samtools/htslib/releases/download/1.3/htslib-1.3.tar.bz2 | tar xj && \
    cd htslib-1.3 && ./configure && make && cd /home && \
    wget -qO- https://github.com/alexdobin/STAR/archive/2.5.2b.tar.gz | tar xz && \
    git clone --recursive https://github.com/STAR-Fusion/STAR-Fusion.git && \
    wget -qO- https://github.com/FusionInspector/FusionInspector/releases/download/v0.8.0/FusionInspector_v0.8.FULL.tar.gz | tar xz && \
    wget -qO- wget https://github.com/trinityrnaseq/trinityrnaseq/archive/Trinity-v2.3.2.tar.gz | tar xz && \
    cd trinityrnaseq-Trinity-v2.3.2 && make && cd /home && \
    wget -qO- wget http://research-pub.gene.com/gmap/src/gmap-gsnap-2016-11-07.tar.gz | tar xz && \
    cd gmap-2016-11-07 && ./configure && make && make check && make install

# Add tools to path
ENV PATH "/home/htslib-1.3/:/home/STAR-2.5.2b/bin/Linux_x86_64/:/home/STAR-Fusion/:/home/FusionInspector_v0.8/:$PATH"

# FusionInspector needs the TRINITY_HOME environment variable
ENV TRINITY_HOME "/home/trinityrnaseq-Trinity-v2.3.2/"

# Add wrapper scripts 
ADD star_fusion_wrapper.sh /home/star_fusion_wrapper.sh
ADD star_fusion_pipeline.py /home/star_fusion_pipeline.py
ADD genelist.txt /home/genelist.txt

# Data processing occurs at /data
WORKDIR /data

ENTRYPOINT ["sh", "/home/star_fusion_wrapper.sh"]
CMD ["-h"]
