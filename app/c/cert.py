#!/bin/python

# dependencies - flask, flask-pymongo
# pip install Flask, Flask-PyMongo

#html/rest
from flask import Flask, jsonify, abort, make_response, request
# mail
import smtplib
from email.mime.text import MIMEText
import smtplib
import sys
import os
# data
from flask.ext.pymongo import PyMongo

import ConfigParser
config = ConfigParser.RawConfigParser()
configFile = os.path.dirname(__file__)+'../m/config.cfg'
config.readfp(open(configFile))



app = Flask(__name__)

mongo = PyMongo(app)
# replace dict w/ mongoDB. 
# just load all keys on load, and perform the same in memory tasks 
# as if using dev dict, below. 
# not ideal, but will work for now. can be updated when scale matters

users = [
    {
        'id': 1,
        'email': u'lixia@cs.ucla.edu',
        'ndn-name': u'ucla.edu/cs/lixia',
        'pubkey': u'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAtm/yyYAcs55LgbFLQHAyjs/iZJfuHV2NGLg/m0tx0s6at3GW9WaQ0q7sxUgZi/eoLrTxbq4zYCebYNIqi1p/5/PFGHI0rEnnbkM+4zmp12dAGIhAtaR+JPKcPi5pd/EhwkgETE93WUAV9GZIaFXRaUznyAmCjmux5FN94AGgzBrqJPxw+KaMdJNck4l8J5p/LhAA3ej05AS2gDd8uOCl5ho8hEpsNVQO8QbSOZhJrACWu8IBwD5g7/OCS2W/TlQBI/IvqRZ5no15R98lUh5rKP8y4V5APcJZbps7EzoygUyYD7zPFiWQWbMoOTx3gzXYTCaKNEYuVFEIx+FoJ1MsAw== nano@wifi-131-179-38-226.host.ucla.edu',
        #cert is base64 encoded binary
        'cert': u'BIICqgOyCIVmm8hfsGdZ2oni17K8iAcT3QtAC7EHSpCHZA8o2KuA3iY+3HKkgX4wMWg75mfYHWJ9CTYQDDOlu6x1jfD9x763kk5tsQiUZY/9+bkbIK0SEXujSHTUB7wqb0MVesIal82eivrUG3YcrARY1SgZRHC5L8FuTUuMdJmsXqisVD8gqAAA8vqdbmRuAPqla2V5cwD6xXVjbGEuZWR1APqlYXBwcwD6xWFsZXhuYW5vAPr9Y2NueC1hdXRvY29uZmlnAPoCtcEuTS5LAFbjBPHkaaMthRcgHXfmffRzVVlD+/CII+mWScj+MPHGAPq9/QEAUWNo/QD6jQAAAAGiA+IChcM87XwUvlfVPr7/uJ3ez892UbS5Zn3mDa7bpeP+XLwWAAK6tQUWNo/b9gACwp0oRj8AA9KmMjAwMAAD2o0AAAHiAery+p1uZG4A+qVrZXlzAPrFdWNsYS5lZHUA+qVhcHBzAPrFYWxleG5hbm8A+gK1wS5NLksAwzztfBS+V9U+vv+4nd7Pz3ZRtLlmfeYNrtul4/5cvBYAAAAAAAGaCpUwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAKcxsUOOwMUdBz66GwX/FhAami+Rj+NSgeFP4xz3iE5ibf+jPK1Svy9imzlmGeWkhM4o8p/kwa+h2lz4Td25yP7SZ/EGkg/SfvBOwErowvdK/+7/Vayw3TwCAOema5VG8NdCVAgYXT+BBLgIN9k7TaNpS4PRsvY2RnBPzIqo7TwtAgMBAAEAAASCAqoDsgiFgBYerX0TM9HaZsYcBxKNupt0UpVszdeUQrL3Rg0SuM+9azhX9i4x6Q7pNE4c4b0D+ySlop3j2EilJIb+iqRXNcb+ar46uQWQkKyi4ac6gXTCP8VBP8UpSHCajzfxDd7X3ucYQX2CvWMcd8vLxYmlXCklvw1P2TghiHFyWb1F+lUAAPL6nW5kbgD6pWtleXMA+sV1Y2xhLmVkdQD6pWFwcHMA+sVhbGV4bmFubwD6/WNjbngtYXV0b2NvbmZpZwD6pWluZm8A+gK1wS5NLksAVuME8eRpoy2FFyAdd+Z99HNVWUP78Igj6ZZJyP4w8cYA+r39AQBRY2j9APqNAAAAAaID4gKFwzztfBS+V9U+vv+4nd7Pz3ZRtLlmfeYNrtul4/5cvBYAArq1BRY2j9wZAALCnShGPwAD0qYyMDAwAAPajQAAAeIB6vL6nW5kbgD6pWtleXMA+sV1Y2xhLmVkdQD6pWFwcHMA+sVhbGV4bmFubwD6ArXBLk0uSwDDPO18FL5X1T6+/7id3s/PdlG0uWZ95g2u26Xj/ly8FgAAAAAAAZoHlTxNZXRhPjxOYW1lPmNjbngtYXV0b2NvbmZpZzwvTmFtZT48QWZmaWxpYXRpb24+QWxleGFuZGVyIEhvcm48L0FmZmlsaWF0aW9uPjxWYWxpZF90bz4xMzk3MDAzNjUxPC9WYWxpZF90bz48L01ldGE+CgAA',
        'confirmed': False
    },
    {
        'id': 2,
        'email': u'alexnano@remap.ucla.edu',
        'ndn-name': u'ucla.edu/remap/alexnano',
        'pubkey': u'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAtm/yyYAcs55LgbFLQHAyjs/iZJfuHV2NGLg/m0tx0s6at3GW9WaQ0q7sxUgZi/eoLrTxbq4zYCebYNIqi1p/5/PFGHI0rEnnbkM+4zmp12dAGIhAtaR+JPKcPi5pd/EhwkgETE93WUAV9GZIaFXRaUznyAmCjmux5FN94AGgzBrqJPxw+KaMdJNck4l8J5p/LhAA3ej05AS2gDd8uOCl5ho8hEpsNVQO8QbSOZhJrACWu8IBwD5g7/OCS2W/TlQBI/IvqRZ5no15R98lUh5rKP8y4V5APcJZbps7EzoygUyYD7zPFiWQWbMoOTx3gzXYTCaKNEYuVFEIx+FoJ1MsAw== nano@wifi-131-179-38-226.host.ucla.edu',
        #cert is base64 encoded binary
        'cert': u'BIICqgOyCIVmm8hfsGdZ2oni17K8iAcT3QtAC7EHSpCHZA8o2KuA3iY+3HKkgX4wMWg75mfYHWJ9CTYQDDOlu6x1jfD9x763kk5tsQiUZY/9+bkbIK0SEXujSHTUB7wqb0MVesIal82eivrUG3YcrARY1SgZRHC5L8FuTUuMdJmsXqisVD8gqAAA8vqdbmRuAPqla2V5cwD6xXVjbGEuZWR1APqlYXBwcwD6xWFsZXhuYW5vAPr9Y2NueC1hdXRvY29uZmlnAPoCtcEuTS5LAFbjBPHkaaMthRcgHXfmffRzVVlD+/CII+mWScj+MPHGAPq9/QEAUWNo/QD6jQAAAAGiA+IChcM87XwUvlfVPr7/uJ3ez892UbS5Zn3mDa7bpeP+XLwWAAK6tQUWNo/b9gACwp0oRj8AA9KmMjAwMAAD2o0AAAHiAery+p1uZG4A+qVrZXlzAPrFdWNsYS5lZHUA+qVhcHBzAPrFYWxleG5hbm8A+gK1wS5NLksAwzztfBS+V9U+vv+4nd7Pz3ZRtLlmfeYNrtul4/5cvBYAAAAAAAGaCpUwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAKcxsUOOwMUdBz66GwX/FhAami+Rj+NSgeFP4xz3iE5ibf+jPK1Svy9imzlmGeWkhM4o8p/kwa+h2lz4Td25yP7SZ/EGkg/SfvBOwErowvdK/+7/Vayw3TwCAOema5VG8NdCVAgYXT+BBLgIN9k7TaNpS4PRsvY2RnBPzIqo7TwtAgMBAAEAAASCAqoDsgiFgBYerX0TM9HaZsYcBxKNupt0UpVszdeUQrL3Rg0SuM+9azhX9i4x6Q7pNE4c4b0D+ySlop3j2EilJIb+iqRXNcb+ar46uQWQkKyi4ac6gXTCP8VBP8UpSHCajzfxDd7X3ucYQX2CvWMcd8vLxYmlXCklvw1P2TghiHFyWb1F+lUAAPL6nW5kbgD6pWtleXMA+sV1Y2xhLmVkdQD6pWFwcHMA+sVhbGV4bmFubwD6/WNjbngtYXV0b2NvbmZpZwD6pWluZm8A+gK1wS5NLksAVuME8eRpoy2FFyAdd+Z99HNVWUP78Igj6ZZJyP4w8cYA+r39AQBRY2j9APqNAAAAAaID4gKFwzztfBS+V9U+vv+4nd7Pz3ZRtLlmfeYNrtul4/5cvBYAArq1BRY2j9wZAALCnShGPwAD0qYyMDAwAAPajQAAAeIB6vL6nW5kbgD6pWtleXMA+sV1Y2xhLmVkdQD6pWFwcHMA+sVhbGV4bmFubwD6ArXBLk0uSwDDPO18FL5X1T6+/7id3s/PdlG0uWZ95g2u26Xj/ly8FgAAAAAAAZoHlTxNZXRhPjxOYW1lPmNjbngtYXV0b2NvbmZpZzwvTmFtZT48QWZmaWxpYXRpb24+QWxleGFuZGVyIEhvcm48L0FmZmlsaWF0aW9uPjxWYWxpZF90bz4xMzk3MDAzNjUxPC9WYWxpZF90bz48L01ldGE+CgAA',
        'confirmed': True
    },
    {
        'id': 3,
        'email': u'alexnano@ucla.edu',
        'ndn-name': u'ucla.edu/alexnano',
        'pubkey': u'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAtm/yyYAcs55LgbFLQHAyjs/iZJfuHV2NGLg/m0tx0s6at3GW9WaQ0q7sxUgZi/eoLrTxbq4zYCebYNIqi1p/5/PFGHI0rEnnbkM+4zmp12dAGIhAtaR+JPKcPi5pd/EhwkgETE93WUAV9GZIaFXRaUznyAmCjmux5FN94AGgzBrqJPxw+KaMdJNck4l8J5p/LhAA3ej05AS2gDd8uOCl5ho8hEpsNVQO8QbSOZhJrACWu8IBwD5g7/OCS2W/TlQBI/IvqRZ5no15R98lUh5rKP8y4V5APcJZbps7EzoygUyYD7zPFiWQWbMoOTx3gzXYTCaKNEYuVFEIx+FoJ1MsAw== nano@wifi-131-179-38-226.host.ucla.edu',
        #cert is base64 encoded binary
        'cert': u'BIICqgOyCIVmm8hfsGdZ2oni17K8iAcT3QtAC7EHSpCHZA8o2KuA3iY+3HKkgX4wMWg75mfYHWJ9CTYQDDOlu6x1jfD9x763kk5tsQiUZY/9+bkbIK0SEXujSHTUB7wqb0MVesIal82eivrUG3YcrARY1SgZRHC5L8FuTUuMdJmsXqisVD8gqAAA8vqdbmRuAPqla2V5cwD6xXVjbGEuZWR1APqlYXBwcwD6xWFsZXhuYW5vAPr9Y2NueC1hdXRvY29uZmlnAPoCtcEuTS5LAFbjBPHkaaMthRcgHXfmffRzVVlD+/CII+mWScj+MPHGAPq9/QEAUWNo/QD6jQAAAAGiA+IChcM87XwUvlfVPr7/uJ3ez892UbS5Zn3mDa7bpeP+XLwWAAK6tQUWNo/b9gACwp0oRj8AA9KmMjAwMAAD2o0AAAHiAery+p1uZG4A+qVrZXlzAPrFdWNsYS5lZHUA+qVhcHBzAPrFYWxleG5hbm8A+gK1wS5NLksAwzztfBS+V9U+vv+4nd7Pz3ZRtLlmfeYNrtul4/5cvBYAAAAAAAGaCpUwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAKcxsUOOwMUdBz66GwX/FhAami+Rj+NSgeFP4xz3iE5ibf+jPK1Svy9imzlmGeWkhM4o8p/kwa+h2lz4Td25yP7SZ/EGkg/SfvBOwErowvdK/+7/Vayw3TwCAOema5VG8NdCVAgYXT+BBLgIN9k7TaNpS4PRsvY2RnBPzIqo7TwtAgMBAAEAAASCAqoDsgiFgBYerX0TM9HaZsYcBxKNupt0UpVszdeUQrL3Rg0SuM+9azhX9i4x6Q7pNE4c4b0D+ySlop3j2EilJIb+iqRXNcb+ar46uQWQkKyi4ac6gXTCP8VBP8UpSHCajzfxDd7X3ucYQX2CvWMcd8vLxYmlXCklvw1P2TghiHFyWb1F+lUAAPL6nW5kbgD6pWtleXMA+sV1Y2xhLmVkdQD6pWFwcHMA+sVhbGV4bmFubwD6/WNjbngtYXV0b2NvbmZpZwD6pWluZm8A+gK1wS5NLksAVuME8eRpoy2FFyAdd+Z99HNVWUP78Igj6ZZJyP4w8cYA+r39AQBRY2j9APqNAAAAAaID4gKFwzztfBS+V9U+vv+4nd7Pz3ZRtLlmfeYNrtul4/5cvBYAArq1BRY2j9wZAALCnShGPwAD0qYyMDAwAAPajQAAAeIB6vL6nW5kbgD6pWtleXMA+sV1Y2xhLmVkdQD6pWFwcHMA+sVhbGV4bmFubwD6ArXBLk0uSwDDPO18FL5X1T6+/7id3s/PdlG0uWZ95g2u26Xj/ly8FgAAAAAAAZoHlTxNZXRhPjxOYW1lPmNjbngtYXV0b2NvbmZpZzwvTmFtZT48QWZmaWxpYXRpb24+QWxleGFuZGVyIEhvcm48L0FmZmlsaWF0aW9uPjxWYWxpZF90bz4xMzk3MDAzNjUxPC9WYWxpZF90bz48L01ldGE+CgAA',
        'confirmed': False
    }
]

# return render_template('confirm.html', name=name)

@app.route('/ndn/auth/v1.0/users', methods = ['GET'])
def get_tasks():
    return jsonify( { 'users': users } )

#@app.route('/ndn/auth/v1.0/users/<int:user_id>', methods = ['GET'])
#def get_user(user_id):
#    user = filter(lambda t: t['id'] == user_id, users)
#    if len(user) == 0:
#       abort(404)
#    return jsonify( { 'user': user[0] } )
    
@app.route('/ndn/auth/v1.0/users/<string:user_email>', methods = ['GET'])
def get_user(user_email):
   # wtf = str((request.json))
    #return(wtf)
    user = filter(lambda t: t['email'] == user_email, users)
    #return(request.json['email'])
    if len(user) == 0:
        abort(404)
    if(user[0]['confirmed'] == False):
        mailUser(user[0]['email'])
    return jsonify( { 'confirmed': user[0]['confirmed'],'email': user[0]['email'] } )

@app.route('/ndn/auth/v1.1/users/<string:user_email>', methods = ['GET'])
def get_user(user_email):
   # wtf = str((request.json))
    #return(wtf)
    #user = filter(lambda t: t['email'] == user_email, users)
    user =  mongo.db.find_one({"email":user_email})
    #return(request.json['email'])
    if len(user) == 0:
        user = {
            'email': u'alexnano@remap.ucla.edu',
            'ndn-name': u'get from UI',
            'pubkey': '', #cert is base64 encoded binary
            'cert': '',
            'confirmed': False
        }
        mongo.db.insert(user)
        abort(404)
    if(user[0]['confirmed'] == False):

        mailUser(user[0]['email'])
    return jsonify( { 'confirmed': user[0]['confirmed'],'email': user[0]['email'] } )


    
@app.route('/ndn/auth/v1.0/certs/<string:user_email>', methods = ['GET'])
def get_cert(user_email):
    user = filter(lambda t: t['email'] == user_email, users)
    if len(user) == 0:
        abort(404)
    return jsonify( { 'cert': user[0]['cert'],'email': user[0]['email'] } )

@app.route('/ndn/auth/v1.0/keys/<string:user_email>', methods = ['GET'])
def get_pubkey(user_email):
    user = filter(lambda t: t['email'] == user_email, users)
    if len(user) == 0:
        abort(404)
    return jsonify( { 'pubkey': user[0]['pubkey'],'email': user[0]['email'] } )


def mailUser(email):
    SERVER = "localhost"
    FROM = os.getlogin()
    TO = email

    SUBJECT = "Message From " + os.getlogin()


    TEXT = 'please click on link to authorize your new NDN trust name'

    # Prepare actual message

    message = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    # Send the mail

    server = smtplib.SMTP(SERVER, 1025)
    server.sendmail(FROM, TO, message)
    server.quit()

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( { 'error': 'Not found' } ), 404)
    
# base64.b64decode(s)
# base64.b64encode(s)

if __name__ == '__main__':
    app.run(debug = True)
