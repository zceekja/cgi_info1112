#!/bin/bash

declare -i x=1

for i in confTests/*test.sh
do
	echo  Test $x $i
	./$i
	echo ""
	x=$(( x + 1))
	sleep 0.5
done

for i in myTests/*test.sh
do
	echo  Test $x $i
	./$i
	echo ""
	x=$(( x + 1))

done