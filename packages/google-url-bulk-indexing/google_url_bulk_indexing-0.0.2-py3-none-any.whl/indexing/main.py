from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
import requests
import pandas as pd

def authorize_credentials(api_path):
    try:
        creds = service_account.Credentials.from_service_account_file(api_path, scopes=["https://www.googleapis.com/auth/indexing"])
        creds.refresh(Request())
    except RefreshError:
        creds = None
    return creds

def submit_url(credentials, site_url, request_type):
    if not credentials:
        print("Failed to authenticate. Check your credentials.")
        return None

    endpoint = "https://indexing.googleapis.com/v3/urlNotifications:publish"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {credentials.token}"
    }
    data = {
        "url": site_url,
        "type": request_type
    }
    response = requests.post(endpoint, json=data, headers=headers)
    return response.status_code

def read_urls_from_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        urls = df.iloc[:, 0].tolist()
        return urls
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []

def main():
    API_Path = " user json api link "
    excel_file_path = " excel url "
    creds = authorize_credentials(API_Path)
    requestType = "URL_UPDATED"  # Choose between "URL_UPDATED" or "URL_DELETED"
    urls_to_submit = read_urls_from_excel(excel_file_path)
    for url in urls_to_submit:
        response_code = submit_url(creds, url, requestType)
        if response_code == 200:
            print(f"Successfully submitted: {url}")
        else:
            print(f"Error submitting {url}. Error Code: {response_code}")

if __name__ == "__main__":
    main()
