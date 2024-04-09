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