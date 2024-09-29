import requests
from datetime import datetime, timedelta

def get_repo_download_count_past_90_days(repo_url):

    # Extract the owner and repo name from the URL
    try:
        owner, repo = repo_url.rstrip('/').split('/')[-2:]

    except ValueError:
        print("无效的 GitHub 仓库 URL，请确保它是类似 'https://github.com/owner/repo' 的格式。")
        return
    
    # GitHub API URL to get the releases information
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        releases = response.json()
        total_downloads = 0
        
        # Calculate the date 90 days ago from today
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        
        # Iterate over each release
        for release in releases:
            release_date = datetime.strptime(release['published_at'], "%Y-%m-%dT%H:%M:%SZ")
            
            # Check if the release was published within the last 90 days
            if release_date >= ninety_days_ago:
                # Sum up the download counts of all assets in this release
                for asset in release.get('assets', []):
                    total_downloads += asset.get('download_count', 0)
        
        return total_downloads
    else:
        print(f"Failed to fetch data from GitHub API. Status code: {response.status_code}")
        return None

def main():
    # Ask user to input the GitHub repository URL
    repo_url = 'https://github.com/pytorch/pytorch'
    
    # Get the total download count for the past 90 days
    download_count = get_repo_download_count_past_90_days(repo_url)
    
    if download_count is not None:
        print(f"仓库 过去 90 天内的 Release 总下载次数: {download_count}")
    else:
        print("无法获取下载次数。")

if __name__ == "__main__":
    main()
