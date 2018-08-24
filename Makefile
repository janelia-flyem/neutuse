clean:
	conda remove -n neutuse --all -y
	rm -r ${HOME}/.local/share/neutuse
	sudo rm /usr/local/bin/neutuse

install:
	#conda create --no-default-packages -n neutuse python=3.6 flask requests -y
	test -d ${HOME}/.local/share || mkdir ${HOME}/.local/share
	cp -r neutuse ${HOME}/.local/share/
	sudo cp neutuse/run.sh /usr/local/bin/neutuse
	sudo chmod a+x /usr/local/bin/neutuse
	echo 'neutuse successfully installed at /usr/local/bin'
	echo 'neutuse --help for help'
 
.PHONY: install clean
