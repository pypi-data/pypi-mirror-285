from llama_index.core import (
    VectorStoreIndex,
    ServiceContext,
    StorageContext,
    SimpleDirectoryReader,
)
from llama_index.llms.openai import OpenAI
from llama_index.retrievers.bm25 import BM25Retriever
# from llama_index.core.retrievers import VectorIndexRetriever
# from llama_index.core.retrievers import BaseRetriever
from llama_index.core.retrievers import QueryFusionRetriever

from ara_cli.prompt_handler import read_string_from_file
from ara_cli.ara_config import ConfigManager
from ara_cli.classifier import Classifier

import os

def find_files_in_prompt_config_givens(search_file, prompt_givens_file_path):
    """
    Extracts markdown files paths based on checked items and constructs proper paths respecting markdown header hierarchy.
    """
    file_found = False
    header_stack = []
    modified_lines = []  # To store the modified file content

    with open(prompt_givens_file_path, 'r') as file:
        for line in file:
            if line.strip().startswith('#'):
                level = line.count('#')
                header = line.strip().strip('#').strip()
                # Adjust the stack based on the current header level
                current_depth = len(header_stack)
                if level <= current_depth:
                    header_stack = header_stack[:level-1]
                header_stack.append(header)
            elif os.path.basename(search_file) in line:
                relative_path = line.split(']')[-1].strip()
                full_path = os.path.join('/'.join(header_stack), relative_path)
                if full_path == search_file:
                    line = line.replace('[]', '[x]')  # Replace "[]" with "[x]"
                    file_found = True
                    print(f"found {search_file} and checked [x] selection box")
            modified_lines.append(line)  # Append potentially modified line to list

    if file_found:
        # Rewrite the file with the modified content if any line was changed
        with open(prompt_givens_file_path, 'w') as file:
            file.writelines(modified_lines)

    return file_found

def print_and_select_retrieved_nodes(classifier, param, nodes):
    if not nodes:
        print("No nodes found.")
        return
    print("found-nodes-list")
    sub_directory = Classifier.get_sub_directory(classifier)
    prompt_givens_file_path = f"ara/{sub_directory}/{param}.data/prompt.data/config.prompt_givens.md"
    for index, source_node in enumerate(nodes, start=1):
        print(f"{index}: {source_node.node.metadata['file_path']}")
        print(f"Score: {source_node.score:.2f} - {source_node.text}...\n-----")
        user_input = input("Select this node? Yes/No: ")
        if user_input.lower() in ['yes', 'y']:
            file_path_proposed_file = source_node.node.metadata['file_path'].replace(os.getcwd(), '').strip('/')
            file_found = False
            file_found = find_files_in_prompt_config_givens(file_path_proposed_file, prompt_givens_file_path)
            if not file_found:
                print(f"file not found: {file_path_proposed_file}. Continue? Y/N")
                if input().lower() not in ['y', 'yes']:
                    break

def is_directory_not_empty(directory_path):
    """
    Checks if the specified directory is not empty.
    :param directory_path: Path to the directory to check.
    :return: True if the directory is not empty, False otherwise.
    """
    try:
        # Attempt to list the contents of the directory
        return bool(os.listdir(directory_path))
    except FileNotFoundError:
        # Directory does not exist
        print(f"Directory {directory_path} does not exist or is empty.")
        return False  # Or you might want to handle this case differently
    except PermissionError:
        # Not enough permissions to access the directory
        print(f"Directory {directory_path} permission denied.")
        return False  # Or you might want to handle this case differently
     
def search_and_add_relevant_files_to_prompt_givens(classifier, param):
    config = ConfigManager.get_config()
    dir_list = ["ara"] + [item for ext in config.ext_code_dirs for key, item in ext.items()]  + [config.doc_dir] + [config.glossary_dir]
    documents = []
    for directory in dir_list:
        if is_directory_not_empty(directory):
            print(f"load {directory} to RAG documents")
            documents += SimpleDirectoryReader(directory).load_data()

    llm = OpenAI(model="gpt-4o")
    service_context = ServiceContext.from_defaults(chunk_size=2024, llm=llm)
    nodes = service_context.node_parser.get_nodes_from_documents(documents)

    storage_context = StorageContext.from_defaults()
    storage_context.docstore.add_documents(nodes)

    index = VectorStoreIndex(nodes=nodes, storage_context=storage_context, service_context=service_context)
    
    vector_retriever = index.as_retriever(similarity_top_k=10)
    
    bm25_retriever = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=10)

    retriever = QueryFusionRetriever(
        [vector_retriever, bm25_retriever],
        retriever_weights=[0.6, 0.4],
        similarity_top_k=5,
        num_queries=1,  # set this to 1 to disable query generation
        mode="relative_score",
        use_async=True,
        verbose=True,
    )

    sub_directory = Classifier.get_sub_directory(classifier)
    prompt_path = f"ara/{sub_directory}/{param}.{classifier}"
    context = read_string_from_file(prompt_path)

    # query string for context found in artefact
    query_string = f"{context}"
    nodes = retriever.retrieve(query_string)
    print_and_select_retrieved_nodes(classifier, param, nodes)
