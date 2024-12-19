/*
 * Copyright (c) 2024.
 */

CREATE SCHEMA portfolio;

CREATE TABLE portfolio.users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    address TEXT,
    work_details TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE portfolio.portfolios (
    portfolio_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES portfolio.users(user_id),
    portfolio_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE portfolio.portfolio_items (
    item_id SERIAL PRIMARY KEY,
    portfolio_id INT NOT NULL REFERENCES portfolio.portfolios(portfolio_id),
    item_type VARCHAR(20) NOT NULL, -- 'stock', 'mutual_fund', etc.
    item_symbol VARCHAR(50) NOT NULL,
    quantity DECIMAL(12, 4) NOT NULL,
    purchase_price DECIMAL(12, 2) NOT NULL,
    purchase_date DATE NOT NULL
);

CREATE TABLE portfolio.transactions (
    transaction_id SERIAL PRIMARY KEY,
    portfolio_id INT NOT NULL REFERENCES portfolio.portfolios(portfolio_id),
    item_symbol VARCHAR(50) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL, -- 'buy' or 'sell'
    quantity DECIMAL(12, 4) NOT NULL,
    transaction_price DECIMAL(12, 2) NOT NULL,
    transaction_date TIMESTAMP NOT NULL
);
