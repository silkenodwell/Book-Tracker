import streamlit as st
import pandas as pd
import os

# --- User selection ---
st.title("📚 Book Tracker")
user = st.text_input("Your Name:")

if user:
    DATA_FILE = f"books_{user.lower().replace(' ', '_')}.csv"

    # Load user-specific file
    if os.path.exists(DATA_FILE):
        df_books = pd.read_csv(DATA_FILE)
    else:
        df_books = pd.DataFrame(columns=["Title", "Author", "Rating /5", "Reread?", "Notes"])

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
            df_books.to_csv(DATA_FILE, index=False)
            st.success(f"Added '{title}' to {user}'s list.")

    # --- Search Section ---
    search_query = st.text_input("Search books by title:")

    # Filter DataFrame if search query exists
    if search_query:
        filtered_books = df_books[df_books["Title"].str.contains(search_query, case=False, na=False)]
        st.subheader(f"🔍 Search results for '{search_query}':")
        st.dataframe(filtered_books, use_container_width=True)
    else:
        # Display user's book list
        if not df_books.empty:
            st.subheader(f"{user}'s Books")
            st.dataframe(df_books, use_container_width=True)
            with open(DATA_FILE, "rb") as f:
                st.download_button(
                    label="📥 Download Book List as CSV",
                    data=f,
                    file_name=os.path.basename(DATA_FILE),
                    mime="text/csv"
                )
        else:
            st.info(f"No books added yet for {user}")

else:
    st.warning("Please enter your name to access or create your book list.")
