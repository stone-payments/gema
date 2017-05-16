import urllib2
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
    contents = urllib2.urlopen(response, context=context).read()
    parsed_json = json.loads(contents)

    pipes = ""
    for usr_pipe in parsed_json["pipelines"]:
        pipes = pipes + "\n" + usr_pipe["name"]
        # CHECAR SE O PIPELINE EXISTE NESSE AMBIENTE
    return 'contents: {} \n'.format(pipes)

# Update environments of pipeline
@app.route('/update')
def add():
    pipe = request.args.get('pipeline')
    env = request.args.get('env')
    return 'pipeline: {} | env: {}\n'.format(pipe, env)

if __name__ == '__main__':
    app.run()
