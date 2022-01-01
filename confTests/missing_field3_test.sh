#!/bin/bash

a=$(diff <(python3 webserv.py confTests/configTest3.cfg) <(cat confTests/missing_field.out))
python3 webserv.py confTests/configTest3.cfg | diff - confTests/missing_field.out 
if [[ $a == "" ]]
then
	echo "-----------------------------------------------------------------"
	echo "	Passed!, result matched!"
	echo "-----------------------------------------------------------------"
else
	echo "-----------------------------------------------------------------"	
	echo "	Failed!, Output not matched"
	echo "-----------------------------------------------------------------"
fi	