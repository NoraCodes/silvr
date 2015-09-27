-- Schema file

DROP TABLE IF EXISTS entries;
CREATE TABLE entries (
  id INTEGER PRIMARY KEY NOT NULL ,
  title TEXT NOT NULL ,
  text TEXT NOT NULL
);