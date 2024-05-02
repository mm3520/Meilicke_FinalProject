
Description of Application:

The application that I created was a stock analyzer. The application consists of 5 microservices:
1)	Kafka Producer – This is the main landing page for the application. The user can select a stock symbol to analyze. That stock symbol is then used as the topic that all other microservices subscribe to.
2)	Chart Analyzer – This consumes all stock data being produced and lets the user filter the data by Open, Close, High, Low, and Volume. The filtered data is then displayed on a graph.
3)	Darvas Box Visualizer – This consumes only the Close data being produced. It plots the data, and then draws boxes around each day. The top of the box is the day’s high, and the bottom of the box is the day’s low. The microservice determines if the boxes are increasing or decreasing. It will tell the user if the current stock prices are in an ascending or descending box.
4)	Stock Prediction – This consumes all stock data and trains a time series ridge regression model. The trained ML model then predicts the stock price at the end of the day. Any incoming data is used to update predictions of the model. The trained model is passed to the administrator microservice through Streamlit’s built-in Rest API.
5)	Administrator – This consumes all stock data. The data is plotted on a chart along with the trained model to assess model performance. This microservice is password protected, with the default password being Admin.

Below is the flow diagram of the application.

 
![image](https://github.com/mm3520/Meilicke_FinalProject/assets/137839094/e26c329b-9bf5-4516-b439-b557a74455a8)



Installation:
Steps for installation:
1)	Clone the repository.
 
 ![image](https://github.com/mm3520/Meilicke_FinalProject/assets/137839094/ce52721b-39bc-4e0d-ba3e-5638f7f3f700)

2)	Navigate into main directory.
 
 ![image](https://github.com/mm3520/Meilicke_FinalProject/assets/137839094/b7cdcad7-b39b-4c2c-8619-ab774403f139)

3)	Build Docker Container
 
 ![image](https://github.com/mm3520/Meilicke_FinalProject/assets/137839094/72a68f4b-2b52-497b-a6ee-344225d160ff)

  a.	Note: You will need Docker Desktop installed. Click here for information on how to install Docker Desktop
  
4)	Run Container 
 
 ![image](https://github.com/mm3520/Meilicke_FinalProject/assets/137839094/9cc744c7-7e34-419b-9890-76fbd64e9acd)

5)	The application will be available on localhost:8501




API Documentation:
When the app is started, the user is brought to the welcome page. The welcome page is where the user can select the stock symbol that they would like to analyze. This tool can be use by someone who is just getting into stock trading, to help understand the basics.
In this demo, I will analyze Southwest Airlines, stock symbol LUV. 

![image](https://github.com/mm3520/Meilicke_FinalProject/assets/137839094/f570449c-54e8-4d7e-a2a7-9f525dea925e)

 
Once a stock symbol is entered, the user can go to any of the other pages to view the analysis. Starting with Stock Visualizer, the user can select a stock value; Open, Close, High, Low, or Volume. Once they make a selection, the incoming data is filtered by that value and the live data is displayed on a graph. For this example, I chose to look at volume. 
 ![image](https://github.com/mm3520/Meilicke_FinalProject/assets/137839094/2857cc15-95e5-4f6a-a6de-a77f384b329e)


Users can zoom in and view the data more closely by hovering over the graph and scrolling.


![image](https://github.com/mm3520/Meilicke_FinalProject/assets/137839094/3e045207-8e68-499b-97f7-e27dc8987750)
 

The user is free to switch stock values at any time. For this example, I switched to analyze the close data.

 ![image](https://github.com/mm3520/Meilicke_FinalProject/assets/137839094/f010b869-e0cb-40db-8bca-1fdab0ac3745)


Switching pages the Predict Stock Prices, users can receive a prediction of what the stock price will be at the end of the day. This prediction comes from a ridge regression model that was trained on the last 60 days of data. Additionally, the prediction is updated as new data becomes available.



![image](https://github.com/mm3520/Meilicke_FinalProject/assets/137839094/5761ef71-7a4c-4749-aa5e-0a184a06e4a3)







 

Switching pages to Darvas Boxes, users can see the last week of data. The app will draw boxes around each day with the top of the box being the high, and the bottom of the box being the low of the day. Based on the highs of each day, the app then determines if the boxes are rising or falling. According to the Darvas Box Theory, if the boxes are rising, one should invest when the stock enters a new rising box (i.e. buy when the stock price exceeds the high of the previous day), or they should sell if the stock enters a falling box (i.e. sell when the stock price is lower than the low of the previous day). The app lets the user know if the current stock price is in a rising or falling box.

 ![image](https://github.com/mm3520/Meilicke_FinalProject/assets/137839094/3d54e185-a9dc-44b7-9a4b-47ab0b379a1a)


Finally, the last microservice is the Admin page. This is a password protected page that shows the performance of the ML model used in the prediction page. 


![image](https://github.com/mm3520/Meilicke_FinalProject/assets/137839094/fb7dc0dd-515b-46d6-a064-d9263b02c893)


 

When the user enters the Admin page, they will be asked to enter a password. Default password is “Admin”. When the user enters the correct password, metrics on the ML model are displayed, so the administrator can view model performance and get an idea of how accurate predictions are.
 ![image](https://github.com/mm3520/Meilicke_FinalProject/assets/137839094/20094efc-c508-4641-88ff-0f886406a1ed)

At any time, the user can go back to the Welcome page and select a new stock symbol to analyze.
