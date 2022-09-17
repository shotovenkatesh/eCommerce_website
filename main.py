from flask import Flask, render_template, request,url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from sqlalchemy.orm import relationship
from werkzeug.security import  generate_password_hash, check_password_hash
from trending import Movies

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '3ase7xrc86t9v7y0b8unim59c7tvoypibujnexrcfgvhj'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
movies = Movies()
movies.get_trending_movies()
trending_movies = movies.movie_data


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

            return render_template("movies.html",movies = trending_movies,total = len(trending_movies["title"]))
        else:
            flash("Incorrect Password")
            return redirect(url_for('login_details'))
    else:
        flash("Looks Like you're a new user, kindly sign up")
        return redirect(url_for('create_acc'))


@app.route("/create")
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
    # # redirect them to homepage
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
        # redirect them to homepage
        return render_template("movies.html",movies = trending_movies,total = len(trending_movies["title"]))

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


@app.route("/checkout")
def check_out():
    return "This is checkout page"

if __name__ == "__main__":
    app.run("0.0.0.0",port=80,debug=True)