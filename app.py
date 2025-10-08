from flask import Flask, jsonify, render_template
from routes.usuario import bp_usuario
from routes.cirurgia import bp_cirurgia
from routes.sala import bp_sala
from routes.paginas import bp_paginas

def create_app():
    app = Flask(__name__)

    # Registrar blueprints de API
    app.register_blueprint(bp_usuario, url_prefix="/api")
    app.register_blueprint(bp_cirurgia, url_prefix="/api")
    app.register_blueprint(bp_sala, url_prefix="/api")

    # Registrar blueprint de páginas
    app.register_blueprint(bp_paginas)

    # Tratamento de erros 404
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
