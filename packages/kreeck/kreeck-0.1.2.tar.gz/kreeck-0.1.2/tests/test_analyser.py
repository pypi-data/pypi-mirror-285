import pytest
import git
from collections import defaultdict
from kreeck.analyser import (
    calculate_contributions,
    create_contributions_md,
    create_markdown_report,
    is_github_url,
    check_github_repo_visibility,
    get_github_commits,
    analyze_commit_messages,
    identify_top_commits,
    determine_badges,
    create_historical_comparison
)
from unittest.mock import patch, MagicMock

def test_calculate_contributions_local_repo(tmpdir):
    repo_dir = tmpdir.mkdir("test_repo")
    repo = git.Repo.init(repo_dir)
    repo.index.commit("Initial commit")
    
    contributions, percentages = calculate_contributions(str(repo_dir))
    
    assert contributions == defaultdict(int)
    assert percentages == {}

@patch("kreeck.analyser.requests.get")
def test_calculate_contributions_github_repo(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{
        "commit": {"author": {"email": "test@example.com"}},
        "sha": "12345",
        "files": [{"patch": "diff"}]
    }]
    
    with patch('kreeck.analyser.get_commit_details', return_value={
        "commit": {"author": {"email": "test@example.com"}},
        "files": [{"patch": "diff"}]
    }):
        contributions, percentages = calculate_contributions("https://github.com/test/test_repo")
    
    assert contributions["test@example.com"] == 1
    assert percentages["test@example.com"] == 100.0

def test_is_github_url():
    assert is_github_url("https://github.com/test/test_repo")
    assert not is_github_url("https://gitlab.com/test/test_repo")

@patch("kreeck.analyser.requests.get")
def test_check_github_repo_visibility(mock_get):
    mock_get.return_value.status_code = 404
    visibility = check_github_repo_visibility("https://github.com/test/private_repo")
    assert visibility == 'private'

@patch("kreeck.analyser.requests.get")
def test_get_github_commits(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{"sha": "12345"}]
    commits = get_github_commits("https://github.com/test/test_repo")
    assert len(commits) == 1
    assert commits[0]["sha"] == "12345"

def test_analyze_commit_messages_local_repo(tmpdir):
    repo_dir = tmpdir.mkdir("test_repo")
    repo = git.Repo.init(repo_dir)
    repo.index.commit("Initial commit\nfix: fixed a bug")
    
    messages = analyze_commit_messages(str(repo_dir))
    
    assert "fix" in messages
    assert len(messages["fix"]) == 1

@patch("kreeck.analyser.requests.get")
def test_identify_top_commits_github_repo(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{
        "commit": {"author": {"email": "test@example.com"}},
        "sha": "12345",
        "files": [{"patch": "diff"}]
    }]
    
    with patch('kreeck.analyser.get_commit_details', return_value={
        "commit": {"author": {"email": "test@example.com"}},
        "files": [{"patch": "diff"}]
    }):
        top_commits = identify_top_commits("https://github.com/test/test_repo")
    
    assert len(top_commits) == 1

def test_determine_badges():
    contributions = {"test@example.com": 1000, "test2@example.com": 500}
    badges = determine_badges(contributions)
    
    assert badges["test@example.com"] == "Gold"
    assert badges["test2@example.com"] == "Silver"



@patch("kreeck.analyser.get_github_commits")
@patch("kreeck.analyser.get_commit_details")
def test_create_historical_comparison(mock_get_commit_details, mock_get_github_commits, tmpdir):
    repo_dir = tmpdir.mkdir("test_repo")
    repo = git.Repo.init(repo_dir)
    repo.index.commit("Initial commit")

    mock_get_github_commits.return_value = [{
        "sha": "12345",
        "commit": {"author": {"email": "test@example.com"}},
        "files": [{"patch": "diff"}]
    }]
    
    mock_get_commit_details.return_value = {
        "commit": {"author": {"email": "test@example.com"}},
        "files": [{"patch": "diff"}]
    }

    with patch('kreeck.analyser.calculate_contributions', return_value=(defaultdict(int, {"test@example.com": 10}), {"test@example.com": 100.0})):
        report = create_historical_comparison("https://github.com/test/test_repo")

    assert "Historical Comparison Report" in report
    assert "| test@example.com | 0 | 10 | 10 |" in report
