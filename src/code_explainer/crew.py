from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff
from crewai_tools import DirectoryReadTool, FileReadTool
from .tools.plantuml_tool import PlantUMLDiagramGeneratorTool
from .utils.utils import print_output, check_memory_dir, manage_output_dir, LLM_Config
from .utils.storage_config import (
    get_long_term_memory,
    get_short_term_memory,
    get_entity_memory,
)
import os
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

    @before_kickoff
    def prepare_inputs(self, inputs):
        # the inputs are processed
        inputs["processed"] = True
        return inputs

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
