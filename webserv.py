import sys
import socket
import os
import signal
import time

http_error404 = '<html>\n<head>\n\t<title>404 Not Found</title>\n</head>\n<body bgcolor="white">\n<center>\n\t<h1>404 Not Found</h1>\n</center>\n</body>\n</html>\n'

staticfiles =""
cgibin = ""
port = 0
executable_path = ""
headers = {}
respond = {}
request = ""
post_data = ""
cgi_env = {}

####################################
#								   #
#	timeout handler                #   
#								   #
####################################
def handler(signum, frame):  
	raise Exception("end of time")


####################################
#								   #
#	Check type of request          #   
#								   #
####################################
def checkType(line):

	tmp = line.strip("\n")
	if tmp.endswith(".txt"):
		return "text/plain"
	elif tmp.endswith(".js"):
		return "application/javascript"
	elif tmp.endswith(".css"):
		return "text/css"
	elif tmp.endswith(".png"):
		return "image/png"
	elif tmp.endswith(".jpg") or tmp.endswith(".jpeg"):
		return "image/jpeg"
	elif tmp.endswith(".xml"):
		return "text/xml"
	else:
		return "text/html"

#######################################
#								      #
#	Store header field in headers     #   
#								   	  #
#######################################
def parse_headers(data):
	global headers
	global post_data
	headers = {}
	post_data = ""
	for line in data[1:]:
		line = line.split(":")
		if len(line) >1:
			headers[line[0]] = line[1].strip(" ")
		else:
			post_data += line[0]

#############################################
#								      		#
#	 Extract querry string               	#
#								   	  		#
#############################################
def parse_query(string):
	if string == "":
		return {}
	output = {}
	tmp = string.strip("\n")
	tmp = tmp.split("&")
	for i in tmp:
		pair = i.split("=")
		output[pair[0]]= pair[1]

	return output
#############################################
#								      		#
#	 Check whether querry string included  	#
#								   	  		#
#############################################
def is_querry(line):
	path = line
	if '?' in path:
		return True
	else:
		return False
#################################################
#								      			#
#	 Check whethe path request  isCGI program   #
#									   	  		#
#################################################
def is_cgi(line):


	line = line.split("/")
	if line[1] == cgibin.strip("./"):
		return True
	else:
		return False
#############################################
#								      		#
#	 Check for CGI program header           #
#								   	  		#
#############################################

def cgi_header_handler():

	global respond
	if "\n\n" in respond['data'].decode():
		cgi_headers = respond['data'].decode().split("\n\n")[0]
		cgi_headers = cgi_headers.split("\n")
		for i in cgi_headers:
			if i.lower().startswith("Content-Type".lower()):
				respond['type'] = i.split(':')[1].strip()
			elif i.lower().startswith("Status".lower()):
				respond['status'] = i.split(':')[1].strip().split(' ')[0]
				respond['message'] = ""
				for j in range(1,len(i.split(':')[1].strip().split(' '))):
					respond['message'] +=  i.split(':')[1].strip().split(' ')[j] +" "
				respond['message'] = respond['message'].strip()
		respond['data'] = respond['data'].decode().split("\n\n")[1].strip() + "\n"
		respond['data'] = respond['data'].encode()

#############################################
#								      		#
#	 Excecute CGI program                   #
#								   	  		#
#############################################
def run_cgi(path):
	global cgi_env
	if not os.path.isfile("."+path.split("?")[0]):
		respond["status"] = 404
		respond["message"] = "File not found"
		return http_error404.encode()
	if 'Accept' in headers.keys():
		cgi_env['HTTP_ACCEPT'] = headers["Accept"]
	if 'Host' in headers.keys():
		cgi_env['HTTP_HOST'] = headers["Host"]
	if 'User-Agent' in headers.keys():
		cgi_env['HTTP_USER_AGENT'] = headers["User-Agent"]

	if 'Accept-Encoding' in headers.keys():
		cgi_env['HTTP_ACCEPT_ENCODING'] = headers['Accept-Encoding']
	cgi_env['REMOTE_ADDRESS'] = "" 
	cgi_env['REMOTE_PORT'] = ""
	cgi_env['REQUEST_METHOD'] = respond["request"]
	cgi_env['REQUEST_URI'] = respond["uri"]
	cgi_env['SERVER_ADDR'] = socket.gethostbyname(socket.gethostname())
	cgi_env['SERVER_PORT'] = str(port)

	if 'Content-Type' in headers.keys():
		cgi_env['CONTENT_TYPE'] = headers["Content-Type"]

	else:
		cgi_env['CONTENT_TYPE'] = respond["type"]

	cgi_env['CONTENT_LENGTH'] = ""
	if request == "GET":
		if is_querry(path):
			cgi_env['QUERY_STRING'] = path.split("?")[1]
			path = path.split("?")[0]
	elif request == "POST":
		cgi_env['QUERY_STRING'] = post_data
		cgi_env['CONTENT_LENGTH'] = str(len(post_data))

	r, w = os.pipe()
	
	pid = os.fork()
	if pid == 0:
		os.close(r)#   # Child process
		os.dup2(w,1) 
		os.execve( executable_path,[executable_path, cgibin+ "/"+path.split("/")[2]], cgi_env)
		exit(0)
	elif pid == -1: # Error during os.fork()
		print("Fork failed", file=stderr)
	else: # Parent process
		wval = os.wait()
		os.close(w)
		if wval[1] >> 8:
			respond["status"] = 500
			respond["message"] = "Internal Server Error"
			os.close(r)
			print("hello")
			return "".encode();
		else:

			string = os.read(r,5000)
			respond["status"] = 200
			respond["message"] = "OK"
			os.close(r)
			return string
#
#############################################
#								      		#
#	 Handle GET, HEAD and POST request      #
#								   	  		#
#############################################
def do_request(data):
	global respond
	global request
	respond = {
		"request": "",
		"uri": "",
		"data": "",
		"status": 200,
		"message": "OK",
		"type": "text/html",
		"length": 0,
		"query_strings": {}

	}
	try:
		request = data[0].split(" ")[0]
		respond["request"] = data[0].split(" ")[0]
	except:
		print("Could not extract command")
		return ""

	respond["type"] = checkType(data[0].split(" ")[1].split("/")[-1])

	# HANDLE GET/HEAD REQUEST
	if request == "GET" or request == "HEAD" or request == "POST":

		query = ""
		whole_path = data[0].split(" ")[1]
		respond["uri"] = whole_path
		#CHECK CGI
		if is_cgi(whole_path):

			respond["data"] = run_cgi(whole_path)
			cgi_header_handler()
			return respond
		#CHECK QUERRY
		if is_querry(whole_path):
			whole_path = whole_path.split("?")
			path = whole_path[0].split("/")
			query = whole_path[1]

		else:
			path = whole_path.split("/")

		#CHECK index.html
		if  path[1] == "":

			try:
				f = open(staticfiles+"/index.html","r")
				f.close()
			except:
				respond["status"] = 404
				respond["message"] = "File not found"
				respond["data"] = http_error404.encode()

				return respond
			content = ""
			f = open(staticfiles+"/index.html","r")
			line = f.readline()
			while line != "":
				content += line
				line = f.readline()
			f.close()
			respond["data"] = content.encode()
			return 	respond
		#CHECK files
		else:
			try:
				f = open(staticfiles+"/"+path[1],"r")
				f.close()
			except:
				respond["status"] = 404
				respond["message"] = "File not found"
				respond["data"] = http_error404.encode()

				return respond

			bainary_content = b""
			content = ""
			if respond["type"] == "image/png" or respond["type"] == "image/jpeg":
				f = open(staticfiles+"/"+path[1],"rb")
				bainary_content = f.read()
				f.close()
				respond["data"] = bainary_content
			else:
				f = open(staticfiles+"/"+path[1],"r")
				line = f.readline()
				while line != "":
					content += line
					line = f.readline()
				f.close()
				respond["data"] = content.encode()
			respond["query_strings"] = parse_query(query)
			respond["status"] = 200
			respond["message"] = "OK"
			return respond

	else:
		respond["status"] = 404
		respond["message"] = "File not found"

		respond["data"] = http_error404.encode()
		return respond
#############################################
#								      		#
#	 Create server 					        #
#								   	  		#
#############################################
def server():
	global cgi_env
	signal.signal(signal.SIGALRM, handler)
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


	try:
		serverSocket.bind(("", port)) # blind address and port
		serverSocket.listen(10) 
		while(1):
			conn, addr = serverSocket.accept()  # Waiting for connection
			pid = os.fork()  # fork each connection that connect
			if pid == 0:  # Child process
				cgi_env = {}
				cgi_env['REMOTE_ADDRESS'] = str(addr[0])
				cgi_env['REMOTE_HOST'] = str(addr[0]) 
				serverSocket.close()
				signal.alarm(30) # after 30 second if no respond from client cut connection
				try:
					readData = conn.recv(5000).decode()
				except:
					os._exit(0)
				data = readData.split("\n")
				parse_headers(data) 
				respond = do_request(data)
				data = "HTTP/1.1 {} {}\n".format(respond["status"], respond["message"])
				data += "Content-Type: {}\n".format(respond["type"])
				data += "Content-Length: {}\n".format(len(respond["data"]))
				data += "\n"
				data =  data.encode()
				conn.sendall(data)
				conn.send(respond["data"])

				conn.close() 
				os._exit(0)

			else: # Parent process
				conn.close() #close parent connection

	except:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)
#############################################
#								      		#
#	 Read Configuration File 			    #
#								   	  		#
#############################################
def read_conf():
	global staticfiles
	global cgibin
	global port
	global executable_path
	conf = {}
	#Check for missing configuration argument
	if len(sys.argv) <2:
		print("Missing Configuration Argument")
		exit()
	#Check if file is can open
	try:
		f = open(sys.argv[1],"r")
		f.close()
	except:
		print("Unable To Load Configuration File")
		exit()
	#Check if file contain all 4 properties
	f = open(sys.argv[1],"r")
	line = f.readline()
	while line != "":
		pieces = line.split("=")
		if len(pieces) <2:
			print("Misssing Field From Configuration")
			exit()
		pieces[1]= pieces[1].strip("\n")
		if len(pieces[1]) <1:
			print("Misssing Field From Configuration")
			exit()
		else:
			conf[pieces[0]] = pieces[1]
			line = f.readline()
	#Check if file contain all 4 properties
	if not("staticfiles" in conf) or not("cgibin" in conf) or not("port" in conf) or not("exec" in conf):
		print("Missing Field From Configuration File")
		exit();	


	staticfiles = conf.get("staticfiles")
	cgibin = conf.get("cgibin")
	port = int(conf.get("port"))
	executable_path = conf.get("exec")


#############################################
#								      		#
#	 Main program						    #
#								   	  		#
#############################################
def main():
	read_conf() # Read configuration
	server() # run server

if __name__ == '__main__':
	main()