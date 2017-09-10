import httplib2
import base64
import ssl
import json
import os
from flask import Flask, request

app = Flask(__name__)

gemuser = os.environ['GEMA_USER']
gempass = os.environ['GEMA_PASS']
restrictedenvs = os.environ['RESTRICTED_ENVS']
restrictedenvsarray = restrictedenvs.split(",")
auth = gemuser + ":" + gempass

http = httplib2.Http(disable_ssl_certificate_validation=True)
request_headers = {
    "Accept": "Accept: application/vnd.go.cd.v2+json",
    "Content-Type": "application/json",
    "Authorization": "Basic " + base64.encodestring(auth).replace('\n', '')
}

def envExists (env):

    gocd_url = os.environ['GOCD_URL'] + "/go/api/admin/environments"
    resp, content = http.request(gocd_url, headers=request_headers)
    parsed_json = json.loads(content)

    contains = False

    for usr_env in parsed_json["_embedded"]["environments"]:
        if env == usr_env["name"]:
            contains = True

    return contains

# List environments of pipeline
@app.route('/list')
def list():
    pipeline = request.args.get('pipeline')
    env = request.args.get('env')

    if not envExists(env):
        return 'Environment \'' + env + '\' NOT found!\n'

    gocd_url = os.environ['GOCD_URL'] + "/go/api/admin/environments/" + env
    resp, content = http.request(gocd_url, headers=request_headers)
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

    gocd_url = os.environ['GOCD_URL'] + "/go/api/admin/environments/" + env

    for restrictedenvitem in restrictedenvsarray:
        if env.capitalize() == restrictedenvitem.capitalize():
            return 'Sorry! The '+env+' environment is restricted!\nPipeline NOT added to it!\nPlease ask the QaaS team for help.\n'

    data = "{\"pipelines\":{\"add\":[\"" + pipeline + "\"]}}"

    resp, content = http.request(gocd_url, "PATCH", data, headers=request_headers)
    parsed_json = json.loads(content)

    if "message" in parsed_json:
        if "Failed to update environment" in parsed_json["message"]:
            if "Duplicate unique value" in parsed_json["message"]:
                return 'Pipeline \'' + pipeline + '\' is already in another environment!\n'
            else:
                return 'Pipeline \'' + pipeline + '\' is already in environment \'' + env +'\'!\n'
        else:
            if "with name" in  parsed_json["message"]:
                return 'Pipeline \'' + pipeline + '\' not found!\n'
            else:
                return 'Environment \'' + env + '\' not found!\n'

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

    gocd_url = os.environ['GOCD_URL'] + "/go/api/admin/environments/" + env

# For now we CAN remove pipelines from the production env, but can't add pipelines to it.
#    for restrictedenvitem in restrictedenvsarray:
#        if env == restrictedenvitem:
#            return 'Sorry! The '+env+' environment is restricted!\nPipeline NOT removed from it!\nPlease ask the QaaS team for help.\n'

    data = "{\"pipelines\":{\"remove\":[\"" + pipeline + "\"]}}"
    resp, content = http.request(gocd_url, "PATCH", data, headers=request_headers)
    parsed_json = json.loads(content)

    if "message" in parsed_json:
        return 'Environment \'' + env + '\' not found!\n'

    returnstring = ""
    contains = True
    for usr_pipe in parsed_json["pipelines"]:
        if pipeline == usr_pipe["name"]:
            contains = False
    if contains:
        returnstring = 'Pipeline \'' + pipeline + '\' removed successfully from environment \'' + env + '\'!\n(Or it wasn\'t there before)\n'
    else:
        returnstring = 'Failed to remove pipeline \'' + pipeline + '\' from environment \'' + env + '\'!\n'

    return '{}'.format(returnstring)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
