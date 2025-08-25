#!/usr/bin/env python
import os
import warnings

from code_explainer.crew import CodeExplainer
from .utils.repo_loader import RepoLoader

from .utils.sonarqhube_tool import SonarqubeTool

from .utils.utils import BatchProcessingManager

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
    
    context_chunk_size = int(os.getenv("CONTEXT_CHUNK_SIZE", "6000"))
    model_tiktoken=os.getenv("TIKTOKEN_MODEL", "gpt-4.1-mini")
    print("\n🤖 Determining processing strategy...")
    batch_manager = BatchProcessingManager(
        max_tokens=context_chunk_size,
        model=model_tiktoken
    )
    use_batch_processing = batch_manager.should_use_batch_processing(repo_to_load)

    inputs = {
        "repository_url": repository_url,
        "repo": repo_to_load,
        "code_path": os.getenv("LOCAL_DIR"),
        "diagram_type": diagram_type,
        "output_format": output_format,
        "sonarqube_json": sonarqube_json,
    }
    try:
        print(f"\n🏗️  Initializing CodeExplainer crew...")
        code_explainer = CodeExplainer()
        
        # Execute analysis
        print(f"\n🔄 Starting analysis...")
        print("=" * 50)
        
        if use_batch_processing:
            print("📊 Processing Mode: BATCH PROCESSING")
            print("   - Large codebase will be divided into manageable chunks")
            print("   - Each chunk will be analyzed independently")  
            print("   - Results will be aggregated into a comprehensive report")
            print()
            
            result = code_explainer.process_in_batches(inputs)
        else:
            print("📊 Processing Mode: STANDARD PROCESSING")
            print("   - Codebase will be analyzed in a single pass")
            print()
            
            result = code_explainer.crew().kickoff(inputs=inputs)
        
        print("\n" + "=" * 50)
        print("✅ Analysis completed successfully!")
        print(f"📄 Results have been generated and saved to: {os.getenv('OUTPUT_DIR', './output/')}")
        
        # Optional: Print summary of results
        if isinstance(result, str) and len(result) > 200:
            print(f"\n📋 Analysis Summary (first 200 characters):")
            print(f"   {result[:200]}...")
        
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
        print(f"❌ Analysis Error: {e}")
        print("\n🔄 Attempting recovery strategies...")
        
        # Recovery strategy: Force batch processing if context error
        if any(keyword in str(e).lower() for keyword in ["context", "token", "length", "size"]):
            print("   Issue appears to be context-related, trying batch processing...")
            try:
                code_explainer = CodeExplainer()
                result = code_explainer.process_in_batches(inputs)
                print("✅ Recovery successful with batch processing!")
                return result
            except Exception as recovery_error:
                print(f"❌ Recovery failed: {recovery_error}")
                raise Exception(f"Analysis failed even with batch processing: {recovery_error}")
        else:
            print("   No recovery strategy available for this error type.")
            raise Exception(f"An error occurred while running the crew: {e}")
