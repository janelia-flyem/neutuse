#Desciption
neutuse is a flexibale computing service frame work.

#Installation
##install conda

##install neutuse
git clone https://github.com/ephemera2015/computing_service.git
cd neutuse
make install

#Usage
##Run taskmanager
neutuse run taskmanaer [addr]
default addr is 127.0.0.1:5000, you can open brower type 127.0.0.1:5000/client to moniter the system

##Run service
neutuse run service {name} [taskmanager_addr]
name specify service id
currently only skeletonize is available
Make sure taskmanager is running at taskmanager_addr, default it's 127.0.0.1:5000

##post tasks
see tests/post_skeletonize.py

