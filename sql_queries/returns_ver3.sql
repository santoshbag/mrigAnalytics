drop table if exists TEMP_DAILY_RETURNS;

create table TEMP_DAILY_RETURNS 
(
  id bigserial,
  symbol text not null,
  date date not null,
  price numeric,
  daily_arithmetic_returns numeric,
  daily_log_returns numeric
);

insert into TEMP_DAILY_RETURNS (symbol, date, price, daily_arithmetic_returns,daily_log_returns)

(
(SELECT stock_history.symbol as symbol,
    stock_history.date as date,
    stock_history.close_adj as price,
    stock_history.close_adj / lag(stock_history.close_adj, 1) OVER (PARTITION BY stock_history.symbol ORDER BY stock_history.date) - 1::numeric AS daily_arithmetic_returns,
    ln(stock_history.close_adj / lag(stock_history.close_adj, 1) OVER (PARTITION BY stock_history.symbol ORDER BY stock_history.date)) AS daily_log_returns
   FROM stock_history
  WHERE stock_history.series in ('EQ','IN') and close_adj <> 0
  ORDER BY stock_history.symbol, stock_history.date
)
);

delete from daily_returns;

delete from TEMP_DAILY_RETURNS t1 using TEMP_DAILY_RETURNS t2 
where t1.id > t2.id and t1.date = t2.date and t1.symbol = t2.symbol;

insert into daily_returns (symbol, date, price, daily_arithmetic_returns,daily_log_returns)
(
  select distinct symbol, date, price, daily_arithmetic_returns,daily_log_returns 
  from TEMP_DAILY_RETURNS
);

delete from daily_returns where daily_arithmetic_returns is null;

drop table TEMP_DAILY_RETURNS;

