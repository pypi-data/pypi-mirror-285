import os
import importlib
from support_toolbox.app_handler.token_manager import check_tokens


def get_available_tools():
    package_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

    tools = [t[:-3] for t in os.listdir(package_dir) if
             t.endswith('.py') and t != '__init__.py' and t != 'main.py']

    return tools


def display_tools(tools):
    for idx, tool in enumerate(tools, start=1):
        print(f"{idx}. {tool}")


def start_app():
    print("\nWelcome to the Support Toolbox!")
    while True:
        tools = get_available_tools()
        display_tools(tools)

        selection = input("\nEnter the number corresponding to the tool you want to use, or 'q' to quit: ")

        if selection.lower() == 'q':
            break

        try:
            selected_tool = tools[int(selection) - 1]

            # Check if the tokens for the selected tool exist and set them up if needed
            check_tokens(selected_tool)

            module = importlib.import_module(f"support_toolbox.{selected_tool}")
            module.run()
        except (ValueError, IndexError):
            print("Invalid selection. Please enter a valid number.")

