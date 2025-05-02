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
        title = st.text_input("Book Title:")
        author = st.text_input("Book Author:")
        st.write("Rating:")
        rating = st.feedback('stars')
        reread = st.radio("Would you reread it?", ["Yes", "No", "Maybe"])
        notes = st.text_area("Notes")

        submit = st.button("Add Book")

    if submit:
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

    search_query = st.text_input("Search books by title:")

    # Filter DataFrame if search query exists
    if search_query:
        filtered_books = df_books[
            df_books["Title"].str.contains(search_query, case=False, na=False)
        ]
        st.subheader(f"🔍 Search results for '{search_query}':")
        st.dataframe(filtered_books, use_container_width=True)
    else:
        # Display user's book list
        if not df_books.empty:
            st.subheader(f"My Books")

            st.dataframe(df_books, use_container_width=True)
        else:
            st.info(f"No books added yet for {user_email}")

else:
    st.warning("Please enter your email address to create or access your book tracker.")
