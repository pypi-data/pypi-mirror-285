
# Around With Us Projects - Google Bulk Url Indexing

A Python package to submit URLs for Google Indexing using an Excel file. This package allows you to submit up to 200 URLs daily to Google Search Console for indexing, which can significantly benefit your SEO efforts.

## Features

- Authorizes credentials using a service account file.
- Submits URLs for indexing or deletion.
- Reads URLs from an Excel file.
- Allows submission of up to 200 URLs daily.

## Benefits

- **Fast Implementation**: Quickly set up and start submitting URLs.
- **Excel Integration**: Easily manage URLs in an Excel file.
- **Increased Limit**: Submit up to 200 URLs daily to Google Search Console.

## Installation

To install this package, use pip:

```sh
pip install google-bulk-url-indexing
```

## Usage

### Command Line

After installing, you can use the package from the command line.

```sh
google-bulk-url-indexing
```

### As a Module

You can also use it as a module in your Python code.

```python
from indexing.main import authorize_credentials, submit_url, read_urls_from_excel

# Provide the path to the API key file
API_Path = "path/to/your/service_account.json"

# Provide the path to the Excel file
excel_file_path = "path/to/your/urls.xlsx"

# Authorize credentials
creds = authorize_credentials(API_Path)

# Specify the request type
requestType = "URL_UPDATED"  # or "URL_DELETED"

# Read URLs from Excel
urls_to_submit = read_urls_from_excel(excel_file_path)

# Submit each URL for indexing or deletion
for url in urls_to_submit:
    response_code = submit_url(creds, url, requestType)
    if response_code == 200:
        print(f"Successfully submitted: {url}")
    else:
        print(f"Error submitting {url}. Error Code: {response_code}")

```

## Working Method

1. **Install the Package**
    ```sh
    pip install google-bulk-url-indexing
    ```
2. **Prepare Your Excel File**
    - Create an Excel file (`urls.xlsx`) with the URLs you want to submit, placing each URL in a separate cell in the first column.
3. **Connect Your JSON File**
    - Obtain a service account JSON file from Google Cloud Console and provide the complete path to it in your script.
4. **Run the Code**
    - Execute the script to start submitting your URLs for indexing.

## Project Structure

```
google-bulk-url-indexing/
├── indexing/
│   ├── __init__.py
│   ├── main.py
├── setup.py
├── README.md

```

## Dependencies

- `google-auth`
- `google-auth-oauthlib`
- `requests`
- `pandas`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Around With Us- [mscrabe@gmail.com](mailto:mscrabe@gmail.com)

## Acknowledgments

- [Google OAuth2](https://google-auth.readthedocs.io/)
- [Pandas](https://pandas.pydata.org/)
- [Requests](https://docs.python-requests.org/)

## Contributing

If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are welcome.

## Issues

If you encounter any issues, please open an issue on the repository.
