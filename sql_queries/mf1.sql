drop table if exists temp_mf;

create table temp_mf 
(
id bigserial,
"Date" date,
"Fund House" text,
"Scheme Type" text,
"ISIN Div Payout/ ISIN Growth" text,
"ISIN Div Reinvestment" text,
"Scheme Name" text,
"Net Asset Value" text,
"Repurchase Price" text,
"Sale Price" text
);

insert into temp_mf ("Date","Fund House" ,
"Scheme Type",
"ISIN Div Payout/ ISIN Growth",
"ISIN Div Reinvestment",
"Scheme Name",
"Net Asset Value",
"Repurchase Price",
"Sale Price"
) 

(select * from mf_nav_history);
