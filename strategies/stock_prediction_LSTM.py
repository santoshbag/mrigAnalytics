import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.metrics import mean_squared_error
import datetime
import mrigutilities as mu


def prediction(symbol,showplot=False):

    stock = symbol
    today = datetime.date.today() - datetime.timedelta(days=0)
    start = today - datetime.timedelta(days=365 * 4)

    # Fetch historical stock data (TCS)
    # data = yf.download(stock, start=start, end=today)['Close']
    data = mu.getStockData(stock, start_date=start)['close']
    print(data)

    if showplot:
        # Plot the stock price history
        plt.figure(figsize=(10, 6))
        plt.plot(data, label=stock + " Stock Price")
        plt.title(stock + " Stock Price History")
        plt.xlabel("Date")
        plt.ylabel("Price (INR)")
        plt.legend()
        plt.show()

    # Preprocess data
    scaler = MinMaxScaler(feature_range=(0, 1))
    data_scaled = scaler.fit_transform(np.array(data).reshape(-1, 1))

    # Define training and testing sets
    train_size = int(len(data_scaled) * 0.8)
    train_data, test_data = data_scaled[:train_size], data_scaled[train_size:]


    # Function to create dataset with look-back window
    def create_dataset(dataset, time_step=60):
        X, Y = [], []
        for i in range(len(dataset) - time_step - 1):
            X.append(dataset[i:(i + time_step), 0])
            Y.append(dataset[i + time_step, 0])
        return np.array(X), np.array(Y)


    # Check if the data is long enough for the chosen time_step
    time_step = 60
    if len(train_data) <= time_step or len(test_data) <= time_step:
        raise ValueError(f"Dataset is too short for the selected time_step of {time_step} days.")

    # Create train and test datasets
    X_train, y_train = create_dataset(train_data, time_step)
    X_test, y_test = create_dataset(test_data, time_step)

    # Reshape input to be [samples, time steps, features] for LSTM
    X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
    X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

    # Build LSTM model
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(25))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train, y_train, epochs=50, batch_size=64, validation_data=(X_test, y_test), verbose=1)

    # Predict on test data
    predictions = model.predict(X_test)
    predictions = scaler.inverse_transform(predictions)  # Reverse scaling

    # Invert scaling for y_test to compare predictions with actual prices
    y_test_rescaled = scaler.inverse_transform(y_test.reshape(-1, 1))

    # Plot the predicted vs actual prices
    if showplot:
        plt.figure(figsize=(12, 6))
        plt.plot(y_test_rescaled, label="Actual Price")
        plt.plot(predictions, label="Predicted Price")
        plt.title(stock + " Stock Price Prediction - LSTM")
        plt.xlabel("Days")
        plt.ylabel("Price (INR)")
        plt.legend()
        plt.show()

    # Calculate RMSE for model evaluation
    rmse = np.sqrt(mean_squared_error(y_test_rescaled, predictions))
    print(f"Root Mean Squared Error: {rmse:.2f} INR")

    # Number of days to predict into the future
    num_days = 30

    # Start with the last 60 days of data in the test set
    last_60_days = test_data[-time_step:]
    future_predictions = []

    # Generate predictions iteratively
    for _ in range(num_days):
        # Reshape last_60_days to be [samples, time steps, features]
        X_input = last_60_days.reshape((1, time_step, 1))

        # Predict the next day's price
        next_pred = model.predict(X_input)

        # Store the prediction (in scaled form)
        future_predictions.append(next_pred[0, 0])

        # Update last_60_days by removing the oldest price and adding the new prediction
        last_60_days = np.append(last_60_days[1:], next_pred, axis=0)

    # Inverse scale the predictions to get actual prices
    future_predictions_rescaled = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))

    # Prepare dates for plotting (extend by num_days)
    future_dates = pd.date_range(data.index[-1], periods=num_days + 1, freq='B')[1:]

    # Plot the actual test data, model predictions on test data, and future predictions
    if showplot:
        plt.figure(figsize=(12, 6))
        plt.plot(data.index[-len(y_test):], y_test_rescaled, label="Actual Price")
        plt.plot(data.index[-len(predictions):], predictions, label="Predicted Price")
        plt.plot(future_dates, future_predictions_rescaled, label="Future Predictions", linestyle="--")
        plt.title(stock + " Stock Price Prediction - LSTM")
        plt.xlabel("Date")
        plt.ylabel("Price (INR)")
        plt.legend()
        plt.show()

    return {'actual_price' : {'x' : data.index[-len(y_test):],'y' :y_test_rescaled },
            'predicted_price': {'x': data.index[-len(predictions):], 'y': predictions},
            'future_price': {'x': future_dates, 'y': future_predictions_rescaled},
            }

