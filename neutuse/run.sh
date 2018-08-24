#!/bin/bash

NEUTUSE=${HOME}/.local/share/neutuse

neutuse_help(){
    echo 'Usage:'
    echo 'For help:'
    echo 'neutuse help'
    echo 'Run taskmanager:'
    echo 'neutuse run taskmanager [addr]'
    echo "Default addr is 127.0.0.1:5000"
    echo 'Run service:'
    echo 'neutuse run service {service_name}[taskmanager addr]'
}


neutuse_run_taskmanager(){
    cd ${NEUTUSE}
    source activate neutuse
    addr="127.0.0.1:5000"
    if [ $# -ge 1 ]; then
        addr=$1
    fi
    python app.py taskmanager ${addr}  
}

neutuse_run_service(){
    cd ${NEUTUSE}
    source activate neutuse
    if [ $# -lt 1 ]; then
        echo 'please specify service name'
        exit 1
    fi
    name=$1
    if [ $# -ge 2 ]; then
        addr=$2
    else
        addr="127.0.0.1:5000"
    fi
    python app.py "service" ${name} ${addr}
}

neutuse_run(){
    case $1 in 
    taskmanager)
        shift 
        neutuse_run_taskmanager $*;;
    service)
        shift 
        neutuse_run_service $*;;
    *) neutuse_help;;
    esac
}

neutuse_main(){
    case $1 in
    help) neutuse_help ;;
    run)  shift
          neutuse_run $*;;
    *) neutuse_help;;
    esac
}
neutuse_main $*
