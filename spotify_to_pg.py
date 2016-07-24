import psycopg2
from pprint import pprint

try:
    conn = psycopg2.connect("dbname='hiphopdb' user='kdenny' host='localhost' password='America3!'")
except:
    print "I am unable to connect to the database"


cur = conn.cursor()

# cur.execute("CREATE TABLE rapper (rid serial PRIMARY KEY, name VARCHAR);")
# cur.execute("ALTER TABLE rapper ADD COLUMN city varchar(30);")


cur.execute("INSERT INTO rapper (name, city) VALUES ('Kanye West', 'Chicago');")
cur.execute("UPDATE rapper SET city = 'Chicago' WHERE name = 'Kanye West';;")



# cur.execute("CREATE TABLE features (mainrapper serial REFERENCES rapper, feature serial REFERENCES rapper, songtitle VARCHAR, popularity INTEGER);")




cur.execute("SELECT * FROM rapper;")



a = cur.fetchone()

pprint(a)

conn.commit()

cur.close()
conn.close()

# rows = cur.fetchall()

# cursor = conn.cursor()
# items = pickle.load(open(pickle_file,"rb"))
#
# for item in items:
#     city = item[0]
#     price = item[1]
#     info = item[2]
#
#     query =  "INSERT INTO items (info, city, price) VALUES (%s, %s, %s);"
#     data = (info, city, price)
#
#     cursor.execute(query, data)
#
# conn.commit()