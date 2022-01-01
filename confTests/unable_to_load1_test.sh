#!/bin/bash

a=$(diff <(python3 webserv.py nofile) <(cat confTests/unable_to_load.out))
python3 webserv.py nofile| diff - confTests/unable_to_load.out 
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