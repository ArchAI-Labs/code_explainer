import streamlit as st
import os
from dotenv import load_dotenv
import re
from src.code_explainer.utils.utils import manage_output_dir

load_dotenv()

# Percorso relativo all'immagine del logo
LOGO_PATH = "img/cover.png"

# Colori personalizzati
BACKGROUND_COLOR = "#F3EDE6"
PRIMARY_COLOR = "#35346A"
TEXT_COLOR = PRIMARY_COLOR

# Imposta lo stile dell'app
st.markdown(
    f"""
    <style>
        body {{
            background-color: {BACKGROUND_COLOR};
            color: {TEXT_COLOR};
        }}
        .stApp {{
            background-color: {BACKGROUND_COLOR};
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: {PRIMARY_COLOR};
        }}
        .st-bb {{ 
            border-color: {PRIMARY_COLOR};
            color: {TEXT_COLOR};
        }}
        .st-c8, .st-c7, .st-b6, .st-b5, .st-b4, .st-b3, .st-b2, .st-b1, .st-b0 {{
            border-color: {PRIMARY_COLOR} !important;
            box-shadow: none !important;
            color: {TEXT_COLOR};
        }}
        .stButton > button {{
            color: white;
            background-color: {PRIMARY_COLOR};
            border-color: {PRIMARY_COLOR};
        }}
        .stButton > button:hover {{
            background-color: #585696;
            border-color: #585696;
        }}
        .streamlit-expanderHeader {{
            color: {PRIMARY_COLOR};
        }}
        input {{
            color: {TEXT_COLOR} !important;
        }}
        textarea {{
            color: {TEXT_COLOR} !important;
        }}
        select {{
            color: {TEXT_COLOR} !important;
        }}
        .markdown-box {{
                border: 2px solid {PRIMARY_COLOR};
                padding: 10px;
                border-radius: 5px;
                background-color: white;
                overflow-x: auto;
        }}
        .tree-output {{
            background-color: white;
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            font-family: monospace;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


# Funzione per eseguire il crew
def run_crew(repository_url, local_path, diagram_type, output_format, sonarqube_url, sonarqube_project, sonarqube_token,
             llm_config, local_dir, output_dir, chunking_config):
    os.environ["PROVIDER"] = llm_config["provider"]
    os.environ["MODEL"] = llm_config["model"]
    os.environ["BASE_URL"] = llm_config["base_url"]
    os.environ["TEMPERATURE"] = str(llm_config["temperature"])
    os.environ["MAX_TOKENS"] = str(llm_config["max_tokens"])
    os.environ["TIMEOUT"] = str(llm_config["timeout"])
    os.environ["CONTEXT_CHUNK_SIZE"] = str(chunking_config["chunk_size"])
    os.environ["TIKTOKEN_MODEL"] = chunking_config["tokenizer_model"]
    os.environ["REPOSITORY_URL"] = repository_url if repository_url else ""
    os.environ["LOCAL_PATH"] = local_path if local_path else ""
    os.environ["DIAGRAM_TYPE"] = diagram_type
    os.environ["DIAGRAM_FORMAT"] = output_format
    os.environ["SONARQUBE_URL"] = sonarqube_url if sonarqube_url else ""
    os.environ["SONARQUBE_PROJECT"] = sonarqube_project if sonarqube_project else ""
    os.environ["SONARQUBE_TOKEN"] = sonarqube_token if sonarqube_token else ""
    os.environ["LOCAL_DIR"] = local_dir
    os.environ["OUTPUT_DIR"] = output_dir

    manage_output_dir(output_dir=output_dir)

    # Esegui la tua logica di crew
    try:
        from src.code_explainer.main import run as run_crew_logic
        run_crew_logic()

        st.success("Crew successfully executed!")
        diagram_path = f"{os.path.join(output_dir, 'diagram')}.{output_format}"
        documentation_path = os.path.join(output_dir, "README.md")
        return documentation_path, diagram_path
    except ImportError:
        st.error(
            "Error: Unable to import 'run' function from src.code_explainer.main.py. Make sure the path is correct.")
        return None, None
    except Exception as e:
        st.error(f"An error occurred during the execution of the crew: {e}")
        return None, None


st.image(LOGO_PATH, width=200)
st.title("ArchAI")
st.subheader("Your Code Explainer Assistant")

# Barra laterale per la configurazione
with st.sidebar:
    st.subheader("Directory Setup")
    local_dir = st.text_input("Local Working Path:", value=os.getenv("LOCAL_DIR", "./"))
    output_dir = st.text_input("Output Directory Path:", value=os.getenv("OUTPUT_DIR", "output/"))

    st.subheader("LLM Setup")
    llm_provider = st.selectbox("Provider:", ["anthropic", "google", "groq", "ollama", "openai"], index=1)
    llm_model = st.text_input("Model:", value=os.getenv("MODEL", ""))
    llm_base_url = st.text_input("Base URL (optional):", value=os.getenv("BASE_URL", ""))
    default_temperature = float(os.getenv("TEMPERATURE", "0.7"))
    llm_temperature = st.slider("Temperature:", min_value=0.0, max_value=1.0, value=default_temperature, step=0.01)
    llm_max_tokens = st.number_input("Max Tokens:", min_value=1, value=int(os.getenv("MAX_TOKENS", "1000")), step=100)
    default_timeout = float(os.getenv("TIMEOUT", "60.0"))
    llm_timeout = st.number_input("Timeout (seconds):", min_value=1.0, value=default_timeout, step=1.0)

    llm_config = {
        "provider": llm_provider,
        "model": llm_model,
        "base_url": llm_base_url,
        "temperature": llm_temperature,
        "max_tokens": llm_max_tokens,
        "timeout": llm_timeout,
    }

    st.subheader("Chunking Setup")
    context_chunk_size = st.number_input("Max Tokens:", min_value=100, value=int(os.getenv("CONTEXT_CHUNK_SIZE", "1000")), step=10)
    tiktoken_model = st.text_input("Tiktoken Model:", value=os.getenv("TIKTOKEN_MODEL", ""))

    chunking_config = {
        "chunk_size": context_chunk_size,
        "tokenizer_model" : tiktoken_model
    }

# Main area
st.subheader("Repository Setup")
repository_url = st.text_input("URL of Git Repository:")
local_path = st.text_input("Local Repository Path:")

if not repository_url and not local_path:
    st.warning("Please provide a repository URL or local path.")

st.subheader("Diagram Setup")
diagram_type = st.selectbox("Diagram Type:", ["component", "class", "sequence", "all"])
output_format = st.selectbox("Diagram Output Format:", ["svg", "uml", "png"])

st.subheader("SonarQube Setup (Optional)")
use_sonarqube = st.checkbox("Enable SonarQube analysis")
sonarqube_url = ""
sonarqube_project = ""
sonarqube_token = ""

if use_sonarqube:
    sonarqube_url = st.text_input("URL SonarQube:")
    sonarqube_project = st.text_input("Project Key SonarQube:")
    sonarqube_token = st.text_input("API Token SonarQube:", type="password")

    if sonarqube_url and not sonarqube_project and not sonarqube_token:
        st.warning("Please provide Project Key and API Token from SonarQube..")
    elif not sonarqube_url and sonarqube_project and not sonarqube_token:
        st.warning("Please provide URL and API Token of SonarQube.")
    elif not sonarqube_url and not sonarqube_project and sonarqube_token:
        st.warning("Please provide URL and Project Key of SonarQube.")
    elif sonarqube_url and sonarqube_project and not sonarqube_token:
        st.warning("Please provide the SonarQube Token API.")
    elif sonarqube_url and not sonarqube_project and sonarqube_token:
        st.warning("Please provide the SonarQube Project Key.")
    elif not sonarqube_url and sonarqube_project and sonarqube_token:
        st.warning("Please provide the URL of SonarQube.")

# Execution
KEY_ENV = {
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "groq": "GROQ_API_KEY",
}
if st.button("Run ArchAI"):
    provider = llm_config["provider"].lower()
    key_var = KEY_ENV.get(provider)
    if key_var and not os.getenv(key_var):
        st.error(f" Define your `{key_var}` for use this model.")
        st.stop()
    if repository_url or local_path:
        with st.spinner("ArchAI execution in progress..."):
            doc_path, diagram_path = run_crew(
                repository_url,
                local_path,
                diagram_type,
                output_format,
                sonarqube_url if use_sonarqube else "",
                sonarqube_project if use_sonarqube else "",
                sonarqube_token if use_sonarqube else "",
                llm_config,
                local_dir,
                output_dir,
            )

        # Visualization
        st.subheader("Results")
        if doc_path and os.path.exists(doc_path):
            st.markdown("### Generated Documentation:")
            with open(doc_path, "r") as f:
                documentation_content = f.read()

            st.markdown(
                f'<div class="markdown-box">{documentation_content}</div>',
                unsafe_allow_html=True,
            )


        elif doc_path:
            st.warning("The documentation file could not be found.")

        diagram_path = output_dir + diagram_type + "_diagram." + output_format

        if diagram_path and os.path.exists(diagram_path):
            st.markdown("### Diagram Generated:")
            if output_format == "svg":
                if diagram_type != "all":
                    st.info(f"Diagram in svg format available here: {diagram_path}")
                else:
                    st.info(f"Diagrams in svg format available here: {output_dir}")
            elif output_format == "png":
                if diagram_type != "all":
                    try:
                        st.image(diagram_path, caption=f"Diagram ({diagram_type})", use_container_width=True)
                    except Exception as e:
                        st.error(f"An error occurred during the visualization of the png: {e}")

                else:
                    st.info(f"Diagrams in png format available here: {output_dir}")
            elif output_format == "uml":  # uml
                if diagram_type != "all":
                    st.info(f"Diagram in UML format available here: {diagram_path}")
                else:
                    st.info(f"Diagrams in UML format available here: {output_dir}")
            else:
                st.info(f"Invalid output format")
        elif diagram_path:
            st.warning("The diagram file could not be found.")

    else:
        st.error("Please provide a repository URL or local path before running ArchAI.")
