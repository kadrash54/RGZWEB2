from flask import Flask, session, render_template, redirect, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from Db import db
from Db.models import users, furnitures
from flask_migrate import Migrate



app = Flask(__name__)


app.secret_key = 'moba'  # Ключ для сессий
user_db = "kadr"
host_ip = "127.0.0.1"
host_port = "5432"
database_name = "furnitures"
password = "dota2"


app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user_db}:{password}@{host_ip}:{host_port}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def start():
    return redirect(url_for('index'))

@app.route("/app/index/", methods=['GET', 'POST'])
def index():
    furniture = furnitures.query.all()
    visible_user = session.get('username', 'Anon')

    return render_template('index.html', name=visible_user, furniture=furniture)


@app.route('/app/register', methods=['GET', 'POST'])
def registerPage():
    errors = []

    if request.method == 'GET':
        return render_template("register.html", errors=errors)

    username = request.form.get("username")
    password = request.form.get("password")

    if not (username and password):
        errors.append("Пожалуйста, заполните все поля")
        print(errors)
        return render_template("register.html", errors=errors)

    existing_user = users.query.filter_by(username=username).first()

    if existing_user:
        errors.append('Пользователь с данным именем уже существует')
        return render_template('register.html', errors=errors, resultСur=existing_user)

    hashed_password = generate_password_hash(password)

    new_user = users(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return redirect("/app/login")


@app.route('/app/login', methods=["GET", "POST"])
def loginPage():
    errors = []

    if request.method == 'GET':
        return render_template("login.html", errors=errors)
    
    username = request.form.get("username")
    password = request.form.get("password")

    if not (username and password ):
        errors.append("Пожалуйста, заполните все поля")
        return render_template("login.html", errors=errors)

    user = users.query.filter_by(username=username).first()

    if user is None or not check_password_hash(user.password, password):
        errors.append('Неправильный пользователь или пароль')
        return render_template("login.html", errors=errors)

    session['id'] = user.id
    session['username'] = user.username

    return redirect("index")
