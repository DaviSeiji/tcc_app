from flask import Flask, render_template
from routes.usuario import bp_usuario
from routes.cirurgia import bp_cirurgia
from routes.sala import bp_sala
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key")

    # Registro do blueprint
    app.register_blueprint(bp_usuario, url_prefix="/")
    app.register_blueprint(bp_cirurgia, url_prefix="/")
    app.register_blueprint(bp_sala, url_prefix="/")

    # Página inicial genérica (pode redirecionar pra login)
    @app.route("/")
    def index():
        return render_template("index.html")

    # Tratamento de erro 404
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
