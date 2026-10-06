import duckdb

with duckdb.connect("usuarios.duckdb") as conexion:
    conexion.execute("""
        CREATE OR REPLACE TABLE usuarios AS 
        SELECT id, name, email 
        FROM read_json_auto('https://jsonplaceholder.typicode.com/users')
    """)

    conexion.sql("""
        SELECT id, name, email 
        FROM usuarios 
        ORDER BY id 
        LIMIT 5
    """).show()