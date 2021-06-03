delete from return_correlations;


insert into return_correlations
(select date, stock, daily_log_returns, 
corr(daily_log_returns,nifty) over (partition by stock order by date rows between 19 preceding and current row) as nifty_20_corr,
corr(daily_log_returns,nifty) over (partition by stock order by date rows between 49 preceding and current row) as nifty_50_corr,
corr(daily_log_returns,nifty) over (partition by stock order by date rows between 149 preceding and current row) as nifty_150_corr,
corr(daily_log_returns,nifty) over (partition by stock order by date rows between 249 preceding and current row) as nifty_250_corr,
corr(daily_log_returns,brent) over (partition by stock order by date rows between 19 preceding and current row) as brent_20_corr,
corr(daily_log_returns,brent) over (partition by stock order by date rows between 49 preceding and current row) as brent_50_corr,
corr(daily_log_returns,brent) over (partition by stock order by date rows between 149 preceding and current row) as brent_150_corr,
corr(daily_log_returns,brent) over (partition by stock order by date rows between 249 preceding and current row) as brent_250_corr,
corr(daily_log_returns,gold) over (partition by stock order by date rows between 19 preceding and current row) as gold_20_corr,
corr(daily_log_returns,gold) over (partition by stock order by date rows between 49 preceding and current row) as gold_50_corr,
corr(daily_log_returns,gold) over (partition by stock order by date rows between 149 preceding and current row) as gold_150_corr,
corr(daily_log_returns,gold) over (partition by stock order by date rows between 249 preceding and current row) as gold_250_corr

from
(select sh.date as date, sh.symbol as stock, sh.daily_log_returns as daily_log_returns , sh1.daily_log_returns as nifty , 
 co.daily_log_returns as brent, 
 gp.daily_log_returns as gold
from daily_returns sh
inner join daily_returns sh1 on sh.date = sh1.date
inner join daily_returns co on sh.date = co.date
inner join daily_returns gp on sh.date = gp.date
where sh1.symbol='NIFTY 50' and
co.symbol='BRENT' and gp.symbol='GOLD'
order by sh.symbol, sh.date asc) as dat)