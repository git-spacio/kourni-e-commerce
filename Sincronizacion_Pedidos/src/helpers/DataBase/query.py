import mysql.connector

# Conectar a la base de datos


def execute_query(query):
    db_config = {
        "host": "db.spacionatural.cl",
        "port": 3306,
        "user": "spaciona_luis",
        "password": "N4ter1v3r%",
        "database": "spaciona_prestashopv1.7.7.8"
    }

    # Conectar a la base de datos
    conn = mysql.connector.connect(**db_config)
    
    cur = conn.cursor()
    cur.execute(query)

    # Si la consulta es un SELECT, captura y devuelve los resultados
    if query.strip().upper().startswith("SELECT"):
        results = cur.fetchall()
        cur.close()
        conn.close()
        return results
   
    else:
        conn.commit()  # Asegúrate de guardar los cambios si no es un SELECT
        cur.close()
        conn.close()
        return None

