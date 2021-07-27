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
UNION

(
SELECT "ISIN Div Payout/ ISIN Growth" as symbol,
    mf."Date" as date,
    to_number(mf."Net Asset Value",'9999999.9999') as price,
    to_number(mf."Net Asset Value",'9999999.9999') / lag(to_number(mf."Net Asset Value",'9999999.9999'), 1) OVER (PARTITION BY mf."ISIN Div Payout/ ISIN Growth" ORDER BY mf."Date") - 1::numeric AS daily_arithmetic_returns,
    ln(to_number(mf."Net Asset Value",'9999999.9999') / lag(to_number(mf."Net Asset Value",'9999999.9999'), 1) OVER (PARTITION BY mf."ISIN Div Payout/ ISIN Growth" ORDER BY mf."Date")) AS daily_log_returns
   FROM mf_nav_history mf where mf."Net Asset Value" ~ '^([0-9]+[.]?[0-9]*|[.][0-9]+)$'
   and  to_number(mf."Net Asset Value",'9999999.9999') <> 0 and mf."ISIN Div Payout/ ISIN Growth" ~ '[0-9a-zA-Z]'
  ORDER BY mf."ISIN Div Payout/ ISIN Growth", mf."Date"
)

UNION

(SELECT co.crude_benchmark as symbol,
    co.value_date as date,
    to_number(co.price,'9999999.99') as price,
    to_number(co.price,'9999999.99') / lag(to_number(co.price,'9999999.99'), 1) OVER (PARTITION BY co.crude_benchmark ORDER BY co.value_date) - 1::numeric AS daily_arithmetic_returns,
    ln(to_number(co.price,'9999999.99') / lag(to_number(co.price,'9999999.99'), 1) OVER (PARTITION BY co.crude_benchmark ORDER BY co.value_date)) AS daily_log_returns
   FROM crudeoil_prices co where co.price <> '' and co.crude_benchmark='BRENT'
   ORDER BY co.crude_benchmark, co.value_date
)  
UNION
(
SELECT 'GOLD' as symbol,
    gp.value_date as date,
    to_number(gp.price,'9999999.99') as price,
    to_number(gp.price,'9999999.99') / lag(to_number(gp.price,'9999999.99'), 1) OVER (ORDER BY gp.value_date) - 1::numeric AS daily_arithmetic_returns,
    ln(to_number(gp.price,'9999999.99') / lag(to_number(gp.price,'9999999.99'), 1) OVER (ORDER BY gp.value_date)) AS daily_log_returns
   FROM gold_prices gp where gp.price <> ''
  ORDER BY gp.value_date
)
);

#delete from daily_returns;

delete from TEMP_DAILY_RETURNS t1 using TEMP_DAILY_RETURNS t2 
where t1.id > t2.id and t1.date = t2.date and t1.symbol = t2.symbol;

#insert into daily_returns (symbol, date, price, daily_arithmetic_returns,daily_log_returns)
#(
#  select distinct symbol, date, price, daily_arithmetic_returns,daily_log_returns 
#  from TEMP_DAILY_RETURNS
#);

#delete from daily_returns where daily_arithmetic_returns is null;

#drop table TEMP_DAILY_RETURNS;

