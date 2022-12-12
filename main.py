from flask import Flask, render_template, request,url_for, redirect, flash ,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from sqlalchemy.orm import relationship
from werkzeug.security import  generate_password_hash, check_password_hash
from trending import Movies
import stripe
import json
app = Flask(__name__)

stripe_keys = {
    "secret_key": "sk_test_51LjJupSAelFje3XRnOSlhCJPXUWWohb2OybQZ9eefenyMWwhbTE7gVAsU4z61jmm9RpaXUGEV9NSpliZcDhGjG6A00r2SOfYBN",
    "publishable_key": "sk_test_51LjJupSAelFje3XRnOSlhCJPXUWWohb2OybQZ9eefenyMWwhbTE7gVAsU4z61jmm9RpaXUGEV9NSpliZcDhGjG6A00r2SOfYBN",
}
stripe.api_key = stripe_keys["secret_key"]

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '3ase7xrc86t9v7y0b8unim59c7tvoypibujnexrcfgvhj'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
movies = Movies()
movies.get_trending_movies()
trending_movies = movies.movie_data
carted_movies = []
ADDED_TO_CART = {
    "yes" : "Added to cart",
    "no" : "Add to cart",
}

stripe_checkout_movies = []

#Creating/Configuring Tables

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    c_no = db.Column(db.Integer,unique = True)
    address = db.Column(db.String(500))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    pin_code = db.Column(db.Integer)

class BlogPost(db.Model):
    __tablename__ = "test"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)


# db.create_all()

@app.route("/trending movies")
def show_movies():
    return render_template("movies.html", movies=trending_movies, total=len(trending_movies["title"]))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/', methods=['POST'])
def login_details():
    email = request.form['email']
    password = request.form["pass"]
    user_exist = db.session.query(User).filter_by(email=email).first()
    if user_exist :
        correct_password = check_password_hash(user_exist.password, password)
        if correct_password:
            # print(trending_movies)
            # redirect them to homepage

            # return render_template("movies.html",movies = trending_movies,total = len(trending_movies["title"]))
            return redirect(url_for("show_movies"))
        else:
            flash("Incorrect Password")
            return redirect(url_for('login_details'))
    else:
        flash("Looks Like you're a new user, kindly sign up")
        return redirect(url_for('create_acc'))


@app.route("/create",methods=["GET"])
def create_acc():
    return render_template("signup.html")


@app.route('/create', methods=['POST'])
def signup_details():
    email = request.form['email']
    password = request.form["pass"]
    hashed_password = generate_password_hash(password=password, method="pbkdf2:sha256", salt_length=8)
    name = request.form["name"]
    c_no = request.form["no"]
    address = request.form["address"]
    city = request.form["city"]
    state = request.form["state"]
    pincode = request.form["pincode"]
    # new_user = User(
    #     email=email,
    #     password=hashed_password,
    #     name=name,
    #     c_no=c_no,
    #     address=address,
    #     city=city,
    #     state=state,
    #     pin_code=pincode
    # )
    # db.session.add(new_user)
    # db.session.commit()
    # redirect them to homepage
    # return render_template("movies.html", movies=trending_movies, total=len(trending_movies["title"]))

    existing_user = db.session.query(User).filter_by(email=email).first()
    if existing_user:
        flash("You have already signed up with that email, Use login instead")
        return redirect(url_for('login_details'))
    else:
        new_user = User(
            email=email,
            password=hashed_password,
            name=name,
            c_no=c_no,
            address=address,
            city=city,
            state=state,
            pin_code=pincode
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("show_movies"))
        # redirect them to homepage
        # return redirect(url_for("show_movies"))


@app.route("/screen/<title>")
def show_movie(title):
    index = trending_movies["title"].index(title)
    name = title
    img = trending_movies["poster"][index]
    y_o_r = trending_movies["release_date"][index]
    genre = trending_movies["genre"][index]
    rating = trending_movies["ratings"][index]
    ov = trending_movies["overview"][index]

    # return "Hello"
    return render_template("screen.html",img = img,name = name,year = y_o_r,genre = genre,rating = rating,ov = ov)

@app.route("/search",methods =["GET", "POST"])
def search_movie():
    if request.method == "POST":
        movie_name = request.form.get("search")
        movie_data = movies.find_movie(movie_name)
        return render_template("screen.html",img = movie_data["poster"],name = movie_data["title"],year = movie_data["release_date"],genre = movie_data["genre"],rating = movie_data["ratings"],ov = movie_data["overview"])



@app.route("/cart.js/<title>")
def add_to_cart(title):
    try:
        index = trending_movies["title"].index(title)
    except ValueError:
        searched_movie = movies.find_movie(title)
        add_to_cart_movie = {
            "title": searched_movie["title"],
            "img": searched_movie["poster"],
            "ov": searched_movie["overview"]
        }
    else:
        img = trending_movies["poster"][index]
        ov = trending_movies["overview"][index]
        add_to_cart_movie = {
        "title" : title,
        "img" : img,
        "ov" : ov
    }
    if add_to_cart_movie not in carted_movies:
        carted_movies.append(add_to_cart_movie)
    return '', 204


def create_stripe_product(movie_name):
    product = stripe.Product.create(name =movie_name)
    price = stripe.Price.create(
        product = product.id,
        unit_amount = 999,
        currency = "inr"
    )
    product_id = price.id
    return product_id


@app.route("/showcart")
def show_cart():
    global stripe_checkout_movies
    global carted_movies
    #these below few lines of code gets the movie name of the items in cart and create a stripe product for it
    #the stripe product id is stored in the list for checkout puropse
    movie_names =[]
    for movie in carted_movies:
        stripe_checkout_movies.append(movie["title"])
    # for movie in movie_names:
    #     carted_product_ids.append(create_stripe_product(movie))
    # print(carted_product_ids)
    return render_template("cart.html",cmovies = carted_movies)


@app.route("/cart-checkout",methods = ["POST"])
def cart_checkout():
    global stripe_checkout_movies
    l_i = []
    for m in stripe_checkout_movies:
        a = {
            "price": create_stripe_product(movie_name=m),
            "quantity": 1,
        }
        l_i.append(a)
    domain_url = "https://movie-store-sswp.onrender.com"
    stripe.api_key = "sk_test_51LjJupSAelFje3XRnOSlhCJPXUWWohb2OybQZ9eefenyMWwhbTE7gVAsU4z61jmm9RpaXUGEV9NSpliZcDhGjG6A00r2SOfYBN"
    try:
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url + "cancelled",
            line_items=l_i,
            mode="payment",
        )
    except Exception as e:
        return jsonify(error=str(e)), 403

    return redirect(checkout_session.url, code=303)




@app.route("/create-checkout-session",methods = ["POST"])
def create_checkout_session():
    domain_url = "https://movie-store-sswp.onrender.com"
    stripe.api_key = "sk_test_51LjJupSAelFje3XRnOSlhCJPXUWWohb2OybQZ9eefenyMWwhbTE7gVAsU4z61jmm9RpaXUGEV9NSpliZcDhGjG6A00r2SOfYBN"

    try:
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url + "cancelled",
            line_items=[{
            "price": create_stripe_product(movie_name=request.form.get('m_name')),
            "quantity": 1,
        }],
            mode="payment",
        )
    except Exception as e:
        return jsonify(error=str(e)), 403

    return redirect(checkout_session.url,code=303)

@app.route("/delete/<title>")
def delete_movie(title):
    global carted_movies
    carted_movies = [movie for movie in carted_movies if movie["title"] != title]
    return redirect(url_for('show_cart'))

@app.route("/config")
def get_publishable_key():
    stripe_config = {"publicKey": stripe_keys["publishable_key"]}
    return jsonify(stripe_config)

if __name__ == "__main__":
    app.run("0.0.0.0",port=80,debug=True)