# Finance Flask App README
## Introduction
This Flask app is a simple finance application that allows users to buy and sell stocks using the IEX API. The app allows users to register, login, and check their portfolio balance, transaction history, and buy and sell shares of stocks. The app uses the cs50 module to interact with an SQLite database to store user information and transactions.


 - [Live website]()
## Installation
Clone the repository
Clone the repository using the following command:

```bash
#   Copy code
git clone https://github.com/munyite001/Finance.git
```


### Install requirements
This app uses a number of Python packages that can be installed using pip. Use the following command to install all the requirements:

### Copy code
pip install -r requirements.txt
Set API Key
Before running the app, you will need to set your IEX API key. You can obtain an API key by signing up for a free account at IEX Cloud. Once you have an API key, set it as an environment variable named API_KEY.

For example, on Linux and macOS, you can set the environment variable as follows:

```bash
#   Copy code
export API_KEY=pk_12345678901234567890
#   Replace pk_12345678901234567890 with your IEX API key.
```

You can start the app by running the following command:

```bash
flask run
#   The app will be available at http://localhost:5000.
```
## Usage
### Register
To register, click on the "Register" link on the home page and fill in the registration form. You will be asked to provide a username and a password.

### Login
To login, click on the "Login" link on the home page and enter your username and password.

### Buy
To buy shares of a stock, click on the "Buy" link on the home page and enter the stock symbol and the number of shares you want to buy. If you don't have enough funds, you will not be able to make the purchase.

### Sell
To sell shares of a stock, click on the "Sell" link on the home page and enter the stock symbol and the number of shares you want to sell. If you don't have enough shares, you will not be able to make the sale.

### Portfolio
To view your portfolio, click on the Finance Logo link on the home page. You will see a list of all the stocks you own, their current prices, and the total value of your holdings.

### Transaction History
To view your transaction history, click on the "History" link on the home page. You will see a list of all your transactions, including buys and sells, the stock symbol, the number of shares, the price per share, and the date and time of the transaction.

### Logout
To logout, click on the "Logout" link on the home page.

## Credits
This project was built by [Emmanuel Munyite](https://github.com/munyite001)