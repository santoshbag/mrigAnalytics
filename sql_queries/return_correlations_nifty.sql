delete from return_correlations;


insert into return_correlations
(select date, stock, daily_log_returns, 
corr(daily_log_returns,nifty) over (partition by stock order by date rows between 19 preceding and current row) as nifty_20_corr,
corr(daily_log_returns,nifty) over (partition by stock order by date rows between 49 preceding and current row) as nifty_50_corr,
corr(daily_log_returns,nifty) over (partition by stock order by date rows between 149 preceding and current row) as nifty_150_corr,
corr(daily_log_returns,nifty) over (partition by stock order by date rows between 249 preceding and current row) as nifty_250_corr

from
(select sh.date as date, sh.symbol as stock, sh.daily_log_returns as daily_log_returns , sh1.daily_log_returns as nifty 
from daily_returns sh
inner join daily_returns sh1 on sh.date = sh1.date
where sh1.symbol='NIFTY 50'
order by sh.symbol, sh.date asc) as dat)