import streamlit as st
import pandas as pd
from db_operations import (
    fetch_all_records,
    fetch_todays_transactions,
    fetch_yesterdays_transactions,
    fetch_last_week_transactions,
    fetch_this_month_transactions,
    fetch_last_month_transactions,
)

def display_transactions_page():
    st.title("All Transactions")

    # Define the filter options
    filter_options = [
        "All Transactions",
        "Today's Transactions",
        "Yesterday's Transactions",
        "Last Week's Transactions",
        "This Month's Transactions",
        "Last Month's Transactions",
    ]

    # Use st.radio with a single group and custom CSS for horizontal layout
    st.markdown(
        """
        <style>
            .horizontal-radio {
                display: flex;
                flex-direction: row;
                gap: 10px;
                flex-wrap: wrap;
            }
            .horizontal-radio > div {
                flex: 1 1 30%;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Use st.radio with a single group
    filter_option = st.radio(
        "Filter Transactions:",
        options=filter_options,
        index=0,  # Default to "All Transactions"
        key="filter_option",  # Unique key for the radio group
        horizontal=True,  # Streamlit's built-in horizontal layout
    )

    # Fetch records based on the selected filter
    if filter_option == "All Transactions":
        records = fetch_all_records()
    elif filter_option == "Today's Transactions":
        records = fetch_todays_transactions()
    elif filter_option == "Yesterday's Transactions":
        records = fetch_yesterdays_transactions()
    elif filter_option == "Last Week's Transactions":
        records = fetch_last_week_transactions()
    elif filter_option == "This Month's Transactions":
        records = fetch_this_month_transactions()
    elif filter_option == "Last Month's Transactions":
        records = fetch_last_month_transactions()

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

        # Make the table wider by using the full container width
        st.dataframe(
            df.iloc[start_idx:end_idx],
            hide_index=True,
            use_container_width=True,  # Expand table to full width
        )

        # Pagination controls at the bottom right
        col1, col2, col3 = st.columns([3, 1, 1])
        with col2:
            if st.button("Previous") and st.session_state.pagination_page > 1:
                st.session_state.pagination_page -= 1  # Decrease page number
        with col3:
            if st.button("Next") and st.session_state.pagination_page < total_pages:
                st.session_state.pagination_page += 1  # Increase page number

        # Display current page, total pages, and total number of records
        st.caption(f"Page {st.session_state.pagination_page} of {total_pages} | Total Records: {len(df)}")
    else:
        st.info("No transactions found for the selected filter.")

