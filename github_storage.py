import os
import requests
import base64
import json
from datetime import datetime
import pandas as pd

class GitHubStorage:
    def __init__(self, token_file="token.txt"):
        """Initialize GitHub storage with token from file"""
        self.token = self._load_github_token(token_file)
        self.repo_owner = None  # Will be set when first used
        self.repo_name = None   # Will be set when first used
        self.base_url = "https://api.github.com"
        
    def _load_github_token(self, token_file):
        """Load GitHub token from file"""
        try:
            with open(token_file, 'r') as f:
                content = f.read().strip()
                # Look for GitHub token in the file
                lines = content.split('\n')
                for line in lines:
                    if 'github_token' in line.lower() or 'gh_token' in line.lower():
                        return line.split('=')[-1].strip()
                # If no specific GitHub token found, assume the whole content is the token
                return content
        except FileNotFoundError:
            print(f"[WARNING] {token_file} not found. GitHub storage will not work.")
            return None
    
    def set_repository(self, owner, repo_name):
        """Set the GitHub repository details"""
        self.repo_owner = owner
        self.repo_name = repo_name
    
    def create_repository(self, repo_name, description="BankNifty Option Chain Data Storage"):
        """Create a new GitHub repository"""
        if not self.token:
            return False, "No GitHub token available"
        
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        data = {
            'name': repo_name,
            'description': description,
            'private': False,  # Set to True if you want private repo
            'auto_init': True
        }
        
        response = requests.post(f"{self.base_url}/user/repos", 
                               headers=headers, json=data)
        
        if response.status_code == 201:
            repo_info = response.json()
            self.repo_owner = repo_info['owner']['login']
            self.repo_name = repo_name
            return True, f"Repository created: {repo_info['html_url']}"
        else:
            return False, f"Failed to create repository: {response.text}"
    
    def upload_csv_file(self, file_path, github_path=None, commit_message=None):
        """Upload a CSV file to GitHub repository"""
        if not self.token or not self.repo_owner or not self.repo_name:
            return False, "GitHub not properly configured"
        
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        # Set default GitHub path if not provided
        if github_path is None:
            filename = os.path.basename(file_path)
            github_path = f"data/{filename}"
        
        # Set default commit message if not provided
        if commit_message is None:
            commit_message = f"Update {os.path.basename(file_path)} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Read and encode file content
        with open(file_path, 'rb') as f:
            content = base64.b64encode(f.read()).decode('utf-8')
        
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Check if file already exists to get SHA
        get_url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{github_path}"
        get_response = requests.get(get_url, headers=headers)
        
        data = {
            'message': commit_message,
            'content': content
        }
        
        # If file exists, include SHA for update
        if get_response.status_code == 200:
            data['sha'] = get_response.json()['sha']
        
        # Upload/update file
        put_response = requests.put(get_url, headers=headers, json=data)
        
        if put_response.status_code in [200, 201]:
            file_info = put_response.json()
            return True, f"File uploaded: {file_info['content']['html_url']}"
        else:
            return False, f"Failed to upload file: {put_response.text}"
    
    def upload_dataframe_as_csv(self, df, filename, github_path=None, commit_message=None):
        """Upload a pandas DataFrame as CSV to GitHub"""
        # Save DataFrame to temporary CSV file
        temp_file = f"temp_{filename}"
        df.to_csv(temp_file, index=False)
        
        try:
            # Upload the temporary file
            success, message = self.upload_csv_file(temp_file, github_path, commit_message)
            return success, message
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def list_repository_files(self, path=""):
        """List files in the repository"""
        if not self.token or not self.repo_owner or not self.repo_name:
            return False, "GitHub not properly configured"
        
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{path}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            files = response.json()
            return True, files
        else:
            return False, f"Failed to list files: {response.text}"

# Example usage functions
def setup_github_storage():
    """Setup GitHub storage with your repository"""
    github = GitHubStorage()
    
    if not github.token:
        print("Please add your GitHub token to token.txt file")
        print("Format: github_token=your_token_here")
        return None
    
    # You can either create a new repository or use an existing one
    repo_name = "banknifty-data"
    
    # Try to create repository (will fail if it already exists, which is fine)
    success, message = github.create_repository(repo_name)
    if success:
        print(f"✓ {message}")
    else:
        # If creation failed, assume repository exists and set it manually
        # Replace 'your-username' with your actual GitHub username
        github.set_repository("your-username", repo_name)
        print(f"Using existing repository: your-username/{repo_name}")
    
    return github

def save_option_chain_to_github(option_chain_data, filename=None):
    """Save option chain data to GitHub as CSV"""
    github = setup_github_storage()
    if not github:
        return False, "GitHub setup failed"
    
    if filename is None:
        filename = f"option_chain_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Convert option chain data to DataFrame
    df = pd.DataFrame(option_chain_data)
    
    # Upload to GitHub
    success, message = github.upload_dataframe_as_csv(
        df, filename, 
        github_path=f"option_chains/{filename}",
        commit_message=f"Option chain data update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    return success, message

def save_csv_to_github(csv_file_path):
    """Save any CSV file to GitHub"""
    github = setup_github_storage()
    if not github:
        return False, "GitHub setup failed"
    
    filename = os.path.basename(csv_file_path)
    success, message = github.upload_csv_file(
        csv_file_path,
        github_path=f"csv_files/{filename}",
        commit_message=f"CSV file update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    return success, message

if __name__ == "__main__":
    # Test the GitHub storage
    github = setup_github_storage()
    if github:
        print("GitHub storage setup successful!")
        
        # Test listing files
        success, files = github.list_repository_files()
        if success:
            print("Repository files:")
            for file in files:
                print(f"  - {file['name']} ({file['type']})")
        else:
            print(f"Failed to list files: {files}")