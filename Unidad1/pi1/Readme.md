# Proyecto Integrador 1

## QUERYS

guardar comandos en un txt: 
.output logs_comandos_numcontrol_U1.txt

SET force_download=true;

CREATE TABLE datos_raw AS
SELECT * FROM read_json_auto('https://jsonplaceholder.typicode.com/users');

SELECT * FROM datos_raw LIMIT 5;

SELECT 
address.city AS ciudad,
COUNT(id) AS total_usuarios,
COUNT(DISTINCT regexp_extract(email, '@(.*)$',1)) AS dominios_diferentes,
MIN(CAST(address.geo.lat AS DOUBLE)) AS latitud_minima,
MAX(CAST(address.geo.lat AS DOUBLE)) AS latitud_maxima,
FROM datos_raw
WHERE id % 2 = 0
GROUP BY address.city
ORDER BY total_usuarios DESC, ciudad ASC;

CREATE VIEW v_datos_anonimizados AS
SELECT id, name,
regexp_replace(email, '^(.{2}).*(@.*)$', '$1*****$2') AS email_protegido,
regexp_replace(phone, '.*(.{4})$', '***-***-$1') AS telefono_protegido,
address.city AS ciudad,
company.name AS empresa
FROM datos_raw;

SELECT * FROM v_datos_anonimizados LIMIT 2;

CREATE TABLE historico_usuarios_seguro AS
SELECT * FROM v_datos_anonimizados;

FROM historico_usuarios_seguro LIMIT 2;

DROP TABLE datos_raw;