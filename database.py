import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    
    conn_str = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    return create_engine(conn_str)

def testar_conexao():
    engine = get_connection()
    query = "SELECT version();" 
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
            return f"Conectado com sucesso! Versão do banco: {df.iloc[0,0]}"
    except Exception as e:
        return f"Erro ao conectar na AWS: {e}"