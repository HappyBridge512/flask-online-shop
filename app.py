from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

# Создаем контекст приложения
with app.app_context():
    db.create_all()

# Flask-Admin
admin = Admin(app, name='Admin', template_mode='bootstrap3')
admin.add_view(ModelView(Product, db.session))


@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)


@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart = []
    if 'cart' in session:
        cart = session['cart']
    cart.append(product_id)
    session['cart'] = cart
    return redirect(url_for('index'))


@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    if product_id in cart:
        cart.remove(product_id)
        session['cart'] = cart
    return redirect(url_for('cart'))


@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    product_counts = {}  # Словарь для хранения количества каждого продукта
    total_price = 0

    # Подсчитываем количество каждого продукта
    for product_id in cart:
        product_counts[product_id] = product_counts.get(product_id, 0) + 1

    # Получаем продукты из БД и вычисляем общую стоимость
    products = []
    for product_id, quantity in product_counts.items():
        product = Product.query.get(product_id)
        if product:
            products.append({'product': product, 'quantity': quantity})
            total_price += product.price * quantity

    return render_template('cart.html', products=products, cart=cart, total_price=total_price)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('index'))

    return render_template('login.html')



if __name__ == '__main__':
    app.run(debug=True)
