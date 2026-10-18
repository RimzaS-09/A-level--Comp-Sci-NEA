import os
import sqlite3


connection = sqlite3.connect("../data/graph/graph.db")

cursor = connection.cursor()

cursor.execute("SELECT COUNT (*) FROM nodes WHERE name IS NOT NULL")
print(cursor.fetchall())