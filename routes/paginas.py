from flask import Blueprint, render_template

bp_paginas = Blueprint("paginas", __name__)

@bp_paginas.route("/")
def index():
    return render_template("index.html")

@bp_paginas.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@bp_paginas.route("/login")
def login():
    return render_template("login.html")
