import os
import glob
from os import sys
from ara_cli.prompt_handler import send_prompt
from ara_cli.prompt_extractor import extract_responses
from ara_cli.directory_navigator import DirectoryNavigator
from ara_cli.prompt_handler import load_givens

class Chat:
    def __init__(self, chat_name):
        self.default_chat_content = "#### You:\n"
        self.chat_name = self.setup_chat(chat_name)
        self.chat_history = []
        self.initialize_commands()

    def initialize_commands(self):
        self.commands = {
            "QUIT":             self.execute_quit,
            "q":                self.execute_quit,
            "RERUN":            self.execute_rerun,
            "r":                self.execute_rerun,
            "SEND":             self.execute_send,
            "s":                self.execute_send,
            "CLEAR":            self.execute_clear,
            "c":                self.execute_clear,
            "NEW":              self.execute_new,
            "n":                self.execute_new,
            "HELP":             self.execute_help,
            "h":                self.execute_help,
            "EXTRACT":          self.execute_extract,
            "e":                self.execute_extract,
            "LOAD":             self.execute_load,
            "l":                self.execute_load,
            "LOAD-RULES":       self.execute_load_rules,
            "lr":               self.execute_load_rules,
            "LOAD-INTENTION":   self.execute_load_intention,
            "li":               self.execute_load_intention,
            "LOAD-COMMANDS":    self.execute_load_commands,
            "lc":               self.execute_load_commands,
            "LOAD-GIVENS":      self.execute_load_givens,
            "lg":               self.execute_load_givens
        }
        self.inverse_command_mapping = self.create_inverse_commands_mapping()
        self.command_descriptions = self.create_command_descriptions()

    def create_inverse_commands_mapping(self):
        inverse_commands = {}
        for key, value in self.commands.items():
            if value not in inverse_commands:
                inverse_commands[value] = key
            else:
                inverse_commands[value] += '/' + key
        return inverse_commands

    def create_command_descriptions(self):
        return {
            self.execute_quit: f"{self.inverse_command_mapping[self.execute_quit]}: Exit the application.",
            self.execute_rerun: f"{self.inverse_command_mapping[self.execute_rerun]}: Rerun the last prompt in the chat file.",
            self.execute_send: f"{self.inverse_command_mapping[self.execute_send]}: Send prompt to the LLM.",
            self.execute_clear: f"{self.inverse_command_mapping[self.execute_clear]}: Clear the chat and the file containing it.",
            self.execute_new: f"{self.inverse_command_mapping[self.execute_new]}: Create a new chat. Optionally provide a chat name in-line: NEW new_chat",
            self.execute_help: f"{self.inverse_command_mapping[self.execute_help]}: Display this help message.",
            self.execute_extract: f"{self.inverse_command_mapping[self.execute_extract]}: search for markdown code blocks containing \"# [x] extract\" as first line and \"# filename: <path/filename>\" as second line and copy the content of the code block to the specified file. The extracted code block is then marked with \"# [v] extract\"",
            self.execute_load: f"{self.inverse_command_mapping[self.execute_load]}: Load a file and append its contents to chat file. Can be given the file name in-line. Will attempt to find the file relative to chat file first, then treat the given path as absolute.",
            self.execute_load_rules: f"{self.inverse_command_mapping[self.execute_load_rules]}: Load rules from ./prompt.data/*.rules.md",
            self.execute_load_intention: f"{self.inverse_command_mapping[self.execute_load_intention]}: Load intention from ./prompt.data/*.intention.md",
            self.execute_load_commands: f"{self.inverse_command_mapping[self.execute_load_commands]}: Load commands from ./prompt.data/*.commands.md",
            self.execute_load_givens: f"{self.inverse_command_mapping[self.execute_load_givens]}: Load all files listed in a ./prompt.data/config.prompt_givens.md"
        }

    def setup_chat(self, chat_name):
        if os.path.exists(chat_name):
            return self.handle_existing_chat(chat_name)
        if chat_name.endswith("chat") and os.path.exists(f"{chat_name}.md"):
            return self.handle_existing_chat("chat.md")
        if os.path.exists(f"{chat_name}_chat.md"):
            return self.handle_existing_chat(f"{chat_name}_chat.md")
        return self.initialize_new_chat(chat_name)

    def handle_existing_chat(self, chat_file):
        if not os.path.exists(chat_file):
            print(f"Given chat file {chat_file} does not exist. Provide an existing chat file or create a new chat with its chat name only 'ara chat <chat_name>'. A file extension is not needed for a chat file!")
            sys.exit(1)
        chat_file_short = os.path.split(chat_file)[-1]
        user_input = input(f"{chat_file_short} already exists. Do you want to reset the chat? (y/N): ")
        if user_input.lower() == 'y':
            self.create_empty_chat_file(chat_file)
        self.chat_history = self.load_chat_history(chat_file)
        print(f"Reloaded {chat_file_short} content:")
        return chat_file

    def initialize_new_chat(self, chat_name):
        if chat_name.endswith(".md"):
            chat_name_md = chat_name
        else:
            if not chat_name.endswith("chat"):
                chat_name = f"{chat_name}_chat"
            chat_name_md = f"{chat_name}.md"
        self.create_empty_chat_file(chat_name_md)
        # open(chat_name_md, 'a', encoding='utf-8').close()
        chat_name_md_short = os.path.split(chat_name_md)[-1]
        print(f"Created new chat file {chat_name_md_short}")
        return chat_name_md

    def start(self):
        print("Start chatting (type 'HELP'/'h' for available commands, 'QUIT'/'q' to exit chat mode):")
        while True:
            command, user_input, additional_input = self.get_user_input()
            self.commands[command](user_input=user_input, additional_input=additional_input)

    def get_user_input(self):
        user_input = ""
        while True:
            line = input()
            line_split = line.split()
            if line_split[0] in self.commands.keys():
                additional_input = "".join(line_split[1:])
                return (line_split[0], f"{user_input.strip()}", additional_input)
            user_input += f"{line} "

    def send_message(self):
        prompt_to_send = "\n".join([message for message in self.chat_history])
        response = send_prompt(prompt_to_send)
        print(f"GPT-4: {response}")
        self.save_message("ChatGPT", response)

    def resend_message(self):
        with open(self.chat_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        if lines:
            index_to_remove = self.find_last_reply_index(lines)
            if index_to_remove is not None:
                with open(self.chat_name, 'w', encoding='utf-8') as file:
                    file.writelines(lines[:index_to_remove])
            self.chat_history = self.load_chat_history(self.chat_name)
            self.send_message()

    def find_last_reply_index(self, lines):
        index_to_remove = None
        for i, line in enumerate(reversed(lines)):
            if "#### You" in line:
                break
            if "#### ChatGPT" in line:
                index_to_remove = len(lines) - i - 1
                break
        return index_to_remove

    def save_message(self, role, message):
        role_marker = f"#### {role}:"
        with open(self.chat_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in reversed(lines):
                stripped_line = line.strip()
                if stripped_line:
                    break

        line_to_write = f"{message}\n\n"
        if stripped_line != role_marker:
            line_to_write = f"{role_marker}\n{message}\n\n"

        with open(self.chat_name, 'a', encoding='utf-8') as file:
            file.write(line_to_write)
        self.chat_history.append(line_to_write)

    def load_chat_history(self, chat_file):
        chat_history = []
        if os.path.exists(chat_file):
            with open(chat_file, 'r', encoding='utf-8') as file:
                chat_history = file.readlines()
        return chat_history

    def create_empty_chat_file(self, chat_file):
        with open(chat_file, 'w', encoding='utf-8') as file:
            file.write(self.default_chat_content)
        self.chat_history = []

    def load_file(self, file_name, prefix="", suffix=""):
        current_directory = os.path.dirname(self.chat_name)
        file_path = os.path.join(current_directory, file_name)
        if not os.path.exists(file_path):
            file_path = file_name
        if not os.path.exists(file_path):
            print(f"File {file_name} not found")
            return False
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
        with open(self.chat_name, 'a', encoding='utf-8') as chat_file:
            write_content = f"{prefix}{file_content}{suffix}\n\n"
            chat_file.write(write_content)
            return True
        return False

    def _load_helper(self, directory, pattern, file_type):
        directory_path = os.path.join(os.path.dirname(self.chat_name), directory)
        file_pattern = os.path.join(directory_path, pattern)

        matching_files = glob.glob(file_pattern)

        if not matching_files:
            print(f"No {file_type} file found.")
            return

        if len(matching_files) > 1:
            print(f"Multiple {file_type} files found:")
            for i, file in enumerate(matching_files):
                print(f"{i + 1}: {os.path.basename(file)}")
            choice = input("Please choose a file to load (enter number): ")
            try:
                choice_index = int(choice) - 1
                if choice_index < 0 or choice_index >= len(matching_files):
                    print("Invalid choice. Aborting load.")
                    return
                file_path = matching_files[choice_index]
            except ValueError:
                print("Invalid input. Aborting load.")
                return
        else:
            file_path = matching_files[0]

        if self.load_file(file_path):
            print(f"Loaded {file_type} from {os.path.basename(file_path)}")

    def execute_quit(self, *args, **kwargs):
        print("Chat ended")
        sys.exit()

    def execute_rerun(self, *args, **kwargs):
        self.resend_message()

    def execute_send(self, *args, user_input="", **kwargs):
        self.save_message("You", user_input)
        self.send_message()

    def execute_clear(self, *args, **kwargs):
        user_input = input("Are you sure you want to clear the chat? (y/N): ")
        if user_input.lower() != 'y':
            return
        self.create_empty_chat_file(self.chat_name)
        self.chat_history = self.load_chat_history(self.chat_name)
        print(f"Cleared content of {self.chat_name}")

    def execute_new(self, *args, additional_input="", **kwargs):
        chat_name = additional_input
        if chat_name == "":
            chat_name = input("What should be the new chat name? ")
        current_directory = os.path.dirname(self.chat_name)
        chat_file_path = os.path.join(current_directory, chat_name)
        self.__init__(chat_file_path)
        self.start()

    def execute_help(self, *args, **kwargs):
        help_message = "\nAvailable commands:\n"
        for function, description in self.command_descriptions.items():
            help_message += f"{description}\n"
        print(help_message)

    def execute_load(self, *args, additional_input="", **kwargs):
        file_name = additional_input
        if file_name == "":
            file_name = input("What file do you want to load? ")
            
        current_directory = os.path.dirname(self.chat_name)
        file_pattern = os.path.join(current_directory, file_name)
        matching_files = glob.glob(file_pattern)

        if not matching_files:
            print(f"No files matching pattern {file_name} found.")
            return

        for file_path in matching_files:
            prefix = f"File: {file_path}\n```\n"
            suffix = "\n```\n"
            if self.load_file(file_path, prefix=prefix, suffix=suffix):
                print(f"Loaded contents of file {file_path}")

    def execute_load_rules(self, *args, **kwargs):
        self._load_helper("prompt.data", "*.rules.md", "rules")

    def execute_load_intention(self, *args, **kwargs):
        self._load_helper("prompt.data", "*.intention.md", "intention")

    def execute_load_commands(self, *args, **kwargs):
        self._load_helper("prompt.data", "*.commands.md", "commands")

    def execute_extract(self, *args, **kwargs):
        extract_responses(self.chat_name, True)
        print("End of extraction")

    def execute_load_givens(self, *args, additional_input="", **kwargs):
        file_name = additional_input
        base_directory = os.path.dirname(self.chat_name)
        
        if file_name == "":
            file_name = f"{base_directory}/prompt.data/config.prompt_givens.md"
        
        # Check the relative path first
        relative_givens_path = os.path.join(base_directory, file_name)
        if os.path.exists(relative_givens_path):
            givens_path = relative_givens_path
        elif os.path.exists(file_name):  # Check the absolute path
            givens_path = file_name
        else:
            print(f"No givens file found at {relative_givens_path} or {file_name}")
            user_input = input("Please specify a givens file: ")
            if os.path.exists(os.path.join(base_directory, user_input)):
                givens_path = os.path.join(base_directory, user_input)
            elif os.path.exists(user_input):
                givens_path = user_input
            else:
                print(f"No givens file found at {user_input}. Aborting.")
                return

        cwd = os.getcwd()
        navigator = DirectoryNavigator()
        navigator.navigate_to_target()
        os.chdir('..')
        content, image_data = load_givens(givens_path)
        os.chdir(cwd)
        
        with open(self.chat_name, 'a', encoding='utf-8') as chat_file:
            chat_file.write(content)
        
        print(f"Loaded files listed and marked in {givens_path}")