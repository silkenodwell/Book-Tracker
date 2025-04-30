import streamlit as st
import pandas as pd

# Initialize session state on first run
if "books" not in st.session_state:
    st.session_state.books = []

# --- Input Section ---
st.title("📚 Book Tracker")

title = st.text_input("Book Title:")
reread = st.radio("Would you reread it?", ["Yes", "No", "Maybe"])
submit = st.button("Add Book")

# --- Add Book ---
if submit and title:
    st.session_state.books.append({
        "Title": title,
        "Reread?": reread
    })
    st.success(f"Added '{title}'")

# --- Display Book List ---
if st.session_state.books:
    df = pd.DataFrame(st.session_state.books)
    st.subheader("📖 Your Books")
    st.dataframe(df, use_container_width=True)
else:
    st.info("No books added yet.")
