import os
import requests
from flask import Flask, session,render_template,request,abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import urllib.parse
import urllib.request
import json
import psycopg2

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

    req_books = []
    title = request.form.get("title")
    author = request.form.get("author")
    isbn = request.form.get("isbn")
    title = title.lower()
    author = author.lower()
    isbn = isbn.lower()
    if ((not title) and (not author) and(not isbn)):
        return render_template("error.html",message="Please enter the details of the book :)")
    else:
        connection = psycopg2.connect(user="vssprwfhhsjhyi",
                                  password="445f9361281f744abebdf72e1a375c0c4ef05a82e322a6d6a71ebf955310b154",
                                  host="ec2-54-225-129-101.compute-1.amazonaws.com",
                                  port="5432",
                                  database="d723f6ft1g0vt8")
        cursor = connection.cursor()
        if(title and author and isbn):
            author = '%'+author+'%'
            title = '%'+title+'%'
            isbn = '%'+isbn+'%'
            postgreSQL_select_Query = "select * from books where LOWER(title) LIKE %s AND LOWER(author) LIKE %s AND LOWER(isbn) LIKE %s"
            cursor.execute(postgreSQL_select_Query, (title,author,isbn,))
            req_books = cursor.fetchall()
        elif(title and author and (not isbn)):
            author = '%'+author+'%'
            title = '%'+title+'%'
            postgreSQL_select_Query = "select * from books where LOWER(title) LIKE %s AND LOWER(author) LIKE %s"
            cursor.execute(postgreSQL_select_Query, (title,author,))
            req_books = cursor.fetchall()
        elif(title and isbn and (not author)):
            isbn = '%'+isbn+'%'
            title = '%'+title+'%'
            postgreSQL_select_Query = "select * from books where LOWER(title) LIKE %s AND LOWER(isbn) LIKE %s"
            cursor.execute(postgreSQL_select_Query, (title,isbn,))
            req_books = cursor.fetchall()
        elif(isbn and author and (not title)):
            author = '%'+author+'%'
            isbn = '%'+isbn+'%'
            postgreSQL_select_Query = "select * from books where LOWER(isbn) LIKE %s AND LOWER(author) LIKE %s"
            cursor.execute(postgreSQL_select_Query, (isbn,author,))
            req_books = cursor.fetchall()
        elif(author and (not title) and (not isbn)):
            author = '%'+author+'%'
            postgreSQL_select_Query = "select * from books where LOWER(author) LIKE %s"
            cursor.execute(postgreSQL_select_Query, (author,))
            req_books = cursor.fetchall()
        elif(title and (not author) and (not isbn)):
            title = '%'+title+'%'
            postgreSQL_select_Query = "select * from books where LOWER(title) LIKE %s"
            cursor.execute(postgreSQL_select_Query, (title,))
            req_books = cursor.fetchall()
        elif(isbn and (not title) and (not author)):
            isbn = '%'+isbn+'%'
            postgreSQL_select_Query = "select * from books where LOWER(isbn) LIKE %s"
            cursor.execute(postgreSQL_select_Query, (isbn,))
            req_books = cursor.fetchall()
    if (len(req_books)!=0):
        i=[]
        for req_book in req_books:
            i.append(req_book[1])
        no_of_books=len(req_books)
        return render_template("search.html",bookss = req_books,i=i,no_of_books=no_of_books)
    else:
        return render_template("nobook.html",message="Sorry, No book found.")
    cursor.close()
    connection.close()
@app.route("/search/<string:isbns>")
def book(isbns):
    res = requests.get(url = "https://www.goodreads.com/book/review_counts.json", params = {"key": "oMYVEpw7QCoGq9ItLysw", "isbns": isbns})
    r = res.json()
    r = r['books'][0]['average_rating']
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn":isbns}).fetchone()
    # author = db.execute("SELECT author FROM books WHERE isbn = :isbn",{"isbn":isbns})
    # title = db.execute("SELECT title FROM books WHERE isbn = :isbn",{"isbn":isbns})
    return render_template("book.html",book=book,rating=r)
@app.route("/api/<string:isbns>")
def api(isbns):
    if requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "oMYVEpw7QCoGq9ItLysw", "isbns": isbns}):
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "oMYVEpw7QCoGq9ItLysw", "isbns": isbns})
        r = res.json()
        title,author,year = db.execute("SELECT title,author,year FROM books WHERE isbn = :isbn",{"isbn":isbns}).fetchone()
        ratings_count = r['books'][0]['work_ratings_count']
        average_rating = r['books'][0]['average_rating']
        return render_template("api.html",title=title,author=author,year=year,isbn=isbns,ratings_count=ratings_count,average_rating=average_rating)
    else:
        abort(404)
