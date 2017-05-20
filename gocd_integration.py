import urllib
import urllib2
import httplib2
import base64
import ssl
import json
import os
from flask import Flask
from flask import request

# Fazer:
#ok - Ajustar permissao de git push e usar sistema de issues do github
#- Checar se o pipeline solicitado existe naquele ambiente
#- Ler de uma variavel de ambiente os ambientes 'restritos'
#- Checar se o ambiente selecionado existe!

app = Flask(__name__)

gemuser = os.environ['GEM_USER']
gempass = os.environ['GEM_PASS']
restrictedenvs = os.environ['RESTRICTED_ENVS']
restrictedenvsarray = restrictedenvs.split(",")
auth = gemuser + ":" + gempass

http = httplib2.Http(disable_ssl_certificate_validation=True)
request_headers = {
    "Accept": "Accept: application/vnd.go.cd.v1+json",
    "Content-Type": "application/json",
    "Authorization": "Basic " + base64.encodestring(auth).replace('\n', '')
}

# List environments of pipeline
@app.route('/list')
def list():
    pipeline = request.args.get('pipeline') 
    env = request.args.get('env')
    auth = gemuser + ":" + gempass

    gocd_url = os.environ['GOCD_URL'] + "/go/api/admin/environments/" + env

    request_headers = {
        "Accept": "Accept: application/vnd.go.cd.v1+json",
        "Authorization": "Basic " + base64.encodestring(auth).replace('\n', '')
    }

    ssl_context = ssl._create_unverified_context()
    response = urllib2.Request(gocd_url, headers=request_headers)
######## COLOCAR try PRA LIDAR COM 404 !
    content = urllib2.urlopen(response, context=ssl_context).read()
    parsed_json = json.loads(content)

    returnstring = ""
    contains = false
    for usr_pipe in parsed_json["pipelines"]:
        if pipeline == usr_pipe["name"]:
            contains = true
    if contains:
        returnstring = returnstring + 'Pipeline \'' + pipeline + '\' is already in environment \'' + env + '\'!\n'
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
        if env == restrictedenvitem:
            return 'Sorry! The '+env+' environment is restricted!\nPipeline NOT added to it!\nPlease ask the QaaS team for help.\n'

    data = "{\"pipelines\":{\"add\":[\"" + pipeline + "\"]}}"

######## COLOCAR try PRA LIDAR COM 404! - Caso o pipeline ja esteja no environment
    resp, content = http.request(gocd_url, "PATCH", data, headers=request_headers)
    parsed_json = json.loads(content)

    returnstring = ""
    contains = false
    for usr_pipe in parsed_json["pipelines"]:
        if pipeline == usr_pipe["name"]:
            contains = true
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

    for restrictedenvitem in restrictedenvsarray:
        if env == restrictedenvitem:
            return 'Sorry! The '+env+' environment is restricted!\nPipeline NOT removed from it!\nPlease ask the QaaS team for help.\n'

    data = "{\"pipelines\":{\"remove\":[\"" + pipeline + "\"]}}"
######## COLOCAR try PRA LIDAR COM 404! - Caso o pipeline NAO esteja no environment
    resp, content = http.request(gocd_url, "PATCH", data, headers=request_headers)
    parsed_json = json.loads(content)

    returnstring = ""
    contains = false
    for usr_pipe in parsed_json["pipelines"]:
        if pipeline == usr_pipe["name"]:
            contains = true
    if contains:
        returnstring = 'Pipeline \'' + pipeline + '\' removed successfully from environment \'' + env + '\'!\n'
    else:
        returnstring = 'Failed to remove pipeline \'' + pipeline + '\' from environment \'' + env + '\'!\n'

    return '{}'.format(returnstring)

if __name__ == '__main__':
    app.run()
