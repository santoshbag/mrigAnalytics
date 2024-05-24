/*
 * Copyright (c) 2024.
 */

drop table if exists market_instruments;
create table market_instruments (
	instrument_token text,
	exchange_token text,
	tradingsymbol text,
	name text,
    last_price numeric,
	expiry date,
	strike numeric,
	tick_size numeric,
	lot_size numeric,
    instrument_type text,
	segment text,
	exchange text,
	instrument_date date
);