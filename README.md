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

curl -i localhost:5000/ndn/auth/v1.1/candidates/<string:inst_str>

will return all user candidates with (case-insensitive) 'institution string' (UCI, UCLA, etc)

then, 

curl -i localhost:5000/ndn/auth/v1.1/candidates/<string:email>/addcert/<string:cert>

will add a (base64 encoded) cert to the specified user email. 

that's it ! 

curl -i localhost:5000/ndn/auth/v1.1/debug

is useful for just dumping the entire mongodb contents. 


To Do:
=============

* add ndn-name prefix -> operator email routing
* write certification shell script (to interactively and/or auto-sign new pubkeys)
* do final email delivery of cert (likely in zip to ensure no corruption)