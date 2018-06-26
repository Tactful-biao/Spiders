DROP DATABASE movies;
CREATE DATABASE movies;
USE movies;

CREATE TABLE IF NOT EXISTS keyword(
    id VARCHAR(255) PRIMARY KEY,
    num int not NULL
);

CREATE TABLE IF NOT EXISTS movie(
    id INT auto_increment PRIMARY KEY,
    title CHAR(255) NOT NULL,
    seed CHAR(255) NOT NULL,
    size CHAR(255) NOT NULL,
    addtime CHAR(255) NOT NULL,
    kwd VARCHAR(255),
    CONSTRAINT keyword_fk FOREIGN KEY (kwd) REFERENCES keyword(id)
);
