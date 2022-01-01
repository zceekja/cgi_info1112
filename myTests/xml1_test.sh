python3 webserv.py configTest.cfg &
PID=$!
sleep 1
a=$(diff <(curl 127.0.0.1:8070/bold.xml 2> /dev/null) <(cat myTests/xml_expected.out))
curl 127.0.0.1:8070/bold.xml 2> /dev/null | diff - myTests/xml_expected.out 
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