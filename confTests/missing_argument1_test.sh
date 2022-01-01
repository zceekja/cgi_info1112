#!/bin/bash

a=$(diff <(python3 webserv.py ) <(cat confTests/missing_argument.out))
python3 webserv.py | diff - confTests/missing_argument.out 
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