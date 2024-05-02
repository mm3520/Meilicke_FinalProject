#!/usr/bin/env python

import sys
from random import choice
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from confluent_kafka import Producer

import requests
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import date
from datetime import timedelta
import time
import yfinance as yf
import streamlit as st


import sys
import warnings

# Suppress all warnings
warnings.simplefilter("ignore")


def get_latest_stock_price(stock):
    data = stock.history()
    latest_stock_price = data['Close'].iloc[-1]
    return latest_stock_price

def get_today():
    return date.today()

def get_next_day_str(today):
    return get_date_from_string(today) + timedelta(days=1)

def get_date_from_string(expiration_date):
    return datetime.strptime(expiration_date, "%Y-%m-%d").date()

def get_string_from_date(expiration_date):
    return expiration_date.strftime('%Y-%m-%d')

if __name__ == '__main__':
    
    config_file_path = "getting_started.ini"
    with open(config_file_path, 'r') as config_file:
        config_parser = ConfigParser()
        config_parser.read_file(config_file)
        config = dict(config_parser['default'])
    if 'Symbol' not in st.session_state:
        st.session_state['Symbol'] = 0
    
    if 'Value' not in st.session_state:
        st.session_state['Value'] = 0
    
    if 'Add_Pass' not in st.session_state:
        st.session_state['Add_Pass'] = 'Admin'
    # Prompt for ticker
    st.session_state['Symbol'] = st.text_input(
                    "Stock Symbol",
                    placeholder="Select Symbol"
                    )
    

    ticker = st.session_state['Symbol']
    print('ticker', ticker)
    if st.session_state['Symbol']:
    # Create Producer instance
        producer = Producer(config)
    
        # Optional per-message delivery callback (triggered by poll() or flush())
        # when a message has been successfully delivered or permanently
        # failed delivery (after retries).
        def delivery_callback(err, msg):
            if err:
                print('ERROR: Message failed delivery: {}'.format(err))
            else:
                print("Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
                    topic=msg.topic(), key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))

        count = 0
        # Produce data by repeatedly fetching today's stock prices - feel free to change
        while True:

            # date range
            # sd = get_today()
            sd = get_date_from_string('2024-04-22')
            ed = sd + timedelta(days=1)
            # download data
            dfvp = yf.download(tickers=ticker, start=sd, end=ed, interval="1m")

            topic = ticker
            for index, row in dfvp.iterrows():
                value = f"{row['Close'], row['Open'], row['High'], row['Low'], row['Volume'] }"
                print(index, row['Close']) # debug only
                producer.produce(topic, str(index), str(value), callback=delivery_callback)
                count += 1
                time.sleep(5)

            # Block until the messages are sent.
            producer.poll(10000)
            producer.flush()
