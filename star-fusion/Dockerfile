# STAR-Fusion Dockerfile 
# https://github.com/STAR-Fusion/STAR-Fusion/wiki

FROM ubuntu:16.04

MAINTAINER Jacob Pfeil, jpfeil@ucsc.edu

RUN apt-get update --fix-missing && \
    apt-get install -y python zlib1g-dev gzip perl libdb-dev \
                       build-essential wget make git

# Install perl libraries 
RUN cpan App::cpanminus && cpanm Set::IntervalTree && cpanm DB_File && cpanm URI 

WORKDIR /home

# Need STAR binary
RUN wget https://github.com/alexdobin/STAR/archive/2.5.2b.tar.gz && \
    tar -xzf 2.5.2b.tar.gz && \
    git clone --recursive https://github.com/STAR-Fusion/STAR-Fusion.git

# Add STAR and STAR-Fusion to path
ENV PATH "/home/STAR-2.5.2b/bin/Linux_x86_64/:/home/STAR-Fusion/:$PATH"

# Add wrapper scripts 
ADD star_fusion_wrapper.sh /home/star_fusion_wrapper.sh
ADD star_fusion_pipeline.py /home/star_fusion_pipeline.py
ADD genelist.txt /home/genelist.txt

# Data processing occurs at /data
WORKDIR /data

ENTRYPOINT ["sh", "/home/star_fusion_wrapper.sh"]
CMD ["-h"]
