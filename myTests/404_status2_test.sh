python3 webserv.py configTest.cfg &
PID=$!
sleep 1
a=$(diff <(curl -I 127.0.0.1:8070/cgibin/a 2> /dev/null | grep 'HTTP') <(cat myTests/404_status_expected.out))
curl -I 127.0.0.1:8070/cgibin/a 2> /dev/null | grep 'HTTP' | diff - myTests/404_status_expected.out 
echo $a
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