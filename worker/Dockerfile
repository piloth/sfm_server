FROM ubuntu:20.04

RUN apt update \
&& DEBIAN_FRONTEND=noninteractive apt install -y \
        vim \
        python3 \
        python3-pip \
        openssh-client \
        libopencv-dev

RUN pip3 install \
        opencv-python \
        opencv-contrib-python \
        numpy \
	paramiko \
        commandr \
	plyfile

ADD scripts /var/scripts
