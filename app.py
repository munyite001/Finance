import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    data = db.execute("SELECT * FROM purchases WHERE id = ?", session["user_id"])
    totalBalance = 0
    for stock in data:
        stock_details = lookup(stock["symbol"])
        stock["price"] = stock_details["price"]
        stock["total"] = stock["price"] * stock["shares"]
        totalBalance += stock["total"]

    user_balance = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]['cash']
    totalBalance += user_balance
    headings = ["symbol", "name", "shares", "price", "total"]
    return render_template("index.html", data=data, headings=headings, total=totalBalance, user_balance=user_balance)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """ Buy shares of stock """
    """Get stock quote."""
    #   When user submits the form
    if request.method == "POST":
        #   Store the symbol and shares in variables
        symbol = request.form.get("symbol")
        try:
            shares = int(request.form.get("shares"))
        except ValueError:
            return apology("Invalid Input", 400)
        #   Make sure that the symbol and shares are not  null
        if not symbol or not shares or shares < 0:
            return apology("Invalid Input", 400)

        data = lookup(symbol)
        if data == None:
            return apology("Invalid symbol", 400)
        
        price_per_share = data['price']
        total_price = shares * price_per_share
        
        user_balance = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]['cash']
        
        #   Check if user has the funds
        if user_balance < total_price:
            return apology("Insufficient Funds", 403)
        
        #   If user has the appropriate funds, make the purchase
        user_balance -= total_price

        #   update users table to deduct cash
        db.execute("UPDATE users SET cash = ? WHERE id = ?", user_balance, session["user_id"])
        #   Update the purchases table
        if len(db.execute("SELECT * FROM purchases WHERE id = ? AND symbol = ?", session["user_id"], symbol)) == 0:
            db.execute("INSERT INTO purchases (id, symbol, name, shares, price, total) VALUES (?, ?, ?, ?, ?, ?)", 
                       session["user_id"], symbol, data["name"], shares, price_per_share, total_price)
            
        elif len(db.execute("SELECT * FROM purchases WHERE id = ? AND symbol = ?", session["user_id"], symbol)) == 1:
            db.execute("UPDATE purchases SET shares = shares + ?, price = ?, total = total + ? WHERE symbol = ? AND id = ?", 
                       shares, price_per_share, total_price, symbol, session["user_id"])
        
        #   Update the history table
        db.execute("INSERT INTO history (id, symbol, shares, price, transacted) VALUES(?, ?, ?, ?, datetime('now'))", 
                   session["user_id"], symbol, shares, price_per_share)
        return redirect("/")
    
    #   If user got here via get render the quote template
    if request.method == "GET":
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    history = db.execute("SELECT * FROM history WHERE id = ?", session["user_id"])
    headings = list(history[0].keys())[1:]
    return render_template("history.html", history=history, headings=headings)
    

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    #   When user submits the form
    if request.method == "POST":
        #   Store the symbol in a variable
        symbol = request.form.get("symbol")
        #   Make sure that the symbol is not null
        if not symbol:
            return apology("You have to provide a symbol", 400)
        
        data = lookup(symbol)
        if data == None:
            return apology("Invalid symbol", 400)
        #   If all is well, render the quoted template
        return render_template("quoted.html", data=data)
    #   If user got here via get render the quote template
    if request.method == "GET":
        return render_template("quote.html")
        
    return apology("TODO")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        #   Get a list of all usernames to countercheck with the user's
        users = [user['username'] for user in db.execute("SELECT username FROM users")]
    # Ensure username was submitted
        if not username:
            return apology("Enter a valid username", 400)
        elif username in users:
            print("Username in users")
            return apology("The username has already been taken", 400)
        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)
        #   Ensure that password matches
        elif password != confirmation:
            return apology("passwords do not match", 400)

        #   If everything is okay

        #   First we create a hash for the user password
        user_hash = generate_password_hash(password)

        #   Thern we store the user details in the database
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, user_hash)
        return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock""" 
    user_stocks = db.execute("SELECT * FROM purchases WHERE id = ?", session["user_id"])
        
    symbols = [stock["symbol"] for stock in user_stocks]

    #   If method is POST
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))

        #   Ensure that the user has selected a value
        if symbol == "Symbol" or not shares:
            return apology("Invalid Input", 400)
        
        #   Check that the user, has the specified shares before selling
    
        stock = db.execute("SELECT * FROM purchases WHERE  id = ? and symbol = ?", session["user_id"], symbol)[0]
        user_shares = stock["shares"]
        if user_shares < shares:
            return apology("Insufficient Shares", 400)
        else:
            current_price = lookup(stock["symbol"])["price"]
            cash = current_price * shares

            #   Update user cash in db
            db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", cash, session["user_id"])
            
            #   Update purchases table to deduct share
            db.execute("UPDATE purchases SET shares = shares - ? WHERE symbol = ? AND id = ?", shares, symbol, session["user_id"])
            
            #   Update history table
            db.execute("INSERT INTO history (id, symbol, shares, price, transacted) VALUES(?, ?, ?, ?, datetime('now'))", 
                       session["user_id"], symbol, -shares, current_price)
            
            #   Check if you sold all shares of that stock and update the purchases accordingly
            if user_shares - shares == 0:
                db.execute("DELETE FROM purchases WHERE symbol = ? AND id = ?", symbol, session["user_id"])

            #   Redirect user to home
            return redirect("/")
        
        #   If the request was GET
    return render_template("sell.html", symbols=symbols)
        
