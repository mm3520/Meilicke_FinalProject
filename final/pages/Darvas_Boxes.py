#!/usr/bin/env python

import sys
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from confluent_kafka import Consumer, OFFSET_BEGINNING
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import plotly.graph_objs as go

def get_date_from_string(expiration_date):
    return datetime.strptime(expiration_date, "%Y-%m-%d").date()

def get_MDY(x):
    x['Year'] = x['Datetime'].dt.year
    x['Month'] = x['Datetime'].dt.month
    x['Day'] = x['Datetime'].dt.day
    x['Hour'] = x['Datetime'].dt.hour
    x['Minute'] = x['Datetime'].dt.minute
    x['Date'] = x['Datetime'].dt.date
    x['Time'] = x['Datetime'].dt.time
    return x 


def get_MDY2(date, vol, x):
    split_values = date.split()[0].split("-")
    split_values_vol = vol.replace("(", "").replace(")", "").split(',')
    new_row = {"Close": split_values_vol[0],
                "Year": split_values[0],
                "Month": split_values[1],
                "Day": split_values[2]}
    df_data = x.to_dict('records') 
    df_data.append(new_row) 
    return pd.DataFrame(df_data)  

def graph(sSymbol):
    ed = get_date_from_string('2024-04-12')
    sd = get_date_from_string('2024-04-8')
    dfvp = yf.download(tickers=sSymbol, start=sd, end=ed, interval="1m")
    x = dfvp.drop(columns=["Volume", "High", "Low", "Open", "Adj Close"])
    x = x.reset_index()
    x = get_MDY(x)
    
    
    st.title("Draw Boxes Around Max and Min Points in Line Graph")

    # Create a Plotly line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x['Datetime'], y=x['Close'], mode='lines', name='Boxes'))

    # Find the index of the maximum and minimum points
    grouped = x.groupby('Date')['Close'].agg(['max', 'min']).reset_index()
    grouped["Start"] = grouped.apply(lambda row: f"{row['Date']} 9:30", axis=1)
    grouped["End"] = grouped.apply(lambda row: f"{row['Date']} 15:59", axis=1)

    # Add rectangles around max and min points
    for index, i in enumerate(grouped['Date']):
        fig.add_shape(
            type="rect",
            x0=grouped["Start"][index], y0=grouped["max"][index]+0.1,
            x1=grouped["End"][index], y1=grouped["min"][index]-0.1,
            line=dict(color="red")
        )

    # Render the chart
    st.plotly_chart(fig) 
    return grouped
def rise_fall(df):
    stat = ""
    increasing_columns = ( df['max'].iloc[-1] - df['max'].iloc[0]  > 0)
    decreasing_columns = ( df['max'].iloc[-1] - df['max'].iloc[0]  < 0)
    if increasing_columns:
        stat = "Boxes are Rising"
    elif decreasing_columns:
        stat = "Boxes are Falling"
    return stat

def get_Current(df, value):
    stat = ""
    increasing_columns = ( df['max'].iloc[-1] - value < 0)
    decreasing_columns = ( df['max'].iloc[-1] - value  > 0)
    if increasing_columns and not decreasing_columns:
        stat = "Current Stock Value is in a Rising Box"
    elif not increasing_columns and not decreasing_columns:
        stat = "Current Stock Value is steady"
    elif not increasing_columns and decreasing_columns:
        stat = "Current Stock Value is in a Falling Box'"
    return stat

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

 
    df = pd.DataFrame(columns=["Close", 'Year', 'Month', 'Day'])
    
    # Poll for new messages from Kafka and print them.
    st.write(""" Stock Chart """)
    st.write(topic)
    
    sSymbol = topic

    boxes = graph(sSymbol)
    output_text = st.empty()
    output_text_status = st.empty()
    stats = rise_fall(boxes)
    output_text = output_text.text(stats)

    
    
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
                current_close = float(df['Close'].iloc[-1])
                current_stat = get_Current(boxes, current_close)
                output_text_status.text(current_stat)
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()


