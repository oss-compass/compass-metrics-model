import requests
import matplotlib.pyplot as plt
from datetime import datetime

def parse_date(date_str):
    # 尝试不同的日期格式
    formats = [
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%S'
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {date_str}")

def get_pypi_releases(package_name):
    
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    data = response.json()
    releases = data['releases']
    release_dates = []
    dependencies_counts = []

    for version, info in releases.items():
        if info:
            release_date = info[0].get('upload_time', '')
            if release_date:
                try:
                    release_dates.append(parse_date(release_date))
                except ValueError:
                    continue
            dependencies = info[0].get('requires_dist', [])
            dependencies_counts.append(len(dependencies))
    
    return release_dates, dependencies_counts

def get_npm_releases(package_name):
    url = f"https://registry.npmjs.org/{package_name}"
    response = requests.get(url)
    data = response.json()
    versions = data['versions']
    release_dates = []
    dependencies_counts = []

    for version, info in versions.items():
        release_date = info.get('time', '')
        if release_date:
            try:
                release_dates.append(parse_date(release_date))
            except ValueError:
                continue
        dependencies = info.get('dependencies', {})
        dependencies_counts.append(len(dependencies))

    return release_dates, dependencies_counts

def plot_dependencies(release_dates, dependencies_counts, title,save_name):
    plt.figure(figsize=(12, 6))
    plt.plot([i for i in range(len(dependencies_counts))], dependencies_counts, marker='o', linestyle='-', color='b')
    plt.xlabel('Release Date')
    plt.ylabel('Number of Dependencies')
    plt.title(title)
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(save_name)

def main():
    pypi_package = 'requests'  # Replace with your PyPI package
    npm_package = 'express'  # Replace with your npm package

    # Fetch and plot PyPI data
    #print(f"Fetching data for PyPI package: {pypi_package}")
    #pypi_dates, pypi_counts = get_pypi_releases(pypi_package)
    #plot_dependencies(pypi_dates, pypi_counts, f'{pypi_package} PyPI Dependencies Over Time')

    # Fetch and plot npm data
    print(f"Fetching data for npm package: {npm_package}")
    npm_dates, npm_counts = get_npm_releases(npm_package)
    plot_dependencies(npm_dates, npm_counts, f'{npm_package} npm Dependencies Over Time',npm_package+".png")

if __name__ == "__main__":
    main()
