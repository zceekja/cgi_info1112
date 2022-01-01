python3 webserv.py configTest.cfg &
PID=$!
sleep 1
a=$(diff <(curl -I 127.0.0.1:8070/ 2> /dev/null | grep '200 OK') <(cat myTests/index_status_expected.out))
curl -I 127.0.0.1:8070/ 2> /dev/null | grep '200 OK' | diff - myTests/index_status_expected.out 
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