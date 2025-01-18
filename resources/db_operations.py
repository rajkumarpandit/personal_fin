import sqlite3
from datetime import datetime, date, timedelta
import streamlit as st

db_file_name = st.secrets["api_keys"]["DATABSE_FILE_NAME"]
db_txn_table_name = st.secrets["api_keys"]["DB_TRANSACTION_TABLE_NAME"]
selected_col_names = ("transaction_date, bank_name, account_type, transaction_amount, transaction_currency, "
                      "transaction_category, transaction_desc")

selected_col_names_for_delete = ("id, transaction_date, bank_name, account_type, transaction_amount, "
                                 "transaction_currency, transaction_category, transaction_desc")


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


# Function to fetch all records
def fetch_all_records(delete_mode=False):
    conn = sqlite3.connect(db_file_name)
    cursor = conn.cursor()
    sel = selected_col_names_for_delete if delete_mode else selected_col_names
    cursor.execute(f"""select {sel}
        from  {db_txn_table_name}
        order by transaction_date desc
    """)
    records = cursor.fetchall()
    conn.close()
    return records


# Function to fetch today's transactions
def fetch_todays_transactions(delete_mode=False):
    conn = sqlite3.connect(db_file_name)
    cursor = conn.cursor()
    sel = selected_col_names_for_delete if delete_mode else selected_col_names
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute(f"""SELECT {sel} FROM {db_txn_table_name} 
        WHERE transaction_date = ?
        order by transaction_date desc
    """, (today,))
    records = cursor.fetchall()
    conn.close()
    return records


# Function to fetch yesterday's transactions
def fetch_yesterdays_transactions(delete_mode=False):
    conn = sqlite3.connect(db_file_name)
    cursor = conn.cursor()
    sel = selected_col_names_for_delete if delete_mode else selected_col_names
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    cursor.execute(f"""SELECT {sel} FROM {db_txn_table_name} 
        WHERE transaction_date = ?
        order by transaction_date desc
    """, (yesterday,))
    records = cursor.fetchall()
    conn.close()
    return records


# Function to fetch last week's transactions
def fetch_last_week_transactions(delete_mode=False):
    conn = sqlite3.connect(db_file_name)
    cursor = conn.cursor()
    today = date.today()
    # Calculate the day of the week (Monday=0, Sunday=6)
    today_weekday = today.weekday()
    days_to_subtract = today_weekday
    # if today_weekday != 0:  # If today is Monday or before, subtract 7 days
    days_to_subtract = 7 + today_weekday
    last_monday = today - timedelta(days=days_to_subtract)
    last_week_start = last_monday.strftime("%Y-%m-%d")
    last_week_end = (last_monday + timedelta(days=6)).strftime("%Y-%m-%d")
    sel = selected_col_names_for_delete if delete_mode else selected_col_names
    cursor.execute(f"""SELECT {sel} FROM {db_txn_table_name} 
        WHERE transaction_date >= ? AND transaction_date <= ?
        order by transaction_date desc
    """, (last_week_start, last_week_end,))
    records = cursor.fetchall()
    conn.close()
    return records


# Function to fetch this month's transactions
def fetch_this_month_transactions(delete_mode=False):
    conn = sqlite3.connect(db_file_name)
    cursor = conn.cursor()
    this_month_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    sel = selected_col_names_for_delete if delete_mode else selected_col_names
    cursor.execute(f"""SELECT {sel} FROM {db_txn_table_name} 
        WHERE transaction_date >= ? AND transaction_date <= ?
        order by transaction_date desc
    """, (this_month_start, today,))
    records = cursor.fetchall()
    conn.close()
    return records


# Function to fetch last month's transactions
def fetch_last_month_transactions(delete_mode=False):
    conn = sqlite3.connect(db_file_name)
    cursor = conn.cursor()
    last_month_end = datetime.now().replace(day=1) - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1).strftime("%Y-%m-%d")
    last_month_end = last_month_end.strftime("%Y-%m-%d")
    sel = selected_col_names_for_delete if delete_mode else selected_col_names
    cursor.execute(f"""SELECT {sel} FROM {db_txn_table_name} 
        WHERE transaction_date BETWEEN ? AND ?
        order by transaction_date desc
        """, (last_month_start, last_month_end))
    records = cursor.fetchall()
    conn.close()
    return records


# Function to delete records by their IDs
def delete_records(record_ids):
    """
    Deletes records from the database based on their IDs.
    :param record_ids: List of record IDs to delete.
    """
    conn = sqlite3.connect(db_file_name)
    cursor = conn.cursor()
    # print("Came here-In the delete portion of the DBOperations")
    try:
        # Delete records with the given IDs
        cursor.executemany(f"DELETE FROM {db_txn_table_name} WHERE id = ?", [(row_id,) for row_id in record_ids])
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error deleting records: {e}")
        return False
    finally:
        conn.close()
