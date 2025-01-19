import streamlit as st
from datetime import datetime
import sqlite3
import bcrypt

db_file_name = st.secrets["api_keys"]["DATABASE_FILE_NAME"]
db_txn_table_name = st.secrets["api_keys"]["DB_TRANSACTION_TABLE_NAME"]
db_users_table_name = st.secrets["api_keys"]["DB_USER_TABLE_NAME"]


def hash_password(password: str) -> bytes:
    """Hash a password for storing."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def verify_password(stored_password: bytes, provided_password: str) -> bool:
    """Verify a stored hashed password against one provided by user."""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)


def reset_session_state():
    """Reset session state variables related to sign up and sign in forms."""
    keys_to_reset = ['user_name', 'user_email', 'password', 'signup_user_name', 'signup_user_email', 'signup_password',
                     'signin_user_email', 'signin_password']
    for key in keys_to_reset:
        st.session_state.pop(key, None)
    st.session_state.logged_in = False
    st.session_state.current_page = "auth"


def signup():
    st.title("Sign Up")

    # Create a left-aligned container for the form
    with st.container():
        col1, col2 = st.columns([2, 2])
        with col1:
            with st.form(key='signup_form'):
                user_name = st.text_input("Name", key="signup_user_name")
                user_email = st.text_input("Email ID", key="signup_user_email")
                password = st.text_input("Password", type="password", key="signup_password")
                submit_button = st.form_submit_button(label='Sign Up')

                if submit_button:
                    if user_name and user_email and password:
                        conn = sqlite3.connect(db_file_name)
                        c = conn.cursor()
                        hashed = hash_password(password)

                        try:
                            c.execute(f'''INSERT INTO {db_users_table_name} (user_name, user_email, user_encrypted_password, created_by, created_at) 
                                         VALUES (?, ?, ?, ?, ?)''',
                                      (user_name, user_email, hashed, 'SYSTEM', datetime.now().strftime("%Y-%m-%d")))
                            conn.commit()
                            st.success("Account created successfully!")
                            st.session_state.current_page = "signin"  # Redirect to sign-in page
                            st.rerun()  # Rerun to reflect the changes
                        except sqlite3.IntegrityError:
                            st.error("Email already exists. Sign-in or use a different email.")
                        finally:
                            conn.close()
                    else:
                        st.error("Fill in all required fields.")


def signin():
    st.title("Sign In")

    # Create a left container for the form
    with st.container():
        col1, col2 = st.columns([2, 2])
        with col1:
            with st.form(key='signin_form'):
                user_email = st.text_input("Email ID", key="signin_user_email")
                password = st.text_input("Password", type="password", key="signin_password")

                submit_button = st.form_submit_button(label='Sign In')
                if submit_button:
                    if user_email and password:
                        conn = sqlite3.connect(db_file_name)
                        c = conn.cursor()
                        c.execute(
                            f"SELECT user_name, user_encrypted_password FROM {db_users_table_name} WHERE user_email = ?",
                            (user_email,))
                        result = c.fetchone()
                        conn.close()

                        if result:
                            user_name, stored_password = result
                            if verify_password(stored_password, password):
                                st.session_state.logged_in = True
                                st.session_state.user_email = user_email
                                st.session_state.user_name = user_name
                                st.success("Logged in successfully!")
                                st.session_state.current_page = "home"  # Redirect to home page
                                st.rerun()  # Rerun to reflect the changes
                            else:
                                st.error("Incorrect user ID and/or password. Contact administrator.")
                        else:
                            st.error("User not found. Sign up.")
                    else:
                        st.error("Enter all required fields.")


def check_login():
    """Check if the user is logged in."""
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.error("Sign-in to continue.")
        st.stop()


def auth_page():
    """This function will be called from app.py to handle authentication pages."""
    if not st.session_state.logged_in:
        # Display the appropriate form based on the current page
        if st.session_state.current_page == "signup":
            signup()
        else:
            signin()