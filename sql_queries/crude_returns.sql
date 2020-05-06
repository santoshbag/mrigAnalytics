insert into daily_returns (symbol, date, price, daily_arithmetic_returns,daily_log_returns)

(SELECT co.crude_benchmark as symbol,
    co.value_date as date,
    to_number(co.price,'9999999.99') as price,
    to_number(co.price,'9999999.99') / lag(to_number(co.price,'9999999.99'), 1) OVER (PARTITION BY co.crude_benchmark ORDER BY co.value_date) - 1::numeric AS daily_arithmetic_returns,
    ln(to_number(co.price,'9999999.99') / lag(to_number(co.price,'9999999.99'), 1) OVER (PARTITION BY co.crude_benchmark ORDER BY co.value_date)) AS daily_log_returns
   FROM crudeoil_prices co where co.price <> ''
  and co.crude_benchmark='BRENT'
  ORDER BY co.crude_benchmark, co.value_date
) on conflict (symbol,date) 
do update
set daily_arithmetic_returns = excluded.daily_arithmetic_returns,
	daily_log_returns = excluded.daily_log_returns;

delete from daily_returns where daily_arithmetic_returns is null;

