import streamlit as st
import pandas as pd
import time
from db_operations import (
    fetch_all_records,
    fetch_todays_transactions,
    fetch_yesterdays_transactions,
    fetch_last_week_transactions,
    fetch_this_month_transactions,
    fetch_last_month_transactions,
    delete_records,
)


def delete_transactions_page():
    st.title("Delete Transactions")

    # Initialize session state for messages
    if 'message' not in st.session_state:
        st.session_state.message = None

    # Display message at the top if there is one
    if st.session_state.message:
        st.info(st.session_state.message)
        st.session_state.message = None

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
        key="filter_option_delete",  # Unique key for the radio group
        horizontal=True,  # Streamlit's built-in horizontal layout
    )

    # Fetch records based on the selected filter
    if filter_option == "All Transactions":
        records = fetch_all_records(delete_mode=True)
    elif filter_option == "Today's Transactions":
        records = fetch_todays_transactions(delete_mode=True)
    elif filter_option == "Yesterday's Transactions":
        records = fetch_yesterdays_transactions(delete_mode=True)
    elif filter_option == "Last Week's Transactions":
        records = fetch_last_week_transactions(delete_mode=True)
    elif filter_option == "This Month's Transactions":
        records = fetch_this_month_transactions(delete_mode=True)
    elif filter_option == "Last Month's Transactions":
        records = fetch_last_month_transactions(delete_mode=True)

    if records:
        # Convert records to a DataFrame
        df = pd.DataFrame(records)
        df = df.fillna("")
        df = df.reset_index(drop=True)
        df.columns = ["ID", "Transaction Date", "Bank Name", "Account Type", "Amount", "Currency", "Category",
                      "Short Desc."]

        # Adding a 'Select' column for checkboxes
        df['Select'] = [False] * len(df)

        # Pagination setup
        page_size = 10  # Number of rows per page
        total_pages = (len(df) // page_size) + (1 if len(df) % page_size != 0 else 0)

        # Initialize session state for pagination
        if "pagination_page_delete" not in st.session_state:
            st.session_state.pagination_page_delete = 1  # Start at page 1

        # Initialize session state for all selected rows
        if 'all_selected_rows' not in st.session_state:
            st.session_state.all_selected_rows = set()

        # Display the current page of the DataFrame
        start_idx = (st.session_state.pagination_page_delete - 1) * page_size
        end_idx = start_idx + page_size

        # Display the DataFrame with checkboxes
        st.caption(f"Page {st.session_state.pagination_page_delete} of {total_pages}, Total Records: {len(df)}, Showing {page_size} Rows per page")
        edited_df = st.data_editor(
            df.iloc[start_idx:end_idx],
            hide_index=True,
            use_container_width=True,
            column_config={
                "Select": st.column_config.CheckboxColumn(
                    "Select",
                    help="Select to mark for deletion",
                    default=False
                )
            }
        )

        # Collect selected IDs from the current page
        selected_rows = [row['ID'] for idx, row in edited_df.iterrows() if row['Select']]
        st.session_state.all_selected_rows.update(selected_rows)

        # Initialize session state for confirmation
        if 'confirm_delete' not in st.session_state:
            st.session_state.confirm_delete = False
        if 'delete_success' not in st.session_state:
            st.session_state.delete_success = False

        # Layout for buttons (Delete, Previous, Next)
        col_delete, col_empty, col_empty, col_empty, col_empty, col_empty, col_prev, col_next = st.columns(
            [2, 1, 1, 1, 1, 1, 1, 1])

        # Delete Button
        if col_delete.button("Delete"):
            if selected_rows:
                st.session_state.confirm_delete = True
                st.warning("Are you sure you want to delete the selected records?")
            else:
                st.session_state.message = "Please select at least one record to delete."
                st.rerun()

        # Empty column to push 'Previous' and 'Next' to the right
        col_empty.empty()

        # Confirmation dialog
        if st.session_state.confirm_delete:
            col1, col2 = st.columns(2)
            if col1.button("Confirm Delete"):
                # Call the delete_records function
                if delete_records(list(st.session_state.all_selected_rows)):
                    st.session_state.delete_success = True
                    st.session_state.confirm_delete = False
                    st.session_state.message = f"Deleted {len(st.session_state.all_selected_rows)} records successfully!"
                else:
                    st.session_state.message = ("Failed to delete records. Please check your database connection or "
                                                "try again.")
                    st.session_state.confirm_delete = False
                st.rerun()
            if col2.button("Cancel Delete"):
                st.session_state.all_selected_rows = set()  # Reset selected rows
                st.session_state.confirm_delete = False
                st.rerun()

        # Display success message if delete was successful
        if st.session_state.delete_success:
            st.session_state.message = f"Deleted {len(st.session_state.all_selected_rows)} records successfully!"
            st.session_state.delete_success = False
            st.session_state.all_selected_rows = set()  # Reset selected rows
            st.rerun()

        # Pagination controls
        if col_prev.button("Previous") and st.session_state.pagination_page_delete > 1:
            st.session_state.pagination_page_delete -= 1  # Decrease page number
        if col_next.button("Next") and st.session_state.pagination_page_delete < total_pages:
            # Corrected the typo here
            st.session_state.pagination_page_delete += 1  # Increase page number

    else:
        st.session_state.message = "No transactions found for the selected filter."
        st.rerun()


if __name__ == "__main__":
    delete_transactions_page()






#### This part of the program is wokring - but no pagination
####
# import streamlit as st
# import pandas as pd
# import time
# from db_operations import (
#     fetch_all_records,
#     fetch_todays_transactions,
#     fetch_yesterdays_transactions,
#     fetch_last_week_transactions,
#     fetch_this_month_transactions,
#     fetch_last_month_transactions,
#     delete_records,
# )
#
#
# def delete_transactions_page():
#     st.title("Delete Transactions")
#
#     # Initialize session state for messages
#     if 'message' not in st.session_state:
#         st.session_state.message = None
#
#     # Display message at the top if there is one
#     if st.session_state.message:
#         st.info(st.session_state.message)
#         st.session_state.message = None
#
#     # Define the filter options
#     filter_options = [
#         "All Transactions",
#         "Today's Transactions",
#         "Yesterday's Transactions",
#         "Last Week's Transactions",
#         "This Month's Transactions",
#         "Last Month's Transactions",
#     ]
#
#     # Use st.radio to select the filter
#     filter_option = st.radio(
#         "Filter Transactions:",
#         options=filter_options,
#         index=0,  # Default to "All Transactions"
#         key="filter_option_delete",  # Unique key for the radio group
#         horizontal=True,  # Display options horizontally
#     )
#
#     # Fetch records based on the selected filter
#     if filter_option == "All Transactions":
#         records = fetch_all_records(delete_mode=True)
#     elif filter_option == "Today's Transactions":
#         records = fetch_todays_transactions(delete_mode=True)
#     elif filter_option == "Yesterday's Transactions":
#         records = fetch_yesterdays_transactions(delete_mode=True)
#     elif filter_option == "Last Week's Transactions":
#         records = fetch_last_week_transactions(delete_mode=True)
#     elif filter_option == "This Month's Transactions":
#         records = fetch_this_month_transactions(delete_mode=True)
#     elif filter_option == "Last Month's Transactions":
#         records = fetch_last_month_transactions(delete_mode=True)
#
#     if records:
#         # Convert records to a DataFrame
#         df = pd.DataFrame(records)
#         df = df.fillna("")
#         df = df.reset_index(drop=True)
#         df.columns = ["ID", "Transaction Date", "Bank Name", "Account Type", "Amount", "Currency", "Category",
#                       "Short Desc."]
#
#         # Adding a 'Select' column for checkboxes
#         df['Select'] = [False] * len(df)
#
#         # Display the DataFrame with checkboxes
#         # st.write("Select rows to delete:")
#         edited_df = st.data_editor(
#             df,
#             hide_index=True,
#             column_config={
#                 "Select": st.column_config.CheckboxColumn(
#                     "Select",
#                     help="Select to mark for deletion",
#                     default=False
#                 )
#             }
#         )
#
#         # Collect selected IDs
#         selected_rows = [row['ID'] for idx, row in edited_df.iterrows() if row['Select']]
#
#         # Initialize session state for confirmation
#         if 'confirm_delete' not in st.session_state:
#             st.session_state.confirm_delete = False
#         if 'delete_success' not in st.session_state:
#             st.session_state.delete_success = False
#
#         # Delete Button
#         if st.button("Delete"):
#             if selected_rows:
#                 st.session_state.confirm_delete = True
#                 st.warning("Are you sure you want to delete the selected records?")
#             else:
#                 st.session_state.message = "Please select at least one record to delete."
#                 st.rerun()
#
#         # Confirmation dialog
#         if st.session_state.confirm_delete:
#             col1, col2 = st.columns(2)
#             if col1.button("Confirm Delete"):
#                 # Call the delete_records function
#                 if delete_records(selected_rows):
#                     st.session_state.delete_success = True
#                     st.session_state.confirm_delete = False
#                 else:
#                     st.session_state.message = "Failed to delete records. Please check your database connection or try again."
#                     st.session_state.confirm_delete = False
#                     st.rerun()
#             if col2.button("Cancel Delete"):
#                 st.session_state.selected_rows = set()  # Reset selected rows
#                 st.session_state.confirm_delete = False
#                 st.rerun()
#
#         # Display success message if delete was successful
#         if st.session_state.delete_success:
#             st.session_state.message = f"Deleted {len(selected_rows)} records successfully!"
#             st.session_state.delete_success = False
#             st.rerun()
#
#     else:
#         st.session_state.message = "No transactions found in the database."
#         st.rerun()
#
#
# if __name__ == "__main__":
#     delete_transactions_page()
#
