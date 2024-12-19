#  Copyright (c) 2024.
import datetime

import yfinance as yf
import mrigstatics as ms
import pandas as pd
from fredapi import Fred
import numpy as np
from scipy.optimize import minimize
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import mrigutilities as mu
class port_opt():

    portfolio = []
    fred_key = ms.fred_api
    portfolio_daily_returns = {}
    portfolio_data = {}
    portfolio_metrics = []
    portfolio_optimization = {}
    def __init__(self,portfolio):
        self.portfolio = portfolio
        self.end_date = datetime.date.today()
        self.start_date = self.end_date - datetime.timedelta(days=365)
        self.portfolio_data = self.fetch_stock_data()
        self.portfolio_daily_returns = self.calculate_daily_returns()


    def fetch_stock_data(self):
        """
        Fetch historical stock data from Yahoo Finance.

        :param tickers: List of stock tickers (e.g., ['AAPL', 'MSFT']).
        :param start_date: Start date for data collection (YYYY-MM-DD).
        :param end_date: End date for data collection (YYYY-MM-DD).
        :return: Dictionary of DataFrames with stock data.
        """
        stock_data = {}
        for ticker in self.portfolio:
            # data = yf.download(ticker, start=self.start_date, end=self.end_date)
            data = mu.getStockData(ticker,start_date=self.start_date, end_date=self.end_date)
            stock_data[ticker] = data
        return stock_data

    def calculate_daily_returns(self):
        """
        Calculate daily returns for each stock.

        :param stock_data: Dictionary of DataFrames with stock data.
        :return: Dictionary of DataFrames with daily returns.
        """
        returns = {}

        stock_data = self.portfolio_data
        for ticker, data in stock_data.items():
            # data['Daily Return'] = data['Adj Close'].pct_change()
            data['Daily Return'] = data['close'].pct_change()
            returns[ticker] = data['Daily Return']
        return returns

    # # Example usage
    # tickers = ['AAPL', 'MSFT', 'GOOG']
    # start_date = '2020-01-01'
    # end_date = '2023-01-01'
    # stock_data = fetch_stock_data(tickers, start_date, end_date)

    def fetch_macro_data(self):
        """
        Fetch macroeconomic indicators from FRED.

        :param indicators: Dictionary of indicator IDs and their names.
                           (e.g., {'GDP': 'GDP', 'CPI': 'CPI Inflation'}).
        :param start_date: Start date for data collection (YYYY-MM-DD).
        :param end_date: End date for data collection (YYYY-MM-DD).
        :return: DataFrame with macroeconomic indicators.
        """

        fred = Fred(api_key=self.fred_key)
        indicators = {'GDP': 'GDP', 'CPIAUCSL': 'CPI Inflation', 'DGS10': '10-Year Treasury Rate'}

        macro_data = pd.DataFrame()
        for indicator_id, name in indicators.items():
            data = fred.get_series(indicator_id, self.start_date, self.end_date)
            macro_data[name] = data
        return macro_data

    def calculate_volatility(self):
        """
        Calculate annualized volatility for each stock.

        :param daily_returns: Dictionary of daily returns DataFrames.
        :return: Dictionary with tickers and their volatilities.
        """
        volatilities = {}
        daily_returns = self.portfolio_daily_returns
        for ticker, returns in daily_returns.items():
            volatilities[ticker] = np.std(returns.dropna()) * np.sqrt(252)  # Annualized
        return volatilities

    def calculate_beta(self):
        """
        Calculate beta for each stock.

        :param stock_returns: Dictionary of daily returns DataFrames.
        :param market_returns: DataFrame of market daily returns.
        :return: Dictionary with tickers and their betas.
        """
        betas = {}
        # nifty_50 = yf.download('^NSEI', start=self.start_date, end=self.end_date)
        nifty_50 = mu.getStockData('NIFTY 50',start_date=self.start_date, end_date=self.end_date)
        # nifty_50_returns = nifty_50['Adj Close'].pct_change()
        nifty_50_returns = nifty_50['close'].pct_change()
        market_returns = nifty_50_returns
        stock_returns = self.portfolio_daily_returns
        market_variance = np.var(market_returns.dropna())
        for ticker, returns in stock_returns.items():
            covariance = np.cov(returns.dropna(), market_returns.dropna())[0][1]
            betas[ticker] = covariance / market_variance
        return betas

    def calculate_var(self, confidence_level=0.95):
        """
        Calculate Value at Risk (VaR) for each stock.

        :param daily_returns: Dictionary of daily returns DataFrames.
        :param confidence_level: Confidence level for VaR (e.g., 0.95 for 95%).
        :return: Dictionary with tickers and their VaR values.
        """
        var_values = {}
        daily_returns = self.portfolio_daily_returns
        for ticker, returns in daily_returns.items():
            sorted_returns = sorted(returns.dropna())
            index = int((1 - confidence_level) * len(sorted_returns))
            var_values[ticker] = sorted_returns[index]
        return var_values

    def calculate_correlation_matrix(self):
        """
        Calculate the correlation matrix for stock daily returns.

        :param daily_returns: Dictionary of daily returns DataFrames.
        :return: DataFrame representing the correlation matrix.
        """
        returns_df = pd.DataFrame(self.portfolio_daily_returns)
        correlation_matrix = returns_df.corr()  # Compute correlation matrix
        return correlation_matrix

    def combine_metrics(self):
        """
        Combine all metrics into a single DataFrame.

        :param stock_data: Dictionary of stock data.
        :param volatilities: Dictionary of volatilities.
        :param betas: Dictionary of betas.
        :param var_values: Dictionary of VaR values.
        :return: DataFrame with all metrics.
        """
        metrics = []
        for ticker in self.portfolio_data.keys():
            metrics.append({
                'Ticker': ticker,
                'Volatility': self.calculate_volatility()[ticker],
                'Beta': self.calculate_beta()[ticker],
                'VaR': self.calculate_var()[ticker],
            })
        self.portfolio_metrics = pd.DataFrame(metrics)
        return self.portfolio_metrics

    def portfolio_optimization(self, risk_free_rate=0.01, objective="sharpe", constraints=None):
        """
        Optimize a portfolio based on a given objective.

        :param stock_returns: Dictionary of daily returns DataFrames for each stock.
        :param risk_free_rate: Risk-free rate for Sharpe ratio calculation.
        :param objective: Optimization objective ("sharpe", "min_risk", or "max_return").
        :param constraints: List of constraints (e.g., max weight, sector allocation).
        :return: Optimized portfolio weights and performance metrics.
        """

        stock_returns = self.portfolio_daily_returns
        # Convert returns to DataFrame
        returns_df = pd.DataFrame(stock_returns)

        # Mean and covariance
        mean_returns = returns_df.mean()
        cov_matrix = returns_df.cov()

        num_assets = len(mean_returns)
        initial_weights = np.ones(num_assets) / num_assets  # Equal weights

        # Objective functions
        def neg_sharpe_ratio(weights):
            portfolio_return = np.dot(weights, mean_returns)
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            return -(portfolio_return - risk_free_rate) / portfolio_volatility

        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

        def portfolio_return(weights):
            return -np.dot(weights, mean_returns)

        # Define objective
        if objective == "sharpe":
            objective_function = neg_sharpe_ratio
        elif objective == "min_risk":
            objective_function = portfolio_volatility
        elif objective == "max_return":
            objective_function = portfolio_return
        else:
            raise ValueError("Invalid objective. Choose 'sharpe', 'min_risk', or 'max_return'.")

        # Constraints
        constraints = constraints or [
            {"type": "eq", "fun": lambda x: np.sum(x) - 1}  # Weights must sum to 1
        ]

        # Bounds (weights must be between 0 and 1)
        bounds = [(0, 1) for _ in range(num_assets)]

        # Optimize
        result = minimize(
            objective_function,
            initial_weights,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )

        # Calculate performance metrics
        optimized_weights = result.x
        portfolio_return = np.dot(optimized_weights, mean_returns)
        portfolio_volatility = np.sqrt(np.dot(optimized_weights.T, np.dot(cov_matrix, optimized_weights)))
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility

        self.portfolio_optimization = {
            # "weights": optimized_weights,
            "weights": pd.DataFrame([[s,w] for s,w in zip(self.portfolio,optimized_weights)],columns=['Scrips','Optimized Weights']).to_json(orient='split'),
            "metrics": pd.DataFrame.from_dict({
                "return": [portfolio_return],
                "volatility": [portfolio_volatility],
                "sharpe_ratio": [sharpe_ratio],
            }).to_json(orient='split'),
        }
        # return {
        #     "weights": optimized_weights,
        #     "metrics": {
        #         "return": portfolio_return,
        #         "volatility": portfolio_volatility,
        #         "sharpe_ratio": sharpe_ratio,
        #     },
        # }
        return self.portfolio_optimization
    #
    # # Example Usage
    # tickers = ["AAPL", "MSFT", "GOOG"]
    # daily_returns = {ticker: stock_data[ticker]["Daily Return"] for ticker in stock_data}
    # result = portfolio_optimization(daily_returns, objective="sharpe")
    # print("Optimized Weights:", result["weights"])
    # print("Portfolio Metrics:", result["metrics"])

    def efficient_frontier(self):

        # Fetch stock data for a group of Indian stocks

        tickers = self.portfolio
        if len(tickers) < 1:
            tickers = ['ADANIENT.NS', 'ADANIGREEN.NS', 'ADANIPORTS.NS', 'ADANIPOWER.NS', 'AMBUJACEM.NS', 'ARVINDFASN.NS',
                       'ASHOKLEY.NS', 'ATUL.NS', 'BAJFINANCE.NS', 'BEL.NS', 'BRITANNIA.NS', 'CDSL.NS', 'COALINDIA.NS',
                       'DLF.NS', 'EXIDEIND.NS', 'GLENMARK.NS',
                       'GODREJPROP.NS', 'HAL.NS', 'HAPPSTMNDS.NS', 'HCLTECH.NS', 'HDFCBANK.NS', 'HINDALCO.NS',
                       'HINDUNILVR.NS', 'INDHOTEL.NS', 'INFY.NS', 'IOC.NS', 'ITC.NS', 'JYOTHYLAB.NS', 'KPITTECH.NS',
                       'M&M.NS', 'MTARTECH.NS', 'NATIONALUM.NS', 'NMDC.NS', 'NTPC.NS', 'PFC.NS', 'POWERGRID.NS',
                       'RECLTD.NS', 'SBIN.NS', 'TATAELXSI.NS', 'TATAMOTORS.NS',
                       'TATAPOWER.NS', 'TATASTEEL.NS', 'TCS.NS', 'VBL.NS', 'VEDL.NS', 'ZEEL.NS', 'ZOMATO.NS']


        # stock_data = {ticker: yf.download(ticker, start="2020-01-01", end="2023-01-01") for ticker in tickers}
        stock_data = self.portfolio_data
        # Adjust closing prices
        # adjusted_close = {ticker: data["Adj Close"] for ticker, data in stock_data.items()}
        adjusted_close = {ticker: data["close"] for ticker, data in stock_data.items()}
        prices_df = pd.DataFrame(adjusted_close)

        # Calculate daily returns
        daily_returns = pd.DataFrame(self.portfolio_daily_returns)

        # Mean returns and covariance matrix
        mean_returns = daily_returns.mean()
        cov_matrix = daily_returns.cov()

        # Simulate random portfolios
        num_portfolios = 5000
        results = np.zeros((3, num_portfolios))  # Rows for return, volatility, Sharpe ratio
        weights_record = []

        for i in range(num_portfolios):
            weights = np.random.random(len(tickers))
            weights /= np.sum(weights)  # Normalize to sum to 1
            weights_record.append(weights)

            # Portfolio return and volatility
            portfolio_return = np.dot(weights, mean_returns)
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe_ratio = portfolio_return / portfolio_volatility

            # Store the results
            results[0, i] = portfolio_return
            results[1, i] = portfolio_volatility
            results[2, i] = sharpe_ratio

        # Convert results to a DataFrame for easier manipulation
        portfolio_results_df = pd.DataFrame({
            "Return": results[0],
            "Volatility": results[1],
            "Sharpe_Ratio": results[2],
            # "Weights": weights_record
        })

        return portfolio_results_df

    def visualization(self,type='optimize'):
        """
            Visualize the optimized portfolio allocation using Plotly.

            :param optimized_result: Dictionary containing optimization results.
            :param tickers: List of stock tickers.
            """

        if type == 'optimize':
            weights = self.portfolio_optimization["weights"]
            fig = go.Figure(data=[go.Pie(labels=self.portfolio, values=weights, hole=0.4)])
            fig.update_traces(textinfo="percent+label")
            fig.update_layout(title_text="Optimized Portfolio Allocation", title_x=0.5)
            fig.show()
            return fig

        elif type == 'correlation':
            """
            Create an interactive heatmap using Plotly.

            :param correlation_matrix: DataFrame representing the correlation matrix.
            :param title: Title of the heatmap.
            """
            # fig = px.imshow(
            #     self.calculate_correlation_matrix(),
            #     text_auto=True,
            #     color_continuous_scale='coolwarm',
            #     labels=dict(color="Correlation"),
            #     title='Correlation Matrix'
            # )
            # fig.update_layout(title_x=0.5)  # Center the title
            # fig.show()

            plt.figure(figsize=(10, 8))
            sns.heatmap(self.calculate_correlation_matrix(), annot=True, cmap='coolwarm', fmt=".2f", cbar=True)
            plt.title('Correlation Matrix')
            plt.show()
            return plt

        elif type == 'efficient_f':

            # Plot the Efficient Frontier
            fig = go.Figure()
            portfolio_results_df = self.efficient_frontier()
            # Find the portfolio with the maximum Sharpe ratio
            max_sharpe_idx = portfolio_results_df["Sharpe_Ratio"].idxmax()
            max_sharpe_portfolio = portfolio_results_df.iloc[max_sharpe_idx]
            # print('max_sharpe_idx',max_sharpe_idx)
            # print('max_sharpe_portfolio',max_sharpe_portfolio)
            # Find the portfolio with the minimum volatility
            min_vol_idx = portfolio_results_df["Volatility"].idxmin()
            min_vol_portfolio = portfolio_results_df.iloc[min_vol_idx]
            # print('min_vol_idx',min_vol_idx)
            # print('min_vol_portfolio',min_vol_portfolio)
            # Add scatter plot for all portfolios
            fig.add_trace(go.Scatter(
                x=portfolio_results_df["Volatility"],
                y=portfolio_results_df["Return"],
                mode="markers",
                marker=dict(
                    size=5,
                    color=portfolio_results_df["Sharpe_Ratio"],
                    colorscale="Viridis",
                    colorbar=dict(title="Sharpe Ratio"),
                    showscale=True,
                ),
                name="Portfolios",
            ))

            # Highlight maximum Sharpe ratio portfolio
            fig.add_trace(go.Scatter(
                x=[max_sharpe_portfolio["Volatility"]],
                y=[max_sharpe_portfolio["Return"]],
                mode="markers",
                marker=dict(color="red", size=10, symbol="star"),
                name="Max Sharpe Ratio",
            ))

            # Highlight minimum volatility portfolio
            fig.add_trace(go.Scatter(
                x=[min_vol_portfolio["Volatility"]],
                y=[min_vol_portfolio["Return"]],
                mode="markers",
                marker=dict(color="blue", size=10, symbol="diamond"),
                name="Min Volatility",
            ))

            # Add layout details
            fig.update_layout(
                title="Efficient Frontier",
                xaxis_title="Volatility (Risk)",
                yaxis_title="Return",
                showlegend=True,
                template="plotly_dark"
            )

            fig.show()
            return fig

        else:
            return None

