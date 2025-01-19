import streamlit as st
from datetime import datetime
from transaction_parser import parse_transaction  # Import the parse_transaction function
from db_operations import insert_record  # Import the insert_record function


def add_transaction_page(global_user_email):
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
    st.title("Add Transaction")

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
    st.subheader("Enter Transaction Description in Simple English", divider='gray')

    transaction_input = st.text_input(
        "",
        value=st.session_state.transaction_desc,  # Dynamically set value from session state
        key="transaction_input",
        label_visibility="collapsed",  # Hide label
    )
    st.markdown(
        '<p class="example-text"><small>Example: Today, I ate at the A2B restaurant and paid the bill of Rs 500 using '
        'my Citi savings account.</small></p>',
        unsafe_allow_html=True)

    # Buttons: Parse Transaction and Reset with equal size
    col1, col2 = st.columns(2, gap="small")
    with col1:
        parse_clicked = st.button("Parse This Text", use_container_width=True)
    with col2:
        reset_clicked = st.button("Reset", use_container_width=True)

    # Handle reset button click
    if reset_clicked:
        reset()
        message_placeholder.info("Reset completed.")

    # Handle Parse Transaction button click
    if parse_clicked:
        if not transaction_input.strip():
            message_placeholder.warning("Enter a transaction description to parse.")
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
                parsed_data_with_email = {**st.session_state.parsed_data, 'user_email': global_user_email}
                parsed_data_with_audit = {**parsed_data_with_email, 'created_date': datetime.now().strftime("%Y-%m-%d")}
                save_msg = insert_record(parsed_data_with_audit)  # Save parsed data to the database
                message_placeholder.success(save_msg)
                st.session_state.save_enabled = False  # Disable Save button after saving

            except Exception as e:
                message_placeholder.error(f"Failed to save data: {str(e)}")

        # Handle Cancel button click
        if cancel_clicked:
            reset()
            message_placeholder.info("All data cleared. Ready for a new transaction.")
