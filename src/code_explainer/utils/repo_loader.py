import os
import re
import json
from git import Repo
from git.exc import GitCommandError
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
import javalang
from javalang.parser import JavaSyntaxError
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class RepoLoader:
    def __init__(self, repo_path: str = "./repos/"):
        self.repo_path = repo_path
        self.local_repo_path = None

    def clone_repo(self, remote_repo_url):
        if not os.path.exists(self.repo_path):
            try:
                os.makedirs(self.repo_path)
            except OSError as e:
                error_message = (
                    f"Error creating repository directory '{self.repo_path}': {e}"
                )
                logging.error(error_message)
                print(error_message)
                return None

        match = re.search(r"([^/]+)\.git$", remote_repo_url)
        if not match:
            error_message = "Could not extract repository name from URL. Please check the URL format."
            logging.error(error_message)
            print(error_message)
            return None

        repo_name = match.group(1)
        self.local_repo_path = os.path.join(self.repo_path, repo_name)

        if os.path.exists(self.local_repo_path):
            logging.info(
                f"Local repo path '{self.local_repo_path}' already exists. Skipping cloning."
            )
            print("Local repo path already exists. Not cloning.")
            return self.local_repo_path
        else:
            logging.info(
                f"Cloning repo '{remote_repo_url}' to '{self.local_repo_path}'..."
            )
            try:
                Repo.clone_from(remote_repo_url, to_path=self.local_repo_path)
                return self.local_repo_path
            except GitCommandError as e:
                error_message = f"Error cloning repository '{remote_repo_url}' to '{self.local_repo_path}': {e}"
                logging.error(error_message)
                print(error_message)
                return None

    def parse_java_file(self, file_path: str):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()

            try:
                tree = javalang.parse.parse(code)
                info = []

                for path, node in tree:
                    if isinstance(node, javalang.tree.ClassDeclaration):
                        info.append(f"Class: {node.name}")
                    elif isinstance(node, javalang.tree.MethodDeclaration):
                        params = ", ".join(
                            [param.type.name for param in node.parameters]
                        )
                        info.append(f"Method: {node.name}({params})")
                    elif isinstance(node, javalang.tree.FieldDeclaration):
                        fields = [decl.name for decl in node.declarators]
                        info.append(f"Field(s): {', '.join(fields)}")

                return "\n".join(info) if info else code
            except JavaSyntaxError as e:
                warning_message = f"Failed to parse '{file_path}' with javalang due to syntax error: {e}. Falling back to raw text."
                logging.warning(warning_message)
                print(warning_message)
                return code  # Return the raw code even if parsing failed
            except Exception as e:
                warning_message = f"An unexpected error occurred while parsing '{file_path}' with javalang: {e}. Falling back to raw text."
                logging.warning(warning_message)
                print(warning_message)
                return code  # Return the raw code as a fallback

        except FileNotFoundError:
            error_message = f"Error: Java file not found at '{file_path}'."
            logging.error(error_message)
            print(error_message)
            return None
        except Exception as e:
            error_message = f"Failed to read Java file '{file_path}': {e}"
            logging.error(error_message)
            print(error_message)
            return None

    def load_repo(self, local_path: str = None, parser_threshold: int = 50):
        target_path = local_path or self.local_repo_path
        if not target_path:
            print("Error: No local repository path specified or cloned.")
            return None

        document_dicts = []

        # Load all files except .java with LanguageParser
        suffixes = [
            ".py",
            ".go",
            ".c",
            ".cpp",
            ".h",
            ".cs",
            ".php",
            ".js",
            ".ts",
            ".scala",
            ".rs",
            ".xml",
            ".gradle",
            ".properties",
        ]
        try:
            loader = GenericLoader.from_filesystem(
                target_path,
                glob="**/*",
                suffixes=suffixes,
                parser=LanguageParser(parser_threshold=parser_threshold),
                show_progress=True,
            )
            for doc in loader.load():
                document_dicts.append(
                    {
                        "source_filename": doc.metadata["source"],
                        "programming_language": doc.metadata.get("language", "unknown"),
                        "source_file_contents": doc.page_content,
                    }
                )
        except Exception as e:
            error_message = f"Error loading non-Java files: {e}"
            logging.error(error_message)
            print(error_message)
            # Decide if you want to continue loading Java files even if this fails
            # For now, let's continue.

        # Manually parse Java files with javalang
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith(".java"):
                    path = os.path.join(root, file)
                    parsed = self.parse_java_file(path)
                    if parsed is not None:
                        document_dicts.append(
                            {
                                "source_filename": path,
                                "programming_language": "java",
                                "source_file_contents": parsed,
                            }
                        )

        total_size = sum(sum(len(str(v)) for v in d.values()) for d in document_dicts)
        print(f"Total size of all documents: {total_size}")
        return json.dumps(document_dicts, ensure_ascii=False)
