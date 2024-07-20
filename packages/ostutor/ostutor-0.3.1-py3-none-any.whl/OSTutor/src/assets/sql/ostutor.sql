DROP TABLE IF EXISTS inst;

DROP TABLE IF EXISTS opt;

DROP TABLE IF EXISTS inst_extra;

DROP TABLE IF EXISTS synonyms;

CREATE TABLE inst(
    id INTEGER PRIMARY KEY NOT NULL,
    name         TEXT NOT NULL,
    description  TEXT,
    brief        TEXT,
    synopsis     TEXT,
    rpm          TEXT,
    score        TEXT,
    example      TEXT,
    type         TEXT,
    uploader     INT DEFAULT 0,
    exist        INT DEFAULT 0
);

CREATE TABLE opt(
    id INTEGER PRIMARY KEY NOT NULL,
    inst_id INTEGER NOT NULL,
    name       TEXT,
    content    TEXT
);

CREATE TABLE inst_extra(
    id INTEGER PRIMARY KEY NOT NULL,
    inst_id INTEGER NOT NULL,
    title    TEXT,
    text     TEXT
);

CREATE TABLE synonyms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    synonym TEXT NOT NULL
);