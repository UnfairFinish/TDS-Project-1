#Code for Scraping and Cleaning Data
import requests
import csv
import time

# GitHub API token
GITHUB_TOKEN = 'MY_TOKEN'
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def clean_company_name(company):
    if company:
        company = company.strip().lstrip('@').upper()
    return company

# Function to fetch users from the GitHub API
def fetch_users(city="Boston", min_followers=100):
    users = []
    page = 1

    while True:
        url = f"https://api.github.com/search/users?q=location:{city}+followers:>{min_followers}&page={page}&per_page=100"
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        #print(data)
        if 'items' not in data or not data['items']:
            break

        for user in data['items']:
            user_url = user['url']
            user_response = requests.get(user_url, headers=HEADERS)
            user_data = user_response.json()
            users.append({
                'login': user_data['login'],
                'name': user_data['name'],
                'company': clean_company_name(user_data['company']),
                'location': user_data['location'],
                'email': user_data['email'],
                'hireable': user_data['hireable'],
                'bio': user_data['bio'],
                'public_repos': user_data['public_repos'],
                'followers': user_data['followers'],
                'following': user_data['following'],
                'created_at': user_data['created_at'],
            })
        page += 1
        time.sleep(1)
    return users

def fetch_repositories(user_login):
    repositories = []
    page = 1

    while True:
        url = f"https://api.github.com/users/{user_login}/repos?per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS)
        repo_data = response.json()

        if not repo_data:
            break

        for repo in repo_data:
            repositories.append({
                'login': user_login,
                'full_name': repo['full_name'],
                'created_at': repo['created_at'],
                'stargazers_count': repo['stargazers_count'],
                'watchers_count': repo['watchers_count'],
                'language': repo['language'],
                'has_projects': repo['has_projects'],
                'has_wiki': repo['has_wiki'],
                'license_name': repo['license']['key'] if repo['license'] else None,
            })

        if len(repo_data) < 100:
            break

        page += 1  
        time.sleep(1)  

    return repositories

def save_users_to_csv(users, filename="users.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=users[0].keys())
        writer.writeheader()
        writer.writerows(users)

def save_repositories_to_csv(repositories, filename="repositories.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=repositories[0].keys())
        writer.writeheader()
        writer.writerows(repositories)

def main():
    print("Fetching users...")
    users = fetch_users()
    print(users)
    save_users_to_csv(users)
    print(f"Saved {len(users)} users to users.csv")

    print("Fetching repositories...")
    all_repositories = []
    for user in users:
        user_repos = fetch_repositories(user["login"])
        all_repositories.extend(user_repos)
        print(f"Fetched {len(user_repos)} repositories for user {user['login']}")

    save_repositories_to_csv(all_repositories)
    print(f"Saved {len(all_repositories)} repositories to repositories.csv")

if __name__ == "__main__":
    main()
