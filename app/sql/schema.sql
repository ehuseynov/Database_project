-- Drop tables if exist (for clean setup)
DROP TABLE IF EXISTS favorites CASCADE;
DROP TABLE IF EXISTS portfolio CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS stocks CASCADE;
DROP TABLE IF EXISTS currency CASCADE;

-- Users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    mail VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Stocks table
CREATE TABLE stocks (
    stock_id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255),
    price NUMERIC(10,2),
    field_of_work VARCHAR(255),
    number_of_shares NUMERIC(15,2),
    last_5_years_gain NUMERIC(10,2),
    last_52_weeks_high NUMERIC(10,2)
);

-- Favorites table
CREATE TABLE favorites (
    favorite_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    stock_id INT NOT NULL REFERENCES stocks(stock_id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT NOW()
);

-- Portfolio table
-- Note: As per the requirement, multiple stocks can be listed.
-- This is tricky because ideally you'd store multiple entries (one per stock).
-- Storing lists is not normalized. But since you requested "make it list", 
-- we'll store arrays. We'll just store arrays in a single row as demonstration.

CREATE TABLE portfolio (
    portfolio_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    stock_id INT[] NOT NULL,      -- array of stock ids
    quantity INT[] NOT NULL,      -- array of corresponding quantities
    price NUMERIC(10,2)[] NOT NULL -- array of corresponding buy prices
);

-- Currency table
CREATE TABLE currency (
    currency_code VARCHAR(10) PRIMARY KEY,
    currency_name VARCHAR(255),
    buy_rate NUMERIC(10,4),                        
    sell_rate NUMERIC(10,4),    
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Favorite currency table
CREATE TABLE Favorite_currency (
	favorite_currency_id SERIAL PRIMARY KEY,
	user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
	currency_code VARCHAR(10) NOT NULL REFERENCES currency(currency_code) ON DELETE CASCADE,
	updated_at TIMESTAMP DEFAULT NOW()
);




\COPY stocks(symbol, name, field_of_work, number_of_shares,last_5_years_gain,last_52_weeks_high) FROM 'app/sql/bist100.csv' DELIMITER ',' CSV HEADER;





