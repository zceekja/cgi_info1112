python3 webserv.py configTest.cfg &
PID=$!
sleep 1
a=$(diff <(curl -I 127.0.0.1:8070/home.js 2> /dev/null | grep 'Type') <(cat myTests/js_type_expected.out))
curl -I 127.0.0.1:8070/home.js  2> /dev/null | grep 'Type' | diff - myTests/js_type_expected.out 

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