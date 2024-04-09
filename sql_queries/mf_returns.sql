insert into mf_returns (scheme_name,isin,nav_date,nav,daily_arithmetic_return,daily_log_return)
(SELECT mf_history.scheme_name as scheme_name,
 	mf_history.isin as isin,
    mf_history.nav_date as nav_date,
    mf_history.nav as nav,
    mf_history.nav / lag(mf_history.nav, 1) 
	OVER (PARTITION BY mf_history.scheme_name,mf_history.isin
    ORDER BY mf_history.nav_date) - 1::numeric AS daily_arith_return,
    ln(mf_history.nav / lag(mf_history.nav, 1)
	OVER (PARTITION BY mf_history.scheme_name,mf_history.isin
     ORDER BY mf_history.nav_date)) AS daily_log_return
   FROM mf_history
  WHERE nav > 0 and isin is not NULL
  ORDER BY mf_history.scheme_name, mf_history.isin,mf_history.nav_date desc)