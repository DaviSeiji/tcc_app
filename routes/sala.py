from flask import Blueprint, request, jsonify
from models.sala import Sala

bp_sala = Blueprint("sala", __name__)
