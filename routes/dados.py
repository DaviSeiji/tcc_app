from flask import Blueprint, render_template, request, redirect, url_for, session
from models.agenda import Agenda
from models.sala import Sala
from models.cirurgia import Cirurgia
from datetime import datetime, date, time

bp_dados = Blueprint("dados", __name__)


@bp_dados.route("/agendas")
def dados_usuario():
    return