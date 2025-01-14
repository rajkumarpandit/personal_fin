import streamlit as st
import os
import pandas as pd
from transaction_parser import parse_transaction  # Import the parse_transaction function
from db_operations import insert_record, fetch_all_records  # Import database functions

# Image file path
image_path = os.path.join(os.path.dirname(__file__), "./images/finance_image.jpg")


# Function for the Home page
def home_page():
    st.title("Personal Finance App")
    if os.path.exists(image_path):
        st.image(image_path, caption="Manage your finances efficiently!", width=400)  # Fixed width
    else:
        st.error(f"Image file not found! {image_path}")


# Function for the Add Transaction page
def add_transaction_page():
    # Initialize session state for input, output, and save button state
    if "transaction_desc" not in st.session_state:
        st.session_state.transaction_desc = ""
    if "parsed_data" not in st.session_state:
        st.session_state.parsed_data = None
    if "save_enabled" not in st.session_state:
        st.session_state.save_enabled = False  # Disable Save button initially

    # Function to handle reset
    def reset():
        st.session_state.transaction_desc = ""  # Clear input text box
        st.session_state.parsed_data = None  # Clear parsed data
        st.session_state.save_enabled = False  # Disable Save button
        st.rerun()  # Force a rerun to refresh the UI

    # Title of the app
    st.title("Transaction Details Parser")

    # Custom CSS for styling
    st.markdown(
        """
        <style>
        .input-box {
            border: 1px solid #ddd;
            padding: 8px;
            border-radius: 4px;
            width: 100%;
        }
        .example-text {
            color: #999999;
            font-size: 0.9em;
        }
        .button {
            display: inline-block;
            width: 100%;
            padding: 8px;
            text-align: center;
            border-radius: 4px;
        }
        .disabled-button {
            pointer-events: none;
            opacity: 0.5;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Placeholder for success/information messages at the top
    message_placeholder = st.empty()

    # Text input for the transaction description
    st.subheader("Enter Transaction Description in Simple English:", divider='gray')
    st.markdown(
        '<p class="example-text"><small>Example: Today, I ate at the A2B restaurant and paid the bill of Rs 500 using '
        'my Citi savings account.</small></p>',
        unsafe_allow_html=True)
    transaction_input = st.text_input(
        "",
        value=st.session_state.transaction_desc,  # Dynamically set value from session state
        key="transaction_input",
        label_visibility="collapsed",  # Hide label
    )

    # Buttons: Parse Transaction and Reset with equal size
    col1, col2 = st.columns(2, gap="small")
    with col1:
        parse_clicked = st.button("Parse Transaction", use_container_width=True)
    with col2:
        reset_clicked = st.button("Reset", use_container_width=True)

    # Handle reset button click
    if reset_clicked:
        reset()
        message_placeholder.info("Reset completed. Please enter a new transaction.")

    # Handle Parse Transaction button click
    if parse_clicked:
        if not transaction_input.strip():
            message_placeholder.warning("Please enter a transaction description before parsing.")
            st.session_state.parsed_data = None
        else:
            try:
                # Parse the input using parse_transaction
                st.session_state.parsed_data = parse_transaction(transaction_input)
                st.session_state.transaction_desc = transaction_input  # Save the input
                st.session_state.save_enabled = True  # Enable Save button
                # message_placeholder.success("Transaction parsed successfully!")
            except Exception as e:
                message_placeholder.error(f"Error: {str(e)}")
                st.warning("Ensure the LLM API key and environment variables are correctly set up.")
                st.session_state.parsed_data = None

    # Display the output if parsed data exists
    if st.session_state.parsed_data:
        st.subheader("Parsed Transaction Details")

        # Prepare the data for a 4-column table
        table_data = list(st.session_state.parsed_data.items())
        rows = []
        for i in range(0, len(table_data), 2):
            row = [
                table_data[i][0],  # Label for column 1
                table_data[i][1],  # Value for column 2
                table_data[i + 1][0] if i + 1 < len(table_data) else "",  # Label for column 3
                table_data[i + 1][1] if i + 1 < len(table_data) else "",  # Value for column 4
            ]
            rows.append(row)

        # Display the table without headers
        st.write(
            f"""
            <style>
                .no-header-table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                .no-header-table td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                }}
            </style>
            <table class="no-header-table">
                {"".join(
                f"<tr><td><b>{row[0]}</b></td><td>{row[1]}</td><td><b>{row[2]}</b></td><td>{row[3]}</td></tr>"
                for row in rows
            )}
            </table>
            """,
            unsafe_allow_html=True,
        )

        # Add Save and Cancel buttons below the table
        col1, col2 = st.columns(2, gap="small")
        with col1:
            # Add "disabled-button" class if Save is disabled
            save_classes = "button" + (" disabled-button" if not st.session_state.save_enabled else "")
            save_clicked = st.button("Save", use_container_width=True, key="save_button",
                                     disabled=not st.session_state.save_enabled)
        with col2:
            cancel_clicked = st.button("Cancel", use_container_width=True)

        # Handle Save button click
        if save_clicked:
            try:
                save_msg = insert_record(st.session_state.parsed_data)  # Save parsed data to the database
                message_placeholder.success(save_msg)
                st.session_state.save_enabled = False  # Disable Save button after saving

            except Exception as e:
                message_placeholder.error(f"Failed to save data: {str(e)}")

        # Handle Cancel button click
        if cancel_clicked:
            reset()
            message_placeholder.info("All data cleared. Ready for a new transaction.")


# Function for the Display Transactions page
def display_transactions_page():
    st.title("All Transactions")
    records = fetch_all_records()  # Fetch all records from the database

    if records:
        # Convert records to a DataFrame
        df = pd.DataFrame(records)
        df = df.fillna("")
        df = df.reset_index(drop=True)
        df.columns = ["Transaction Date", "Bank Name", "Account Type", "Amount", "Currency", "Category", "Short Desc."]

        # Ensure all columns are of type string to avoid slicing issues
        df = df.astype(str)

        # Pagination
        page_size = 10  # Number of rows per page
        total_pages = (len(df) // page_size) + (1 if len(df) % page_size != 0 else 0)

        # Initialize session state for pagination
        if "pagination_page" not in st.session_state:
            st.session_state.pagination_page = 1  # Start at page 1

        # Display the current page of the DataFrame
        start_idx = (st.session_state.pagination_page - 1) * page_size
        end_idx = start_idx + page_size
        st.dataframe(df.iloc[start_idx:end_idx], hide_index=True)

        # Pagination controls at the bottom right
        col1, col2, col3 = st.columns([3, 1, 1])
        with col2:
            if st.button("Previous") and st.session_state.pagination_page > 1:
                st.session_state.pagination_page -= 1  # Decrease page number
        with col3:
            if st.button("Next") and st.session_state.pagination_page < total_pages:
                st.session_state.pagination_page += 1  # Increase page number

        # Display current page and total pages
        st.caption(f"Page {st.session_state.pagination_page} of {total_pages}")
    else:
        st.info("No transactions found in the database.")


# Main function to handle the app layout and navigation
def main():
    # Set the browser title
    st.set_page_config(page_title="Personal Finance")

    # Initialize session state for the current page
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"

    # Sidebar menu with buttons of the same size
    st.sidebar.title("Menu")
    st.sidebar.markdown(
        """
        <style>
            .sidebar-button {
                width: 100%;
                margin: 5px 0;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if st.sidebar.button("Home", key="home_button"):
        st.session_state.current_page = "home"
    if st.sidebar.button("Add Transaction", key="add_transaction_button"):
        st.session_state.current_page = "add_transaction"
    if st.sidebar.button("Display Transactions", key="display_transactions_button"):
        st.session_state.current_page = "display_transactions"

    # Display the selected page based on session state
    if st.session_state.current_page == "home":
        home_page()
    elif st.session_state.current_page == "add_transaction":
        add_transaction_page()
    elif st.session_state.current_page == "display_transactions":
        display_transactions_page()


# Run the app
if __name__ == "__main__":
    main()