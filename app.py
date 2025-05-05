import streamlit as st
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe, get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import os

# --- Authenticate and connect to sheet ---
@st.cache_resource
def connect_to_gsheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    gspread_client = gspread.authorize(creds)
    return gspread_client

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
        worksheet.update([["Title", "Author", "Rating /5", "Reread?", "Notes"]])

    worksheet = sh.get_worksheet(0)
    df_books = get_as_dataframe(worksheet).dropna(how="all")


    # Book input
    with st.expander("📘 Add a New Book"):
        with st.form("new_book_submit_form"):
            title = st.text_input("Book Title:")
            author = st.text_input("Book Author:")
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
            }])
            df_books = pd.concat([df_books, new_entry], ignore_index=True)
            set_with_dataframe(worksheet, df_books)
            
            st.success(f"Added '{title}' to the book list for {user_email}.")

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
        st.text(min_rating)
        filtered_books = filtered_books[
            (filtered_books["Rating /5"] >= min_rating) | filtered_books['Rating /5'].isna()
        ]

        # Reread
        if reread_filter != "All":
            filtered_books = filtered_books[filtered_books["Reread?"] == reread_filter]

        st.dataframe(filtered_books)

    else:
        # Display user's book list
        if not df_books.empty:
            st.dataframe(df_books, use_container_width=True)
        else:
            st.info(f"No books added yet for {user_email}")

else:
    st.warning("Please enter your email address to create or access your book tracker.")
