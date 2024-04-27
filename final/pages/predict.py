#!/usr/bin/env python

import sys
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from confluent_kafka import Consumer, OFFSET_BEGINNING
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from sklearn.linear_model import Ridge


def get_date_from_string(expiration_date):
    return datetime.strptime(expiration_date, "%Y-%m-%d").date()

def get_MDY(x):
    for index, i in enumerate(x['Date']):
        i = str(i)
        split_values = i.split()[0].split("-")
        x.loc[(index, 'Year')] = split_values[0]
        x.loc[(index, 'Month')] = split_values[1]
        x.loc[(index, 'Day')] = split_values[2]
    return x 

def get_MDY2(date, vol, x):
    split_values = date.split()[0].split("-")
    split_values_vol = vol.replace("(", "").replace(")", "").split(',')
    new_row = {"Volume": split_values_vol[4],
                "Year": split_values[0],
                "Month": split_values[1],
                "Day": split_values[2]}
    df_data = x.to_dict('records') 
    df_data.append(new_row) 
    return pd.DataFrame(df_data)  
 

def train_model(sSymbol):
    sd = get_date_from_string('2023-04-01')
    ed = get_date_from_string('2024-03-29')
    dfvp = yf.download(tickers=sSymbol, start=sd, end=ed, interval="1d")
    y = dfvp["Close"]
    x = dfvp.drop(columns = ["Close", "High", "Low", "Open", "Adj Close"])
    x['Year'] = None
    x['Month'] = None
    x['Day'] = None
    x = x.reset_index()
    x = get_MDY(x)
    x = x.drop(columns= ["Date"])

    SVR_model = Ridge(positive = True)
    model = SVR_model.fit(x, y)

    return model, y

if __name__ == '__main__':
 
   # Prompt for configuration file
    config_file_path = "getting_started.ini"
    with open(config_file_path, 'r') as config_file:
        config_parser = ConfigParser()
        config_parser.read_file(config_file)
        config = dict(config_parser['default'])
        config.update(config_parser['consumer'])

    # Prompt for tickers
 
        
    topic = st.session_state.Symbol
    tickers = topic
    # Create Consumer instance
    consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(consumer, partitions):
        # No command-line argument for --reset, assuming it's always True
        for p in partitions:
            p.offset = OFFSET_BEGINNING
        consumer.assign(partitions)

    # Subscribe to topics
    consumer.subscribe([topic], on_assign=reset_offset)
    print('topics', tickers)


    def decode(value, topic, df):
        split_values = value.timestamp1.split()[0]
        new_row = {"Close": float(split_values[0]),
                "Open": float(split_values[1]),
                "High": float(split_values[2]),
                "Low": float(split_values[3]),
                "Volume": float(split_values[4]),
                "Symbol": topic}
        df_data = df.to_dict('records') 
        df_data.append(new_row) 
        return pd.DataFrame(df_data)  

    df = pd.DataFrame(columns=[ "Volume", 'Year', 'Month', 'Day'])
    
    # Poll for new messages from Kafka and print them.
    st.write(""" Stock Chart """)
    
    
    model, old = train_model(tickers)
    chart = st.line_chart(old)
    st.title('Prediction')

    output_text = st.empty()

    try:
        while True:
            msg = consumer.poll(1.0)
            print('msg', msg)
            if msg is None:
                # Initial message consumption may take up to
                # `session.timeout.ms` for the consumer group to
                # rebalance and start consuming
                print("Waiting...")
            elif msg.error():
                print("ERROR: %s".format(msg.error()))
            else:
                # Extract the (optional) key and value, and print.
                key = msg.key().decode('utf-8')
                value = msg.value().decode('utf-8')
                topic = msg.topic()
                print("Consumed event from topic {topic}: key = {key:12} value = {value:12}".format(
                    topic=msg.topic(), key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))
                df = get_MDY2(value,key,df)
                y_pred = model.predict(df)
                output_text.text(str(y_pred[-1]))

                
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()
