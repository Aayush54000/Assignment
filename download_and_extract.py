import requests
import io
import zipfile
import os
from datetime import datetime

class CricketDataDownloader:
    def __init__(self, download_url, extract_base_path):
        self.download_url = download_url
        self.extract_base_path = extract_base_path

    def download_data(self):
        """
        Downloads the zip file from the provided URL and returns the file object.
        
        :return: A file-like object containing the downloaded zip file data.
        """
        print("Starting download...")
        try:
            response = requests.get(self.download_url)
            response.raise_for_status()  # Raise an error if the download fails
            print(f"Download completed successfully with status code: {response.status_code}")
            return io.BytesIO(response.content)
        except requests.exceptions.HTTPError as http_err:
            # Print only the required error information
            print(f"HTTP error occurred: {http_err}")
            print(f"Status code: {response.status_code}")
        except requests.exceptions.RequestException as req_err:
            # Print only the required error information
            print(f"Request error occurred: {req_err}")
        except Exception as e:
            # Print only the required error information
            print(f"An unexpected error occurred: {e}")
        finally:
            # This block is executed whether or not an exception occurred
            print("Download attempt finished.")
        return None

    def extract_data(self, file_obj):
        """
        Extracts the content of the downloaded zip file to a directory with a timestamp.
        
        :param file_obj: A file-like object containing the zip file data. 
        """
        if file_obj is None:
            print("No file to extract. Please check the download process.")
            return
        
        # Generate a directory name with the current date
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        extract_path = os.path.join(self.extract_base_path, f"data_{date_str}")
        
        # Ensure the extraction directory exists
        if not os.path.exists(extract_path):
            os.makedirs(extract_path)
        
        print(f"Extraction directory: {extract_path}")
        print("Starting extraction...")
        try:
            with zipfile.ZipFile(file_obj) as zip_ref:
                zip_ref.extractall(extract_path)
            print(f"Extraction completed. Files are saved to {extract_path}")
        except zipfile.BadZipFile as bz_err:
            # Print only the required error information
            print(f"Error extracting zip file: {bz_err}")
        except Exception as e:
            # Print only the required error information
            print(f"An unexpected error occurred during extraction: {e}")
        finally:
            # This block is executed whether or not an exception occurred
            print("Extraction attempt finished.")

# Example usage
download_url = "https://cricsheet.org/downloads/odis_json.zip"  # Update this URL if necessary
extract_base_path = "./data"

downloader = CricketDataDownloader(download_url, extract_base_path)
file_obj = downloader.download_data()
downloader.extract_data(file_obj)