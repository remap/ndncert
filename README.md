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


Development Notes:
==================

the host for cert.ndn.ucla.edu is 164.67.204.101
path is /var/www/ndncert (which corresponds to github app/deploy/)
contact nano@remap.ucla.edu if you want access. 

to work locally, i ssh -L 27017:localhost:27017 164.67.204.101

so i can use a local mongodb viewer (like rockmongo) to control mongo storage while debugging. 


