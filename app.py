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


@app.route('/add_to_cart/<int:furniture_id>', methods=['POST'])
def add_to_cart(furniture_id):
    errors = []
    if 'id' not in session:
        errors.append('Сначала вам нужно зарегистрироваться')
        return redirect(url_for('index'))

    user_id = session['id']
    user = users.query.get(user_id)
    furniture = furnitures.query.get(furniture_id)

    # Используем сессии Flask для хранения товаров в корзине пользователя
    cart_items = session.get('cart_items', [])
    
    if furniture_id not in cart_items:
        cart_items.append(furniture_id)
        session['cart_items'] = cart_items

    return redirect(url_for('index'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'id' not in session:
        return redirect(url_for('index'))

    user_id = session['id']
    user = users.query.get(user_id)

    # Используем сессии Flask для хранения товаров в корзине пользователя
    cart_items_ids = session.get('cart_items', [])
    cart_items = furnitures.query.filter(furnitures.id.in_(cart_items_ids)).all()

    if request.method == 'POST':
        # Обработка оформления заказа
        # Очистка корзины, обновление базы данных и т.д.
        session.pop('cart_items', None)
        return redirect(url_for('index'))

    return render_template('checkout.html', user=user, cart_items=cart_items)


@app.route('/cart')
def view_cart():
    if 'id' not in session:
        return redirect(url_for('loginPage'))

    user_id = session['id']
    user = users.query.get(user_id)

    # Используем сессии Flask для хранения товаров в корзине пользователя
    cart_items_ids = session.get('cart_items', [])
    cart_items = furnitures.query.filter(furnitures.id.in_(cart_items_ids)).all()

    return render_template('cart.html', user=user, cart_items=cart_items)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    return redirect(url_for('index'))