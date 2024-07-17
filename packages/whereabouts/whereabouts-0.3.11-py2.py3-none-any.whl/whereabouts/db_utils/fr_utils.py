# Clean French address data and transform into format suitable for
# whereabouts package
# Alex Lee
# 26 06 24

import os
import duckdb

db = duckdb.connect('fr_test.db')

filename = '/Users/alexlee/Desktop/Data/geo/addresses_france/adresses-france.csv'

query = f"""
COPY (
    WITH addresses_basic AS (
        SELECT row_number() over () addr_id, 
        numero, nom_voie, code_postal, nom_commune, lon, lat
        FROM
        read_csv('{filename}')
    )
    select 
    addr_id, 
    numero || ' ' || nom_voie || ' ' || code_postal || ' ' || nom_commune address,
    numero,
    nom_voie,
    code_postal,
    nom_commune,
    lat,
    lon
    from addresses_basic
)
TO 'addresses_fr.parquet'
(FORMAT 'parquet');
"""

db.execute(query).df()

query = """
with table_simple as (
    select nom_commune, code_postal from 
    read_csv('/Users/alexlee/Desktop/Data/geo/addresses_france/adresses-france.csv')
)
select * from table_simple
where code_postal="06230"
limit 5;
"""
