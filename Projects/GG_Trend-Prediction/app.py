
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas_datareader as data
import streamlit as st
from sklearn import metrics


start = '2010-01-01'
end = '2019-12-31'

st.title('Stock Trend Prediction')

user_input = st.text_input('Enter Stock Ticker', 'AAPL')
df = data.DataReader(user_input, 'yahoo', start, end)

#Describing Data
st.subheader('Data from 2010 - 2019')
st.write(df.describe())

#Visualizations
st.subheader('Closing Price vs Time Chart')
fig = plt.figure(figsize = (12,6))
plt.plot(df.Close, 'b', label='Close')
plt.legend(loc="upper left")
st.pyplot(fig)

st.subheader('Closing Price vs Time Chart with 100MA')
ma100 = df.Close.rolling(100).mean()
fig = plt.figure(figsize = (12,6))
plt.plot(ma100, 'g', label='ma100')
plt.plot(df.Close, 'b', label='Close')
plt.legend(loc="upper left")
st.pyplot(fig)


st.subheader('Closing Price vs Time Chart with 100MA and 200MA')
ma100 = df.Close.rolling(100).mean()
ma200 = df.Close.rolling(200).mean()
fig = plt.figure(figsize = (12,6))
plt.plot(ma100, 'g', label='ma100')
plt.plot(ma200, 'r', label='ma200')
plt.plot(df.Close, 'b', label='Close')
plt.legend(loc="upper left")
st.pyplot(fig)

#Splitting data into Training and Testing

data_training = pd.DataFrame(df['Close'][0:int(len(df)*0.7)])
data_testing = pd.DataFrame(df['Close'][int(len(df)*0.7):int(len(df))])

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0,1))

data_training_array = scaler.fit_transform(data_training)

#Splitting data into x-train and y-train

x_train = []
y_train = []

for i in range(100, data_training_array.shape[0]):
    x_train.append(data_training_array[i-100: i])
    y_train.append(data_training_array[i, 0])
    
x_train, y_train = np.array(x_train), np.array(y_train)

#Load model
from keras.models import load_model
model = load_model('keras_model.h5')

#Test the model

past_100_days =  data_training.tail(100)
final_df = past_100_days.append(data_testing, ignore_index = True)

x_test = []
y_test = []

input_data = scaler.fit_transform(final_df)

for i in range(100, input_data.shape[0]):
    x_test.append(input_data[i-100: i])
    y_test.append(input_data[i, 0])

x_test, y_test = np.array(x_test), np.array(y_test)

#Making Prediction

y_predicted = model.predict(x_test)
scaler = scaler.scale_
scale_factor = 1/scaler[0]
y_predicted = y_predicted*scale_factor
y_test = y_test*scale_factor

st.subheader('Predicted vs Actual')
fig2 = plt.figure(figsize=(12,6))
plt.plot(y_test, 'b', label = 'Original Price')
plt.plot(y_predicted, 'r', label = 'Predicted Price')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
st.pyplot(fig2)

# R squared error
score_1 = metrics.r2_score(y_test, y_predicted)

# Mean Absolute Error
score_2 = metrics.mean_absolute_error(y_test, y_predicted)

st.title(score_1)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 