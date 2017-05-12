from flask import Flask
from flask import request

app = Flask(__name__)

# List environments of pipeline
@app.route('/list')
def list():
    pipe = request.args.get('pipe')
    env  = request.args.get('env')
    return 'pipeline: {} | env: {}\n'.format(pipe, env)

# Update environments of pipeline
@app.route('/update')
def add():
    pipe = request.args.get('pipe')
    env  = request.args.get('env')
    return 'pipeline: {} | env: {}\n'.format(pipe, env)

if __name__ == '__main__':                                                 
    app.run()
