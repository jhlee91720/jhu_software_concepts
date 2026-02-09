import psycopg

"""This is just a connection smoke test before we write any table/loader code. 
If this fails, nothing else matters yet. If it works, 
your environment + psycopg + Postgres permissions are good."""


conn = psycopg.connect("dbname=gradcafe")
cur = conn.cursor()
cur.execute("SELECT version();")
print(cur.fetchone()[0])

cur.close()
conn.close()