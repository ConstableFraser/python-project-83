def init_db(cur, conn):
    cur.execute("DROP TABLE IF EXISTS url_checks")
    cur.execute("DROP TABLE IF EXISTS urls")

    cur.execute("CREATE TABLE urls( \
                 id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY, \
                 name varchar(255) UNIQUE NOT NULL, \
                 created_at float)")

    cur.execute("CREATE TABLE url_checks( \
                 id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY, \
                 url_id bigint REFERENCES urls (id), \
                 status_code integer, \
                 h1 text, \
                 title varchar(255), \
                 description text, \
                 created_at float)")

    conn.commit()
