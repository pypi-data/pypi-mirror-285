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
            if data['action_input']['operations']:
                print("These file operations will be executed:")
                for operation in data['action_input']['operations']:
                    print(f"{operation['operation']} on {operation['file']}")
                user_input = input("do you want to continue? [y/n]")
                while user_input not in ["y", "n"]:
                    user_input = input("Invalid input, please enter y or n")
                if user_input in ["y", "Y"]:
                    pass
                elif user_input in ["n", "N"]:
                    return "User cancelled the operation"
            result = process_file_operations(data['action_input']['operations'])
            print(result)
            return result
        elif data['action'] == 'bash_command':
            if data['action_input']["commands"]:
                print("these commands will be executed")
                for cmd in data['action_input']["commands"]:
                    print(cmd)
                user_input = input("do you want to continue? [y/n]")
                while user_input not in ["y", "n"]:
                    user_input = input("Invalid input, please enter y or n")
                if user_input in ["y", "Y"]:
                    pass
                elif user_input in ["n", "N"]:
                    return "User cancelled the operation"
            result = executor.execute_commands(json.dumps(data['action_input']))
            output = "Result:\n" + result
            print(output)
            return output
        elif data['task_completed']:
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
    response = requests.post(f"{API_URL}", headers=headers, json={'message': task}, timeout=90)
    response.raise_for_status()
    if response.status_code != 200:
        print(f"Failed to create thread. Status code: {response.status_code}")
        return
    
    response = response.json()

    thread_id = response['thread_id']
    
    print(f"Thread created with ID: {thread_id}")

    result = json.loads(response["output_message"])["task_completed"]
    while not result:
        output_response = response["output_message"]

        if output_response:
            result = process_assistant_response(output_response)

            if type(result) == str:
                user_input = input("Do you want to say something? ([e]xit)")
                if user_input == "e":
                    break
                else:
                    print("sending message", end="\r")
                    response = requests.put(f"{API_URL}/{thread_id}/", headers=headers, json={'message': result + "\n\n" + user_input}, timeout=90)
                    response.raise_for_status()
                    result = json.loads(response.json()["output_message"])["task_completed"]


            if type(result) == bool and result:
                user_input = input("Do you want to say something else? ([e]xit)")
                if user_input == "e":
                    break
                elif user_input == "":
                    result = True
                    pass
                elif user_input:
                    print("sending message", end="\r")
                    response = requests.put(f"{API_URL}/{thread_id}/", headers=headers, json={'message': user_input}, timeout=90).json()
                    response.raise_for_status()
                    result = json.loads(response["output_message"])["task_completed"]
            
        response = response.json()
    
    print("Task completed")

@cli.command()
def login():
    try:
        ensure_auth()
    except Exception as e:
        print(f"Login failed: {e}")

@cli.command()
def logout():
    from .auth import logout as auth_logout
    auth_logout()

if __name__ == "__main__":
    cli()