import httplib2
import base64
import ssl
import json
import os
import stopwatch
from datetime import datetime
from flask import Flask, request

app = Flask(__name__)

gemuser = os.environ['GEMA_USER']
gempass = os.environ['GEMA_PASS']
restrictedenvs = os.environ['RESTRICTED_ENVS']
restrictedenvsarray = restrictedenvs.split(",")
auth = gemuser + ":" + gempass

http = httplib2.Http(disable_ssl_certificate_validation=True)

cookie = ""

@app.route('/')
def wrongRoute():
    return "GEMA\n"
def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError, e:
        return False
    return True

def sendRequest(gocd_url, method_http, data, requestHeader):
    
    startDate = datetime.now()
    if method_http is None:
        resp,content = http.request(gocd_url, headers=requestHeader)
    else:
        resp,content = http.request(gocd_url, method_http, data, headers=requestHeader)
    endDate = datetime.now()
    duration = endDate - startDate

    return resp,content

def authenticate():
    request_headers_aut = {
        "Accept": "Accept: application/vnd.go.cd.v1+json",
        "Content-Type": "application/json",
        "Authorization": "Basic " + base64.encodestring(auth).replace('\n', '')
    }

    global cookie
    if not checkCookieValidate() :
        gocd_url = os.environ['GOCD_URL'] + "/go/api/version"
        resp,content = sendRequest(gocd_url, None, None, request_headers_aut)
        #resp, content = http.request(gocd_url, headers=request_headers_aut)
        if not is_json(content):
            return None
        parsed_json = json.loads(content)
        cookie = resp['set-cookie']
    return cookie

def checkCookieValidate():
    
    if  cookie :
        strCookie = cookie.split(';')
        strDateCookie = strCookie[2].split(',') 
        dateCookie = datetime.strptime(strDateCookie[1], " %d-%b-%Y %H:%M:%S %Z") 
        currentDate =datetime.now()
        #print dateCookie 
        #print currentDate
        if currentDate < dateCookie :
            return True
    return False

def envExists (env):
    
    authGocd = authenticate()
    if authGocd is None:
        return "GoCD is overwhelmed. Please try again!\n"

    request_headers = {
        "Accept": "Accept: application/vnd.go.cd.v2+json",
        "Content-Type": "application/json",
        'Cookie': authGocd
    }

    gocd_url = os.environ['GOCD_URL'] + "/go/api/admin/environments"
    resp,content = sendRequest(gocd_url, None, None, request_headers)
    #resp, content = http.request(gocd_url, headers=request_headers)
    parsed_json = json.loads(content)

    contains = False
    for usr_env in parsed_json["_embedded"]["environments"]:
        if env == usr_env["name"]:
            contains = True

    return contains

def pipeExists (pipeline):
    
    authGocd = authenticate()
    if authGocd is None:
        return "GoCD is overwhelmed. Please try again!\n"
    
    request_headers_pipe = {
        "Accept": "Accept: application/vnd.go.cd.v4+json",
        "Content-Type": "application/json",
        'Cookie': authGocd
    }

    gocd_url = os.environ['GOCD_URL'] + "/go/api/admin/pipelines/" + pipeline
    resp,content = sendRequest(gocd_url, None, None, request_headers_pipe)
    #resp, content = http.request(gocd_url, headers=request_headers_pipe)
    parsed_json = json.loads(content)

    if "message" in parsed_json:
        return False

    if pipeline == parsed_json["name"]:
        return True

    return False

# List environments of pipeline
@app.route('/list')
def list():
    pipeline = request.args.get('pipeline')
    env = request.args.get('env')

    if not envExists(env):
        return 'Environment \'' + env + '\' NOT found!\n'

    if not pipeExists(pipeline):
        return 'Pipeline \'' + pipeline + '\' NOT found!\n'

    authGocd = authenticate()
    if authGocd is None:
        return "GoCD is overwhelmed. Please try again!\n"

    request_headers = {
        "Accept": "Accept: application/vnd.go.cd.v2+json",
        "Content-Type": "application/json",
        'Cookie': authGocd
    }

    gocd_url = os.environ['GOCD_URL'] + "/go/api/admin/environments/" + env
    resp,content = sendRequest(gocd_url, None, None, request_headers)
    #resp, content = http.request(gocd_url, headers=request_headers)
    parsed_json = json.loads(content)

    returnstring = ""
    contains = False

    for usr_pipe in parsed_json["pipelines"]:
        if pipeline == usr_pipe["name"]:
            contains = True
    if contains:
        returnstring = returnstring + 'Pipeline \'' + pipeline + '\' is in environment \'' + env + '\'!\n'
    else:
        returnstring = returnstring + 'Pipeline \'' + pipeline + '\' is NOT in environment \'' + env + '\'!\n'
    return '{}'.format(returnstring)

# Update environments of pipeline
@app.route('/add')
def add():
    pipeline = request.args.get('pipeline')
    env = request.args.get('env')

    if not envExists(env):
        return 'Environment \'' + env + '\' NOT found!\n'

    if not pipeExists(pipeline):
        return 'Pipeline \'' + pipeline + '\' NOT found!\n'

    for restrictedenvitem in restrictedenvsarray:
        if env.capitalize() == restrictedenvitem.capitalize():
            return 'Sorry! The '+env+' environment is restricted!\nPipeline NOT added to it!\nPlease ask the QaaS team for help.\n'

    gocd_url = os.environ['GOCD_URL'] + "/go/api/admin/environments/" + env

    data = "{\"pipelines\":{\"add\":[\"" + pipeline + "\"]}}"

    authGocd = authenticate()
    if authGocd is None:
        return "GoCD is overwhelmed. Please try again!\n"

    request_headers = {
        "Accept": "Accept: application/vnd.go.cd.v2+json",
        "Content-Type": "application/json",
        'Cookie': authGocd
    }

    resp,content = sendRequest(gocd_url,"PATCH",data, request_headers)
    #resp, content = http.request(gocd_url, "PATCH", data, headers=request_headers)
    parsed_json = json.loads(content)

    if "message" in parsed_json:
        if "Failed to update environment" in parsed_json["message"]:
            if "Duplicate unique value" in parsed_json["message"]:
                return 'Pipeline \'' + pipeline + '\' is already in another environment!\n'
            else:
                return 'Pipeline \'' + pipeline + '\' is already in environment \'' + env +'\'!\n'

    returnstring = ""
    contains = False
    for usr_pipe in parsed_json["pipelines"]:
        if pipeline == usr_pipe["name"]:
            contains = True
    if contains:
        returnstring = 'Pipeline \'' + pipeline + '\' added successfully to environment \'' + env + '\'!\n'
    else:
        returnstring = 'Failed to add pipeline \'' + pipeline + '\' to environment \'' + env + '\'!\n'

    return '{}'.format(returnstring)

@app.route('/remove')
def remove():
    pipeline = request.args.get('pipeline')
    env = request.args.get('env')

    if not envExists(env):
        return 'Environment \'' + env + '\' NOT found!\n'

    if not pipeExists(pipeline):
        return 'Pipeline \'' + pipeline + '\' NOT found!\n'

    gocd_url = os.environ['GOCD_URL'] + "/go/api/admin/environments/" + env

    data = "{\"pipelines\":{\"remove\":[\"" + pipeline + "\"]}}"

    authGocd = authenticate()
    if authGocd is None:
        return "GoCD is overwhelmed. Please try again!\n"

    request_headers = {
        "Accept": "Accept: application/vnd.go.cd.v2+json",
        "Content-Type": "application/json",
        'Cookie': authGocd
    }

    resp,content = sendRequest(gocd_url,"PATCH",data, request_headers)
    #resp, content = http.request(gocd_url, "PATCH", data, headers=request_headers)
    parsed_json = json.loads(content)

    if "message" in parsed_json:
        return "There is no pipeline '" + pipeline + "' in the '" + env + "' environment.\n"

    returnstring = ""
    contains = True
    for usr_pipe in parsed_json["pipelines"]:
        if pipeline == usr_pipe["name"]:
            contains = False
    if contains:
        returnstring = 'Pipeline \'' + pipeline + '\' removed successfully from environment \'' + env + '\'!\n'
    else:
        returnstring = 'Failed to remove pipeline \'' + pipeline + '\' from environment \'' + env + '\'!\n'

    return '{}'.format(returnstring)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
