insert into daily_returns (symbol, date, price, daily_arithmetic_returns,daily_log_returns)
(SELECT 'GOLD' as symbol,
    gp.value_date as date,
    to_number(gp.price,'9999999.99') as price,
    to_number(gp.price,'9999999.99') / lag(to_number(gp.price,'9999999.99'), 1) OVER (ORDER BY gp.value_date) - 1::numeric AS daily_arithmetic_returns,
    ln(to_number(gp.price,'9999999.99') / lag(to_number(gp.price,'9999999.99'), 1) OVER (ORDER BY gp.value_date)) AS daily_log_returns
   FROM gold_prices gp where gp.price <> ''
  ORDER BY gp.value_date
) on conflict (symbol,date) 
do update
set daily_arithmetic_returns = excluded.daily_arithmetic_returns,
	daily_log_returns = excluded.daily_log_returns;

delete from daily_returns where daily_arithmetic_returns is null;
