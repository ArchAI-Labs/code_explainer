# -*- coding: utf-8 -*-
import pytest
import os
import json
from unittest.mock import patch, MagicMock, mock_open, call
from code_explainer.utils.repo_loader import RepoLoader


# ---------------------------------------------------------------------------
# clone_repo
# ---------------------------------------------------------------------------

@patch('code_explainer.utils.repo_loader.Repo')
@patch('code_explainer.utils.repo_loader.os.makedirs')
@patch('code_explainer.utils.repo_loader.os.path.exists', return_value=False)
def test_clone_repo_success(mock_exists, mock_makedirs, mock_repo_class):
    """clone_repo clones and returns the local path when nothing exists yet."""
    utils = RepoLoader()
    remote_url = 'https://github.com/someuser/somerepo.git'
    expected_path = os.path.join('./repos/', 'somerepo')

    result = utils.clone_repo(remote_url)

    mock_repo_class.clone_from.assert_called_once_with(remote_url, to_path=expected_path)
    assert result == expected_path


@patch('code_explainer.utils.repo_loader.Repo')
def test_clone_repo_existing_path_returns_path(mock_repo_class, tmp_path):
    """clone_repo returns the existing path and skips cloning."""
    repo_base = str(tmp_path)
    existing_repo = os.path.join(repo_base, 'somerepo')
    os.makedirs(existing_repo)

    utils = RepoLoader(repo_path=repo_base)
    remote_url = 'https://github.com/someuser/somerepo.git'

    result = utils.clone_repo(remote_url)

    mock_repo_class.clone_from.assert_not_called()
    assert result == existing_repo


@patch('code_explainer.utils.repo_loader.Repo')
@patch('code_explainer.utils.repo_loader.os.makedirs')
@patch('code_explainer.utils.repo_loader.os.path.exists', return_value=False)
def test_clone_repo_invalid_url_returns_none(mock_exists, mock_makedirs, mock_repo_class):
    """clone_repo returns None for a URL that doesn't match the expected pattern."""
    utils = RepoLoader()
    result = utils.clone_repo('invalid_url')

    assert result is None
    mock_repo_class.clone_from.assert_not_called()


@patch('code_explainer.utils.repo_loader.Repo')
@patch('code_explainer.utils.repo_loader.os.makedirs')
@patch('code_explainer.utils.repo_loader.os.path.exists', return_value=False)
def test_clone_repo_git_error_returns_none(mock_exists, mock_makedirs, mock_repo_class):
    """clone_repo returns None when a GitCommandError is raised."""
    from git.exc import GitCommandError
    mock_repo_class.clone_from.side_effect = GitCommandError('clone', 128)

    utils = RepoLoader()
    result = utils.clone_repo('https://github.com/someuser/somerepo.git')

    assert result is None


# ---------------------------------------------------------------------------
# parse_java_file
# ---------------------------------------------------------------------------

JAVA_CODE = """
public class Foo {
    private int bar;
    public void doSomething(String arg) {}
}
"""

def test_parse_java_file_success(tmp_path):
    """parse_java_file extracts class/method/field info from valid Java."""
    java_file = tmp_path / "Foo.java"
    java_file.write_text(JAVA_CODE, encoding="utf-8")

    loader = RepoLoader()
    result = loader.parse_java_file(str(java_file))

    assert result is not None
    assert "Foo" in result


def test_parse_java_file_not_found():
    """parse_java_file returns None when the file does not exist."""
    loader = RepoLoader()
    result = loader.parse_java_file("/nonexistent/path/Foo.java")
    assert result is None


def test_parse_java_file_syntax_error_falls_back_to_raw(tmp_path):
    """parse_java_file falls back to raw text when the Java is unparseable."""
    bad_java = tmp_path / "Bad.java"
    bad_java.write_text("this is not java %%% !!!", encoding="utf-8")

    loader = RepoLoader()
    result = loader.parse_java_file(str(bad_java))

    assert result == "this is not java %%% !!!"


# ---------------------------------------------------------------------------
# load_repo
# ---------------------------------------------------------------------------

def test_load_repo_no_path_raises():
    """load_repo raises ValueError when no path has been set or provided."""
    loader = RepoLoader()
    with pytest.raises(ValueError, match="No local repository path"):
        loader.load_repo()


def test_load_repo_returns_json(tmp_path):
    """load_repo returns a JSON string with document dicts for code files."""
    py_file = tmp_path / "hello.py"
    py_file.write_text("print('hello')", encoding="utf-8")

    loader = RepoLoader()
    result = loader.load_repo(local_path=str(tmp_path))

    docs = json.loads(result)
    assert isinstance(docs, list)
    assert len(docs) >= 1
    sources = [d["source_filename"] for d in docs]
    assert any("hello.py" in s for s in sources)


def test_load_repo_java_files_included(tmp_path):
    """load_repo includes Java files parsed via javalang."""
    java_file = tmp_path / "App.java"
    java_file.write_text(JAVA_CODE, encoding="utf-8")

    loader = RepoLoader()
    result = loader.load_repo(local_path=str(tmp_path))

    docs = json.loads(result)
    java_docs = [d for d in docs if d["programming_language"] == "java"]
    assert len(java_docs) == 1
    assert "Foo" in java_docs[0]["source_file_contents"]
