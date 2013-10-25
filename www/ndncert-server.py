#!/usr/bin/env python

# dependencies - flask, flask-pymongo
# pip install Flask, Flask-PyMongo

#html/rest
from flask import Flask, jsonify, abort, make_response, request, render_template
from flask.ext.pymongo import PyMongo
from flask.ext.mail import Mail, Message

# mail
import smtplib
from email.mime.text import MIMEText
import smtplib
import os
import string
import random
import datetime
import base64
import ndn

################################################################################
###                                CONFIG                                    ###
################################################################################

URL = "http://ndncert.named-data.net:5000"

SMTP_SERVER = "localhost"
SMTP_FROM = "NDN Testbed Certificate Robot <noreply-ndncert@ndn.ucla.edu>"

################################################################################
################################################################################

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# name of app is also name of mongodb "database"
app = Flask("ndncert", template_folder=tmpl_dir)
app.config['MAIL_SERVER'] = SMTP_SERVER
mongo = PyMongo(app)
mail = Mail(app)

@app.route('/', methods = ['GET'])
@app.route('/tokens/request/', methods = ['GET', 'POST'])
def request_token():
    if request.method == 'GET':
        #################################################
        ###              Token request                ###
        #################################################
        return render_template('token-request-form.html', URL=URL)
    
    else: # 'POST'    
        #################################################
        ###        Token creation & emailing          ###
        #################################################
        user_email = request.form['email']
        try:
            # pre-validation
            get_operator_for_email(user_email)
        except:
            return 'some shit with %s' % user_email
            return render_template('error-unknown-site.html')
        
        token = {
            'email': user_email,
            'token': generate_token(),
            'created_on': datetime.datetime.utcnow(), # to periodically remove unverified tokens
            }
        mongo.db.tokens.insert(token)

        msg = Message("[NDN Certification] Request confirmation",
                      sender = SMTP_FROM,
                      recipients = [user_email],
                      body = render_template('token-email.txt', URL=URL, **token),
                      html = render_template('token-email.html', URL=URL, **token))
        mail.send(msg)
        
        return render_template('token-sent.html', email=user_email)

@app.route('/cert-requests/submit/', methods = ['GET', 'POST'])
def submit_request():
    if request.method == 'GET':
        # Email and token (to authorize the request==validate email)
        user_email = request.args.get('email')
        user_token = request.args.get('token')
    
        token = mongo.db.tokens.find_one({'email':user_email, 'token':user_token})
        if (token == None):
            abort(403)
    
        # infer parameters from email
        try:
            # pre-validation
            params = get_operator_for_email(user_email)
        except:
            abort(403)

        # don't delete token for now, just give user a form to input stuff
        return render_template('request-form.html', URL=URL, email=user_email, token=user_token, **params)
    
    else: # 'POST'
        # Email and token (to authorize the request==validate email)
        user_email = request.form['email']
        user_token = request.form['token']
    
        token = mongo.db.tokens.find_one({'email':user_email, 'token':user_token})
        if (token == None):
            abort(403)

        # OK. authorized, proceed to the next step
        mongo.db.tokens.remove(token)

        # Now, do basic validation of correctness of user input, save request in the database and notify the operator
        user_fullname = request.form['fullname']
        user_homeurl   = request.form['homeurl']
        #optional parameters
        user_group   = request.form['group']   if 'group'   in request.form else ""
        user_advisor = request.form['advisor'] if 'advisor' in request.form else ""

        user_cert_request = base64.b64decode(request.form['cert-request'])
        user_cert_data    = ndn.Data.fromWire(user_cert_request)

        # infer parameters from email
        try:
            # pre-validation
            params = get_operator_for_email(user_email)
        except:
            abort(403)

        # check if the user supplied correct name for the certificate request
        if not params['assigned_namespace'].isPrefixOf(user_cert_data.name):
            abort(403)
        
        cert_request = {
                'operator_id': str(params['operator']['_id']),
                'fullname': user_fullname,
                'organization': params['operator']['site_name'],
                'email': user_email,
                'homeurl': user_homeurl,
                'group': user_group,
                'advisor': user_advisor,
                'cert-request': base64.b64encode(user_cert_request), # for no particular reason, re-encoding again...
            }
        mongo.db.requests.insert (cert_request)
        
        return render_template('request-thankyou.html')


# ## NEW / 'final' operator routes

# @app.route('/ndn/auth/v1.1/candidates/<string:inst_str>', methods = ['GET'])
# def get_candidates(inst_str):
#     # get all valid users containing 'institution_str'where cert=null
#     all = mongo.db.users.find({'cert':'', 'confirmed':True, "ndn-name": {'$regex':inst_str}})
#     all_str = ""
#     for user in all:
#         all_str+=str(user)+"<br/>"
#     return (all_str)


# @app.route('/ndn/auth/v1.1/candidates/<string:email>/addcert/<string:cert>', methods = ['GET'])
# def write_cert(email, cert):
#      # "denied" | cert_str
#      ok = mongo.db.users.update({ 'email': email },{"$set": { 'cert': cert }})
#      return str(ok)
     
     
# LEGACY DICT / NONMONGO

# @app.route('/ndn/auth/v1.0/certs/<string:user_email>', methods = ['GET'])
# def get_cert(user_email):
#     user = filter(lambda t: t['email'] == user_email, users)
#     if len(user) == 0:
#         abort(404)
#     return jsonify( { 'cert': user[0]['cert'],'email': user[0]['email'] } )

# @app.route('/ndn/auth/v1.0/keys/<string:user_email>', methods = ['GET'])
# def get_pubkey(user_email):
#     user = filter(lambda t: t['email'] == user_email, users)
#     if len(user) == 0:
#         abort(404)
#     return jsonify( { 'pubkey': user[0]['pubkey'],'email': user[0]['email'] } )




def mailTokenToUser(token):
    print "Suppose to send data for token"
    pass
    # TO = user['email']
    # ndnname = user['ndn-name']

    # SUBJECT = "Message From " + FROM
    # m = hashlib.sha256()
    # m.update(str(user['_id']))
    # TEXT = 'please visit following URL to authorize your new NDN trust name, '+user['ndn-name']+'\n'
    # TEXT += URL+'/ndn/auth/v1.1/validate/?email='+user['email']+'&token='+str(m.hexdigest())

    # # Prepare actual message

    # message = """\
    # From: %s
    # To: %s
    # Subject: %s

    # %s
    # """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    # # Send the mail

    # server = smtplib.SMTP(SERVER)
    # server.sendmail(FROM, TO, message)
    # server.quit()

def generate_token():
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(60)])

def ndnify (dnsName):
    ndnName = ndn.Name ()
    for component in reversed (dnsName.split (".")):
        ndnName = ndnName.append (str (component))
    return ndnName

def get_operator_for_email(email):
    # very basic pre-validation
    user, domain = email.split('@', 2)
    operator = mongo.db.operators.find_one({'site_emails': {'$in':[ domain ]}})    
    if (operator == None):
        raise Exception ("Unknown site for domain [%s]" % domain)

    ndn_domain = ndnify(domain)
    assigned_namespace = \
        ndn.Name('/ndn') \
        .append(ndn_domain) \
        .append(user)
    
    # return various things
    return {'operator':operator, 'user':user, 'domain':domain, 'ndn_domain':ndn_domain, 'assigned_namespace':assigned_namespace}

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0')
