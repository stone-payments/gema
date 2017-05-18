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
#ok 00- Ajustar permissao de git push e usar sistema de issues do github
# 0- Checar se o pipeline solicitado existe naquele ambiente
# 1- Ler de uma variavel de ambiente os ambientes 'restritos'
# 2- Ter 2 usuarios e senhas:
#    2.1- Usuario dev, que so sera usado para checar se o pipeline solicitado existe
#    2.2- Usuario do tsuru, com privilegios de adm no gocd
# Checar se o ambiente selecionado existe!

app = Flask(__name__)

# List environments of pipeline
@app.route('/list')
def list():
    usrname = os.environ['USR']
    usrpass = os.environ['PAS']
    pipe = request.args.get('pipeline')
    env = request.args.get('env')
    auth = usrname + ":" + usrpass

    request_headers = {
        "Accept": "Accept: application/vnd.go.cd.v1+json",
        "Authorization": "Basic " + base64.encodestring(auth).replace('\n', '')
    }

    gocd = "https://cd.stone.com.br:8154/go/api/admin/environments/" + env
    context = ssl._create_unverified_context()
    response = urllib2.Request(gocd, headers=request_headers)
######## COLOCAR try PRA LIDAR COM 404 !
    contents = urllib2.urlopen(response, context=context).read()
    parsed_json = json.loads(contents)

    retstr = ""
    contem = 0
    for usr_pipe in parsed_json["pipelines"]:
        if pipe == usr_pipe["name"]:
            contem = 1
    if contem == 1:
        retstr = retstr + 'Pipeline \'' + pipe + '\' is already in environment \'' + env + '\'!\n'
    else:
        retstr = retstr + 'Pipeline \'' + pipe + '\' is NOT in environment \'' + env + '\'!\n'
    return '{}'.format(retstr)

# Update environments of pipeline
@app.route('/add')
def add():
    usrname = os.environ['USR']
    usrpass = os.environ['PAS']

    pipe = request.args.get('pipeline')
    env = request.args.get('env')
    auth = usrname + ":" + usrpass

    http = httplib2.Http(disable_ssl_certificate_validation=True)
    gocd = "https://cd.stone.com.br:8154/go/api/admin/environments/" + env
    request_headers = {
        "Accept": "Accept: application/vnd.go.cd.v1+json",
        "Content-Type": "application/json",
        "Authorization": "Basic " + base64.encodestring(auth).replace('\n', '')
    }
    data = "{\"pipelines\":{\"add\":[\"" + pipe + "\"]}}"

######## COLOCAR try PRA LIDAR COM 404! - Caso o pipeline já esteja no environment
    resp, contents = http.request(gocd, "PATCH", data, headers=request_headers)
    parsed_json = json.loads(contents)

    retstr = ""
    contem = 0
    for usr_pipe in parsed_json["pipelines"]:
        if pipe == usr_pipe["name"]:
            contem = 1
    if contem == 1:
        retstr = retstr + 'Pipeline \'' + pipe + '\' added successfully to environment \'' + env + '\'!\n'
    else:
        retstr = retstr + 'Failed to add pipeline \'' + pipe + '\' to environment \'' + env + '\'!\n'
    return '{}'.format(retstr)


"""
@app.route('/remove')
def remove():
    usrname = os.environ['USR']
    usrpass = os.environ['PAS']
    pipe = request.args.get('pipeline')
    env = request.args.get('env')
    return 'pipeline: {} | env: {}\n'.format(pipe, env)
"""

if __name__ == '__main__':
    app.run()
