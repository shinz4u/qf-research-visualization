import sqlite3

with sqlite3.connect("dash_user.db") as connection:
    c = connection.cursor()
    c.execute("DROP TABLE users")
    c.execute("CREATE TABLE users(users_id INTEGER PRIMARY KEY, username TEXT, password TEXT, is_admin INTEGER )")
    c.execute("INSERT INTO users VALUES(1,'admin','admin', 1)")
    c.execute("INSERT INTO users VALUES(2,'mohammed','shinoy', 0)")
    c.execute("INSERT INTO users VALUES(3,'rachel','fernandez', 0)")
    c.execute("INSERT INTO users VALUES(4,'noora','fetais', 1)")