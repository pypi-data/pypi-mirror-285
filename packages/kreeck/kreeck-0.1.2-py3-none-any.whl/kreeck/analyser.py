import git
from collections import defaultdict, Counter
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import re
from dotenv import load_dotenv
from tqdm import tqdm
import requests
import json
import base64

# Load environment variables from .env file
load_dotenv()

# GitHub token configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

def is_github_url(url):
    return url.startswith('https://github.com/')

def check_github_repo_visibility(url):
    if not GITHUB_TOKEN:
        raise Exception("GitHub token is missing. Please set it in the .env file.")
    
    api_url = url.replace('https://github.com/', 'https://api.github.com/repos/')
    headers = {'Authorization': f'token ' + GITHUB_TOKEN}
    response = requests.get(api_url, headers=headers)
    if response.status_code == 401:
        raise Exception("GitHub token is invalid or does not have the necessary permissions.")
    if response.status_code == 404:
        return 'private'
    response.raise_for_status()
    return 'public'

def get_github_commits(url):
    if not GITHUB_TOKEN:
        raise Exception("GitHub token is missing. Please set it in the .env file.")
    
    api_url = url.replace('https://github.com/', 'https://api.github.com/repos/') + '/commits'
    headers = {'Authorization': f'token ' + GITHUB_TOKEN}
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    return response.json()

# Ensure get_commit_details returns a dictionary and handle accordingly in calculate_contributions and identify_top_commits
def get_commit_details(url, sha):
    api_url = url.replace('https://github.com/', 'https://api.github.com/repos/') + f'/commits/{sha}'
    headers = {'Authorization': f'token ' + GITHUB_TOKEN}
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    return response.json()


def calculate_contributions(repo_path='.'):
    contributions = defaultdict(int)
    
    if is_github_url(repo_path):
        try:
            visibility = check_github_repo_visibility(repo_path)
        except Exception as e:
            print(e)
            return {}, {}
        
        if visibility == 'private':
            print("The repository is private. Please run the analysis on a local environment with the command 'kreeck report' or 'kreeck report /project/path/'.")
            return {}, {}
        
        commits = get_github_commits(repo_path)
        for commit in tqdm(commits, desc="Calculating contributions from GitHub"):
            try:
                commit_details = get_commit_details(repo_path, commit['sha'])
                author = commit_details['commit']['author']['email']
                lines_added = sum(len(diff['patch'].splitlines()) for diff in commit_details.get('files', []) if 'patch' in diff)
                contributions[author] += lines_added
            except KeyError:
                # Skip commits that do not have 'files' key
                continue
    else:
        try:
            repo = git.Repo(repo_path)
        except git.exc.InvalidGitRepositoryError:
            raise Exception(f"The directory {repo_path} is not a valid Git repository.")
        
        for commit in tqdm(repo.iter_commits(), desc="Calculating contributions"):
            author = commit.author.email
            contributions[author] += sum(
                (len(diff.a_blob.data_stream.read().decode('utf-8', errors='ignore').splitlines())
                 for diff in commit.diff(commit.parents or git.NULL_TREE).iter_change_type('M'))
            )

    total_lines = sum(contributions.values())
    
    if total_lines == 0:
        return {}, {}  # Return empty dictionaries if there are no lines counted
    
    percentages = {author: (lines / total_lines) * 100 for author, lines in contributions.items()}

    return contributions, percentages

# Function to create the contributions markdown file
def create_contributions_md(contributions, percentages, repo_path):
    if not contributions:
        content = "# Contributions\n\nNo contributions found.\n"
    else:
        sorted_contributions = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
        content = "# Contributions\n\n"
        content += "This file lists the contributions of each user to the project, ranked by the percentage of the total contributions.\n\n"
        content += "| Rank | Contributor | Percentage | Lines Added |\n"
        content += "|------|-------------|------------|-------------|\n"
        
        for rank, (author, percentage) in enumerate(sorted_contributions, start=1):
            content += f"| {rank} | {author} | {percentage:.2f}% | {contributions[author]} |\n"
    
    contributions_md_path = os.path.join(repo_path, 'Contributions.md')
    with open(contributions_md_path, 'w') as file:
        file.write(content)

# Function to create commit frequency chart (only for local repositories)
def create_commit_frequency_chart(repo_path):
    if is_github_url(repo_path):
        return None  # Skip chart generation for GitHub URLs

    commit_dates = []
    repo = git.Repo(repo_path)
    for commit in repo.iter_commits():
        commit_dates.append(commit.committed_datetime.date())

    commit_counts = Counter(commit_dates)
    dates, counts = zip(*sorted(commit_counts.items()))

    # Format dates as YY-MM-DD
    formatted_dates = [date.strftime('%y-%m-%d') for date in dates]

    df = pd.DataFrame({'Date': formatted_dates, 'Commits': counts})
    df.set_index('Date', inplace=True)

    plt.figure(figsize=(10, 5))
    df.plot(kind='line')
    plt.title('Commit Frequency Over Time')
    plt.xlabel('Date')
    plt.ylabel('Number of Commits')
    plt.grid(True)

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)

    chart_path = os.path.join(repo_path, 'commit_frequency_chart.png')
    plt.savefig(chart_path)
    plt.close()
    return chart_path

# Function to analyze file type contributions
def analyse_file_type_contributions(repo_path):
    file_type_contributions = defaultdict(lambda: defaultdict(int))
    
    # Define known file types
    known_file_types = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.html': 'HTML',
        '.css': 'CSS',
        '.java': 'Java',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.cpp': 'C++',
        '.c': 'C',
        '.cs': 'C#',
        '.go': 'Go',
        '.rs': 'Rust',
        '.sh': 'Shell',
        '.xml': 'XML',
        '.json': 'JSON',
        '.yml': 'YAML',
        '.md': 'Markdown',
    }

    def process_file(file_type, author, lines_added):
        if file_type in known_file_types:
            file_type_contributions[known_file_types[file_type]][author] += lines_added
        elif file_type == '':
            file_type_contributions['unknown'][author] += lines_added
        else:
            file_type_contributions[file_type][author] += lines_added

    if is_github_url(repo_path):
        try:
            visibility = check_github_repo_visibility(repo_path)
        except Exception as e:
            print(e)
            return {}
        
        if visibility == 'private':
            print("The repository is private. Please run the analysis on a local environment with the command 'kreeck report' or 'kreeck report /project/path/'.")
            return {}
        
        commits = get_github_commits(repo_path)
        for commit in commits:
            author = commit['commit']['author']['email']
            for file in commit.get('files', []):
                file_type = os.path.splitext(file['filename'])[1].lower()
                lines_added = len(file['patch'].splitlines()) if 'patch' in file else 0
                process_file(file_type, author, lines_added)
    else:
        repo = git.Repo(repo_path)
        for commit in repo.iter_commits():
            author = commit.author.email
            for diff in commit.diff(commit.parents or git.NULL_TREE).iter_change_type('M'):
                try:
                    file_type = os.path.splitext(diff.a_path)[1].lower()
                    lines_added = len(diff.a_blob.data_stream.read().decode('utf-8', errors='ignore').splitlines())
                    process_file(file_type, author, lines_added)
                except AttributeError:
                    continue

    return file_type_contributions


# Function to analyze commit messages
def analyze_commit_messages(repo_path):
    message_patterns = defaultdict(list)
    
    if is_github_url(repo_path):
        try:
            visibility = check_github_repo_visibility(repo_path)
        except Exception as e:
            print(e)
            return {}
        
        if visibility == 'private':
            print("The repository is private. Please run the analysis on a local environment with the command 'kreeck report' or 'kreeck report /project/path/'.")
            return {}
        
        commits = get_github_commits(repo_path)
        for commit in commits:
            message = commit['commit']['message'].lower()
            if 'fix' in message:
                message_patterns['fix'].append(commit)
            elif 'feature' in message or 'add' in message:
                message_patterns['feature'].append(commit)
            elif 'refactor' in message:
                message_patterns['refactor'].append(commit)
            elif 'test' in message:
                message_patterns['test'].append(commit)
    else:
        repo = git.Repo(repo_path)
        for commit in repo.iter_commits():
            message = commit.message.lower()
            if 'fix' in message:
                message_patterns['fix'].append(commit)
            elif 'feature' in message or 'add' in message:
                message_patterns['feature'].append(commit)
            elif 'refactor' in message:
                message_patterns['refactor'].append(commit)
            elif 'test' in message:
                message_patterns['test'].append(commit)

    return message_patterns

# Function to identify top commits
def identify_top_commits(repo_path):
    top_commits = []

    if is_github_url(repo_path):
        try:
            visibility = check_github_repo_visibility(repo_path)
        except Exception as e:
            print(e)
            return []
        
        if visibility == 'private':
            print("The repository is private. Please run the analysis on a local environment with the command 'kreeck report' or 'kreeck report /project/path/'.")
            return []
        
        commits = get_github_commits(repo_path)
        for commit in commits:
            try:
                commit_details = get_commit_details(repo_path, commit['sha'])
                lines_changed = sum(len(diff['patch'].splitlines()) for diff in commit_details.get('files', []) if 'patch' in diff)
                top_commits.append((commit_details, lines_changed))
            except KeyError:
                # Skip commits that do not have 'files' key
                continue
    else:
        repo = git.Repo(repo_path)
        for commit in repo.iter_commits():
            lines_changed = sum(
                (len(diff.a_blob.data_stream.read().decode('utf-8', errors='ignore').splitlines())
                 for diff in commit.diff(commit.parents or git.NULL_TREE).iter_change_type('M'))
            )
            top_commits.append((commit, lines_changed))

    top_commits = sorted(top_commits, key=lambda x: x[1], reverse=True)[:5]
    return top_commits

# Function to create historical comparison
def load_historical_data(repo_path):
    if is_github_url(repo_path):
        return []
    historical_data_path = os.path.join(repo_path, 'historical_contributions.json')
    if os.path.exists(historical_data_path):
        with open(historical_data_path, 'r') as file:
            return json.load(file)
    return []

def save_historical_data(repo_path, historical_data):
    if is_github_url(repo_path):
        return
    historical_data_path = os.path.join(repo_path, 'historical_contributions.json')
    with open(historical_data_path, 'w') as file:
        json.dump(historical_data, file, indent=4)

def calculate_differences(current_data, historical_data):
    differences = {}
    historical_latest = historical_data[-1] if historical_data else {}

    for contributor, current_lines in current_data.items():
        historical_lines = historical_latest.get(contributor, 0)
        differences[contributor] = current_lines - historical_lines

    return differences

def calculate_historical_contributions_from_commits(repo_path, commits):
    historical_contributions = []
    for commit in commits:
        contributions = defaultdict(int)
        commit_details = get_commit_details(repo_path, commit['sha'])
        for file in commit_details.get('files', []):
            lines_added = len(file['patch'].splitlines()) if 'patch' in file else 0
            contributions[commit['commit']['author']['email']] += lines_added
        historical_contributions.append(contributions)
    return historical_contributions


def create_historical_comparison(repo_path):
    if is_github_url(repo_path):
        historical_data = []
        is_github = True
    else:
        historical_data = load_historical_data(repo_path)
        is_github = False

    current_contributions, current_percentages = calculate_contributions(repo_path)

    if not current_contributions:
        return "No current contributions to compare."

    if is_github:
        commits = get_github_commits(repo_path)
        historical_contributions = calculate_historical_contributions_from_commits(repo_path, commits)
        historical_data = historical_contributions
    else:
        differences = calculate_differences(current_contributions, historical_data)
        historical_data.append(current_contributions)
        save_historical_data(repo_path, historical_data)

    comparison_report = "# Historical Comparison Report\n\n"
    comparison_report += "| Contributor | Historical Lines | Current Lines | Difference |\n"
    comparison_report += "|-------------|------------------|---------------|------------|\n"

    for contributor, current_lines in current_contributions.items():
        historical_lines = historical_data[-2].get(contributor, 0) if len(historical_data) > 1 else 0
        difference = current_lines - historical_lines
        comparison_report += f"| {contributor} | {historical_lines} | {current_lines} | {difference} |\n"

    if not is_github:
        dates = [f"Version {i+1}" for i in range(len(historical_data))]
        data = {contributor: [version.get(contributor, 0) for version in historical_data] for contributor in current_contributions}

        df = pd.DataFrame(data, index=dates)
        df.plot(kind='bar', figsize=(10, 5))
        plt.title('Contributions Over Time')
        plt.xlabel('Versions')
        plt.ylabel('Lines of Code')
        plt.xticks(rotation=45)

        chart_path = os.path.join(repo_path, 'historical_comparison_chart.png')
        plt.savefig(chart_path)
        plt.close()

        comparison_report += f"\n![Historical Comparison Chart]({chart_path})\n"
    else:
        comparison_report += "\n\n\n\n Historical Comparison Chart not available for Online Repositories"

    return comparison_report



# Function to determine badges for contributors
def determine_badges(contributions):
    badges = {}
    for author, lines in contributions.items():
        if lines >= 1000:
            badges[author] = 'Gold'
        elif lines >= 500:
            badges[author] = 'Silver'
        elif lines >= 100:
            badges[author] = 'Bronze'
        else:
            badges[author] = 'No Badge'
    return badges

# Function to create a Markdown report
def create_markdown_report(repo_path):
    contributions, percentages = calculate_contributions(repo_path)
    if not contributions and not percentages:
        return
    
    if not is_github_url(repo_path):
        commit_frequency_chart = create_commit_frequency_chart(repo_path)
    else:
        commit_frequency_chart = None

    file_type_contributions = analyse_file_type_contributions(repo_path)
    commit_message_analysis = analyze_commit_messages(repo_path)
    top_commits = identify_top_commits(repo_path)
    historical_comparison = create_historical_comparison(repo_path)
    badges = determine_badges(contributions)

    report_content = "# Contribution Report\n\n"

    report_content += "## Commit Frequency\n\n"
    if commit_frequency_chart:
        report_content += f"![Commit Frequency Chart]({commit_frequency_chart})\n\n"

    report_content += "## Contributions by File Type\n\n"
    for file_type, contributors in file_type_contributions.items():
        report_content += f"### {file_type}\n"
        report_content += "| Contributor | Lines Added |\n"
        report_content += "|-------------|-------------|\n"
        for author, lines in contributors.items():
            report_content += f"| {author} | {lines} |\n"
        report_content += "\n"

    report_content += "## Commit Message Analysis\n\n"
    for pattern, commits in commit_message_analysis.items():
        report_content += f"### {pattern.capitalize()}\n"
        report_content += "| Commit Message | Author | Date |\n"
        report_content += "|----------------|--------|------|\n"
        for commit in commits:
            if is_github_url(repo_path):
                report_content += f"| {commit['commit']['message'].strip()} | {commit['commit']['author']['email']} | {commit['commit']['author']['date']} |\n"
            else:
                report_content += f"| {commit.message.strip()} | {commit.author.email} | {commit.committed_datetime} |\n"
        report_content += "\n"

    report_content += "## Top Commits\n\n"
    report_content += "| Commit Message | Author | Lines Changed | Date |\n"
    report_content += "|----------------|--------|---------------|------|\n"
    for commit, lines in top_commits:
        if is_github_url(repo_path):
            report_content += f"| {commit['commit']['message'].strip()} | {commit['commit']['author']['email']} | {lines} | {commit['commit']['author']['date']} |\n"
        else:
            report_content += f"| {commit.message.strip()} | {commit.author.email} | {lines} | {commit.committed_datetime} |\n"

    report_content += "\n## Historical Comparison\n\n"
    report_content += historical_comparison

    report_content += "\n## Badges\n\n"
    report_content += "| Contributor | Badge |\n"
    report_content += "|-------------|-------|\n"
    for author, badge in badges.items():
        report_content += f"| {author} | {badge} |\n"

    report_content += "\n## Leaderboard\n\n"
    sorted_contributions = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
    report_content += "| Rank | Contributor | Percentage | Lines Added |\n"
    report_content += "|------|-------------|------------|-------------|\n"
    for rank, (author, percentage) in enumerate(sorted_contributions, start=1):
        report_content += f"| {rank} | {author} | {percentage:.2f}% | {contributions[author]} |\n"

    if not is_github_url(repo_path):
        report_path = os.path.join(repo_path, 'Report.md')
        with open(report_path, 'w') as file:
            file.write(report_content)

    print(report_content)

# Main function to create the report
def create_report(repo_path='.'):
    create_markdown_report(repo_path)
