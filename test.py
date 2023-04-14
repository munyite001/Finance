#!/usr/bin/python3

from cs50 import SQL
from helpers import apology, login_required, lookup, usd

db = SQL("sqlite:///finance.db")

user_data = db.execute("SELECT * FROM purchases WHERE id = 7")
# headings = list(user_data[0].keys())[1:]
# print(headings)
for stock in user_data:
    data = lookup(stock["symbol"])
    print(data)


print(user_data)
