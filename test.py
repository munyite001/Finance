#!/usr/bin/python3

from cs50 import SQL
from helpers import apology, login_required, lookup, usd

db = SQL("sqlite:///finance.db")

current = lookup("nflx")["price"]


print(current)
