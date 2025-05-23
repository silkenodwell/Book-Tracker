import streamlit as st
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe, get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import time
from datetime import date, timedelta

MIN_DATE = '2000-01-01'

# --- Authenticate and connect to sheet ---
@st.cache_resource
def connect_to_gsheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    gspread_client = gspread.authorize(creds)
    return gspread_client

def show_success_message_for_short_time(success_message, s=3):
    # Placeholder message to only show success message for short time
    msg = st.empty()
    msg.success(success_message)
    time.sleep(2)
    msg.empty()

st.title("📚 Book Tracker")
user_email = st.text_input("Email Address:")

if user_email:
    sheet_name = f"book_tracker_{user_email.lower()}"

    gspread_client = connect_to_gsheets()

    # Try to open the sheet, or create it if it doesn't exist
    try:
        sh = gspread_client.open(sheet_name)
    except gspread.SpreadsheetNotFound:
        sh = gspread_client.create(sheet_name)
        # Share with your email or keep private for service account
        st.success(f'Google Spreadsheet "{sheet_name}" was created and shared with {user_email}')
        sh.share(user_email, perm_type='user', role='writer')
        # Create default worksheet
        worksheet = sh.get_worksheet(0)
        worksheet.update([["Title", "Author", "Rating /5", "Reread?", "Notes", "Date Read"]])

    worksheet = sh.get_worksheet(0)
    df_books = get_as_dataframe(worksheet).dropna(how="all")


    # Book input
    with st.expander("📘 Add a New Book"):
        with st.form("new_book_submit_form"):
            title = st.text_input("Book Title:")
            author = st.text_input("Book Author:")
            date_read = st.date_input(
                "Date Read", value="today", min_value=MIN_DATE, max_value="today", key="date_read"
            )
            st.write("Rating:")
            rating = st.feedback('stars')
            reread = st.radio("Would you reread it?", ["Yes", "No", "Maybe"])
            notes = st.text_area("Notes")

            new_book_submitted = st.form_submit_button("Add Book")

    if new_book_submitted:
        if not title:
            st.error("Enter a book title before submitting")
        else:
            new_entry = pd.DataFrame([{
                "Title": title,
                "Author": author,
                "Rating /5": rating + 1 if rating is not None else None,
                "Reread?": reread,
                "Notes": notes,
                "Date Read": date_read,
            }])
            df_books = pd.concat([df_books, new_entry], ignore_index=True)
            set_with_dataframe(worksheet, df_books)

            show_success_message_for_short_time(f"Added '{title}' to the book list for {user_email}.")

    heading_col, filter_col = st.columns([0.4, 0.6])
    with heading_col:
        st.subheader('My Books')
    with filter_col:
        with st.expander("Filter Books"):
            with st.form("filter_form"):

                col1, col2 = st.columns(2)
                with col1:
                    search_field = st.selectbox("Search in", ["Title", "Author", "Title or Author"])
                    min_rating = st.slider("Minimum rating", 1, 5, 1)
                with col2:
                    search_query = st.text_input("Keyword")
                    reread_filter = st.selectbox("Reread filter", ["All", "Yes", "No", "Maybe"])

                end_date = date.today()
                start_date = end_date - timedelta(days=364) # date range inclusive of start and end dates
                # Date range input
                date_range = st.date_input(
                    "Date Range",
                    (start_date, end_date)
                )
                filters_submitted = st.form_submit_button("Apply Filters")

    if filters_submitted:
        # Apply filters only after user submits
        filtered_books = df_books.copy()

        # Keyword
        if search_query:
            if search_field == "Title":
                filtered_books = filtered_books[
                    filtered_books["Title"].str.contains(search_query, case=False, na=False)]
            elif search_field == "Author":
                filtered_books = filtered_books[
                    filtered_books["Author"].str.contains(search_query, case=False, na=False)]
            else:
                mask = (
                        filtered_books["Title"].str.contains(search_query, case=False, na=False) |
                        filtered_books["Author"].str.contains(search_query, case=False, na=False)
                )
                filtered_books = filtered_books[mask]

        # Rating
        filtered_books = filtered_books[
            (filtered_books["Rating /5"] >= min_rating) | filtered_books['Rating /5'].isna()
        ]

        # Reread
        if reread_filter != "All":
            filtered_books = filtered_books[filtered_books["Reread?"] == reread_filter]

        # Date Range
        filtered_books = filtered_books[
            (pd.Timestamp(date_range[0]) <= pd.to_datetime(filtered_books['Date Read']))
            &
            (pd.to_datetime(filtered_books['Date Read']) <= pd.Timestamp(date_range[1]))
        ]

        st.text('Filtered results')
        st.dataframe(filtered_books)

    else:
        # Display user's book list
        if not df_books.empty:
            st.dataframe(df_books, use_container_width=True)
        else:
            st.info(f"No books added yet for {user_email}")

else:
    st.warning("Please enter your email address to create or access your book tracker.")
