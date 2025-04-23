import psycopg2

def connect():
    try:
        conn = psycopg2.connect(
            dbname='taous.oumaouche',  # Nom de la base
            host='localhost',          # Serveur local
            port='5432',               # Port PostgreSQL
            user='postgres',           # Ton utilisateur PostgreSQL
            password='jedi'            # Ton mot de passe
        )
        conn.autocommit = True
        print("Connexion réussie à la base de données.")
        return conn
    except Exception as e:
        print(f"Erreur lors de la connexion : {e}")
        return None
