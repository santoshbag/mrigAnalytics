delete from temp_mf t1 using temp_mf t2
where t1.id > t2.id and t1."Date"=t2."Date" and t1."Scheme Name"=t2."Scheme Name";


delete from mf_nav_history;


insert into mf_nav_history ("Date","Fund House" ,
"Scheme Type",
"ISIN Div Payout/ ISIN Growth",
"ISIN Div Reinvestment",
"Scheme Name",
"Net Asset Value",
"Repurchase Price",
"Sale Price"
)

(select distinct "Date","Fund House" ,
"Scheme Type",
"ISIN Div Payout/ ISIN Growth",
"ISIN Div Reinvestment",
"Scheme Name",
"Net Asset Value",
"Repurchase Price",
"Sale Price" from temp_mf);
