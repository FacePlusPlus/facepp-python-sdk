#!/bin/bash
if type python2 > /dev/null
then
	python2 cmdtool.py 
else
	python cmdtool.py
fi
