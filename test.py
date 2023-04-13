#!/usr/bin/python3

from cs50 import SQL

db = SQL("sqlite:///finance.db")

row = db.execute("SELECT * FROM purchases WHERE id = 1")

print(row)
print(len(row))
