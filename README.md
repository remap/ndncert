ndncert
=============

utility for initial NDN testbed trust management

as of writing, basic REST API in place. 

see doc/ for specification

see app/ for model/view/control 

Usage:
=============

on server (borges): 

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

To Do:
=============

-curl -i localhost:5000/ndn/auth/v1.0/keys/new

-store/read from database instead of dict
-email
-UI
-enable user flow

then:

-give API to Alex A for op scripting