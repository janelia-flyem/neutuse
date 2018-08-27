#!/bin/bash

NEUTUSE=${HOME}/.local/share/neutuse

source activate neutuse
cd ${NEUTUSE}
python neutuse.py $*
