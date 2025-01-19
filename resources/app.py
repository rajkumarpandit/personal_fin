import streamlit as st
from auth import auth_page, check_login, signup, signin, reset_session_state
from home_page import home_page
from add_transaction_page import add_transaction_page
from display_transactions_page import display_transactions_page
from delete_transactions_page import delete_transactions_page
from user_utils import display_user_info


# Function to display the sidebar menu
def display_sidebar_menu():
    st.sidebar.title("Menu")
    if st.session_state.logged_in:
        # Display menu items for logged-in users
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
            .logout-button {
                background-color: #f44336; /* Red */
                border: none;
                color: white;
                padding: 5px 10px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 14px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 5px;
            }
            .logout-button:hover {
                background-color: #da190b;
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

        if st.sidebar.button("🏠 Home", key="home_button"):
            st.session_state.current_page = "home"
        if st.sidebar.button("➕ Add Transaction", key="add_transaction_button"):
            st.session_state.current_page = "add_transaction"
        if st.sidebar.button("📄 Display Transactions", key="display_transactions_button"):
            st.session_state.current_page = "display_transactions"
        if st.sidebar.button("🗑️ Delete Transactions", key="delete_transactions_button"):
            st.session_state.current_page = "delete_transactions"
        if st.sidebar.button("Logout", key="logout_button"):
            reset_session_state()  # Reset session state
            st.session_state.current_page = "auth"  # Redirect to auth page
            st.rerun()  # Rerun the app to reflect changes
    else:
        # Display SignIn and SignUp options at the top of the sidebar
        menu = ["Sign In", "Sign Up"]
        choice = st.sidebar.radio("", menu, key="auth_choice")
        st.session_state.current_page = choice.lower().replace(" ", "")  # Set current page based on choice

    # Add footer message at the bottom of the sidebar
    st.sidebar.markdown(
        '<div class="footer"></br></br></br></br></br></br></br></br></br></br></br></br></br>'
        '<small>All rights reserved @rajkumarpandit</small></div>',
        unsafe_allow_html=True,
    )


# Main function to handle the app layout and navigation
def main():
    # Set the browser title
    st.set_page_config(page_title="Personal Finance", layout="wide")

    # Initialize all session state variables
    if "current_page" not in st.session_state:
        st.session_state.current_page = "auth"  # Start with the auth page
    if "pagination_page" not in st.session_state:
        st.session_state.pagination_page = 1
    if "transaction_desc" not in st.session_state:
        st.session_state.transaction_desc = ""
    if "parsed_data" not in st.session_state:
        st.session_state.parsed_data = None
    if "save_enabled" not in st.session_state:
        st.session_state.save_enabled = False
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    if "user_name" not in st.session_state:
        st.session_state.user_name = None

    # Handle authentication and redirects
    if not st.session_state.logged_in:
        st.session_state.current_page = "auth"  # Force auth page if not logged in

    # Display user name in top right corner if logged in
    display_user_info()

    # Display the sidebar menu
    display_sidebar_menu()

    # Display the selected page based on session state
    if st.session_state.current_page == "auth":
        auth_page()  # Call auth_page to handle authentication
    elif st.session_state.current_page == "signup":
        signup()
    elif st.session_state.current_page == "signin":
        signin()
    elif st.session_state.current_page == "home":
        check_login()
        home_page()
    elif st.session_state.current_page == "add_transaction":
        check_login()
        add_transaction_page(st.session_state.user_email)
    elif st.session_state.current_page == "display_transactions":
        check_login()
        display_transactions_page(st.session_state.user_email)
    elif st.session_state.current_page == "delete_transactions":
        check_login()
        delete_transactions_page(st.session_state.user_email)


# Run the app
if __name__ == "__main__":
    main()
