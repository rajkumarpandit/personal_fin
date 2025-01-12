import sqlite3
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
db_file_name = os.getenv("DATABSE_FILE_NAME")
db_txn_table_name = os.getenv("DB_TRANSACTION_TABLE_NAME")


def fetch_transactions(db_path: str) -> pd.DataFrame:
    """
    Fetch all transaction records from the SQLite database and return as a Pandas DataFrame.

    Args:
        db_path (str): Path to the SQLite database file.

    Returns:
        pd.DataFrame: A DataFrame containing all transactions.
    """
    # Connect to the database
    conn = sqlite3.connect(db_path)

    try:
        # Fetch data from the transactions table
        query = f"SELECT * FROM {db_txn_table_name};"
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        raise RuntimeError(f"Error fetching data: {e}")
    finally:
        conn.close()

    return df
