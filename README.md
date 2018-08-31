# Desciption

neutuse is a flexibale computing service frame work.

# Installation

git clone https://github.com/ephemera2015/neutuse.git   
cd neutuse   
python setup.py install

# Usage
    1) Run database:
    neutuse run database [-a ADDR] [-b BACKEND] [-d DEBUG] [-r RETRY] [-l LOG]
    ADDR: Default is 127.0.0.1:5000
    BACKEND: Backend data base, default is sqlite:test.db
    DEBUG: debug mode
    RETRY: enable retry if tasks are expired
    LOG: Log file
    
    2) Run process:
    neutuse run process NAME [-a ADDR] [-n NUMBER] [-l LOG]
    ADDR: which address the database is running
    Default ADDR is 127.0.0.1:5000
    NAME: specifies the name of process
    NUMBER: Numbers of workers
    LOG: Log file
    
    3) Post task:
    neutuse post FILE [-a ADDR]
    ADDR: which address the database is running
    Default ADDR is 127.0.0.1:5000
    FILE: File describes the task
    

