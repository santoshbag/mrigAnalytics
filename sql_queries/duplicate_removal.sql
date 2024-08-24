-- step 1
CREATE TABLE basket_temp (LIKE ratios);
 
-- step 2
INSERT INTO basket_temp
SELECT 
    DISTINCT *
FROM ratios; 
 
-- step 3
DROP TABLE ratios;
 
-- step 4
ALTER TABLE basket_temp 
RENAME TO ratios;


delete from mf_returns mr using (SELECT nav_date,scheme_name FROM public.mf_returns
group by nav_date,scheme_name having count(*) > 1 order by nav_date desc) tmp
where mr.nav_date = tmp.nav_date and mr.scheme_name = tmp.scheme_name