import os
import pytest
from unittest.mock import patch, MagicMock
from code_explainer.utils.utils import (
    check_memory_dir,
    manage_output_dir,
    BatchProcessingManager,
    ContextManager,
    LLM_Config,
)


# ---------------------------------------------------------------------------
# check_memory_dir
# ---------------------------------------------------------------------------

def test_check_memory_dir_creates_dir(tmp_path):
    memory_dir = str(tmp_path / "memory")
    check_memory_dir(memory_dir)
    assert os.path.isdir(memory_dir)


def test_check_memory_dir_existing_dir(tmp_path, capsys):
    memory_dir = str(tmp_path / "memory")
    os.makedirs(memory_dir)
    check_memory_dir(memory_dir)
    captured = capsys.readouterr()
    assert "memory exists" in captured.out


# ---------------------------------------------------------------------------
# manage_output_dir
# ---------------------------------------------------------------------------

def test_manage_output_dir_creates_new(tmp_path):
    output_dir = str(tmp_path / "output/")
    manage_output_dir(output_dir)
    assert os.path.isdir(output_dir)


def test_manage_output_dir_renames_existing(tmp_path):
    output_dir = str(tmp_path / "output/")
    os.makedirs(output_dir)
    manage_output_dir(output_dir)
    # The original dir should be gone (renamed) and a new one created
    assert os.path.isdir(output_dir)
    # At least one renamed dir should exist
    siblings = list(tmp_path.iterdir())
    assert len(siblings) >= 2  # renamed + new


# ---------------------------------------------------------------------------
# BatchProcessingManager / ContextManager alias
# ---------------------------------------------------------------------------

def test_context_manager_alias():
    assert ContextManager is BatchProcessingManager


def test_count_tokens_returns_int():
    mgr = BatchProcessingManager(max_tokens=1000)
    count = mgr.count_tokens("hello world")
    assert isinstance(count, int)
    assert count > 0


def test_chunk_files_by_tokens_empty():
    mgr = BatchProcessingManager(max_tokens=1000)
    result = mgr.chunk_files_by_tokens({})
    assert result == []


def test_chunk_files_by_tokens_single_small_file():
    mgr = BatchProcessingManager(max_tokens=1000)
    files = {"file.py": "x = 1"}
    chunks = mgr.chunk_files_by_tokens(files)
    assert len(chunks) == 1
    assert "file.py" in chunks[0]["files"]


def test_chunk_files_by_tokens_splits_large_file():
    mgr = BatchProcessingManager(max_tokens=10)
    # Generate content larger than 10 tokens
    large_content = "\n".join([f"line_{i} = {i}" for i in range(50)])
    files = {"big.py": large_content}
    chunks = mgr.chunk_files_by_tokens(files)
    assert len(chunks) > 1


def test_chunk_files_by_tokens_multiple_files_grouped():
    mgr = BatchProcessingManager(max_tokens=100)
    files = {f"file_{i}.py": f"x_{i} = {i}" for i in range(5)}
    chunks = mgr.chunk_files_by_tokens(files)
    total_files = sum(len(c["files"]) for c in chunks)
    assert total_files == 5


@patch.dict(os.environ, {"ENABLE_BATCH_PROCESSING": "true"})
def test_should_use_batch_processing_true_when_large():
    mgr = BatchProcessingManager(max_tokens=1)
    assert mgr.should_use_batch_processing("a very long text that exceeds one token") is True


@patch.dict(os.environ, {"ENABLE_BATCH_PROCESSING": "true"})
def test_should_use_batch_processing_false_when_small():
    mgr = BatchProcessingManager(max_tokens=10000)
    assert mgr.should_use_batch_processing("short") is False


@patch.dict(os.environ, {"ENABLE_BATCH_PROCESSING": "false"})
def test_should_use_batch_processing_disabled():
    mgr = BatchProcessingManager(max_tokens=1)
    assert mgr.should_use_batch_processing("any text") is False


# ---------------------------------------------------------------------------
# LLM_Config
# ---------------------------------------------------------------------------

@patch('code_explainer.utils.utils.LLM')
def test_llm_config_valid_provider(mock_llm):
    mock_llm.return_value = MagicMock()
    result = LLM_Config(provider="openai", model="gpt-4", temperature=0.5, max_tokens=100, timeout=30.0)
    mock_llm.assert_called_once()
    call_kwargs = mock_llm.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4"
    assert call_kwargs["temperature"] == 0.5
    assert call_kwargs["max_tokens"] == 100


@patch('code_explainer.utils.utils.LLM')
def test_llm_config_invalid_provider(mock_llm):
    with pytest.raises(ValueError, match="Provider not supported"):
        LLM_Config(provider="unsupported", model="some-model")


@patch('code_explainer.utils.utils.LLM')
def test_llm_config_ollama_sets_base_url(mock_llm):
    mock_llm.return_value = MagicMock()
    LLM_Config(provider="ollama", model="llama3", base_url="http://localhost:11434")
    call_kwargs = mock_llm.call_args.kwargs
    assert call_kwargs["base_url"] == "http://localhost:11434"


@patch('code_explainer.utils.utils.LLM')
def test_llm_config_omits_none_params(mock_llm):
    mock_llm.return_value = MagicMock()
    LLM_Config(provider="openai", model="gpt-4")
    call_kwargs = mock_llm.call_args.kwargs
    assert "temperature" not in call_kwargs
    assert "max_tokens" not in call_kwargs
    assert "timeout" not in call_kwargs
