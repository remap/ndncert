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
import json
import urllib

from bson import json_util

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# name of app is also name of mongodb "database"
app = Flask("ndncert", template_folder=tmpl_dir)
app.config.from_pyfile('%s/settings.py' % os.path.dirname(os.path.abspath(__file__)))
mongo = PyMongo(app)
mail = Mail(app)

#############################################################################################
# User-facing components
#############################################################################################

@app.route('/', methods = ['GET'])
@app.route('/tokens/request/', methods = ['GET', 'POST'])
def request_token():
    if request.method == 'GET':
        #################################################
        ###              Token request                ###
        #################################################
        return render_template('token-request-form.html', URL=app.config['URL'])
    
    else: # 'POST'    
        #################################################
        ###        Token creation & emailing          ###
        #################################################
        user_email = request.form['email']
        try:
            # pre-validation
            get_operator_for_email(user_email)
        except:
            return render_template('error-unknown-site.html')
        
        token = {
            'email': user_email,
            'token': generate_token(),
            'created_on': datetime.datetime.utcnow(), # to periodically remove unverified tokens
            }
        mongo.db.tokens.insert(token)

        msg = Message("[NDN Certification] Request confirmation",
                      sender = app.config['MAIL_FROM'],
                      recipients = [user_email],
                      body = render_template('token-email.txt', URL=app.config['URL'], **token),
                      html = render_template('token-email.html', URL=app.config['URL'], **token))
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
        return render_template('request-form.html', URL=app.config['URL'], email=user_email, token=user_token, **params)
    
    else: # 'POST'
        # Email and token (to authorize the request==validate email)
        user_email = request.form['email']
        user_token = request.form['token']
    
        token = mongo.db.tokens.find_one({'email':user_email, 'token':user_token})
        if (token == None):
            abort(403)

        # Now, do basic validation of correctness of user input, save request in the database and notify the operator
        user_fullname = request.form['fullname']
        user_homeurl   = request.form['homeurl']
        #optional parameters
        user_group   = request.form['group']   if 'group'   in request.form else ""
        user_advisor = request.form['advisor'] if 'advisor' in request.form else ""
        
        # infer parameters from email
        try:
            # pre-validation
            params = get_operator_for_email(user_email)
        except:
            return "403"
            abort(403)
            return

        try:
            user_cert_request = base64.b64decode(request.form['cert-request'])
            user_cert_data    = ndn.Data.fromWire(user_cert_request)
        except:
            return render_template('request-form.html', error="Incorrectly generated NDN certificate request, please try again",
                                   URL=app.config['URL'], email=user_email, token=user_token, **params)

        # check if the user supplied correct name for the certificate request
        if not params['assigned_namespace'].isPrefixOf(user_cert_data.name):
            return render_template('request-form.html', error="Incorrectly generated NDN certificate request, please try again",
                                   URL=app.config['URL'], email=user_email, token=user_token, **params)

        cert_name = str(extract_cert_name(user_cert_data.name))
        # remove any previous requests for the same certificate name
        mongo.db.requests.remove({'cert_name': cert_name})
            
        cert_request = {
                'operator_id': str(params['operator']['_id']),
                'fullname': user_fullname,
                'organization': params['operator']['site_name'],
                'email': user_email,
                'homeurl': user_homeurl,
                'group': user_group,
                'advisor': user_advisor,
                'cert_name': cert_name,
                'cert_request': base64.b64encode(user_cert_request), # for no particular reason, re-encoding again...
                'created_on': datetime.datetime.utcnow(), # to periodically remove unverified tokens
            }
        mongo.db.requests.insert (cert_request)
        
        # OK. authorized, proceed to the next step
        mongo.db.tokens.remove(token)

        msg = Message("[NDN Certification] User certification request",
                      sender = app.config['MAIL_FROM'],
                      recipients = [params['operator']['email']],
                      body = render_template('operator-notify-email.txt', URL=app.config['URL'], 
                                             operator_name=params['operator']['name'], 
                                             **cert_request),
                      html = render_template('operator-notify-email.html', URL=app.config['URL'], 
                                             operator_name=params['operator']['name'], 
                                             **cert_request))
        mail.send(msg)
        
        return render_template('request-thankyou.html')

@app.route('/cert/get/', methods = ['GET'])
def get_certificate():
    name = request.args.get('name')
    ndn_name = ndn.Name(str(name))

    cert = mongo.db.certs.find_one({'name': str(name)})
    if cert == None:
        abort(404)

    response = make_response(cert['cert'])
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Disposition'] = 'attachment; filename=%s.ndncert' % str(ndn_name[-3])
    return response

@app.route('/cert/list/', methods = ['GET'])
def get_certificates():
    certificates = mongo.db.certs.find().sort([('name', 1)])
    return make_response(render_template('cert-list.txt', certificates=certificates), 200, {
            'Content-Type': 'text/plain'
            })


#############################################################################################
# Operator-facing components
#############################################################################################

@app.route('/cert-requests/get/', methods = ['POST'])
def get_candidates():
    keyLocator = request.form['keyLocator']
    timestamp  = request.form['timestamp']
    signature  = request.form['signature']
        
    query = \
        ndn.Name('/cert-requests/get') \
        .append(keyLocator) \
        .append(timestamp) \
        .append(base64.b64decode(signature))

    operator = mongo.db.operators.find_one({'site_prefix': keyLocator})
    if operator == None:
        abort(403)

    # do verification

    requests = mongo.db.requests.find({'operator_id': str(operator['_id'])})
    output = []
    for req in requests:
        output.append (req)

    # return json.dumps (output)
    return json.dumps(output, default=json_util.default)

@app.route('/cert/submit/', methods = ['POST'])
def submit_certificate():
    data = ndn.Data.fromWire(base64.b64decode(request.form['data']))

    operator_prefix = data.signedInfo.keyLocator.keyName[:-3]

    operator = mongo.db.operators.find_one({'site_prefix': str(operator_prefix)})
    if operator == None:
        return make_response('operator not found [%s]' % operator_prefix, 403)
        abort(403)

        
    # verify data packet
    # verify timestamp

    cert_name = str(extract_cert_name(data.name))
    cert_request = mongo.db.requests.find_one({'cert_name': cert_name})

    if cert_request == None:
        abort(403)
    
    # infer parameters from email
    try:
        # pre-validation
        params = get_operator_for_email(cert_request['email'])
    except:
        abort(403)
        return
        
    if len(data.content) == 0:
        # (no deny reason for now)
        # eventually, need to check data.type: if NACK, then content contains reason for denial
        #                                      if KEY, then content is the certificate
        
        msg = Message("[NDN Certification] Rejected certification",
                      sender = app.config['MAIL_FROM'],
                      recipients = [cert_request['email']],
                      body = render_template('cert-rejected-email.txt', URL=app.config['URL'], **cert_request),
                      html = render_template('cert-rejected-email.html', URL=app.config['URL'], **cert_request))
        mail.send(msg)
        
        mongo.db.requests.remove(cert_request)
        
        return "OK. Certificate has been denied"
    else:
        cert = {
            'name': str(data.name),
            'cert': request.form['data'],
            'created_on': datetime.datetime.utcnow(), # to periodically remove unverified tokens
            }
        mongo.db.certs.insert(cert)

        msg = Message("[NDN Certification] NDN certificate issued",
                      sender = app.config['MAIL_FROM'],
                      recipients = [cert_request['email']],
                      body = render_template('cert-issued-email.txt',  
                                             URL=app.config['URL'], 
                                             assigned_namespace=params['assigned_namespace'],
                                             quoted_cert_name=urllib.quote(cert['name'], ''), cert_id=str(data.name[-3]), 
                                             **cert_request),
                      html = render_template('cert-issued-email.html', 
                                             URL=app.config['URL'], 
                                             assigned_namespace=params['assigned_namespace'],
                                             quoted_cert_name=urllib.quote(cert['name'], ''), cert_id=str(data.name[-3]), 
                                             **cert_request))
        mail.send(msg)

        mongo.db.requests.remove(cert_request)
        
        return "OK. Certificate has been approved and notification sent to the requester"

#############################################################################################
# Helpers
#############################################################################################

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
        operator = mongo.db.operators.find_one({'site_emails': {'$in':[ 'guest' ]}})

        if (operator == None):
            raise Exception ("Unknown site for domain [%s]" % domain)

        # Special handling for guests
        ndn_domain = ndn.Name("/ndn/guest")
        assigned_namespace = \
            ndn.Name('/ndn/guest') \
            .append(email)
    else:
        if domain == "operators.named-data.net":
            ndn_domain = ndn.Name(user)
            assigned_namespace = ndn.Name(user)
        else:
            ndn_domain = ndnify(domain)
            assigned_namespace = \
                ndn.Name('/ndn') \
                .append(ndn_domain) \
                .append(user)
    
    # return various things
    return {'operator':operator, 'user':user, 'domain':domain, 'ndn_domain':ndn_domain, 'assigned_namespace':assigned_namespace}

def extract_cert_name(name):
    # remove two last components and remove "KEY" keyword at any position
    return ndn.Name([component for component in name[:-2] if str(component) != 'KEY'])

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0')
    
