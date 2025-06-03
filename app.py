
from flask import Flask, render_template, request, redirect, url_for




# inicializacao
app = Flask(__name__) 
from views import *
from models import *



if __name__ == "__main__":
    app.run(debug=True)

