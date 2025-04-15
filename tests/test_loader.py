# -*- coding: utf-8 -*-
import pytest
from unittest.mock import patch, MagicMock
from code_explainer.utils.repo_loader import RepoLoader
import os
import shutil
from pathlib import Path
import json

# Fixtures
@pytest.fixture
def mock_repo():
    # Create a mock Git repository
    mock_repo = MagicMock()
    mock_repo.clone_from = MagicMock(return_value=None)
    return mock_repo

# Test GitUtils

@patch('code_explainer.utils.repo_loader.Repo', autospec=True)
def test_clone_repo_success(mock_repo_class):
    # Arrange
    utils = RepoLoader()
    remote_url = 'https://github.com/someuser/somerepo.git'
    # Act
    utils.clone_repo(remote_url)
    # Assert
    mock_repo_class.clone_from.assert_called_once_with(remote_url, to_path='repos/somerepo')
    # assert os.path.exists('./repos/somerepo') == True #Temporary Assert, this assert will fail because the repo is not cloned

@patch('code_explainer.utils.repo_loader.Repo', autospec=True)
def test_clone_repo_existing_path_return_none(mock_repo_class):
    # Arrange
    remote_url = 'https://github.com/someuser/somerepo.git'
    local_path = 'repos/somerepo'
    utils = RepoLoader()

    # Create the directory *before* the test
    os.makedirs(local_path, exist_ok=True)

    # Act
    result = utils.clone_repo(remote_url)

    # Assert
    assert result is None # or assert result == False, based on what you return

    try:
        shutil.rmtree(local_path)  # Delete the directory and its contents
        print(f"Directory '{local_path}' deleted successfully.")
    except OSError as e:
        print(f"Error deleting directory '{local_path}': {e}")


@patch('code_explainer.utils.repo_loader.Repo', autospec=True)
def test_clone_repo_invalid_url(mock_repo_class):
    utils = RepoLoader()
    remote_url = 'invalid_url'
    with pytest.raises(SystemExit) as excinfo:
        utils.clone_repo(remote_url)
    assert excinfo.value.code == 1
    mock_repo_class.clone_from.assert_not_called()