DROP TABLE IF EXISTS urls;

CREATE TABLE urls(
    id bigint PRIMARY KEY,
    name varchar(255) UNIQUE NOT NULL,
    created_at timestamp
);
