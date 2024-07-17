# Download class for downloading address datasets from specific countries
import requests 
from json import loads as read_json
import zipfile
import os

metadata_filename = "dataset_metadata.json"

def read_metadata(filename):
    """
    Read the metadata for the country address info and return as dict
    """
    with open(filename, 'r') as file:
        metadata = json.load(file)
    return metadata

class Downloader:
    def __init__(self, 
                 country_name, 
                 state_name=None):
        """
        Args
        ----
        country_name (str): abbreviation of a country name
        state_name (list[str], optional, default=None): the names of states within the country
        """
        self.metadata = read_metadata(metadata_filename)
        country_names = self.metadata['country_name'].keys()

        # check that the specified country is valid
        if country_name not in country_names:
            print(f"Country name {country_name} not valid. \nPlease specify one from {country_names}")
        else:
            self.country_name = country_name
            self.state_name = state_name
            self.metadata = self.metadata[country_name]

    def download(self, 
                 output_path):
        """
        Download the data for a given country to a particular path

        Args
        ----
        path (str): path to download the data to
        """
        download_path = self.metadata['data_url']
        r = requests.get(download_path)
        if r.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(r.content)
            print("Successfully downloaded data")
        else:
            print("Could not access data")

    def extract_data(self, 
                     zip_path, 
                     extract_to):
        """
        Extract compressed data
        """
        # Ensure the directory exists
        if not os.path.exists(extract_to):
            os.makedirs(extract_to)
        
        # Unzip the file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

