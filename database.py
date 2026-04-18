import streamlit as st
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    user = st.secrets.get("DB_USER") or os.getenv("DB_USER")
    password = st.secrets.get("DB_PASS") or os.getenv("DB_PASS")
    host = st.secrets.get("DB_HOST") or os.getenv("DB_HOST")
    port = st.secrets.get("DB_PORT") or os.getenv("DB_PORT")
    db_name = st.secrets.get("DB_NAME") or os.getenv("DB_NAME")
    if not port:
        raise ValueError("A porta do banco de dados (DB_PORT) não foi configurada!")

    conn_str = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    return create_engine(conn_str)