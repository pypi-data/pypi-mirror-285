#!/bin/bash
WD=$PWD;
#PIP_NO_BINARY="" cd ~/sdrterm && python -m pip install build twine --upgrade && python -m build && twine check dist/* && twine upload dist/*
#export DSD_CMD="/home/peads/dsd/build/dsd -q -i - -o /dev/null -n";
deactivate;
cd ~/.virtualenvs/ && . .venv/bin/activate && PIP_NO_BINARY="scipy,numpy" pip install sdrterm[gui] --upgrade && cd /tmp \
  && cp ~/sdrterm/*.sh . && DSD_CMD="/home/peads/dsd/build/dsd -q -i - -o /dev/null -n" NO_CLEAN=1 ./test.sh && deactivate;
cd $WD;
