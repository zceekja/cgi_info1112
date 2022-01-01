python3 webserv.py configTest.cfg &
PID=$!
sleep 1
a=$(diff <(curl -I 127.0.0.1:8070/cgibinTest/cgi_custom_status 2> /dev/null | grep 'HTTP') <(cat myTests/cgi_custom_status_header_expected.out))
curl -I 127.0.0.1:8070/cgibinTest/cgi_custom_status 2> /dev/null | grep 'HTTP' | diff - myTests/cgi_custom_status_header_expected.out 
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