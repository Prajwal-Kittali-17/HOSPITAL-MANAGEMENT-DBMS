# utils/db_helpers.py
import pandas as pd
from db_config import get_connection

def fetch_all(query, params=None):
    conn = get_connection()
    try:
        df = pd.read_sql(query, conn, params=params)
        return df
    finally:
        conn.close()

def fetch_one(query, params=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchone()
    finally:
        conn.close()

def execute_query(query, params=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()

def call_procedure(proc_name, params=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.callproc(proc_name, params or [])
        results = []
        for rs in cur.stored_results():
            results.append(rs.fetchall())
        conn.commit()
        return results
    finally:
        conn.close()

def call_function(func_name, params=None):
    conn = get_connection()
    try:
        placeholders = ", ".join(["%s"] * len(params))
        query = f"SELECT {func_name}({placeholders})"
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchone()[0]
    finally:
        conn.close()
