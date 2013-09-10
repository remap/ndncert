ndncert
=============

utility for initial NDN testbed trust management

as of writing, basic REST API in place. 

see doc/ for specification

see app/src for model/view/control in development

see app/deploy/ for 'production' version

Usage:
=============

on server:

	python cert.py 

on client (script):

	curl -i localhost:5000/ndn/auth/v1.0/users/

	curl -i localhost:5000/ndn/auth/v1.0/certs/

	curl -i localhost:5000/ndn/auth/v1.0/keys/

will list all users, certs, keys. 

appending an email after the user/cert/key prefix, will return the value. IE - 

	curl -i localhost:5000/ndn/auth/v1.0/users/[email]

	curl -i localhost:5000/ndn/auth/v1.0/certs/[email]

	curl -i localhost:5000/ndn/auth/v1.0/keys/[email]
	
for more examples, see 'cm_scratch.txt'


To Do:
=============

* add ndn-name prefix -> operator email routing
* write certification shell script (to interactively and/or auto-sign new pubkeys)
