import os
from flask import Flask, render_template, Blueprint, request, jsonify
import instaloader
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configurar la aplicación Flask
app = Flask(__name__)

# Definir el blueprint principal
main = Blueprint("main", __name__)

# Variable global para Instaloader
L = instaloader.Instaloader()

# Ruta principal
@main.route("/")
def index():
    return render_template("main/index.html")

# Ruta de inicio de sesión
@main.route("/login", methods=["POST"])
def login():
    USERNAME = os.getenv('INSTAGRAM_USERNAME')
    PASSWORD = os.getenv('INSTAGRAM_PASSWORD')
    try:
        L.login(USERNAME, PASSWORD)
        return jsonify({"requires_2fa": False})
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        return jsonify({"requires_2fa": True})
    except Exception as e:
        app.logger.error(f"Error durante el inicio de sesión: {e}")
        return render_template("main/error.html", error_message="Ocurrió un error durante el inicio de sesión."), 500

# Ruta para obtener seguidores
@main.route("/followers")
def followers():
    try:
        followers = get_followers()
        return render_template("instagram/followers.html", followers=followers)
    except Exception as e:
        app.logger.error(f"Error al obtener seguidores: {e}")
        return render_template("main/error.html", error_message="Ocurrió un error al obtener los seguidores."), 500

# Ruta para obtener usuarios que no siguen de vuelta
@main.route("/not_following_back")
def not_following_back():
    try:
        not_following_back_users = get_not_following_back()
        return render_template("instagram/not_following_back.html", not_following_back_users=not_following_back_users)
    except Exception as e:
        app.logger.error(f"Error al obtener usuarios que no siguen de vuelta: {e}")
        return render_template("main/error.html", error_message="Ocurrió un error al obtener usuarios que no siguen de vuelta."), 500

# Ruta para obtener usuarios que sigues pero no te siguen
@main.route("/following_not_followed")
def following_not_followed():
    try:
        following_not_followed_users = get_following_not_followed()
        return render_template("instagram/following_not_followed.html", following_not_followed_users=following_not_followed_users)
    except Exception as e:
        app.logger.error(f"Error al obtener usuarios que no sigues: {e}")
        return render_template("main/error.html", error_message="Ocurrió un error al obtener usuarios que no sigues."), 500

# Ruta para autenticación de dos factores
@main.route("/two_factor_auth", methods=["POST"])
def two_factor_auth():
    code = request.json.get('code')
    try:
        L.two_factor_login(code)
        return jsonify({"success": True})
    except Exception as e:
        app.logger.error(f"Error durante la autenticación 2FA: {e}")
        return render_template("main/error.html", error_message="Ocurrió un error durante la autenticación 2FA."), 500

# Funciones para obtener datos de Instagram
def get_followers():
    profile = instaloader.Profile.from_username(L.context, os.getenv('INSTAGRAM_USERNAME'))
    return list(profile.get_followers())

def get_not_following_back():
    profile = instaloader.Profile.from_username(L.context, os.getenv('INSTAGRAM_USERNAME'))
    followers = set(profile.get_followers())
    followees = set(profile.get_followees())
    return list(followees - followers)

def get_following_not_followed():
    profile = instaloader.Profile.from_username(L.context, os.getenv('INSTAGRAM_USERNAME'))
    followers = set(profile.get_followers())
    followees = set(profile.get_followees())
    return list(followers - followees)

# Registro del blueprint principal en la aplicación Flask
app.register_blueprint(main)

if __name__ == "__main__":
    app.run(debug=True)
