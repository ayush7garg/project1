CREATE TABLE collections (
    userid VARCHAR REFERENCES users(userid),
    isbn_books_reviewed text,
    ratings NUMBER,
    reviews text,
    PRIMARY KEY(userid,isbn_books_reviewed)
);
