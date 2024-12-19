#  Copyright (c) 2024.
import json

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import yfinance as yf
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.metrics import pairwise_distances
import plotly.figure_factory as ff
import mrigutilities as mu
import datetime

def analysis(scrip_data='nifty',show_plots=False):
    # Define stock symbols and sectors
    stocks = {
        "RELIANCE.NS": "Energy",
        "TCS.NS": "Technology",
        "INFY.NS": "Technology",
        "HDFCBANK.NS": "Finance",
        "ICICIBANK.NS": "Finance",
        "HINDUNILVR.NS": "Consumer Goods",
        "ITC.NS": "Consumer Goods",
        "LT.NS": "Industrial",
        "SBIN.NS": "Finance",
        "ONGC.NS": "Energy"
    }

    engine = mu.sql_engine()
    sql = '''
    SELECT symbol||'.NS' as symbol, industry
    	FROM security_master 
    	where symbol in 
    	('ADANIENT', 'ADANIPORTS', 'APOLLOHOSP', 'ASIANPAINT', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BEL', 'BPCL', 'BHARTIARTL', 'BRITANNIA', 'CIPLA', 'COALINDIA', 'DRREDDY', 'EICHERMOT', 'GRASIM', 'HCLTECH', 'HDFCBANK', 'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO', 'HINDUNILVR', 'ICICIBANK', 'ITC', 'INDUSINDBK', 'INFY', 'JSWSTEEL', 'KOTAKBANK', 'LT', 'M&M', 'MARUTI', 'NTPC', 'NESTLEIND', 'ONGC', 'POWERGRID', 'RELIANCE', 'SBILIFE', 'SHRIRAMFIN', 'SBIN', 'SUNPHARMA', 'TCS', 'TATACONSUM', 'TATAMOTORS', 'TATASTEEL', 'TECHM', 'TITAN', 'TRENT', 'ULTRACEMCO', 'WIPRO')
    '''
    n50 = pd.read_sql(sql, engine).set_index('symbol')['industry'][:20].to_dict()
    stocks = n50

    # Fetch stock price data for the last 4 years
    stock_symbols = list(stocks.keys())
    today = datetime.date.today() - datetime.timedelta(days=3)
    start = today - datetime.timedelta(days=365 * 4)
    # Download historical data for one year
    data = yf.download(stock_symbols, start=start, end=today)['Adj Close']

    # Fill missing values if any
    data.fillna(method="ffill", inplace=True)

    if show_plots:
        # Plot the stock price history
        plt.figure(figsize=(14, 7))
        for symbol in stocks:
            plt.plot(data[symbol], label=symbol)
        plt.title("Stock Price History of Selected Indian Stocks")
        plt.xlabel("Date")
        plt.ylabel("Adjusted Close Price (INR)")
        plt.legend(loc="upper left")
        plt.show()

    # Calculate daily returns
    returns = data.pct_change().dropna()
    # Fill missing values in returns with forward fill and drop any remaining NaN rows
    print("Checking for NaN values in returns DataFrame:")
    print(returns.isna().sum())
    returns = returns.fillna(method="ffill").dropna()

    print("Data types in returns DataFrame:")
    print(returns.dtypes)

    # Add sector labels
    sector_labels = [stocks[symbol] for symbol in returns.columns]

    # Standardize returns for clustering
    scaler = StandardScaler()
    returns_scaled = scaler.fit_transform(returns)

    print("Shape of scaled returns data:", returns_scaled.shape)
    print("Type of returns_scaled:", type(returns_scaled))

    print("First few rows of scaled data:", returns_scaled[:5])

    # Perform PCA to reduce dimensionality
    pca = PCA(n_components=2)
    pca_results = pca.fit_transform(returns_scaled)
    pca_data = [
        {"stock": stock, "sector": stocks[stock], "pca_x": x, "pca_y": y}
        for stock, (x, y) in zip(stock_symbols, pca_results)
    ]

    pca_results_json = pca_results.tolist()

    if show_plots:
        # Plot the PCA results with sector labels
        plt.figure(figsize=(10, 6))
        for sector in set(sector_labels):
            indices = [i for i, s in enumerate(sector_labels) if s == sector]
            plt.scatter(pca_results[indices, 0], pca_results[indices, 1], label=sector)
        plt.xlabel("PCA Component 1")
        plt.ylabel("PCA Component 2")
        plt.title("PCA of Stock Returns by Sector")
        plt.legend()
        plt.show()

    # Correlation Analysis
    corr_matrix = returns.corr()
    correlation_matrix = corr_matrix.values.tolist()
    print('SECTOR CORR',correlation_matrix)

    if show_plots:
        plt.figure(figsize=(12, 8))
        sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", xticklabels=returns.columns, yticklabels=returns.columns)
        plt.title("Correlation Matrix of Stock Returns")
        plt.show()

    # Hierarchical Clustering with Dendrogram
    # linked = linkage(pairwise_distances(returns_scaled, metric='euclidean'), method='ward')
    # Transpose returns_scaled to have stocks as rows (for clustering)
    returns_scaled_T = returns_scaled.T

    # Perform hierarchical clustering directly on the scaled returns
    linked = linkage(returns_scaled_T, method='ward')
    dendrogram_data = {
        'icoord': [],
        'dcoord': [],
        'ivl': [],
        'leaves': []
    }
    dendrogram_result = dendrogram(linked, no_plot=True)
    dendrogram_data['icoord'] = dendrogram_result['icoord']
    dendrogram_data['dcoord'] = dendrogram_result['dcoord']
    dendrogram_data['ivl'] = dendrogram_result['ivl']
    dendrogram_data['leaves'] = dendrogram_result['leaves']

    # Create dendrogram
    # Create dendrogram with correct orientation
    fig = ff.create_dendrogram(returns_scaled_T, orientation='bottom', labels=stock_symbols,
                               color_threshold=0.5 * max(linked[:, 2]))
    fig.update_layout(
        width=1000,
        height=600,
        xaxis=dict(title="Stocks", tickvals=list(range(len(stock_symbols))), ticktext=stock_symbols, automargin=True),
        yaxis=dict(title="Distance", automargin=True),
        margin=dict(t=50, l=50, r=50, b=150)
    )

    # Convert Plotly figure to JSON for React frontend
    fig_json = json.loads(fig.to_json())

    if show_plots:
        plt.figure(figsize=(10, 7))
        dendrogram(linked, labels=returns.columns, orientation='top', leaf_rotation=90)
        plt.title("Hierarchical Clustering Dendrogram")
        plt.xlabel("Stocks")
        plt.ylabel("Distance")
        plt.show()

    # K-Means Clustering
    # kmeans = KMeans(n_clusters=3)
    kmeans = KMeans(n_clusters=3, random_state=42)  # Added random_state for reproducibility
    clusters = kmeans.fit_predict(returns_scaled)
    cluster_data = [
        {"stock": stock, "sector": stocks[stock], "pca_x": x, "pca_y": y, "cluster": int(cluster)}
        for stock, (x, y), cluster in zip(stock_symbols, pca_results, clusters)
    ]
    clusters_json = clusters.tolist()


    try:
        kmeans.fit(returns_scaled)
        cluster_labels = kmeans.labels_
        print("Cluster labels for each stock:", dict(zip(returns.columns, cluster_labels)))
    except Exception as e:
        # Print error details
        print("An error occurred during KMeans fitting:", e)
        print("Shape of returns_scaled:", returns_scaled.shape)
        print("First few rows of scaled data:", returns_scaled[:5])
        print("Type of returns_scaled:", type(returns_scaled))

    # Visualize K-means Clustering in PCA space
    if show_plots:
        plt.figure(figsize=(10, 6))
        plt.scatter(pca_results[:, 0], pca_results[:, 1], c=cluster_labels, cmap="viridis")
        for i, symbol in enumerate(returns.columns):
            plt.text(pca_results[i, 0], pca_results[i, 1], symbol)
        plt.xlabel("PCA Component 1")
        plt.ylabel("PCA Component 2")
        plt.title("K-Means Clustering of Stock Returns")
        plt.colorbar(label="Cluster Label")
        plt.show()

    return {
        "pca_with_sector": pca_data,            # PCA results with sector labels
        "pca_with_clusters": cluster_data,                      # PCA results with KMeans clustering
        "correlation_matrix": correlation_matrix,       # Correlation matrix
        "dendrogram_data": dendrogram_data,              # Dendrogram data
        "dendrogram_fig": fig_json,  # Dendrogram Figure
        "labels" : stock_symbols
    }