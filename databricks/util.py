import os
import re

from openai import OpenAI


def _get_client() -> tuple[OpenAI, str]:
    """Create an OpenAI client pointed at Databricks Foundation Models.

    Databricks serving endpoints use the OpenAI-compatible Chat Completions API:
      POST https://{host}/serving-endpoints/{model}/invocations

    Returns:
        (client, host) tuple — host is needed to build per-model base_url.
    """
    # Try Databricks notebook context first (works inside any Databricks notebook)
    try:
        import IPython
        ns = IPython.get_ipython().user_ns if IPython.get_ipython() else {}
        dbutils = ns.get("dbutils")
        spark = ns.get("spark")

        if dbutils and spark:
            token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
            host = spark.conf.get("spark.databricks.workspaceUrl")
            return token, host
    except Exception:
        pass

    # Fall back to env vars (useful for local testing)
    host = os.environ.get("DATABRICKS_HOST", "").rstrip("/").replace("https://", "")
    token = os.environ.get("DATABRICKS_TOKEN", "")
    if host and token:
        return token, host

    raise RuntimeError(
        "No Databricks credentials found. "
        "Set DATABRICKS_HOST and DATABRICKS_TOKEN env vars, "
        "or run inside a Databricks notebook."
    )


# Default model endpoint name
DEFAULT_MODEL = "databricks-claude-sonnet-4-6"


def llm_call(prompt: str, system_prompt: str = "", model: str = DEFAULT_MODEL) -> str:
    """Call a Databricks Foundation Model via the OpenAI-compatible API.

    Args:
        prompt: The user prompt.
        system_prompt: Optional system prompt.
        model: Databricks serving endpoint name. Defaults to databricks-claude-sonnet-4-6.

    Returns:
        The model's text response.
    """
    token, host = _get_client()

    client = OpenAI(
        api_key=token,
        base_url=f"https://{host}/serving-endpoints",
    )

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=4096,
        temperature=0.1,
    )
    return response.choices[0].message.content


def extract_xml(text: str, tag: str) -> str:
    """Extract content from an XML tag in a string.

    Args:
        text: Text containing XML.
        tag: XML tag to extract.

    Returns:
        Content inside the tag, or empty string if not found.
    """
    match = re.search(f"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
    return match.group(1) if match else ""
