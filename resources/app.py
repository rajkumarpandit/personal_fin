import streamlit as st
from home_page import home_page
from add_transaction_page import add_transaction_page
from display_transactions_page import display_transactions_page
from delete_transactions_page import delete_transactions_page  # Import the new page


# Main function to handle the app layout and navigation
def main():
    # Set the browser title
    st.set_page_config(page_title="Personal Finance", layout="wide")

    # Initialize all session state variables
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    if "pagination_page" not in st.session_state:
        st.session_state.pagination_page = 1
    if "transaction_desc" not in st.session_state:
        st.session_state.transaction_desc = ""
    if "parsed_data" not in st.session_state:
        st.session_state.parsed_data = None
    if "save_enabled" not in st.session_state:
        st.session_state.save_enabled = False

    # Sidebar menu with styled buttons
    st.sidebar.title("Menu")
    st.sidebar.markdown(
        """
        <style>
            .sidebar-button {
                width: 100%;
                padding: 10px;
                margin: 5px 0;
                text-align: center;
                font-size: 16px;
                border-radius: 5px;
                border: 1px solid #ccc;
                background-color: #f0f2f6;
                color: #333;
                transition: background-color 0.3s, color 0.3s;
            }
            .sidebar-button:hover {
                background-color: #4CAF50;
                color: white;
                border: 1px solid #4CAF50;
            }
            .footer {
                font-size: 12px;
                text-align: center;
                margin-top: 20px;
                color: #777;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Add buttons to the sidebar
    if st.sidebar.button("🏠 Home", key="home_button"):
        st.session_state.current_page = "home"
    if st.sidebar.button("➕ Add Transaction", key="add_transaction_button"):
        st.session_state.current_page = "add_transaction"
    if st.sidebar.button("📄 Display Transactions", key="display_transactions_button"):
        st.session_state.current_page = "display_transactions"
    if st.sidebar.button("🗑️ Delete Transactions", key="delete_transactions_button"):  # New button
        st.session_state.current_page = "delete_transactions"

    # Add footer message at the bottom of the sidebar
    st.sidebar.markdown(
        '<div class="footer"></br></br></br></br></br></br></br></br></br></br></br></br></br></br></br></br></br>'
        'All rights reserved @rajkumarpandit</div>',
        unsafe_allow_html=True,
    )

    # Display the selected page based on session state
    if st.session_state.current_page == "home":
        home_page()
    elif st.session_state.current_page == "add_transaction":
        add_transaction_page()
    elif st.session_state.current_page == "display_transactions":
        display_transactions_page()
    elif st.session_state.current_page == "delete_transactions":
        delete_transactions_page()


# Run the app
if __name__ == "__main__":
    main()
