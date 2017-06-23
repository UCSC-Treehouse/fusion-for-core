# Fusion detection DockerFile using STAR-Fusion and FusionInspector software
# https://github.com/STAR-Fusion/STAR-Fusion/wiki
# https://github.com/FusionInspector/FusionInspector

FROM ubuntu:16.04

MAINTAINER Jacob Pfeil, jpfeil@ucsc.edu

# Update and install required software
RUN apt-get update --fix-missing

RUN apt-get install -y python zlib1g-dev gzip perl libdb-dev dpkg build-essential \
                       make unzip libtbb-dev libncurses-dev apt-utils

# Perl libraries
RUN cpan App::cpanminus && cpanm Set::IntervalTree && cpanm DB_File && cpanm URI

WORKDIR /opt

# java
RUN echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main" | tee /etc/apt/sources.list.d/webupd8team-java.list && \
    echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main" | tee -a /etc/apt/sources.list.d/webupd8team-java.list && \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys EEA14886 && \
    apt-get update && \
    echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections && \
    apt-get install -y oracle-java8-installer

# htslib 1.3
RUN wget -qO- https://github.com/samtools/htslib/releases/download/1.3/htslib-1.3.tar.bz2 | tar xj && \
    cd htslib-1.3 && ./configure && make && cd /opt

# samtools 1.3.1
RUN wget -qO- https://downloads.sourceforge.net/project/samtools/samtools/1.3.1/samtools-1.3.1.tar.bz2 | tar xj && \
    cd samtools-1.3.1 && ./configure && make && cd /opt

# STAR
RUN wget -qO- https://github.com/alexdobin/STAR/archive/2.5.2b.tar.gz | tar xz

# Download STAR-Fusion
RUN wget -qO- https://github.com/STAR-Fusion/STAR-Fusion/releases/download/v1.0.0/STAR-Fusion-v1.0.0.FULL.tar.gz | tar xz

ENV PATH "/opt/samtools-1.3.1:/opt/htslib-1.3:/opt/STAR-2.5.2b/bin/Linux_x86_64:/opt/STAR-Fusion-v1.0.0:$PATH"

# FusionInspector
RUN wget -qO- https://github.com/FusionInspector/FusionInspector/releases/download/v1.0.1/FusionInspector-v1.0.1.FULL.tar.gz | tar xz

# Trinity
RUN wget -qO- https://github.com/trinityrnaseq/trinityrnaseq/archive/Trinity-v2.4.0.tar.gz | tar xz && \
    cd trinityrnaseq-Trinity-v2.4.0 && make && cd /opt

# gmap
RUN wget -qO- http://research-pub.gene.com/gmap/src/gmap-gsnap-2016-11-07.tar.gz | tar xz && \
    cd gmap-2016-11-07 && ./configure && make && make check && make install && cd /opt

# bowtie
RUN wget https://downloads.sourceforge.net/project/bowtie-bio/bowtie2/2.3.1/bowtie2-2.3.1-linux-x86_64.zip && \
    unzip bowtie2-2.3.1-linux-x86_64.zip && chmod +x /opt/bowtie2-2.3.1/bowtie2*

# FusionInspector needs the TRINITY_HOME environment variable
ENV TRINITY_HOME "/opt/trinityrnaseq-Trinity-v2.4.0/"
ENV PATH "/opt/bowtie2-2.3.1:/opt/trinityrnaseq-Trinity-v2.4.0:/opt/FusionInspector-v1.0.1:$PATH"

# Add wrapper scripts
COPY star_fusion_pipeline.py /opt/star_fusion_pipeline.py
COPY gene-list /home/gene-list
COPY save-list /home/save-list
COPY delete-list /home/delete-list

# Data processing occurs at /data
WORKDIR /data

ENTRYPOINT ["python", "/opt/star_fusion_pipeline.py"]
CMD ["-h"]
