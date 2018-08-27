install:
	conda install python=3.6 flask requests -y
	@test -d ${HOME}/.local/share || mkdir ${HOME}/.local/share
	cp -r neutuse ${HOME}/.local/share/
	cp neutuse/run.sh ${CONDA_PREFIX}/bin/neutuse
	chmod a+x ${CONDA_PREFIX}/bin/neutuse
	@echo 'neutuse successfully installed at '${CONDA_PREFIX}'/bin/neutuse'
	@echo 'neutuse --help for help'
 
.PHONY: install
