from typing import Type, Literal
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import os
import requests
import time
import re
from plantweb.render import render

class PlantUMLDiagramGeneratorInput(BaseModel):
    text: str = Field(..., description="PlantUML diagram content.")
    output_format: Literal["uml", "svg", "png"] = Field("svg", description="Output format: 'uml' for the code, 'svg' or 'png' for the image.")
    diagram_type: Literal["class", "component", "sequence", "all"] = Field(..., description="Type of diagram: 'class', 'component', 'sequence', or 'all' for multiple diagrams.")


class PlantUMLDiagramGeneratorTool(BaseTool):
    name: str = "PlantUML Diagram Generator Tool"
    description: str = "Accepts text that represents a diagram in PlantUML format and generates a SVG, PNG, or UML file from it."
    args_schema: Type[BaseModel] = PlantUMLDiagramGeneratorInput

    def _run(self, text: str, output_format: str = "svg", output_dir: str = os.getenv("OUTPUT_DIR", "output"), diagram_type: str = "class") -> str:
        os.makedirs(output_dir, exist_ok=True)

        output_format = output_format.lower().strip()
        diagram_type = diagram_type.lower().strip()
        text = text.strip()

        print(f"DEBUG: output_format={output_format}, diagram_type={diagram_type}")

        if diagram_type == "all":
            diagrams = self._split_diagrams(text)
            paths = []

            for dtype, diagram_text in diagrams.items():
                print(f"DEBUG: Generating diagram {dtype} in format {output_format}")
                file_path = self._generate_diagram(diagram_text, output_format, output_dir, dtype)
                paths.append(file_path)

            print(f"All diagrams generated successfully: {paths}")
            return ", ".join(paths)

        else:
            print(f"DEBUG: Generating single diagram of type {diagram_type}")
            file_path = self._generate_diagram(text, output_format, output_dir, diagram_type)
            return file_path

    def _generate_diagram(self, diagram_text: str, output_format: str, output_dir: str, diagram_type: str) -> str:
        # Prepara contenuto
        if not diagram_text.startswith("@startuml"):
            diagram_text = "@startuml\n" + diagram_text
        if not diagram_text.endswith("@enduml"):
            diagram_text += "\n@enduml"

        if "!theme cerulean" not in diagram_text:
            diagram_text = diagram_text.replace("@startuml", "@startuml\n!theme cerulean", 1)

        diagram_name = f"{diagram_type}_diagram.{output_format}"
        file_path = os.path.join(output_dir, diagram_name)

        try:
            if output_format == "uml":
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(diagram_text + "\n")
                print(f"UML file saved successfully at: {file_path}")
                return file_path

            elif output_format in ["svg", "png"]:
                print(f"Attempting local rendering with PlantUML for {diagram_type} diagram...")
                output = render(diagram_text, engine="plantuml", format=output_format, cacheopts={"use_cache": False})
                with open(file_path, "wb") as file:
                    file.write(output[0])
                print(f"{output_format.upper()} file saved successfully at: {file_path}")
                return file_path

            else:
                raise ValueError(f"Unsupported output format: {output_format}")

        except Exception as e:
            print(f"Local rendering failed: {e}. Falling back to PlantUML server...")
            return self._fetch_from_plantuml_server(diagram_text, output_format, output_dir, diagram_type)

    def _fetch_from_plantuml_server(self, uml_code: str, output_format: str, output_dir: str, diagram_type: str,
                                    max_retries: int = 5, initial_delay: float = 1) -> str:
        PLANTUML_SERVER = f"http://www.plantuml.com/plantuml/{output_format}"
        diagram_name = f"{diagram_type}_diagram.{output_format}"
        file_path = os.path.join(output_dir, diagram_name)

        if "!theme cerulean" not in uml_code:
            uml_code = uml_code.replace("@startuml", "@startuml\n!theme cerulean", 1)

        for attempt in range(max_retries):
            try:
                response = requests.post(PLANTUML_SERVER, data=uml_code.encode("utf-8"))
                response.raise_for_status()
                with open(file_path, "wb") as file:
                    file.write(response.content)
                print(f"Diagram successfully saved at {file_path} (PlantUML Server - Attempt {attempt + 1})")
                return file_path

            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                print(f"HTTP Error {status_code} (Attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    print(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    raise ValueError(f"Failed to render diagram after {max_retries} attempts. Last error: {e}")

            except requests.exceptions.RequestException as e:
                print(f"Request Exception (Attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    print(f"Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                else:
                    raise ValueError(f"Failed to render diagram after {max_retries} attempts. Last error: {e}")

    def _split_diagrams(self, text: str) -> dict:
        sections = re.split(r"^##\s+", text, flags=re.MULTILINE)
        diagrams = {}

        for section in sections:
            if section.strip():
                lines = section.strip().splitlines()
                title = lines[0].strip().lower().replace(" diagram", "")
                diagram_text = "\n".join(lines[1:]).strip()
                diagrams[title] = diagram_text

        return diagrams
