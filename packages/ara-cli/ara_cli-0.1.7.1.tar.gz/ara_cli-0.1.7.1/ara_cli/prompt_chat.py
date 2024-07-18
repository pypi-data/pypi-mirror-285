import os
import shutil
from ara_cli.chat import Chat
from ara_cli.classifier import Classifier
from ara_cli.update_config_prompt import update_artefact_config_prompt_files

def initialize_prompt_chat_mode(classifier, param, chat_name):
    sub_directory = Classifier.get_sub_directory(classifier)
    artefact_data_path = os.path.join("ara", sub_directory, f"{param}.data") # f"ara/{sub_directory}/{parameter}.data"

    if chat_name is None:
        chat_name = classifier

    update_artefact_config_prompt_files(classifier, param, automatic_update=True)

    classifier_chat_file = os.path.join(artefact_data_path, f"{chat_name}")
    start_chat_session(classifier_chat_file)

def start_chat_session(chat_file):
    chat = Chat(chat_file)
    chat.start()