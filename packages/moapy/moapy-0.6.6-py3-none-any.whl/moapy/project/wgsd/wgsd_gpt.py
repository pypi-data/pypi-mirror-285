import openai
import os

OPENAI_API_KEY = 'sk-proj-ODbxVzACO9AO0V6opSRJT3BlbkFJB8UEFH7zwxx9I7pS1Oj7'

# Ensure your OpenAI API key is set as an environment variable
openai.api_key = OPENAI_API_KEY

def get_python_code_from_openai(json_str: str, doWhat: str, model: str = "gpt-4o") -> str:
    """
    Sends a prompt to the OpenAI API and returns the response as Python code.

    Parameters:
    prompt (str): The prompt to send to the API.
    model (str): The model to use for the response. Default is 'gpt-3.5-turbo'.
    max_tokens (int): The maximum number of tokens to generate in the response. Default is 150.

    Returns:
    str: The Python code response from the OpenAI API.
    """

    prompt = f"""
        Given the following JSON data:
        {json_str}

        Write a Python function that {doWhat} from this data.
        Please provide only the code in a single code block.
        There is a penalty for not including code
        """
    try:
        # Format the messages for the chat model
        messages = [
            {"role": "system", "content": "You are a helpful assistant that writes Python code."},
            {"role": "user", "content": prompt}
        ]

        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            tool_choice="required",
            max_tokens=150,
            n=1,
            stop="```",
            temperature=0.6
        )

        # Extract the Python code from the response
        python_code = response.choices[0].message['content'].strip()
        return python_code
    except Exception as e:
        return f"An error occurred: {e}"

# Example usage
json_str = '{"moapy.project.wgsd.wgsd_flow.MaterialConcrete":{"grade":{"design_code":"ACI318M-19","grade":"C12"},"curve_uls":[{"stress":0,"strain":0},{"stress":0,"strain":0.0004500000000000001},{"stress":10.2,"strain":0.0004500000000000001},{"stress":10.2,"strain":0.003}],"curve_sls":[{"stress":0,"strain":0},{"stress":12,"strain":0.003}]}}'
doWhat = "2D 그래프로 그려줘"
response = get_python_code_from_openai(json_str, doWhat)
print(response)