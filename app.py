from flask import Flask, request, jsonify,render_template
from flask_cors import CORS,cross_origin
import json
import sys
import os
from Server import railMate

app = Flask(__name__)


BASEDIR = os.path.abspath(os.path.dirname(__file__))
# sys.path.append(os.path.join(BASEDIR,"chart_api/"))

cors = CORS(app)
@app.route("/")
def index():
    return render_template("selfie.html")
# @app.route('/', methods=["GET", "POST"])
# @cross_origin()
# def main():
#     try:
#         print("Server main.py started ")
#         dbParams = json.loads(request.args.get('dbParams'))
#         module = railMate
#         function_name = dbParams["functionName"]
#         if hasattr(module, function_name):
#             func = getattr(module, function_name)
#             if request.method == "POST":
#                 response = func(request)
#             else:
#                 response = func(dbParams)

#         else:
#             response = {"error":f"No function with name {function_name}"}
#     except Exception as exc:
#         print(91,str(exc))
#         response = {"error":str(exc)}

#     return (response,200)


if __name__ == '__main__':
    app.run(debug=True,use_reloader=False)
   