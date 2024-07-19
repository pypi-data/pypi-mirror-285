import os
from ara_cli.classifier import Classifier
from ara_cli.prompt_handler import generate_config_prompt_template_file, generate_config_prompt_givens_file

def read_file(filepath):
    """Read and return the content of a file."""
    with open(filepath, 'r') as file:
        return file.read()

def write_file(filepath, content):
    """Write content to a file."""
    with open(filepath, 'w') as file:
        file.write(content)

def find_checked_items(content):
    """
    Find all checked items ([x]) in the content and return a list of their sections and items.
    """
    sections = []
    checked_items = []
    lines = content.split('\n')
    
    for line in lines:
        if line.startswith('#'):
            header_level = line.count('#')
            sections = sections[:header_level-1]  # Trim sections to the current header level
            sections.append(line)
        if '[x]' in line:
            item = ''.join(sections) + line.strip()
            checked_items.append(item)

    return checked_items


def update_items_in_file(content, checked_items):
    """
    Update items in the content based on the checked items found.
    """
    sections = []
    updated_lines = []
    lines = content.split('\n')

    for line in lines:
        if line.startswith('#'):
            header_level = line.count('#')
            sections = sections[:header_level-1]  # Trim sections to the current header level
            sections.append(line)
        section_path = ''.join(sections)
        if '[]' in line:
            for item in checked_items:
                if section_path in item and line.strip() in item.replace('[x]', '[]'):
                    line = line.replace('[]', '[x]')
                    #print(f"Debug Updated: {item}")
                    break
        updated_lines.append(line)

    return '\n'.join(updated_lines)

def update_config_prompt_files(input1, input2):
    """
    Update the prompt config files with the new chat.
    """
    content1 = read_file(input1)
    content2 = read_file(input2)
    
    checked_items = find_checked_items(content1)
    
    updated_content2 = update_items_in_file(content2, checked_items)
    
    write_file(input2, updated_content2)
    
    # Overwrite input1 with input2 and delete input2
    os.replace(input2, input1)
    
    print("Update process completed.")

def update_artefact_config_prompt_files(classifier, param, automatic_update=False):
    sub_directory = Classifier.get_sub_directory(classifier)
    artefact_data_path = os.path.join("ara", sub_directory, f"{param}.data") # f"ara/{sub_directory}/{parameter}.data"
    prompt_data_path = os.path.join(artefact_data_path, "prompt.data")  # f"ara/{sub_directory}/{parameter}.data/prompt.data"

    if not os.path.exists(prompt_data_path):
        os.makedirs(prompt_data_path)

    givens_file_name = "config.prompt_givens.md"
    givens_tmp_file_name = "config.prompt_givens_tmp.md"
    template_file_name = "config.prompt_templates.md"
    template_tmp_file_name = "config.prompt_templates_tmp.md"
    
    prompt_config_givens = os.path.join(prompt_data_path, givens_file_name)
    prompt_config_givens_tmp = os.path.join(prompt_data_path, givens_tmp_file_name)

    prompt_config_templates = os.path.join(prompt_data_path, template_file_name)
    prompt_config_templates_tmp = os.path.join(prompt_data_path, template_tmp_file_name)

    if not os.path.exists(prompt_config_givens):
        generate_config_prompt_givens_file(prompt_data_path, givens_file_name)
    else:
        if automatic_update:
            generate_config_prompt_givens_file(prompt_data_path, givens_tmp_file_name)
            update_config_prompt_files(prompt_config_givens, prompt_config_givens_tmp)
        if not automatic_update:
            # logic to ask for overwrite or update
            action = input(f"{prompt_config_givens} already exists. Do you want to overwrite (o) or update (u)? ")
            if action.lower() == 'o':
                generate_config_prompt_givens_file(prompt_data_path, givens_file_name)
            elif action.lower() == 'u':
                generate_config_prompt_givens_file(prompt_data_path, givens_tmp_file_name)
                update_config_prompt_files(prompt_config_givens, prompt_config_givens_tmp)

    if not os.path.exists(prompt_config_templates):
        generate_config_prompt_template_file(prompt_data_path, template_file_name)
    else:
        if automatic_update:
            generate_config_prompt_template_file(prompt_data_path, template_tmp_file_name)
            update_config_prompt_files(prompt_config_templates, prompt_config_templates_tmp)
        
        if not automatic_update:
        # logic to ask for overwrite or update
            action = input(f"{prompt_config_templates} already exists. Do you want to overwrite (o) or update (u)? ")
            if action.lower() == 'o':
                generate_config_prompt_template_file(prompt_data_path, template_file_name)
            elif action.lower() == 'u':
                generate_config_prompt_template_file(prompt_data_path, template_tmp_file_name)
                update_config_prompt_files(prompt_config_templates, prompt_config_templates_tmp)

