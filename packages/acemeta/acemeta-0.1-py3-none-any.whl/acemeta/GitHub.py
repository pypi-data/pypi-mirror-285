import requests as WEB
import base64

class Repository():
    """
    Contains the information to access a GitHub repository

    #### Arguments:
        repository (str): The repository wanted to access in the scheme `"annhilati/acemeta"`
        token (str): A PAT-Token that has access to the requested repository

    #### Methods:
        upload(): Uploads a file to the repository
        download(): Downloads a file from the repository
    """
    def __init__(self, repository: str, token: str):
        self.repository = repository
        self.token = token

        self._url = f"https://api.github.com/repos/{self.repository}/contents"

    def upload(self, file: str, directory: str, msg: str) -> None:
        """
        Uploads a file to the GitHub repository

        #### Arguments:
            file (str): Path to the file to upload
            directory (str): Path of the file that is to be created
            msg (str): An optional upload information displayed as the commit summary

        #### Raises:
            FileExistsError: If a file with the same content already exists in the requested directory
            Exception: For other errors encountered during download
        """

        target = f"{self._url}/{directory}"
        
        with open(file, 'rb') as f:
            content = f.read()
            content_base64 = base64.b64encode(content).decode("utf-8")

        headers = {
            'Authorization': f'token {self.token}',
            'Content-Type': 'application/json'
        }
        data = {
        'message': msg,
        'content': content_base64
        }
    
        response = WEB.put(target, json=data, headers=headers)

        if response.status_code == 422:
            raise FileExistsError(f"File '{self.repository}/{directory}' already exists with the exact same content")
        response.raise_for_status()


    def download(self, file: str, destination: str) -> None:
        """
        Downloads a file from the GitHub repository.

        #### Arguments:
            file (str): Path to the file in the GitHub repository
            destination (str): Local path where the file should be saved

        #### Raises:
            FileNotFoundError: If the file is not found in the repository
            Exception: For other errors encountered during download
        """

        target = f"{self._url}/contents/{file}"
        
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3.raw'  # Accept header for raw content
        }
        
        response = WEB.get(target, headers=headers)
        
        if response.status_code == 404:
            raise FileNotFoundError(f"File '{file}' not found in the repository")
        response.raise_for_status()
        
        content_base64 = response.content
        content = base64.b64decode(content_base64)
        
        with open(destination, 'wb') as f:
            f.write(content)