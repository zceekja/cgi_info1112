python3 webserv.py configTest.cfg &
PID=$!
sleep 1
a=$(diff <(curl -I 127.0.0.1:8070/ 2> /dev/null | grep 'Type') <(cat myTests/index_type_expected.out))
curl -I 127.0.0.1:8070/ 2> /dev/null | grep 'Type' | diff - myTests/index_type_expected.out 

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
kill $PID