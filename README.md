# Desciption

neutuse is a flexibale computing service frame work.

# Installation
## install conda

1)Install conda, see https://conda.io/docs/  
2)conda create -n neutuse

## install neutuse

git clone https://github.com/ephemera2015/neutuse.git   
cd neutuse
source activate neutuse
make install

# Usage
## Run taskmanager

neutuse run taskmanaer [addr]   
default addr is 127.0.0.1:5000, you can open brower type 127.0.0.1:5000/client to moniter the system

## Run service

neutuse run service {name} [taskmanager_addr]   
Name specifies service id, currently only skeletonize is available   
Make sure taskmanager is running at taskmanager_addr, default it's 127.0.0.1:5000

## post tasks
See tests/post_skeletonize.py

