# ArchAI - Your Code Explainer

<br>

![cover](https://github.com/ArchAI-Labs/code_explainer/blob/main/img/cover.png)

<br>

## Overview
The ArchAI project is designed to automatically analyze, document, and visualize codebases. It serves as a comprehensive tool for developers, architects, and stakeholders seeking to understand the structure, quality, and functionality of software projects. Unlike a simple code linter or documentation generator, the ArchAI leverages AI agents orchestrated by the CrewAI framework to provide a holistic view of a codebase. This includes cloning repositories, parsing code in multiple languages, generating PlantUML diagrams, and integrating with SonarQube for code quality analysis. The project aims to reduce the manual effort required to understand and maintain complex software systems by providing automated insights and documentation.

This repository contains the core logic for the ArchAI, defining the agents, tasks, and tools used in the analysis process. The modules within this repository are responsible for:

*   **Repository Loading:** Cloning and parsing source code files.
*   **Code Analysis:** Utilizing AI agents to understand the code's structure and functionality.
*   **Diagram Generation:** Creating visual representations of the codebase using PlantUML.
*   **Code Quality Assessment:** Integrating with SonarQube to gather code quality metrics.
*   **Crew Orchestration:** Managing the interactions between different AI agents to achieve the overall goal of code explanation and documentation.

## Installation

Ensure you have *Python >=3.10 <3.13* and *Git* installed on your system. 
This project uses [CrewAI](https://www.crewai.com/) (and [UV](https://docs.astral.sh/uv/) for dependency management and package handling) offering a seamless setup and execution experience.

First, install CrewAI:

```bash
pip install crewai crewai-tools
```

Optional, if you haven't already and is required, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Configure environment variables

**Create an `.env` file in the project root (use `.env.example` as template) and define the following variables:**

* `REPOSITORY_URL`: The URL of the Git repository to analyze.
* `LOCAL_DIR`: The local directory where the repository will be cloned.
* `OUTPUT_DIR`: The directory where the generated documentation and diagrams will be saved.
* `DIAGRAM_TYPE`: The type of diagram to generate (e.g., `component`, `class`, `sequence`, `all`).
* `DIAGRAM_FORMAT`: The output format for the diagrams (e.g., `svg`, `uml`, `png`).
* `SONARQUBE_URL`: The URL of the SonarQube server (optional).
* `SONARQUBE_PROJECT`: The SonarQube project key (optional).
* `SONARQUBE_TOKEN`: The SonarQube API token (optional).
*	`PROVIDER`: The LLM provider (e.g., `openai`, `google`, `ollama`).
*	`MODEL`: The LLM model to use (e.g., `gpt-4`, `gemini-1.5-pro`, `llama2`).
*	`GEMINI_API_KEY` or `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`: The API KEY to use (follow the `.env.example`).
*	`BASE_URL`: The LLM base URL (optional, required for ollama).
*	`TEMPERATURE`: The LLM temperature (optional).
*	`MAX_TOKENS`: The LLM max tokens (optional).
*	`TIMEOUT`: The LLM timeout (optional).
*	`QDRANT_MODE`: The Qdrant mode (e.g., `memory`, `cloud`, `docker`).
*	`QDRANT_HOST`: The Qdrant host (required for cloud mode).
*	`QDRANT_API_KEY`: The Qdrant API key (required for cloud mode).
*	`QDRANT_URL`: The Qdrant URL (required for docker mode).
*	`EMBEDDER`: The embedding model to use (e.g., `jinaai/jina-embeddings-v2-base-code`).

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ streamlit run ./streamlit_app.py
```

This command initializes the ArchAI Crew, assembling the agents and assigning them tasks as defined in your configuration.

Follow the instructions.

Enter the git repo to clone:

```bash
Please enter the GitHub repository URL (i.e. 'https://github.com/yourprofile/yourrepo.git'): https://github.com/mygitprofile/myrepo.git
```

### Qdrant Configuration

<br>

![qdrant](https://github.com/qdrant/qdrant-client/raw/master/docs/images/try-develop-deploy.png)

<br>

1. **memory**: In memory is default choiche to try the app.

2. **cloud**: You need an account on [Qdrant Cloud](https://login.cloud.qdrant.io/), then insert your `QDRANT_HOST` and `QDRANT_API_KEY` in `.env` file and set `QDRANT_MODE=cloud`.

3. **docker**: Before to start the crewai app you need to install Docker. Then open a terminal and:
  - First step is to download the latest Qdrant image from Dockerhub:

```bash
docker pull qdrant/qdrant
```

  - Second step, go into the project folder (if you created the `memory` folder go into), run the service:

```bash
docker run -p 6333:6333 -p 6334:6334 -v "$(pwd)/qdrant_storage:/qdrant/storage:z" qdrant/qdrant
```

  - Third step, open another terminal and run the project:

```bash
$ streamlit run ./streamlit_app.py
```

### Ollama

Ollama is an open-source app that lets you run, create, and share large language models locally with a command-line interface on MacOS ,Linux and Windows.
**If you want to use [Ollama](https://ollama.com/) the first step is to download it.**
Ollama has access to a wide range of LLMs directly available from their library, which can be downloaded using a single command. Once downloaded, you can start using it through a single command execution.

After the installation You have the option to use the default model save path, typically located at:

```bash
C:\Users\your_user\.ollama
```

Then download the model from the command prompt (e.g. phi3):

```bash
$ ollama pull llama3
```

Now you can modify your `.env` file to use Ollama model.

Make sure Ollama is running in the background:

```bash
$ ollama serve
```

***N.B. Most likely, local models will need a GPU in order not to have very long response times and go into timeout.***

## Understanding Your Crew

The ArchAI Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

### Technology Stack
The project employs a diverse set of technologies, frameworks, and libraries that enhance its functionality and capability. 

- **Language:** Python - The primary programming language used to build the application.
  
- **Frameworks:** 
  - [crewAI](https://crewai.com) - This framework underpins the orchestration of agents and processes, allowing for effective management of tasks and facilitating collaboration between different components of the system.
  - [Qdrant](https://qdrant.tech/) - Qdrant is the most advanced vector database with highest RPS, minimal latency, fast indexing, high control with accuracy, and so much more.

- **Libraries:**
  - **dotenv:** Utilized for managing environment variables, extracting configuration data from a `.env` file, which aids in flexible deployment.
  - **GitPython:** A library that enables interaction with Git repositories, used in the code’s Git utility handler `GitUtils`.
  - **Langchain:** Employed for document loading capabilities, managing the parsing of different language-specific code files into usable formats.
  - **PlantWeb:** This library renders PlantUML diagrams, converting textual representation of diagrams into SVG files that can be easily integrated and displayed.

- **Tools:** 
  - **DirectoryReadTool:** Reads directory contents for file analysis.
  - **FileReadTool:** A tool that reads the content of files for further processing.
  - **PlantUMLDiagramGeneratorTool:** A custom tool specialized in generating SVG diagrams based on PlantUML formatted text.
  - **SonarqubeTool:** A tool to retrieve information from SonarQube.

### Module Usage

*   **`RepoLoader`:** This module is responsible for cloning the Git repository and loading the source code files. To use it in an external project, you can instantiate the `RepoLoader` class with the desired repository path and then call the `clone_repo` method with the repository URL. After cloning, use the `load_repo` method to parse the code and return a JSON string containing the source code and metadata.

*   **`PlantUMLDiagramGeneratorTool`:** This module generates diagrams from PlantUML code. It can be integrated into other projects as a tool for visualizing code structure and relationships. The `PlantUMLDiagramGeneratorTool` class takes PlantUML code as input and generates diagrams in SVG, PNG, or UML format, either locally or by using the PlantUML server.

*   **`SonarqubeTool`:** This module retrieves project data from SonarQube, providing insights into code quality metrics. To use it, you need to provide the SonarQube URL, project key, and API token. The `run` method returns a JSON string containing the SonarQube data.

*   **`CodeExplainer`:** This module orchestrates the entire code explanation process. It defines the agents, tasks, and workflow for analyzing and documenting the codebase. To use it, you need to configure the agents and tasks in YAML files and then instantiate the `CodeExplainer` class. The `crew` method returns a CrewAI `Crew` object, which can be kicked off with the necessary inputs.

<br>

![components](https://github.com/ArchAI-Labs/code_explainer/blob/main/img/component_diagram.png)

<br>

### Directory Structure
The project adheres to a structured directory layout, enabling ease of navigation and management of files and resources:

```
├── img/ - Contains images for the README.
│   ├── cover.png
│   ├── componets.png
│   ├── class.png
├── knowledge/
│   ├── plantuml_help/ - Contains PlantUML documentation.
├── src/
│   ├── code_explainer/
│   │   ├── crew.py  - Core CodeExplainer class and CrewAI integration
│   │   ├── main.py - Main entry point for running the tool
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   └── plantuml_tool.py - PlantUML diagram generation tool
│   │   └── utils/
│   │       ├── repo_loader.py - Repository loading and parsing utilities
│   │       ├── sonarqhube_tool.py - Integrates with SonarQube for code quality analysis.
│   │       ├── storage_config.py - Configuration for long-term, short-term, and entity memory
│   │       ├── storage_qdrant.py - Extends Storage to handle embeddings for memory entries using Qdrant and FastEmbed.
│   │       └── utils.py       - Helper functions
│   └── ...
├── tests/
│   ├── test_crew.py - Unit tests for the CodeExplainer class
│   ├── test_gitutils.py - Unit tests for Git-related utilities
│   └── ...
└── config/
    ├── agents.yaml - YAML configuration for agents
    └── tasks.yaml - YAML configuration for tasks
```

## Functional Analysis

<br>

![sequence](https://github.com/ArchAI-Labs/code_explainer/blob/main/img/sequence_diagram.png)

<br>

### 1. Main Responsibilities of the System

The primary responsibility of the ArchAI is to automate the process of understanding and documenting codebases. It orchestrates a series of tasks, including:

*   **Code Acquisition:** Cloning remote Git repositories or loading local code.
*   **Code Parsing:** Analyzing source code files to extract relevant information.
*   **Diagram Generation:** Creating visual representations of the code's structure and relationships.
*   **Code Quality Analysis:** Integrating with SonarQube to assess code quality.
*   **Documentation Generation:** Producing human-readable documentation based on the analysis.

The system provides foundational services for code understanding by automating the extraction of key information and presenting it in a structured and accessible format.

### 2. Problems the System Solves

The ArchAI addresses several key challenges in software development:

*   **Onboarding new developers:** Reduces the time required for new team members to understand a codebase.
*   **Understanding legacy code:** Provides insights into the structure and functionality of older systems.
*   **Maintaining code quality:** Integrates with SonarQube to identify and track code quality issues.
*   **Generating documentation:** Automates the creation of documentation, reducing the manual effort required.
*   **Visualizing complex systems:** Creates diagrams to help developers understand the relationships between different parts of the code.

The system meets these needs by providing automated analysis, documentation, and visualization capabilities.

### 3. Interaction of Modules and Components

The ArchAI utilizes a CrewAI framework to orchestrate the interactions between different modules and components. The `CodeExplainer` class defines the agents, tasks, and workflow for the analysis process. The agents communicate and collaborate through tasks, with each agent responsible for a specific aspect of the analysis.

The `RepoLoader` module provides code to the agents. The `SonarQubeTool` fetches code quality metrics, which are then used by the agents to generate documentation and diagrams. The `PlantUMLDiagramGeneratorTool` generates diagrams based on the analysis performed by the agents.

### 4. User-Facing vs. System-Facing Functionalities

The ArchAI provides both user-facing and system-facing functionalities:

*   **User-Facing:**
    *   **Generated Documentation:** The primary user-facing output is the generated documentation, which provides a human-readable description of the codebase.
    *   **Diagrams:** The generated diagrams provide a visual representation of the code's structure and relationships.
*   **System-Facing:**
    *   **Code Parsing:** The code parsing functionality is used internally by the agents to analyze the code.
    *   **SonarQube Integration:** The SonarQube integration is used to gather code quality metrics.
    *   **CrewAI Orchestration:** The CrewAI framework is used to manage the interactions between the different agents.

The user-facing functionalities provide value to developers and stakeholders by providing insights into the codebase, while the system-facing functionalities enable the automated analysis and documentation process.

## Architectural Patterns and Design Principles
The design of the ArchAI project incorporates several architectural patterns that contribute to its robustness and maintainability.

1. **Decorator Pattern**: This pattern is utilized extensively in defining agents and tasks, streamlining the process of organizing tasks into actionable units with clear responsibilities.

2. **Separation of Concerns**: Each class and module within the project bears a specific responsibility, thus enhancing modularity, which simplifies debugging and future developments.

3. **Configuration Management**: The application’s architecture leverages the `dotenv` library for managing configurations dynamically, which reduces hardcoding and allows for easier configuration changes in different environments.

4. **Command Pattern**: The execution of tasks through defined interfaces promotes clarity; agents follow commands received via task definitions, thereby maintaining structured interactions.

5. **Sequential Processing**: The project ensures a controlled execution flow through the sequential management of tasks, aiding in task dependency management where analysis needs to be completed before documentation and diagram generation begins.

## Weaknesses and Areas for Improvement
The following items represent potential areas for improvement and future development, framed as actionable TODOs:

*    **Improve Documentation Generation:** Enhance the quality and completeness of the generated documentation.
*    **Add More Diagram Types:** Expand the `PlantUMLDiagramGeneratorTool` to support additional diagram types beyond class, component, and sequence diagrams.
*    **Enhance Test Coverage:** Increase test coverage for the core modules, particularly the `RepoLoader`, `PlantUMLDiagramGeneratorTool`, and `SonarqubeTool` classes.
*    **Improve Configuration Management:** Implement a more robust configuration management system, potentially using a library like `ConfigParser` or `Hydra`.
*    **Add Support for More Languages:** Expand the code parsing functionality to support additional programming languages.
*    **Implement a UI:** Develop a user interface for the ArchAI to make it more accessible to non-technical users.
*    **Refactor Complex Modules:** Identify and refactor complex modules to improve maintainability and readability.
*    **Address High-Priority Security Vulnerabilities:** If SonarQube reports high-priority security vulnerabilities, address them promptly.

Overall, the ArchAI project provides a structured and detailed approach to codebase analysis and documentation, while also presenting a solid foundation for further improvements that could enhance its usability and robustness.

## Further Areas of Investigation

The following areas warrant further investigation and analysis:

*   **Performance Bottlenecks:** Identify and address potential performance bottlenecks, particularly in the code parsing and diagram generation processes.
*   **Scalability Considerations:** Evaluate the scalability of the ArchAI and identify potential limitations.
*   **Integration with External Systems:** Explore potential integrations with other external systems, such as code review tools or CI/CD pipelines.
*   **Advanced Features:** Research and implement advanced features, such as code smell detection or automated refactoring suggestions.
*   **Codebase Analysis:** Perform a deeper analysis of the codebase to identify areas with significant code smells or low test coverage.

## crewAI Support

For support, questions, or feedback regarding crewAI.
- Visit crewAI [documentation](https://docs.crewai.com)
- Reach out to crewAI through their [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join crewAI Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with crewAI docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.

## Attribution

Generated with the support of [ArchAI](https://github.com/ArchAI-Labs/code_explainer), an automated documentation system.
