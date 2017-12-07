# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 19:44:28 2017

@author: kevinzen
"""

from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import pandas as pd
from alpha_vantage.timeseries import TimeSeries as ts
import re, os, requests, sys, traceback, logging, time
from datetime import datetime as dt
import numpy as np
from pandas.tseries.offsets import BDay

def get_most_advance(url):
	pat = r"^http://www.nasdaq.com/symbol/(.*)/premarket$"

	for i in range(0,5):
	    print("Trying to hit nasdaq attempt", i)
	    try:
	        soup = bs(urlopen(url), "html.parser")
	    except Exception as e:
	        logging.error(traceback.print_exc())
	        print(e.fp.read())
	        time.sleep(45) # wait 45 sec before attempting to hit nasdaq again.

	    else:
	        break
	else:
	    sys.exit("We failed all attempts")

	possible_stocks = []
	for link in soup.find_all('a'):
	    stock = link.get('href')
	    if (stock):
	        tmp = re.search(pat, stock)
	        if (tmp):
	            possible_stocks.append(tmp.group(1))
	prices = soup.find_all('td', text=re.compile("\$"))[10:20]
	prices = [str(x) for x in prices]
	prices = [re.findall(r"<td>\$ (.*) </td>", x)[0]for x in prices]
	return (possible_stocks[10:20], prices)


def get_5day_report(old_df):
    rv = []

    for i in range(1,6):
        past_date = str((dt.now().date() - BDay(i)).date())
        tmp_df = old_df.loc[old_df['datetime'] == past_date]

        if (tmp_df.shape[0] == 0): break
        # Get the last not null column (should contain price) [must ignore stock]
        price_col = tmp_df.loc[1].notnull()[:-1][::-1].idxmax()
        tmp = pd.Series(range(1, len(tmp_df)+1)).map(str) + ". " + tmp_df["stock"].map(str.upper)+ " $" + tmp_df[price_col].map(str)
        rv = rv + [past_date] + (list(tmp.dropna()))
    return ("\n".join(rv))

####
# Query live stock prices
COUNT = 0

# Delete_Texts() has to happen once a day at midnight
# MATT ADDED THIS
def Delete_Texts():
    global COUNT
    COUNT = 0
    open("Django_Proj/Django_Proj/Daily_Logs.txt", 'w').close()
    open("Django_Proj/Django_Proj/5_Day_Log.txt", 'w').close()


def send_email(recipients, subject, msg):
    # MATT'S CHANGES START
    global COUNT
    COUNT = COUNT + 1
    print(COUNT)
    Count = COUNT
    # print("Count: " + str(Count))
    if Count != 2 and Count < 5:
        print("Count < 5")
        f = open("Django_Proj/Django_Proj/Daily_Logs.txt", "a+")
        f.write("\nNew Log\n\n" + msg)
        f.close()
    if Count == 2:
        print("Count = 2")
        f = open("Django_Proj/Django_Proj/5_Day_Log.txt", "a+")
        f.write("\n5-Day Log\n\n" + msg)
        f.close()
    # MATT'S CHANGES END

    domain_name = "sandbox2a36f3429ca4422ea31fe6d54e4688f0.mailgun.org"
    private_key = "key-422738ce8b1490c3f11f6df34adac083"
    return (requests.post(
        "https://api.mailgun.net/v3/" + domain_name +"/messages",
        auth=("api", private_key),
        data={"from": "Support & Resist <postmaster@"+domain_name+">",
              "to": recipients,
              "subject": subject,
              "text": msg}))


def read_df(df_path):
    if os.path.exists(df_path):
        old_df = pd.read_csv(df_path)
    else:
        df_cols = ["stock",
        "datetime",
        "day0_8_58",
        "day0_9_19",
        "day0_12_12",
        "day0_15_51",
    	"day1",
    	"day2",
    	"day3",
    	"day4",
    	"day5"]

        old_df = pd.DataFrame(columns = df_cols)

    return(old_df)

def get_stock_price(stock, target_time = "09:09:00"):
	'''
		stock_getter (alpha_vantage timeseries object)
		stock (string) stock symbol
		target_time (string) of format "hh::mm::ss"
	'''
	try:
		alpha_key = "TD91BTQT213NQ21R"
		stock_getter= ts(alpha_key ,output_format = 'pandas')
		data, meta_data = stock_getter.get_intraday(stock, interval = '1min', outputsize='compact')
		rv = data.filter(regex= '^'+target_time + '$', axis=0)['close']
		if(len(rv) == 0):
			# use Last observation carried forward if target time can't be found
			rv = data.loc[: str(dt.now().date()) + ' ' + target_time][-1:]
			rv = rv.iloc[0]['close']
		return (rv)
	except :
		print("Couldn't retrieve stock data")
		return(-1)


def run_most_advance(email_adrs, tmp_df_path = "new_stocks.csv"):
    # Create a temp dataframe with the day's most advanced stocks.

    print("Starting to scrape from nasdaq.com")

    url = "http://www.nasdaq.com/extended-trading/premarket-mostactive.aspx"
    df_cols = ["stock",
    "datetime",
    "day0_8_58",
    "day0_9_19",
    "day0_12_12",
    "day0_15_51",
	"day1",
	"day2",
	"day3",
	"day4",
	"day5"]

    new_df = pd.DataFrame(columns = df_cols)
    most_advance, prices = get_most_advance(url)
    print(most_advance)
    print(prices)
    new_df = new_df.append(pd.DataFrame({'stock':most_advance, 'datetime':[str(dt.now().date())]*len(most_advance), 'day0_8_58':prices}))
    new_df.to_csv(tmp_df_path, index=False)

    # ADDED EMAIL LOGIC
    new_df_copy = pd.read_csv('new_stocks.csv')
    date = new_df_copy['datetime'][0].split()[0]
    formatted_date = dt.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
    subject = "8:58 AM (" + formatted_date + ") Pre-Market Report"

    stock_values = pd.Series(range(1, len(new_df) + 1)).map(str) + ".\t" + new_df["stock"].map(str.upper)+ "\t$" + new_df["day0_8_58"].map(str)
    stock_values = stock_values.dropna()
    stock_values = "\n\n".join(list(stock_values))

    message = "Here are your 8:58 AM pre-market values for " + formatted_date + ":\n\n" + stock_values + "\n"
    send_email(email_adrs, subject, message)


def run_update_old_stocks(email_adrs, old_df_path = os.path.join("old_stocks.csv")):
    # Read in old dataframe containing past stock info.
    old_df = read_df(old_df_path)
    # Update data table with a price at 9:09
    # dt = stock, start_datetime, day0_9_19, day0_12_12, day0_15_51, day1, day2, day3, day4, day5
    print("Starting to scrape old stocks for day 9_09")
    day_col = ['day5', 'day4','day3','day2','day1', 'day0_9_19']
    for index, day in enumerate(day_col[:-1]):
        prev_day = day_col[index+1]
        col_stocks = old_df.loc[pd.isnull(old_df[day]) & pd.notnull(old_df[prev_day]), 'stock']
        old_df.loc[pd.isnull(old_df[day]) & pd.notnull(old_df[prev_day]), day]= np.vectorize(get_stock_price, otypes = [np.float])(col_stocks, ["09:09:00"]*col_stocks.shape[0])
    #email(email_adrs, "updated old stocks")
    old_df.to_csv(old_df_path, index=False)
    message = get_5day_report(old_df)
    subject = "5-Day Watchlist (9:09 AM) Price Report"
    send_email(email_adrs, subject, message)


def run_day0_9_19(email_adrs, tmp_df_path = "new_stocks.csv"):

    new_df = read_df(tmp_df_path)
    print("Starting to scrape old stocks for day 09_19")
    new_df['day0_9_19'] = np.vectorize(get_stock_price)(list(new_df['stock']), ["09:19:00"]*new_df.shape[0])
    new_df.to_csv(tmp_df_path, index=False)

    # ADDED EMAIL LOGIC
    new_df_copy = pd.read_csv('new_stocks.csv')
    date = new_df_copy['datetime'][0].split()[0]
    formatted_date = dt.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
    subject = "9:19 AM (" + formatted_date + ") Price Report"

    stock_values = pd.Series(range(1, len(new_df) + 1)).map(str) + ".\t" + new_df["stock"].map(str.upper)+ "\t$" + new_df["day0_9_19"].map(str)
    stock_values = stock_values.dropna()
    stock_values = "\n\n".join(list(stock_values))

    message = "Here is your 9:19 AM price report for " + formatted_date + ":\n\n" + stock_values + "\n"
    send_email(email_adrs, subject, message)


def run_day0_12_12(email_adrs, tmp_df_path = "new_stocks.csv"):

    new_df = read_df(tmp_df_path)
    print("Starting to scrape old stocks for day 12_12")
    new_df['day0_12_12'] = np.vectorize(get_stock_price)(list(new_df['stock']), ["12:12:00"]*new_df.shape[0])
    new_df.to_csv(tmp_df_path, index=False)

    # ADDED EMAIL LOGIC
    new_df_copy = pd.read_csv('new_stocks.csv')
    date = new_df_copy['datetime'][0].split()[0]
    formatted_date = dt.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
    subject = "12:12 PM (" + formatted_date + ") Price Report"

    stock_values = pd.Series(range(1, len(new_df) + 1)).map(str) + ".\t" + new_df["stock"].map(str.upper)+ "\t$" + new_df["day0_12_12"].map(str)
    stock_values = stock_values.dropna()
    stock_values = "\n\n".join(list(stock_values))

    message = "Here is your 12:12 PM price report for " + formatted_date + ":\n\n" + stock_values
    send_email(email_adrs, subject, message)


def run_day0_15_51(email_adrs, old_df_path ="old_stocks.csv",  tmp_df_path = "new_stocks.csv"):

    new_df = read_df(tmp_df_path)
    print("Starting to scrape old stocks for day 15_12")
    new_df['day0_15_51'] = np.vectorize(get_stock_price)(list(new_df['stock']), ["15:51:00"]*new_df.shape[0])

    # Last reading, we append the new tmp df to the old df.
    old_df = read_df(old_df_path)
    old_df = old_df.append(new_df)
    old_df.to_csv(old_df_path, index=False)

    # ADDED EMAIL LOGIC
    new_df_copy = pd.read_csv('new_stocks.csv')
    date = new_df_copy['datetime'][0].split()[0]
    formatted_date = dt.strptime(date, "%Y-%m-%d").strftime("%m/%d/%Y")
    subject = "3:51 PM (" + formatted_date + ") Price Report"

    stock_values = pd.Series(range(1, len(new_df) + 1)).map(str) + ".\t" + new_df["stock"].map(str.upper)+ "\t$" + new_df["day0_15_51"].map(str)
    stock_values = stock_values.dropna()
    stock_values = "\n\n".join(list(stock_values))

    message = "Here is your 3:51 PM price report for " + formatted_date + ":\n\n" + stock_values
    send_email(email_adrs, subject, message)

    # Delete the new_df csv
    os.remove(tmp_df_path)

def run_one_day(run_mode):
    if(dt.today().weekday() >= 5):
        return()
    options = {'advanced' : run_most_advance,
                'old' : run_update_old_stocks,
                'time1' : run_day0_9_19,
                'time2' : run_day0_12_12,
                'time3' : run_day0_15_51
        }
    # LIVE LIST
    options[run_mode](email_adrs = ["kzenstratus@gmail.com", "matthewchan2147@gmail.com", "asitwala17@gmail.com", "joepeeer@yahoo.com"])
    # TEST LIST
    # options[run_mode](email_adrs = ["kzenstratus@gmail.com", "matthewchan2147@gmail.com", "asitwala17@gmail.com"])
    print("Successfully recorded old and new stocks.")



