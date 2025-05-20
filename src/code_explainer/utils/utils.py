import os
from typing import Any, Dict, List, Literal, Optional, Type, Union, cast
import time

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