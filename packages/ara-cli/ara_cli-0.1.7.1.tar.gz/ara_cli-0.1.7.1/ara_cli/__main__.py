import os
import sys
import argparse
import json
from ara_cli.version import __version__


def check_validity(condition, error_message):
    if not condition:
        print(error_message)
        sys.exit(1)


def create_action(args):
    from ara_cli.artefact_creator import ArtefactCreator
    from ara_cli.classifier_validator import is_valid_classifier
    from ara_cli.filename_validator import is_valid_filename
    from ara_cli.template_manager import SpecificationBreakdownAspects

    if args.parameter and args.classifier and args.aspect:
        sba = SpecificationBreakdownAspects()
        try:
            sba.create(args.parameter, args.classifier, args.aspect)
        except ValueError as ve:
            print(f"Error: {ve}")
            sys.exit(1)

    check_validity(is_valid_classifier(args.classifier), "Invalid classifier provided. Please provide a valid classifier.")
    check_validity(is_valid_filename(args.parameter), "Invalid filename provided. Please provide a valid filename.")

    parent_classifier, parent_name = args.contributes_to
    if parent_classifier and parent_name:
        check_validity(is_valid_classifier(parent_classifier), "Invalid parent classifier provided. Please provide a valid classifier")
        check_validity(is_valid_filename(parent_name), "Invalid filename provided for parent. Please provide a valid filename.")

    template_path = os.path.join(os.path.dirname(__file__), 'templates')
    artefact_creator = ArtefactCreator()
    artefact_creator.run(args.parameter, args.classifier, template_path, parent_classifier, parent_name)


def delete_action(args):
    from ara_cli.artefact_deleter import ArtefactDeleter

    artefact_deleter = ArtefactDeleter()
    artefact_deleter.delete(args.parameter, args.classifier)


def rename_action(args):
    from ara_cli.artefact_renamer import ArtefactRenamer
    from ara_cli.classifier_validator import is_valid_classifier
    from ara_cli.filename_validator import is_valid_filename

    check_validity(is_valid_filename(args.parameter), "Invalid filename provided. Please provide a valid filename.")
    check_validity(is_valid_classifier(args.classifier), "Invalid classifier provided. Please provide a valid classifier.")
    check_validity(is_valid_filename(args.aspect), "Invalid new filename provided. Please provide a valid filename.")

    artefact_renamer = ArtefactRenamer()
    artefact_renamer.rename(args.parameter, args.aspect, args.classifier)


def list_action(args):
    from ara_cli.artefact_lister import ArtefactLister

    artefact_lister = ArtefactLister()
    if (args.tags):
        artefact_lister.list_files(tags=args.tags)
        return
    artefact_lister.list_files()


def get_tags_action(args):
    from ara_cli.tag_extractor import TagExtractor

    tag_extractor = TagExtractor()
    tags = tag_extractor.extract_tags()

    if args.json:
        output = json.dumps({"tags": tags})
        print(output)
        return

    output = "\n".join(f"- {tag}" for tag in tags)
    print(output)


def prompt_action(args):
    from ara_cli.prompt_handler import initialize_prompt_templates, load_selected_prompt_templates
    from ara_cli.prompt_handler import create_and_send_custom_prompt
    from ara_cli.prompt_extractor import extract_and_save_prompt_results
    from ara_cli.update_config_prompt import update_artefact_config_prompt_files
    from ara_cli.prompt_rag import search_and_add_relevant_files_to_prompt_givens
    from ara_cli.prompt_chat import initialize_prompt_chat_mode
    from ara_cli.classifier_validator import is_valid_classifier
    from ara_cli.filename_validator import is_valid_filename

    check_validity(is_valid_classifier(args.classifier), "Invalid classifier provided. Please provide a valid classifier.")
    check_validity(is_valid_filename(args.parameter), "Invalid filename provided. Please provide a valid filename.")

    classifier = args.classifier
    param = args.parameter
    init = args.steps
    chat_file = args.chat_file

    if (init == 'init'):
        initialize_prompt_templates(classifier, param)
    if (init == 'init-rag'):
        initialize_prompt_templates(classifier, param)
        search_and_add_relevant_files_to_prompt_givens(classifier, param)
    if (init == 'load'):
        load_selected_prompt_templates(classifier, param)
    if (init == 'send'):
        create_and_send_custom_prompt(classifier, param)
    if (init == 'extract'):
        extract_and_save_prompt_results(classifier, param)
        print(f"automatic update after extract")
        update_artefact_config_prompt_files(classifier, param, automatic_update=True)
    if (init == 'chat'):
        initialize_prompt_chat_mode(classifier, param, chat_file)
    if (init == 'update'):
        update_artefact_config_prompt_files(classifier, param, automatic_update=True)


def chat_action(args):
    from ara_cli.chat import Chat

    if args.name:
        # Start or continue specific chat
        chat_name = args.name
    else:
        # Start or continue default chat
        chat_name = "chat"
    cwd = os.getcwd()
    chat_file_path = os.path.join(cwd, chat_name)
    chat = Chat(chat_file_path)
    chat.start()


def template_action(args):
    from ara_cli.classifier import Classifier
    from ara_cli.template_manager import TemplatePathManager

    check_validity(Classifier.is_valid_classifier(args.classifier), "Invalid classifier provided. Please provide a valid classifier.")
    check_validity(Classifier.is_valid_classifier(args.classifier), "Invalid classifier provided. Please provide a valid classifier.")

    template_manager = TemplatePathManager()
    content = template_manager.get_template_content(args.classifier)


def handle_invalid_action(args):
    sys.exit("Invalid action provided. Type ara -h for help")


def create_parser(subparsers):
    create_parser = subparsers.add_parser("create", help="Create a classified artefact with data directory")
    create_parser.add_argument("classifier", help="Classifier that also serves as file extension for the artefact file to be created. Valid Classifiers are: businessgoal, capability, keyfeature, feature, epic, userstory, example, task")
    create_parser.add_argument("parameter", help="Artefact name that serves as filename")
    create_parser.add_argument("-a", "--aspect", help="Adds additional specification breakdown aspects in data directory. Valid aspects are: customer, persona, concept, technology")
    create_parser.add_argument("-c", "--contributes-to", help="Specifies the parent artefact the created artefact should contribute to or illustrate", nargs=2, default=(None, None), metavar=('PARENT_CLASSIFIER', 'PARENT_NAME'))


def delete_parser(subparsers):
    delete_parser = subparsers.add_parser("delete", help="Delete an artefact file including its data directory")
    delete_parser.add_argument("classifier", help="Classifier of the artefact to be deleted")
    delete_parser.add_argument("parameter", help="Filename of artefact")


def rename_parser(subparsers):
    rename_parser = subparsers.add_parser("rename", help="Rename a classified artefact and its data directory")
    rename_parser.add_argument("classifier", help="Classifier of the artefact")
    rename_parser.add_argument("parameter", help="Filename of artefact")
    rename_parser.add_argument("aspect", help="New artefact name and new data directory name")


def list_parser(subparsers):
    list_parser = subparsers.add_parser("list", help="List files with optional tags")
    list_parser.add_argument("tags", nargs="*", help="Tags for listing files")


def get_tags_parser(subparsers):
    tags_parser = subparsers.add_parser("get-tags", help="Show tags")
    tags_parser.add_argument("--json", "-j", help="Output tags as JSON", action=argparse.BooleanOptionalAction)


def prompt_parser(subparsers):
    prompt_parser = subparsers.add_parser("prompt", help="Base command for prompt interaction mode")
    prompt_parser.add_argument("steps", choices=['init', 'load', 'send', 'extract', 'update', 'chat', 'init-rag'],
                               help="steps to be performed: 'init', 'load', 'send', 'extract', 'update', 'chat', or 'init-rag' the prompt config files in the prompt directory")
    prompt_parser.add_argument("classifier", help="Classifier of the artefact")
    prompt_parser.add_argument("parameter", help="Name of artefact data directory for prompt creation and interaction")
    prompt_parser.add_argument("chat_file", nargs='?', default=None)


def chat_parser(subparsers):
    chat_parser = subparsers.add_parser("chat", help="Command line chatbot. Chat control with SEND/s | RERUN/r | QUIT/q")
    chat_parser.add_argument("name", help="Optional name for a specific chat. Pass the .md file to continue an existing chat", nargs='?', default=None)


def template_parser(subparsers):
    template_parser = subparsers.add_parser("template", help="Outputs a classified ara template in the terminal")
    template_parser.add_argument("classifier", help="Classifier of the artefact type")


def cli():
    parser = argparse.ArgumentParser(description="Ara tools for creating files and directories.")
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')

    subparsers = parser.add_subparsers(dest="action", help="Action to perform")
    create_parser(subparsers)
    delete_parser(subparsers)
    rename_parser(subparsers)
    list_parser(subparsers)
    get_tags_parser(subparsers)
    prompt_parser(subparsers)
    chat_parser(subparsers)
    template_parser(subparsers)

    action_mapping = {
        "create": create_action,
        "delete": delete_action,
        "rename": rename_action,
        "list": list_action,
        "get-tags": get_tags_action,
        "prompt": prompt_action,
        "chat": chat_action,
        "template": template_action
    }

    args = parser.parse_args()
    if hasattr(args, 'action') and args.action:
        action = action_mapping.get(args.action, handle_invalid_action)
        action(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    cli()