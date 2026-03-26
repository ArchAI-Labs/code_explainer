import requests
import json
import base64
import logging

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 10


class SonarqubeTool:
    def __init__(
        self,
        sonarqube_url: str,
        project_key: str,
        api_token: str = None,
    ):
        """Retrieves project data from SonarQube using the API."""
        self.sonarqube_url = sonarqube_url
        self.project_key = project_key
        self.api_token = api_token

    def run(self) -> str:
        if not self.project_key or str(self.project_key).strip().lower() in ["", "none", "null"]:
            return ""

        headers = {}
        if self.api_token:
            base64_token = base64.b64encode(f"{self.api_token}:".encode()).decode("utf-8")
            headers["Authorization"] = f"Basic {base64_token}"

        try:
            measures_url = f"{self.sonarqube_url}/api/measures/component"
            params = {
                "component": self.project_key,
                "metricKeys": "bugs,vulnerabilities,code_smells,coverage,duplicated_lines_density",
            }
            measures_response = requests.get(measures_url, headers=headers, params=params, timeout=REQUEST_TIMEOUT)
            measures_response.raise_for_status()
            measures_data = measures_response.json().get("component", {}).get("measures", [])

            if not measures_data:
                return ""

            project_url = f"{self.sonarqube_url}/api/projects/search"
            project_params = {"q": self.project_key}
            project_response = requests.get(project_url, headers=headers, params=project_params, timeout=REQUEST_TIMEOUT)
            project_response.raise_for_status()
            project_info = project_response.json().get("components", [])

            results = {
                "project_info": project_info,
                "measures": {
                    measure["metric"]: measure["value"] for measure in measures_data
                },
            }

            return json.dumps(results, indent=4)

        except requests.exceptions.RequestException as e:
            logger.error(f"SonarQube connection failed for project '{self.project_key}': {e}")
            return ""

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from SonarQube for project '{self.project_key}': {e}")
            return ""
