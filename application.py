import os
import requests
from flask import Flask, session,render_template,request,abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import urllib.parse
import urllib.request
import json

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login",methods=["POST"])
def login():
	return render_template("login.html")

@app.route("/signup",methods=["POST"])
def signup():
	return render_template("signup.html")

@app.route("/user",methods=["POST"])
def user():
	name = request.form.get("name")
	userid = request.form.get("userid")
	email = request.form.get("email")
	password = request.form.get("password")
	if db.execute("SELECT * FROM users WHERE userid = :userid OR email = :email", {"userid": userid,"email":email}).rowcount == 0:
		db.execute("INSERT INTO users (name,userid,email,password) VALUES (:name,:userid,:email,:password)",
			{"name":name,"userid":userid,"email":email,"password":password})
		db.commit()
		return render_template("success.html")
	else:
		return render_template("error1.html",message="User-name is already used or the email-id is already registered with us.")

@app.route("/afterlogin",methods=['POST'])
def afterlogin():
	email = request.form.get("email")
	password = request.form.get("password")
	if db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).rowcount == 0:
		return render_template("error.html", message="This email id is not registered with us.")
	elif db.execute("SELECT * FROM users WHERE password = :password AND email = :email", {"email": email,"password":password}).rowcount ==0:
		return render_template("error.html", message="Please enter the correct password.")
	return render_template("loggedin.html")

@app.route("/search",methods=['POST'])
def search():
    books = db.execute("SELECT*FROM books").fetchall()
    req_books = []
    author = request.form.get("author")
    title = request.form.get("title")
    isbn = request.form.get("isbn")
    if (author=="NULL" and title=="NULL" and isbn=="NULL" ):
        return render_template("error.html",message="Please enter the details of the book :)")
    else:
        for book in books:
            if (author!="NULL" and author in book.author and book not in req_books):
                req_books.append(book)
            elif (title!="NULL" and title in book.title and book not in req_books):
                req_books.append(book)
            elif (isbn!="NULL" and isbn in book.isbn and book not in req_books):
                req_books.append(book)
            # if ((author in book.author) or (title in book .title) or (isbn in book.isbn)):
            #     req_books.append(book)

    if (len(req_books)!=0):
        return render_template("search.html",bookss = req_books)
    # if db.execute("SELECT * FROM books WHERE (author LIKE (author) OR title LIKE (title) OR isbn LIKE (isbn))",{"author":author,"title":title,"isbn":isbn}).rowcount!=0:
    # 	bookss = db.execute("SELECT * FROM books WHERE (author LIKE (author) OR title LIKE (title) OR isbn LIKE (isbn))",{"author":author,"title":title,"isbn":isbn}).fetchall()
    # 	return render_template("search.html",bookss = bookss)
    # else:
    # 	return render_template("error.html",message="Sorry, No book found.")

@app.route("/search/<string:isbns>")
def book(isbns):
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "oMYVEpw7QCoGq9ItLysw", "isbns": "isbns"})
    res = res.json()
    r = json.loads(res)
    # r = res.json()
    r = r.get("average_rating","")
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn":isbns}).fetchone()
    # author = db.execute("SELECT author FROM books WHERE isbn = :isbn",{"isbn":isbns})
    # title = db.execute("SELECT title FROM books WHERE isbn = :isbn",{"isbn":isbns})
    return render_template("book.html",book=book,rating=r)
@app.route("/api/<isbns>")
def api(isbns):
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "oMYVEpw7QCoGq9ItLysw", "isbns": "isbns"})
    r = res.json()
    re = json.loads(r)
    if r!="NULL":
        print(re)
    else:
        abort(404)
