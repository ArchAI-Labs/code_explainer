from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff
from crewai_tools import DirectoryReadTool, FileReadTool
from .tools.plantuml_tool import PlantUMLDiagramGeneratorTool
from .utils.utils import print_output, check_memory_dir, manage_output_dir, LLM_Config, ContextManager
from .utils.storage_config import (
    get_long_term_memory,
    get_short_term_memory,
    get_entity_memory,
)
import os
from pathlib import Path
from typing import Any, Dict, List
from dotenv import load_dotenv


load_dotenv()


@CrewBase
class CodeExplainer:
    """CodeExplainer crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    directory_read_tool = DirectoryReadTool(directory="./knowledge/plantuml_help")
    plant_uml_tool = PlantUMLDiagramGeneratorTool()
    file_read_tool = FileReadTool()

    local_dir = os.getenv("LOCAL_DIR")
    output_dir = os.getenv("OUTPUT_DIR")
    check_memory_dir()
    # manage_output_dir(output_dir=output_dir)

    llm = LLM_Config(
        provider=os.getenv("PROVIDER"),
        model=os.getenv("MODEL"),
        base_url=os.getenv("BASE_URL"),
        temperature=float(os.getenv("TEMPERATURE")),
        max_tokens=int(os.getenv("MAX_TOKENS")),
        timeout=float(os.getenv("TIMEOUT")),
        callbacks=[print_output],
    )

    ltm = get_long_term_memory()
    stm = get_short_term_memory()
    entity = get_entity_memory()

    # initialize context manager
    context_manager = ContextManager(
        max_tokens=int(os.getenv("CONTEXT_CHUNK_SIZE", "6000")),
        model=os.getenv("MODEL", "gpt-4")
    )

    @before_kickoff
    def prepare_inputs(self, inputs):
        """Prepares inputs and manages batching if necessary"""
        inputs["processed"] = True

        if "current_chunk" not in inputs:
            inputs["current_chunk"] = ""
        if "chunk_number" not in inputs:
            inputs["chunk_number"] = 1
        if "total_chunks" not in inputs:
            inputs["total_chunks"] = 1

        if "code_path" in inputs and inputs["code_path"]:
            files_content = self._read_codebase(inputs["code_path"])
            chunks = self.context_manager.chunk_files_by_tokens(files_content)
            if chunks:
                inputs["code_chunks"] = chunks
                inputs["total_chunks"] = len(chunks)
                print(f"Codice diviso in {len(chunks)} chunk per l'elaborazione")
        return inputs
    
    def _read_codebase(self, code_path: str) -> Dict[str, str]:
        """Reads all files in the codebase"""
        files_content = {}
        code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.go', '.rb', '.php'}
        
        path_obj = Path(code_path)
        if path_obj.is_file():
            if path_obj.suffix in code_extensions:
                with open(path_obj, 'r', encoding='utf-8', errors='ignore') as f:
                    files_content[str(path_obj)] = f.read()
        else:
            for file_path in path_obj.rglob('*'):
                if file_path.is_file() and file_path.suffix in code_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            files_content[str(file_path)] = f.read()
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
        
        return files_content

    @agent
    def software_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["software_analyst"],
            verbose=True,
            allow_delegation=False,
            max_iter=10,
            memory=True,
            llm=self.llm,
        )
    
    @agent
    def batch_coordinator(self) -> Agent:
        """Nuovo agente per coordinare l'analisi batch"""
        return Agent(
            config=self.agents_config["batch_coordinator"],
            verbose=True,
            allow_delegation=True,
            max_iter=5,
            memory=True,
            llm=self.llm,
        )

    @agent
    def sonar_quality_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["sonar_quality_analyst"],
            verbose=True,
            allow_delegation=False,
            max_iter=5,
            memory=True,
            llm=self.llm,
        )

    @agent
    def documentation_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["documentation_writer"],
            verbose=True,
            max_iter=5,
            allow_delegation=False,
            memory=True,
            llm=self.llm,
        )

    @agent
    def code_diagramming_agent(self):
        return Agent(
            config=self.agents_config["code_diagramming_agent"],
            verbose=True,
            max_iter=5,
            allow_delegation=False,
            memory=True,
            llm=self.llm,
            tools=[
                self.plant_uml_tool,
                self.file_read_tool,
                self.directory_read_tool,
            ],
        )
    
    @task
    def batch_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["batch_analysis_task"], agent=self.batch_coordinator()
        )
    
    @task
    def chunk_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["chunk_analysis_task"], agent=self.software_analyst()
        )

    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["analysis_task"], agent=self.software_analyst()
        )

    @task
    def code_quality_task(self) -> Task:

        return Task(
            config=self.tasks_config["code_quality_task"],
            agent=self.sonar_quality_analyst(),
        )

    @task
    def documentation_task(self) -> Task:
        context_tasks = [self.analysis_task()]

        sonar_url = os.getenv("SONARQUBE_URL")
        sonar_key = os.getenv("SONARQUBE_PROJECT")
        sonar_token = os.getenv("SONARQUBE_TOKEN")

        if sonar_url and sonar_key and sonar_token:
            context_tasks.append(self.code_quality_task())

        return Task(
            config=self.tasks_config["documentation_task"],
            agent=self.documentation_writer(),
            context=context_tasks,
            callback=print_output,
            human_input=False,
            async_execution=True,
            output_file=self.output_dir + "README.md",
        )

    @task
    def diagram_task(self) -> Task:
        return Task(
            config=self.tasks_config["diagram_task"],
            agent=self.code_diagramming_agent(),
            context=[self.analysis_task()],
            inputs={
                "output_format": "{output_format}",
                "diagram_type": "{diagram_type}",
            },
        )
    
    def process_in_batches(self, inputs: Dict[str, Any]) -> Any:
        """Main process for managing batch analysis"""
        if "code_chunks" not in inputs:
            # If there are no chunks, run normally.
            return self.crew().kickoff(inputs=inputs)
        
        chunks = inputs["code_chunks"]
        all_results = []
        
        print(f"Start work for {len(chunks)} chunk...")
        
        for i, chunk in enumerate(chunks):
            print(f"Working chunk {i+1}/{len(chunks)} ({chunk['file_count']} file, {chunk['total_tokens']} token)")
            
            # Create input for single chunk
            chunk_inputs = {
                **inputs,
                "current_chunk": chunk,
                "chunk_number": i + 1,
                "total_chunks": len(chunks)
            }
            
            # Chunk analysis
            chunk_result = self.crew().kickoff(inputs=chunk_inputs)
            all_results.append({
                "chunk_id": i + 1,
                "files": list(chunk["files"].keys()),
                "result": chunk_result
            })
        
        # Aggergation
        return self._aggregate_results(all_results, inputs)
    
    def _aggregate_results(self, results: List[Dict], inputs: Dict[str, Any]) -> str:
        """Aggregate the results of all chunks"""
        print("Aggregation of final results...")
        
        # create aggregation task
        aggregation_task = Task(
            config=self.tasks_config["diagram_task"],
            agent=self.batch_coordinator(),
        )
        
        mini_crew = Crew(
            agents=[self.batch_coordinator()],
            tasks=[aggregation_task],
            process=Process.sequential,
            verbose=True
        )
        
        return mini_crew.kickoff()

    @crew
    def crew(self) -> Crew:
        """Crea il crew CodeExplainer"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            long_term_memory=self.ltm,
            short_term_memory=self.stm,
            entity_memory=self.entity,
        )
