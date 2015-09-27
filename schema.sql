-- Schema file

DROP TABLE IF EXISTS entries;
CREATE TABLE entries (
  id INTEGER PRIMARY KEY NOT NULL ,
  posted TEXT NOT NULL , -- The date on which the post was posted.
  title TEXT NOT NULL ,
  text TEXT NOT NULL
);