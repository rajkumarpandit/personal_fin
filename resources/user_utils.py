import streamlit as st

def display_user_info():
    """Display user information if logged in."""
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        user_name = st.session_state.get('user_name', 'User')
        capitalized_name = user_name.title()  # Capitalize each word in the user name

        # Use columns to position the user info
        col1, col2 = st.columns([1, 1])
        with col2:
            # Display the user name
            st.markdown(f"""
            <div style="text-align: right;">
                <p>Welcome, {capitalized_name}!</p>
            </div>
            """, unsafe_allow_html=True)