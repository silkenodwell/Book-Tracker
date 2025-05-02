import streamlit as st
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe, get_as_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import os

# --- Authenticate and connect to sheet ---
@st.cache_resource
def connect_to_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    client = gspread.authorize(creds)
    return client.open("book_tracker").worksheet("books")

# --- User selection ---
st.title("📚 Book Tracker")
user = st.text_input("Your Name:")

if user:
    sheet = connect_to_gsheet()
    df_books = get_as_dataframe(sheet).dropna(how="all")


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
                "User": user,
            }])
            df_books = pd.concat([df_books, new_entry], ignore_index=True)
            set_with_dataframe(sheet, df_books)
            st.success(f"Added '{title}' to {user}'s list.")

    user_books = df_books[df_books["User"] == user].drop(columns=['User'])
    # --- Search Section ---
    search_query = st.text_input("Search books by title:")

    # Filter DataFrame if search query exists
    if search_query:
        filtered_books = user_books[
            user_books["Title"].str.contains(search_query, case=False, na=False)
        ]
        st.subheader(f"🔍 Search results for '{search_query}':")
        st.dataframe(filtered_books, use_container_width=True)
    else:
        # Display user's book list
        if not df_books.empty:
            st.subheader(f"{user}'s Books")

            st.dataframe(user_books, use_container_width=True)
        else:
            st.info(f"No books added yet for {user}")

else:
    st.warning("Please enter your name to access or create your book list.")
