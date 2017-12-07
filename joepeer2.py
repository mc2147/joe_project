# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 19:44:28 2017

@author: kevinzen
"""
from bs4 import BeautifulSoup as bs
import pandas as pd
import re, os, requests, sys, traceback, logging
from datetime import datetime as dt
import numpy as np
from pandas.tseries.offsets import BDay

import urllib2

def test_scrape(url = "https://www.wsj.com/"):
    req = urllib2.Request(url = url, headers={'User-Agent' : "Magic Browser"})
    try:
        urllib2.urlopen(req)
        #soup = bs(urlopen(url), "html.parser")
    except Exception as e:
        logging.error(traceback.print_exc())
        print(e.fp.read())
        sys.exit(0)

# Tests
test_scrape("http://www.nasdaq.com/")
#run_one_day('advanced')
#run_one_day('time1')


