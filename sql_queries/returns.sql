insert into daily_returns (symbol, date, price, daily_arithmetic_returns,daily_log_returns)

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
) on conflict (symbol,date) 
do update
set daily_arithmetic_returns = excluded.daily_arithmetic_returns,
	daily_log_returns = excluded.daily_log_returns;

delete from daily_returns where daily_arithmetic_returns is null;
