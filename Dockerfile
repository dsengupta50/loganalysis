# specify a base image
FROM ubuntu:latest

# set a working directory
WORKDIR /usr/loganalysis

# copy some files from local machine that is required for the install
#COPY ./package.json ./

# install some dependencies (pyod, tensorflow, keras)
RUN apt update
RUN apt install python3-pip -y
RUN pip3 install pyod
RUN pip3 install tensorflow
RUN pip3 install keras


# copy everything else
#COPY ./ ./

# default command
#CMD ["npm", "start"]