# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 19:44:28 2017

@author: kevinzen
"""

from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import pandas as pd
import urllib.request
from alpha_vantage.timeseries import TimeSeries as ts
import re, os, requests, sys
from datetime import datetime as dt
import numpy as np

def get_most_advance(url):
	pat = r"^http://www.nasdaq.com/symbol/(.*)/premarket$"
	try:
		soup = bs(urlopen(url), "html.parser")
	except urllib.error.HTTPError as e:
		print(e)
		sys.exit(0)
	possible_stocks = []
	for link in soup.find_all('a'):
	    stock = link.get('href')
	    if (stock):
	        tmp = re.search(pat, stock)
	        if (tmp):
	            possible_stocks.append(tmp.group(1))

	return (possible_stocks[10:20])

####
# Query live stock prices

Email_Count = int("0")
# Email_Count = 0
# COUNT = 0

def email(recipient ,msg):
    # global COUNT
    # COUNT = COUNT + 1
    # print(Test_String)
    # print(Email_Count)
    # print(Count_Dict["Count"])
    # Count = Email_Count
    # Test = Test_String
    # Count = Email_Count
    # Count = Email_Count
    # print("email function begins")
    Count = 2
    # print("Count: " + str(Count))
    if Count != 2 && Count < 5:
        print("Count < 5")
        f = open("Django_Proj/Django_Proj/Daily_Logs.txt", "a+")
        f.write("\nNew Log\n\n" + msg)
        f.close()
    if Count == 2:
        print("Count = 2")
        f = open("Django_Proj/Django_Proj/5_Day_Log.txt", "a+")
        f.write("\n5-Day Log\n\n" + msg)
        f.close()
    if Count == 5:
        print("Count = 5")
        open("Django_Proj/Django_Proj/Daily_Logs.txt", 'w').close()
        open("Django_Proj/Django_Proj/5_Day_Log.txt", 'w').close()

    print("msg: " + msg)
    domain_name = "sandbox2a36f3429ca4422ea31fe6d54e4688f0.mailgun.org"
    private_key = "key-422738ce8b1490c3f11f6df34adac083"
    return (requests.post(
        "https://api.mailgun.net/v3/" + domain_name +"/messages",
        auth=("api", private_key),
        data={"from": "Excited User <postmaster@"+domain_name+">",
              "to": recipient,
              "subject": "Hello",
              "text": msg}))

def read_df(df_path):
    if os.path.exists(df_path):
        old_df = pd.read_csv(df_path)
    else:
        df_cols = ["stock",
        "datetime",
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

    url = "http://www.nasdaq.com/extended-trading/premarket-mostactive.aspx"
    df_cols = ["stock"
        , "datetime"
		, "day0_9_19"
		, "day0_12_12"
		, "day0_15_51"
		, "day1"
		, "day2"
		, "day3"
		, "day4"
		, "day5"]

    new_df = pd.DataFrame(columns = df_cols)
    most_advance = get_most_advance(url)
    email(email_adrs, str(most_advance))
    new_df = new_df.append(pd.DataFrame({'stock':most_advance, 'datetime':[str(dt.now())]*10}))
    new_df.to_csv(tmp_df_path, index=False)

def run_update_old_stocks(email_adrs, old_df_path = os.path.join("old_stocks.csv")):

	# Read in old dataframe containing past stock info. TODO: PULL FROM DROPBOX
	old_df = read_df(old_df_path)

    # Update data table with a price at 9:09
	# dt = stock, start_datetime, day0_9_19, day0_12_12, day0_15_51, day1, day2, day3, day4, day5
	print("Starting to scrape old stocks for day 9_09")

	day_col = ['day5', 'day4','day3','day2','day1']
	for index, day in enumerate(day_col[:-1]):
	    prev_day = day_col[index+1]
	    col_stocks = old_df.loc[pd.isnull(old_df[day]) & pd.notnull(old_df[prev_day]), 'stock']
	    old_df.loc[pd.isnull(old_df[day]) & pd.notnull(old_df[prev_day]), day]= np.vectorize(get_stock_price, otypes = [np.float])(col_stocks, ["09:09:00"]*col_stocks.shape[0])

	email(email_adrs, "updated old stocks")
	old_df.to_csv(old_df_path, index=False)

def run_day0_9_19(email_adrs, tmp_df_path = "new_stocks.csv"):

    new_df = read_df(tmp_df_path)
    print("Starting to scrape old stocks for day 09_19")
    try:
        new_df['day0_9_19'] = np.vectorize(get_stock_price)(list(new_df['stock']), ["09:19:00"]*new_df.shape[0])
        # print("9:10 Execution: " + new_df[['datetime','day0_9_19']])
        email(email_adrs, new_df[['datetime','day0_9_19']].to_csv())
        new_df.to_csv(tmp_df_path, index=False)
    except ValueError:
        print("Error")
        return 0

def run_day0_12_12(email_adrs, tmp_df_path = "new_stocks.csv"):
    new_df = read_df(tmp_df_path)
    print("Starting to scrape old stocks for day 12_12")
    new_df['day0_12_12'] = np.vectorize(get_stock_price)(list(new_df['stock']), ["12:12:00"]*new_df.shape[0])
    # print("12:12 Execution: " + new_df[['datetime','day0_12_12']])
    email(email_adrs, new_df[['datetime','day0_12_12']].to_csv())
    new_df.to_csv(tmp_df_path, index=False)

def run_day0_15_51(email_adrs, old_df_path ="old_stocks.csv",  tmp_df_path = "new_stocks.csv"):

    new_df = read_df(tmp_df_path)
    print("Starting to scrape old stocks for day 15_12")
    new_df['day0_15_51'] = np.vectorize(get_stock_price)(list(new_df['stock']), ["15:51:00"]*new_df.shape[0])
    email(email_adrs, new_df[['datetime','day0_15_51']].to_csv())
    # print("15:51 Execution: " + new_df[['datetime','day0_15_12']])

    # Last reading, we append the new tmp df to the old df.
    old_df = read_df(old_df_path)
    old_df = old_df.append(new_df)
    old_df.to_csv(old_df_path, index=False)

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

    options[run_mode](email_adrs = ["matthewchan2147@gmail.com"])
    print("Successfully recorded old and new stocks.")

run_one_day('advanced')
run_one_day('time2')
run_one_day('time1')
run_one_day('time1')
run_one_day('time1')
run_one_day('time1')