# Book Tracker App

## Background
I created this app for my grandmother. She wanted to keep track of 
books she had read, and whether she would reread any given book. The book
list would also have to be easily searchable.

## How to run locally
### 1. Set up a Google Service Account
1. Go to the [Google Cloud Console](console.cloud.google.com/apis/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API and Google Drive API
4. Go to Credentials > Create Credentials > Service Account
5. After creating it, go to Keys > Add Key > Create new key > JSON

This downloads a .json file of the service account details and private key.

### 2. Paste it into local .streamlit/secrets.toml file
You will need to create a ``secrets.toml`` file inside a ``.streamlit`` folder, containing
the details of the Google Service Account in the following format:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = """-----BEGIN PRIVATE KEY-----
YOUR
PRIVATE
KEY
-----END PRIVATE KEY-----"""
client_email = "your-service-account@project-id.iam.gserviceaccount.com"
```

To run the app locally, run the following commands in the terminal:
1. (Optional but recommended) Create a virtual environment ``python -m venv venv``; and
activate this environment, ``source venv/bin/activate``.
2. Install the requirements, ``pip install -r requirements.txt``
3. Run ``streamlit run app.py`` to launch the app

## How to deploy & run deployed app
This app is currently deployed at ``https://silkenodwell-book-tracker-app-mibcug.streamlit.app/``.

To deploy at a different location, choose the "Deploy" button on the app, and select 
Streamlit Community Cloud (or a different option if desired). 