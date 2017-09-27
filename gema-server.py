import httplib2
import base64
import ssl
import json
import os
import datetime
import pytz
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
    
    if "html" in myjson:
        return False

    try:
        json_object = json.loads(myjson)
    except ValueError, e:
        return False
    return True

def cerberusLog (endpoint, action, env, pipeline, duration):

    now = datetime.datetime.now().utcnow().replace(tzinfo=pytz.utc)
    dateNow = str(now.year) +"-"+ str (now.strftime('%02m')) +"-"+ str(now.day)
    hourNow = str(now.strftime('%02H')) +":"+ str(now.strftime('%02M')) +":"+ str(now.strftime('%02S')) +"."+ str(now.microsecond) + "+00:00"
    timestampCerberus = dateNow + "T" + hourNow

    #print now
    #print timestampCerberus

    #cerberusDev = "http://dev-logger.stone.com.br:8733/v1/log"
    #cerberusProd = "http://lgcb.buy4sc.local:8733/v1/log"
    
    cerberusEndpoint = os.environ['CERBERUS']
    method_http = "POST"

    data = '''[
    {
        \"AdditionalData\" : 
        {
             \"Action\" : \"'''+ str(action) +'''\",
             \"Environment\" : \"''' + str(env) + '''",
             \"Pipeline\" : \"'''+ str(pipeline) +'''",
             \"Duration\" : '''+ str(duration) +''',
             \"ID\" : \"500\"
        },
        \"ApplicationId\" : "",
        \"MachineName\" : \"Gema",
        \"ManagedThreadId\" : "",
        \"ManagedThreadName\" : null,
        \"Message\" : \"Logs from GEMA",
        \"NativeProcessId\" : \"0",
        \"NativeThreadId\" : \"0",
        \"OSFullName\" : \"Linux",
        \"ProcessName\" : \"Gema",
        \"ProcessPath\" : "/",
        \"ProductCompany\" : \"Buy4",
        \"ProductName\" : \"GEMA",
        \"ProductVersion\" : \"1.0",
        \"Severity\" : \"Info",
        \"Tags\" : [],
        \"Timestamp\" : \"'''+ timestampCerberus +'''",
        \"TypeName\" : \"Gema\"
    }
    ]'''

    request_headers = {
        "Content-Type": "application/json",
    }

    print "Sending logs to cerberus:"
    print data

    resp,content = http.request(cerberusEndpoint, method_http, data, headers=request_headers)
    
    print "\nCerberus response:"
    print content

    return "good"

def sendRequest(gocd_url, action, method_http, data, requestHeader, env, pipeline):
    
    startDate = datetime.datetime.now()
    if method_http is None:
        resp,content = http.request(gocd_url, headers=requestHeader)
    else:
        resp,content = http.request(gocd_url, method_http, data, headers=requestHeader)
    endDate = datetime.datetime.now()
    duration = endDate - startDate

    cerberusLog (gocd_url, action, env, pipeline, duration.total_seconds())

    #print "Cookie: "+cookie
    #print "content: "+content

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
        resp,content = sendRequest(gocd_url, "auth", None, None, request_headers_aut, None, None)
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
        dateCookie = datetime.datetime.strptime(strDateCookie[1], " %d-%b-%Y %H:%M:%S %Z") 
        currentDate =datetime.datetime.now()
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
    resp,content = sendRequest(gocd_url, "EnvDiscovery", None, None, request_headers, env, None)
    #resp, content = http.request(gocd_url, headers=request_headers)
    if not is_json(content):
        return "GoCD is overwhelmed. Please try again!\n"
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
    resp,content = sendRequest(gocd_url, "PipelineDiscovery", None, None, request_headers_pipe, None, pipeline)
    #resp, content = http.request(gocd_url, headers=request_headers_pipe)

    if not is_json(content):
        return "GoCD is overwhelmed. Please try again!\n"
    parsed_json = json.loads(content)

    if "message" in parsed_json:
        return False

    if pipeline == parsed_json["name"]:
        return True

    return False

# List environments of pipeline
@app.route('/list')
def list():
    global cookie
    cookie = ""
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
    resp,content = sendRequest(gocd_url, "list", None, None, request_headers, env, pipeline)
    #resp, content = http.request(gocd_url, headers=request_headers)
    #cookie = ""

    if not is_json(content):
        return "GoCD is overwhelmed. Please try again!\n"
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
    global cookie
    cookie = ""
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

    resp,content = sendRequest(gocd_url, "add", "PATCH", data, request_headers, env, pipeline)
    #resp, content = http.request(gocd_url, "PATCH", data, headers=request_headers)

    if not is_json(content):
        return "GoCD is overwhelmed. Please try again!\n"
    parsed_json = json.loads(content)

    if "message" in parsed_json:
        if "Failed to update environment" in parsed_json["message"]:
            if "Duplicate unique value" in parsed_json["message"] or "which is already part" in parsed_json["message"]:
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
    global cookie
    cookie = ""

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

    resp,content = sendRequest(gocd_url, "remove", "PATCH", data, request_headers, env, pipeline)
    #resp, content = http.request(gocd_url, "PATCH", data, headers=request_headers)

    if not is_json(content):
        return "GoCD is overwhelmed. Please try again!\n"
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
