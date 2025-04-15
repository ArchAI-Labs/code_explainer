#!/usr/bin/env python
import os
import warnings

from code_explainer.crew import CodeExplainer
from .utils.repo_loader import RepoLoader

from .utils.sonarqhube_tool import SonarqubeTool

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information


def run():
    """
    Run the crew.
    """
    git_tools = RepoLoader(repo_path=os.getenv("LOCAL_DIR"))

    repository_url = os.getenv("REPOSITORY_URL")
    local_path = os.getenv("LOCAL_PATH")
    if repository_url:
        git_tools.clone_repo(repository_url)
        repo_to_load = git_tools.load_repo()
    elif not repository_url and local_path:
        repo_to_load = git_tools.load_repo(local_path=local_path)
    else:
        raise ValueError("Set a Repository URL or Local Path to your code")

    diagram_type = os.getenv("DIAGRAM_TYPE")

    if diagram_type not in ["component", "class", "sequence", "all"]:
        raise ValueError("diagram type must be component, class, sequence or all")

    output_format = os.getenv("DIAGRAM_FORMAT")

    if output_format not in ["svg", "uml", "png"]:
        raise ValueError("diagram output must be 'svg' or 'uml' or 'png'.")

    sonarqube_url = os.getenv("SONARQUBE_URL")
    project_key = os.getenv("SONARQUBE_PROJECT")
    api_token = os.getenv("SONARQUBE_TOKEN")

    if sonarqube_url and project_key and api_token:
        sonarqube_json = SonarqubeTool(
            sonarqube_url=sonarqube_url, project_key=project_key, api_token=api_token
        ).run()
    else:
        sonarqube_json = {}

    inputs = {
        "repository_url": repository_url,
        "repo": repo_to_load,
        "diagram_type": diagram_type,
        "output_format": output_format,
        "sonarqube_json": sonarqube_json,
    }
    try:
        CodeExplainer().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
