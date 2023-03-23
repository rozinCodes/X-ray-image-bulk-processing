import psycopg2


conn = psycopg2.connect( host="localhost", database="Users", user="postgres", password="1234")

cur = conn.cursor()

cur.execute("CREATE TABLE users (username VARCHAR(255), email VARCHAR(255), password VARCHAR(255))")
conn.commit()

cur.close()

conn.close()