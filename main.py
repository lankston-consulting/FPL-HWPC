import os
from flask import Flask, request
from flask_cors import CORS

import hwpccalc

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def handle():
    p = request.args.get('p')
    q = request.args.get('q')
    print(p)
    print(q)
    hwpccalc.run(p,q)
    return p, 200, {}

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.

    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)), debug=True)