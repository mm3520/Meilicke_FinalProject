import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split


password = st.text_input(
                    "Admin Password",
                    placeholder="Please Enter Password"
                    )

if password == st.session_state['Add_Pass']:
    model = st.session_state['Model']
    x = st.session_state['Model_x']
    y = st.session_state['Model_y']
    x_train = x[0:(x.shape[0]-200)]
    x_test = x[(x.shape[0]-200):-1]
    y_train = y[0:(y.shape[0]-200)]
    y_test = y[(y.shape[0]-200):-1]
    model.fit(x_train,y_train)
    y_pred = model.predict(x)
    df = pd.DataFrame({'Actual': y, 'Predicted': y_pred})
    chart = st.line_chart(df)
