import os
import sys
import subprocess
import OpenSSL
import json
import random
import pwd

WD = os.path.dirname(os.path.realpath(__file__))
CERT_FILE = "selfsigned.crt"
KEY_FILE = "selfsigned.key"

def mkdir(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)

def get_directories(path):
	dirs = [os.path.join(path, item) for item in os.listdir(path)]
	if "." in dirs:
		dirs.remove(".")
	if ".." in dirs:
		dirs.remove("..")
	return dirs

def replace_value(data, values):
	if type(data) is unicode:
		data = data.encode('ascii','ignore')

	if type(data) is dict:
		res = {}
		for idx in data:
			res[idx] = replace_value(data[idx], values)
		return res

	if type(data) is str:
		res = data
		for idx in values:
			res = res.replace("$(" + idx + ")", str(values[idx]))
		return res

	return data


def create_self_signed_cert(cert_dir):
    if not os.path.exists(os.path.join(cert_dir, CERT_FILE)) or not os.path.exists(os.path.join(cert_dir, KEY_FILE)):
        # create a key pair
        k = OpenSSL.crypto.PKey()
        k.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)

        # create a self-signed cert
        cert = OpenSSL.crypto.X509()
        cert.get_subject().C = "CA"
        cert.get_subject().ST = "AutoConf"
        cert.get_subject().L = "AutoConf"
        cert.get_subject().O = "AutoConf"
        cert.get_subject().OU = "NSA"
        cert.get_subject().CN = "AutoConf"
        cert.set_serial_number(random.randint(0, 2<<160 - 1))
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(1*365*24*60*60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, 'sha256')

        open(os.path.join(cert_dir, CERT_FILE), "wt").write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert))
        open(os.path.join(cert_dir, KEY_FILE), "wt").write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, k))

        return True

    return False

if len(sys.argv) < 3:
	print "Usage %s [directory] [hostname]"
	exit()

challenges = get_directories(sys.argv[1])
challenge_id = 0

apache_configuration = """
<VirtualHost *:80>
	ServerAdmin webmaster@localhost
	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined

	ProxyRequests Off
	ProxyPreserveHost On
	%s
</VirtualHost>
"""

apache_proxy_configuration = """
	ProxyPass /%s http://127.0.0.1:%d/ retry=0 timeout=5
	ProxyPassReverse /%s http://127.0.0.1:%d/
	"""

apache_tmp = ""
ctfd_json_data = '{ "challenges" : [ %s ] }'
ctfd_json_data_tmp = ""

for challenge in challenges:
	print "Setting up '%s' ..." % challenge
	
	challenge_id += 1
	uniq_name = os.path.basename(challenge)
	compose_dir = os.path.join(WD + "/challenges/", uniq_name)
	mkdir(compose_dir)

	# Take down previous docker
	os.chdir(compose_dir)
	subprocess.call(["docker-compose", "stop"])

	# Build a new compose file
	configuration = open(os.path.join(challenge, ".config"), "rb").read()
	configuration = json.loads(configuration)
	compose_template = open(os.path.join(challenge, "docker-compose.template"), "rb").read()

	env = {
		"CHALLENGE" : uniq_name,
		"PORT" : challenge_id + 1500,
		"DOCKERFILE" : "img_" + uniq_name,
		"HOST" : sys.argv[2],
		"CURRENT_FOLDER" : challenge
	}

	configuration = replace_value(configuration, env)
	compose_content = replace_value(compose_template, env)

	open(os.path.join(compose_dir, "docker-compose.yml"), "wb").write(compose_content)

	# Build the docker image
	dockerfile_location = os.path.join(challenge, "Dockerfile")
	dockerfile_folder = challenge
	dockerfile_tag = env["DOCKERFILE"]
	subprocess.call(["docker" , "build", "-f", dockerfile_location, "-t", dockerfile_tag, dockerfile_folder])

	# Start it
	subprocess.call(["docker-compose", "up", "-d"])

	# Only add a reverse proxy configuration if it's a web challenge
	if "web-folder" in configuration:
		apache_tmp += apache_proxy_configuration % (env["CHALLENGE"], env["PORT"], env["CHALLENGE"], env["PORT"])

	# Configure the challenge data
	name = json.dumps(configuration["name"])
	category = json.dumps(configuration["category"])
	description = json.dumps(configuration["description"])
	value = configuration["value"]
	flag = json.dumps(configuration["flag"])

	ctfd_challenge_template = '{ \n  "name" : %s, \n  "category" : %s, \n  "message" : %s, \n  "value" : %d, \n  "key" : [ { "flag" : %s, "type" : "static" } ], \n  "files" : [] \n}\n'
	ctfd_json_data_tmp += ctfd_challenge_template % (name, category, description, value, flag)
	ctfd_json_data_tmp += ","

ctfd_json_data_tmp = ctfd_json_data_tmp[:-1]

# Write new Apache configuration and restart
print "Setting up the HTTP Apache configuration ..."
open("/etc/apache2/sites-available/000-default.conf", "wb").write(apache_configuration % apache_tmp)
subprocess.call(["service", "apache2", "restart"])

# Configure SSL CTFd
print "Setting up the HTTPS Apache configuration ..."
mkdir("/etc/apache2/ssl/")

# Create the SSL configuration only once to avoid overwriting things like LetsEncrypt
if create_self_signed_cert("/etc/apache2/ssl/"):
	apache_configuration_ssl = """
	<VirtualHost *:443>
		SSLEngine On
		SSLCertificateFile /etc/apache2/ssl/selfsigned.crt
		SSLCertificateKeyFile /etc/apache2/ssl/selfsigned.key

		ProxyRequests Off
		ProxyPreserveHost On
		ProxyPass / http://127.0.0.1:4000/ retry=0 timeout=5
		ProxyPassReverse / http://127.0.0.1:4000/

		RequestHeader set X-Scheme https
		RequestHeader set X-Forwarded-Proto 'https'

		ErrorLog ${APACHE_LOG_DIR}/error.log
		CustomLog ${APACHE_LOG_DIR}/access.log combined
	</VirtualHost>
	"""

	open("/etc/apache2/sites-available/default-ssl.conf", "wb").write(apache_configuration_ssl)
	subprocess.call(["a2ensite", "default-ssl.conf"])
	subprocess.call(["service", "apache2", "reload"])
	subprocess.call(["service", "apache2", "restart"])

# Fixing the 
print "Fixing folder permission for SQLite and file upload ..."
os.chdir(sys.argv[1])
subprocess.call(["/bin/sh", os.path.join(WD, "fix-www-data-permission.sh")])

print "Configuring CTFd ..."

# Creating if needed the lower priviledge user "ctfd".
ctfd_uid = -1
attempt = 0

while ctfd_uid == -1 and attempt < 3:
	attempt += 1
	try:
	    ctfd_uid = pwd.getpwnam('ctfd').pw_uid
	except KeyError:
	    os.system("useradd ctfd")

if ctfd_uid == -1:
	print "Could not create the user 'ctfd'."
	exit()

os.chdir(os.path.join(WD, "../CTFd/"))

# Data file is created before the downgrade, so it's owned by root
open("../CTFd-import/data.json", "wb").write(ctfd_json_data % ctfd_json_data_tmp)

# Make sure the folder and its content is owned by "ctfd"
os.system("chown -R ctfd:ctfd .")

# Downgrade to the "ctfd" user
os.setuid(ctfd_uid)
os.system("cp ../CTFd-import/import.py .")
subprocess.call(["python", "import.py", "../CTFd-import/data.json"])

open("serve.py", "wb").write("""
from CTFd import create_app

class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

app = create_app()
app.wsgi_app = ReverseProxied(app.wsgi_app)
app.run(debug=False, threaded=True, host="127.0.0.1", port=4000)
""")

print "Starting CTFd ..."
mkdir("CTFd/logs/")
subprocess.call(["/bin/bash", "-c", "python serve.py &>> CTFd/logs/out.log &"])



