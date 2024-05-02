#!/usr/bin/env python

import sys
from argparse import ArgumentParser, FileType
from configparser import ConfigParser
from confluent_kafka import Consumer, OFFSET_BEGINNING
import streamlit as st
import pandas as pd



if __name__ == '__main__':

    config_file_path = "getting_started.ini"
    with open(config_file_path, 'r') as config_file:
        config_parser = ConfigParser()
        config_parser.read_file(config_file)
        config = dict(config_parser['default'])
        config.update(config_parser['consumer'])

        
    
    # Create Consumer instance
    consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(consumer, partitions):
        # No command-line argument for --reset, assuming it's always True
        for p in partitions:
            p.offset = OFFSET_BEGINNING
        consumer.assign(partitions)
    

    def decode(value, topic, df):
        split_values = value.replace("(", "").replace(")", "").split(',')
        new_row = {"Close": float(split_values[0]),
                "Open": float(split_values[1]),
                "High": float(split_values[2]),
                "Low": float(split_values[3]),
                "Volume": float(split_values[4]),
                "Symbol": topic}
        df_data = df.to_dict('records') 
        df_data.append(new_row) 
        return pd.DataFrame(df_data)  


    st.write(""" Stock Chart """)
    df = pd.DataFrame(columns=['Close', 'Open', 'High', 'Low', 'Volume', 'Symbol'])
    # Poll for new messages from Kafka and print them.
    chart = st.line_chart(df.Close)
    sSymbol = st.session_state.Symbol 
    st.session_state['Value'] = st.selectbox(
                "Stock Value",
                ('Open', "Close", 'High', "Low", "Volume"),
                index=None,
                placeholder="Select Value"
                )
    if st.session_state['Value']:
        sValue = st.session_state['Value']
        topic = st.session_state.Symbol
        tickers = topic
        consumer.subscribe([topic], on_assign=reset_offset)
        print('topics', tickers)
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
                    df = decode(key,topic,df)
                    df2 = df.loc[df['Symbol'] == sSymbol]
                    chart.add_rows(df2[sValue])
                    print("Consumed event from topic {topic}: key = {key:12} value = {value:12}".format(
                        topic=msg.topic(), key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))
        except KeyboardInterrupt:
            pass
        finally:
            # Leave group and commit final offsets
            consumer.close()
