select distinct date as "STOCK" from stock_history order by date desc limit 1;
select max(date) as "RETURNS" from daily_returns;
select distinct "Date" as "MF" from mf_nav_history order by "Date" desc limit 1;
select max(date) as "OC" from option_chain_history;
