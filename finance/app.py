import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

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
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


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
    #set session
    user_id = session["user_id"]

    #if the there are some transactions, do the following
    try:
        #make a table in index.html that displays symbol, shares, and price as the headers of columns
        portfolio_db = db.execute("SELECT symbol, SUM(shares) AS shares, price FROM portfolio WHERE user_id = ? GROUP BY symbol", user_id)
        #get how much cash the user currently has
        current_cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        #take just the cash number
        cash = current_cash_db[0]["cash"]
        #in the index.html template, use the table and the cash number to fill the database
        return render_template("index.html", database = portfolio_db, cash=cash)
    #if no transactions have been made yet, just show the blank index
    except:
        cash = 10000
        return render_template("index.html", cash=cash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    #set the session
    user_id = session["user_id"]
    if request.method == "GET":
        return render_template("buy.html")
    else:
        #get input symbol
        symbol = request.form.get("symbol")
        #return apologies if symbol was not inputed
        if not symbol:
            return apology("Please provide a symbol")
        #if shares was not inputed, give apology
        if not request.form.get("shares"):
            return apology("Please enter number of shares")
        #get input shares as an integer
        shares = request.form.get("shares")

        if not shares.isdigit():
            return apology("error")
        else:
            shares = int(shares)
            
        #return apologies if shares is not greater than 0
        if not shares > 0:
            return apology("Pease provide number of shares greater than 0")
        #lookup the symbol
        quote = lookup(symbol)
        #return apology if the symbol doesn't exist
        if quote == None:
            return apology("Not valid symbol")

        #calculate how much the cost of how much stock the user is buying
        buy_cost = shares * quote["price"]

        #get how much cash the user currently has
        current_cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        #get the current cash number
        current_cash = current_cash_db[0]["cash"]


        #if the cost of stock is greater than how much cash the user current has, give an apology
        if current_cash < buy_cost:
            return apology("Not enough cash")

        #calculate the updated cash amount
        updated_cash = current_cash - buy_cost
        #get the date and time at the time of buying the stock
        date = datetime.datetime.now()
        #update users table with the new cash amount
        db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_cash, user_id)
        #update the portfolio table
        db.execute("INSERT INTO portfolio (user_id, symbol, shares, price, date) VALUES (?, ?, ?, ?, ?)", user_id, quote["symbol"], shares, quote["price"], date)
        #flash a message, Bought!
        flash("Bought!")

        return redirect("/")



@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    #set the session
    user_id = session["user_id"]
    #if transactions have been made, do the following
    try:
        #get the portfolio table of the user
        portfolio_db = db.execute("SELECT symbol, shares, price, date FROM portfolio WHERE user_id = ?", user_id)
        #open history.html page with the database showing the portfolio table of the user
        return render_template("history.html", database=portfolio_db)
    #if no transactions yet, just show blank history
    except:
        return render_template("history.html")


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
    if request.method == "GET":
        #display form to request stock quote
        return render_template("quote.html")

    else:
        #input symbol
        symbol = request.form.get("symbol")

        #render apology if input is blank
        if symbol == "":
            return apology("please input a symbol")

        #call lookup function
        results = lookup(symbol)

        #render apology if symbol doesn't exist
        if results == None:
            return apology("symbol not found")

        #Displaying results
        return render_template("quoted.html", name=results["name"], symbol=results["symbol"], price=usd(results["price"]))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    session.clear()

    if request.method == "GET":
        #return register template
        return render_template("register.html")

    else:
        #input username
        username = request.form.get("username")

        #render apology if input is blank
        if username == "":
            return apology("please input a username")

        #render apology username already exists
        check = db.execute("SELECT username FROM users WHERE username = ?", username)
        if len(check) != 0:
            return apology("username already taken")

        #input password
        password = request.form.get("password")

        #require password to have 8 characters
        if len(password) < 8:
            return apology("Passwords must be at least 8 characters long")

        # min 1 upper case letter, 1 lowercase letter, 1 special character & 1 num
        #set sum of each required character & define allowed special characters
        sumupperletter = 0
        sumlowerletter = 0
        sumspecialchar = 0
        sumnum = 0
        specialchar = ['!', '#', '$', '%', '*', '@']

        #loop through every character
        for character in password:
            if character.isupper():
                sumupperletter += 1
            elif character.islower():
                sumlowerletter += 1
            elif character.isdigit():
                sumnum += 1
            else:
                if character in specialchar:
                    sumspecialchar += 1

        #if sum = 0 for any category, return apology
        if sumupperletter == 0 or sumlowerletter == 0 or sumspecialchar == 0 or sumnum == 0:
            return apology("Passwords must include at least 1 upper case letter, 1 lower case letter, 1 special character (!,#,$,%,*,@), and 1 number")

        #input password again
        confirmation = request.form.get("confirmation")

        #render apology if either input is blank or passwords don't match
        password = request.form.get("password")

        if password != confirmation:
            return apology("passwords do not match")

        if password == "":
            return apology("please input a password")

        #insert new user into users, storing hash of users password
        hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        #set session id
        session_id = db.execute("SELECT id FROM users WHERE users.username = ?", username)
        session["user_id"] = session_id[0]["id"]

        return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    #set the session
    user_id = session["user_id"]

    if request.method == "GET":
        available_symbols_db = db.execute("SELECT symbol FROM portfolio WHERE user_id = ? GROUP BY symbol", user_id)
        return render_template("sell.html", database = available_symbols_db)
    else:
        #get input symbol
        symbol = request.form.get("sell_symbol")
        #if shares was not inputed, give apology
        if not request.form.get("shares"):
            return apology("Please enter number of shares")
        #get input shares as an integer
        try:
            shares = int(request.form.get("shares"))
        except(ValueError):
            return apology("error")
        #return apologies if a symbol is not returned or if shares is not greater than 0
        if not symbol:
            return apology("Please provide a symbol")
        if not shares > 0:
            return apology("Pease provide number of shares greater than 0")
        #lookup the symbol
        quote = lookup(symbol)
        #return apology if the symbol doesn't exist
        if quote == None:
            return apology("Not valid symbol")

        #get a table with the number of shares the user has of the symbol it wants to sell
        available_shares_db = db.execute("SELECT SUM(shares) AS shares FROM portfolio WHERE user_id = ? AND symbol = ? GROUP BY symbol", user_id, symbol)
        #get just the number of shares
        available_shares = available_shares_db[0]["shares"]
        #if the user wants to sell more shares than it has, give an apology
        if shares > available_shares:
            return apology("Not enough shares")

        #calculate how much the user will get by selling the stock
        sell_cost = int(request.form.get("shares")) * quote["price"]
        #get how much cash the user currently has
        current_cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        #get the current cash number
        current_cash = current_cash_db[0]["cash"]

        #calculate the updated cash amount
        updated_cash = current_cash - sell_cost
        #get the date and time at the time of selling the stock
        date = datetime.datetime.now()
        #update users table with the new cash amount
        db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_cash, user_id)
        #update the portfolio table
        db.execute("INSERT INTO portfolio (user_id, symbol, shares, price, date) VALUES (?, ?, ?, ?, ?)", user_id, quote["symbol"], shares * -1, quote["price"], date)
        #flash a message, Sold!
        flash("Sold!")

        return redirect("/")
