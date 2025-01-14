import sqlite3
# from dotenv import load_dotenv
import os
import streamlit as st

# load_dotenv()
# db_file_name = os.getenv("DATABSE_FILE_NAME")
# db_txn_table_name = os.getenv("DB_TRANSACTION_TABLE_NAME")
db_file_name = st.secrets["api_keys"]["DATABSE_FILE_NAME"]
db_txn_table_name = st.secrets["api_keys"]["DB_TRANSACTION_TABLE_NAME"]


def create_table():
    """
    Creates the transactions table if it doesn't already exist.
    """
    conn = sqlite3.connect(db_file_name)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {db_txn_table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_date TEXT,
            bank_name TEXT,
            account_type TEXT,
            transaction_amount REAL,
            transaction_currency TEXT,
            transaction_category TEXT,
            transaction_desc TEXT
        )
    """)
    conn.commit()
    conn.close()


def insert_record(record):
    """
    Inserts a record into the transactions table if it does not already exist.
    """
    conn = sqlite3.connect(db_file_name)
    cursor = conn.cursor()

    # Check if the record already exists
    cursor.execute(f"""
        SELECT * FROM {db_txn_table_name}
        WHERE transaction_date = ? AND coalesce(bank_name,'X') = coalesce(?,'X') 
        AND coalesce(account_type,'X') = coalesce(?,'X') 
        AND transaction_amount = ? 
        AND coalesce(transaction_currency,'X') = coalesce(?,'X') 
        AND coalesce(transaction_category,'X') = coalesce(?,'X') 
        AND upper(coalesce(transaction_desc,'X')) = Upper(coalesce(?,'X')) 
    """, (
        record["Transaction Date"],
        record["Bank Name"],
        record["Account Type"],
        record["Transaction Amount"],
        record["Transaction Currency"],
        record["Transaction Category"],
        record["Transaction Description"]
    ))

    existing_record = cursor.fetchone()

    # Insert the record only if it doesn't exist
    if not existing_record:
        cursor.execute(f"""
            INSERT INTO {db_txn_table_name} (
                transaction_date, bank_name, account_type,
                transaction_amount, transaction_currency,
                transaction_category, transaction_desc
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            record["Transaction Date"],
            record["Bank Name"],
            record["Account Type"],
            record["Transaction Amount"],
            record["Transaction Currency"],
            record["Transaction Category"],
            record["Transaction Description"]
        ))
        conn.commit()
        print("Committed")
        return "Transaction details saved successfully!"
    else:
        print("Not inserted. Duplicate record.")
        return "Transaction details could NOT be saved!. Duplicate record."
    conn.close()


def get_all_table_name():
    conn = sqlite3.connect(db_file_name)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    result = cursor.fetchall()
    all_tables = [result[i][0] for i in range(len(result))]
    return all_tables
    conn.close()


def fetch_all_records():
    conn = sqlite3.connect(db_file_name)
    cursor = conn.cursor()
    cursor.execute(f"""select transaction_date, bank_name,account_type,transaction_amount,transaction_currency,transaction_category, transaction_desc
        from  {db_txn_table_name}
        order by transaction_date desc
    """)
    records = cursor.fetchall()
    conn.close()
    return records
