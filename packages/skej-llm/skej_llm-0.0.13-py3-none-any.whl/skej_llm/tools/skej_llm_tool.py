from jinja2 import Template
from promptflow.core import tool
from promptflow.connections import CustomConnection
from promptflow.contracts.types import PromptTemplate
import json
import requests
import datetime
import uuid
import re
from promptflow.core import tool
from typing import Union

@tool
def execute_llm(
    connection: CustomConnection,
    use_notion: bool,
    notion_page_id: str,
    model: str,
    temperature: float,
    llm_execution_id: str,
    node_name: str,
    prompt: PromptTemplate,
    **kwargs
) -> Union[dict, str]:
    NOTION_TOKEN = connection.secrets.get('notion_token')
    OPENAI_API_KEY = connection.secrets.get('openai_api_key')
    LANGSMITH_API_KEY = connection.secrets.get('langsmith_api_key')
    NOTION_VERSION = connection.configs.get('notion_version')
    API_SMITH = connection.configs.get('api_smith')
    PROJECT_NAME = connection.configs.get('project_name')

    # Helper function to fetch Notion page content
    def fetch_notion_page(page_id, notion_token, notion_version):
        url = f'https://api.notion.com/v1/blocks/{page_id}/children'
        headers = {
            'Authorization': f'Bearer {notion_token}',
            'Notion-Version': notion_version
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['results']

    # Helper function to get the prompt from Notion
    def get_prompt(page_id):
        blocks = fetch_notion_page(page_id,  NOTION_TOKEN, NOTION_VERSION)
        prompt_texts = []
        for block in blocks:
            rich_texts = block.get('code', {}).get('rich_text', [])
            for rich_text in rich_texts:
                plain_text = rich_text.get('plain_text', '')
                prompt_texts.append(plain_text)
        combined_prompt = ' '.join(prompt_texts)
        return combined_prompt

    # Helper function to call the OpenAI API
    def call_openai(creds, model, messages):
        api_endpoint = "https://api.openai.com/v1/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {creds}'
        }

        if not model:
            model = "gpt-4o"

        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": 1,
            "n": 1,
            "stream": False,
            "presence_penalty": 0,
            "frequency_penalty": 0,
        }
        response = requests.post(api_endpoint, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    # Helper function to sanitize and parse JSON response
    def get_sanitized_json_response(response):
        if not response:
            return None  # Handle null or undefined responses

        try:
            parsed_response = json.loads(response)
            if isinstance(parsed_response, dict):
                return parsed_response  # It's a valid JSON object
        except json.JSONDecodeError:
            sanitized_json_response = response.replace("```json", '').replace("```", '')
            return json.loads(sanitized_json_response)
    
    # Helper function to initiate run on Langsmith API
    def initiate_run(project_name, run_type, api_key, messages):
        run_id = str(uuid.uuid4())
        start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            response = requests.post(API_SMITH, json={
                'id': run_id,
                'run_type': run_type,
                'start_time': start_time,
                'name': f"meeting_{node_name}_{llm_execution_id}",
                'inputs': {"messages": messages},
                'session_name': project_name
            }, headers={'x-api-key': api_key})
            response.raise_for_status()
            return {'runId': run_id, 'startTime': start_time}
        except requests.exceptions.RequestException as e:
            print(f"Error initiating run: {e}")
            raise
    
    # Helper function to finalize run on Langsmith API
    def finalize_run(run_id, output, api_key):
        end_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            response = requests.patch(f"{API_SMITH}/{run_id}", json={
                'outputs': output,
                'end_time': end_time
            }, headers={'x-api-key': api_key})
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error finalizing run: {e}")
            raise

    def parse_rendered_prompt(rendered_prompt):
        lines = rendered_prompt.split('\n')
        messages = []
        current_role = None
        current_content = []

        for line in lines:
            line = line.strip()
            system_match = re.match(r"#\s*system\s*:", line, re.IGNORECASE)
            user_match = re.match(r"#\s*user\s*:", line, re.IGNORECASE)
            assistant_match = re.match(r"#\s*assistant\s*:", line, re.IGNORECASE)

            if system_match:
                if current_role and current_content:
                    messages.append({"role": current_role, "content": "\n".join(current_content)})
                    current_content = []
                current_role = "system"
                current_content.append(line[system_match.end():].strip())
            elif user_match:
                if current_role and current_content:
                    messages.append({"role": current_role, "content": "\n".join(current_content)})
                    current_content = []
                current_role = "user"
                current_content.append(line[user_match.end():].strip())
            elif assistant_match:
                if current_role and current_content:
                    messages.append({"role": current_role, "content": "\n".join(current_content)})
                    current_content = []
                current_role = "assistant"
                current_content.append(line[assistant_match.end():].strip())
            else:
                current_content.append(line)

        if current_role and current_content:
            messages.append({"role": current_role, "content": "\n".join(current_content)})

        return messages

    for attempt in range(3):  # Maximum of 3 attempts
        try:
            promptTemplate = prompt  # Initialize with the default prompt template

            if use_notion:
                # Fetch the prompt from Notion
                notion_prompt = get_prompt(notion_page_id)
                promptTemplate = notion_prompt  # Update promptTemplate if using Notion

            # Render the template with prompt_input
            rendered_prompt = Template(promptTemplate, trim_blocks=True, keep_trailing_newline=True).render(**kwargs)
            promptWithInput = parse_rendered_prompt(rendered_prompt)
            
            # Initiate tracing run on Langsmith API
            tracing_info = initiate_run(PROJECT_NAME, 'llm', LANGSMITH_API_KEY, promptWithInput)

            # Call the OpenAI API to get the response
            llm_response = call_openai(OPENAI_API_KEY, model, promptWithInput)

            # Finalize tracing run on Langsmith API
            finalize_run(tracing_info['runId'], llm_response, LANGSMITH_API_KEY)

            llm_output = llm_response.get('choices', [{}])[0].get('message', {}).get('content', '')

            # Sanitize and parse the JSON response
            sanitized_response = get_sanitized_json_response(llm_output)

            # Return the parsed JSON response if successful
            return sanitized_response

        except json.JSONDecodeError as e:
            if attempt < 2:  # If not on the last attempt, retry
                continue
            else:  # On the last attempt, return the error
                return {"error": f"JSON decode error: {str(e)}"}
        except requests.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}
