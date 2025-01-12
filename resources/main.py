import json
from db_operations import create_table, insert_record
from transaction_parser import parse_transaction
from dotenv import load_dotenv
import os
load_dotenv()
db_file_name=os.getenv("DATABSE_FILE_NAME")
db_txn_table_name=os.getenv("DB_TRANSACTION_TABLE_NAME")

# Example transaction descriptions
if __name__ == '__main__':
    # Create the table if it doesn't exist
    create_table()

    # test_sentences = [
    #     # "on 2024-02-28, I spent Rs 576 at the A2B restaurant and paid using my Citi savings account.",
    #     # "I paid Rs 1660 to Big Market for RICE & pulses today using my HDFC credit card.",
    #     # "Rs 8500 was spent on petrol yesterday using my SBI debit card.",
    #     # "Last month, I transferred Rs 2000 for Booking flight to Miami using my Axis bank account.",
    #     # "Spent Rs 800 on Diesel today."
    #     "Today, I spent Rs 5700 at the A2B restaurant and paid using my Citi savings account."
    # ]
    input_text=input("Enter your transaction sentence in English sentence:")
    if len(input_text):
        test_sentences=[input_text]

        # Process each transaction description
        for test_sentence in test_sentences:
            print(f"Processing: {test_sentence}")
            try:
                transaction_data = parse_transaction(test_sentence)
                print(json.dumps(transaction_data, indent=4))
                insert_record(transaction_data)
            except Exception as e:
                print(f"Error: {e}")

        # db_path = db_file_name
        from utils import fetch_transactions
        try:
            transactions_df = fetch_transactions(db_file_name)
            print(transactions_df)
        except RuntimeError as e:
            print(f"Error: {e}")
