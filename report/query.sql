-- New Database
USE mysql;
CREATE USER 'henrique'@'%' IDENTIFIED WITH mysql_native_password BY 'Olx@123';
GRANT ALL ON henrique.* TO 'henrique'@'%';



-- Quantidade de anuncios por ano
SELECT modelDate, COUNT(code)
FROM offer
WHERE model like '%OPALA%'
GROUP BY modelDate
ORDER BY 1 ASC;

-- Media de preço por ano
SELECT modelDate AS 'ANO', FORMAT(AVG(price),2) AS 'PREÇO'
FROM offer
WHERE model like '%OPALA%'
  AND price < 1000000
GROUP BY modelDate
ORDER BY 1 ASC;

-- Quantidade de anuncios por estado
SELECT state, COUNT(code)
FROM offer
WHERE model like '%OPALA%'
GROUP BY state
ORDER BY 2 DESC;

-- Média de preço por estado
SELECT state, AVG(price)
FROM offer
WHERE model like '%OPALA%'
  AND (description like '%4c%' OR description like '%4 c%' OR description like '%4 cil%')
  AND modelDate >= 1980
  AND modelDate <= 1984
GROUP BY state
ORDER BY 2 DESC;
