import termos.openai_utils as openai_utils
from termos.file_editor import FileEditor
from termos.bash_cmd_exe import BashCommandExecutor
import os
import json
import signal
import sys
from time import sleep
import click
import requests
from .auth import get_authenticated_headers, API_URL, logout, ensure_auth

@click.group()
def cli():
    pass

def signal_handler(sig, frame):
    print("\nInterrupted by user. Exiting...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def process_file_operations(operations):
    if not operations:
        return "No file operations provided."
    output = []
    for operation in operations:
        editor = FileEditor(data=operation)
        print("processing file operation")
        output.append(editor.process())
    return "\n".join(output)

executor = BashCommandExecutor()
def process_assistant_response(response):
    try:
        data = json.loads(response)
        
        if data['action'] == 'file_operation':
            result = process_file_operations(data['action_input']['operations'])
            print(result)
            return result
        elif data['action'] == 'bash_command':
            result = executor.execute_commands(json.dumps(data['action_input']))
            output = "Bash Command Result:\n" + result
            print(output)
            return output
        elif data['task_completed']:
            print("completed")
            return True
        else:
            print(f"Unknown action: {data['action']}")
            return f"Unknown action: {data['action']}"
    except json.JSONDecodeError:
        print("Error: Invalid JSON response from assistant")
        return False
    except KeyError as e:
        print(f"Error: Missing key in assistant response: {e}")
        return False
    except Exception as e:
        print(f"Error processing assistant response: {e}")
        return False

@cli.command()
@click.option('--task', prompt='Enter the task', help='The task to be performed')
def run(task):
    try:
        headers = get_authenticated_headers()
    except Exception as e:
        print(f"Authentication error: {e}")
        return
    
    print("response Loading", end="\r")

    # Create a new thread
    response = requests.post(f"{API_URL}", headers=headers, json={'message': task})
    if response.status_code != 200:
        print(f"Failed to create thread. Status code: {response.status_code}")
        return
    
    response = response.json()

    thread_id = response['thread_id']
    
    print(f"Thread created with ID: {thread_id}")

    task_completed = False
    while not task_completed:
        output_response = response["output_message"]

        if output_response:
            print(f"Assistant response: {output_response}")
            result = process_assistant_response(output_response)

            if type(result) == str:
                user_input = input("Enter your response ([e]xit)")
                if user_input == "e":
                    break
                elif user_input == "":
                    pass
                elif user_input:
                    response = requests.put(f"{API_URL}/{thread_id}", headers=headers, json={'message': result + "\n\n" + user_input})
                    task_completed = False

            if not task_completed and type(task_completed) is bool:
                user_input = input("Enter your response ([e]xit)")
                if user_input == "e":
                    break
                elif user_input == "":
                    pass
                elif user_input:
                    response = requests.put(f"{API_URL}/{thread_id}", headers=headers, json={'message': user_input}).json()
                    task_completed = False
    
    print("Task completed")

@cli.command()
def login():
    try:
        ensure_auth()
        print("Login successful.")
    except Exception as e:
        print(f"Login failed: {e}")

@cli.command()
def logout():
    from .auth import logout as auth_logout
    auth_logout()

if __name__ == "__main__":
    cli()