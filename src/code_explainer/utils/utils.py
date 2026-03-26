import os
from typing import Any, Dict, List, Optional, Union
import time

import tiktoken

from crewai import LLM
from crewai.tasks.task_output import TaskOutput
import panel as pn


def print_output(output: TaskOutput, chat_interface=None):
    if chat_interface is None:
        chat_interface = pn.chat.ChatInterface()
    message = output.raw
    chat_interface.send(message, user=output.agent, respond=False)


def check_memory_dir(memory_dir: str = "./memory"):
    if not os.path.exists(memory_dir):
        os.makedirs(memory_dir)
    else:
        print("memory exists")

def manage_output_dir(output_dir: str):
    """
    Manages the output directory, renaming it if it already exists,
    or creating it if it doesn't.
    """
    if os.path.exists(output_dir):
        print(f"Output folder '{output_dir}' already exists")
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        new_output_dir = f"{output_dir[:-1]}_old_{timestamp}"
        try:
            os.rename(output_dir, new_output_dir)
            print(f"Automatically renamed output folder to: {new_output_dir}")
        except Exception as e:
            raise ValueError(f"Error renaming output directory: {e}")
    try:
        os.makedirs(output_dir)
        print("Output folder created")
    except Exception as e:
        raise ValueError(f"Error creating output directory: {e}")


def _get_tokenizer(model: str) -> tiktoken.Encoding:
    try:
        return tiktoken.encoding_for_model(model)
    except Exception:
        return tiktoken.get_encoding("cl100k_base")


def LLM_Config(provider: str,
               model: str,
               temperature: Optional[float] = None,
               max_tokens: Optional[int] = None,
               timeout: Optional[Union[float, int]] = None,
               base_url: Optional[str] = None,
               callbacks: Optional[List[Any]] = None):
    callbacks = callbacks or []
    kwargs: Dict[str, Any] = dict(model=model, callbacks=callbacks)

    if temperature is not None:
        kwargs["temperature"] = float(temperature)
    if max_tokens is not None:
        kwargs["max_tokens"] = int(max_tokens)
    if timeout is not None:
        kwargs["timeout"] = float(timeout)

    if provider not in ["openai", "google", "anthropic", "groq", "ollama"]:
        raise ValueError("Provider not supported yet")

    if provider == "ollama" and base_url is not None:
        kwargs["base_url"] = base_url

    return LLM(**kwargs)


class BatchProcessingManager:
    """Manages token counting, chunking, and batch processing decisions."""

    def __init__(self, max_tokens: int = 6000, model: str = "gpt-4.1-mini"):
        self.max_tokens = max_tokens
        self.encoder = _get_tokenizer(model)

    def count_tokens(self, text: str) -> int:
        return len(self.encoder.encode(str(text)))

    def chunk_files_by_tokens(self, files_content: Dict[str, str]) -> List[Dict[str, Any]]:
        """Divide i file in chunk basati sui token"""
        chunks = []
        current_chunk: Dict[str, Any] = {"files": {}, "total_tokens": 0, "file_count": 0}

        for file_path, content in files_content.items():
            file_tokens = self.count_tokens(content)

            if file_tokens > self.max_tokens:
                chunks.extend(self._chunk_single_file(file_path, content))
                continue

            if current_chunk["total_tokens"] + file_tokens > self.max_tokens:
                if current_chunk["files"]:
                    chunks.append(current_chunk)
                current_chunk = {"files": {}, "total_tokens": 0, "file_count": 0}

            current_chunk["files"][file_path] = content
            current_chunk["total_tokens"] += file_tokens
            current_chunk["file_count"] += 1

        if current_chunk["files"]:
            chunks.append(current_chunk)

        return chunks

    def _chunk_single_file(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Divide un singolo file troppo grande in chunk"""
        lines = content.split('\n')
        chunks = []
        current_lines: List[str] = []
        current_tokens = 0

        for line in lines:
            line_tokens = self.count_tokens(line)

            if current_tokens + line_tokens > self.max_tokens:
                if current_lines:
                    chunks.append({
                        "files": {f"{file_path}_part_{len(chunks) + 1}": '\n'.join(current_lines)},
                        "total_tokens": current_tokens,
                        "file_count": 1,
                    })
                current_lines = [line]
                current_tokens = line_tokens
            else:
                current_lines.append(line)
                current_tokens += line_tokens

        if current_lines:
            chunks.append({
                "files": {f"{file_path}_part_{len(chunks) + 1}": '\n'.join(current_lines)},
                "total_tokens": current_tokens,
                "file_count": 1,
            })

        return chunks

    def should_use_batch_processing(self, repo_content: str) -> bool:
        """Determine if batch processing is needed based on content size"""
        token_count = self.count_tokens(repo_content)
        batch_enabled = os.getenv("ENABLE_BATCH_PROCESSING", "true").lower() == "true"

        print(f"Repository token count: {token_count:,}")
        print(f"Max tokens per request: {self.max_tokens:,}")
        print(f"Batch processing enabled: {batch_enabled}")

        if token_count > self.max_tokens:
            if batch_enabled:
                print("🔄 Large repository detected - batch processing will be used")
                return True
            else:
                print("⚠️  Large repository detected but batch processing is disabled")
                print("    This may cause context overflow errors")
                return False
        else:
            print("✅ Repository size is manageable - using standard processing")
            return False


# Backward-compatible alias
ContextManager = BatchProcessingManager
