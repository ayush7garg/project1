CREATE TABLE books (
    id SERIAL,
    isbn text PRIMARY KEY,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year INTEGER NOT NULL
);
