from flask import Flask, request
import os
import socket
import math

app = Flask(__name__)

@app.route("/")
def main():
    return "Welcome to your cluster!"

@app.route("/calculate", methods=['POST'])
def sum():
    if request.method == 'POST':
        params = int(request.form["params"])
        op = request.form["operation"]
        a = request.form["a"]
        b = request.form["b"]
        if params == 2:
            ans = str(eval("math.{0}({1},{2})".format(op,a,b)))
            return ans
        elif params == 1:
            ans = str(eval("math.{0}({1})".format(op,a)))
            return ans
        else:
            ans = str(eval("math.{0}".format(op)))
            return ans

@app.route("/hello")
def hello():
    return "Hello Matheus"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
