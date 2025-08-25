import os
from typing import Any, Dict, List, Optional, Union
import time

import tiktoken

from crewai import LLM
from crewai.tasks.task_output import TaskOutput
import panel as pn


def print_output(output: TaskOutput, chat_interface=pn.chat.ChatInterface()):
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

def LLM_Config(provider:str, 
               model:str, 
               temperature:Optional[float] = None,
               max_tokens:Optional[int] = None, 
               timeout:Optional[Union[float, int]] = None, 
               base_url:Optional[str]=None, 
               callbacks:List[Any] = []):
    ## Manage LLMs
    if provider in ["openai", "google", "anthropic", "groq"]:
        llm = LLM(
            model=model,
            temperature=float(temperature),  # Adjust based on task
            max_tokens=int(max_tokens),  # Set based on output needs
            timeout=int(timeout),   # Longer timeout for complex tasks
            callbacks=callbacks,
        )
    elif provider == "ollama":
        llm = LLM(
            model=model,
            base_url=base_url,
            temperature=float(temperature),  # Adjust based on task
            max_tokens=int(max_tokens),  # Set based on output needs
            timeout=int(timeout),  # Longer timeout for complex tasks
            callbacks=callbacks,
        )
    else:
        raise ValueError("Provider not supported yet")
    return llm

class ContextManager:
    """Gestisce il contesto per evitare overflow"""
    
    def __init__(self, max_tokens=6000, model="gpt-4"):
        self.max_tokens = max_tokens
        try:
            self.encoder = tiktoken.encoding_for_model(model)
        except:
            self.encoder = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Conta i token in un testo"""
        return len(self.encoder.encode(str(text)))
    
    def chunk_files_by_tokens(self, files_content: Dict[str, str]) -> List[Dict[str, Any]]:
        """Divide i file in chunk basati sui token"""
        chunks = []
        current_chunk = {"files": {}, "total_tokens": 0, "file_count": 0}
        
        for file_path, content in files_content.items():
            file_tokens = self.count_tokens(content)
            
            # Se un singolo file supera il limite, lo dividiamo
            if file_tokens > self.max_tokens:
                file_chunks = self._chunk_single_file(file_path, content)
                chunks.extend(file_chunks)
                continue
            
            # Se aggiungendo questo file supereremmo il limite
            if current_chunk["total_tokens"] + file_tokens > self.max_tokens:
                if current_chunk["files"]:  # Se il chunk corrente non è vuoto
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
        current_chunk_lines = []
        current_tokens = 0
        
        for line in lines:
            line_tokens = self.count_tokens(line)
            
            if current_tokens + line_tokens > self.max_tokens:
                if current_chunk_lines:
                    chunk_content = '\n'.join(current_chunk_lines)
                    chunks.append({
                        "files": {f"{file_path}_part_{len(chunks)+1}": chunk_content},
                        "total_tokens": current_tokens,
                        "file_count": 1
                    })
                current_chunk_lines = [line]
                current_tokens = line_tokens
            else:
                current_chunk_lines.append(line)
                current_tokens += line_tokens
        
        if current_chunk_lines:
            chunk_content = '\n'.join(current_chunk_lines)
            chunks.append({
                "files": {f"{file_path}_part_{len(chunks)+1}": chunk_content},
                "total_tokens": current_tokens,
                "file_count": 1
            })
        
        return chunks

class BatchProcessingManager:
    """Manager for determining when to use batch processing"""
    
    def __init__(self, max_tokens:int=6000, model:str="gpt-4.1-mini"):
        self.max_tokens = max_tokens
        try:
            self.encoder = tiktoken.encoding_for_model(model)
        except:
            self.encoder = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoder.encode(str(text)))
    
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