from ara_cli.classifier import Classifier
from functools import lru_cache

class FileClassifier:
    def __init__(self, file_system):
        self.file_system = file_system
    
    @lru_cache(maxsize=None)
    def read_file_content(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def is_binary_file(self, file_path):
        # Heuristic check to determine if a file is binary.
        # This is not foolproof but can help in most cases.
        try:
            with open(file_path, 'rb') as f:
                for byte in f.read(1024):
                    if byte > 127:
                        return True
        except Exception as e:
            # Handle unexpected errors while reading the file in binary mode
            print(f"Error while checking if file is binary: {e}")
        return False

    def classify_files(self, tags=None):
        files_by_classifier = {classifier: [] for classifier in Classifier.ordered_classifiers()}

        for root, _, files in self.file_system.walk("."):
            for file in files:
                file_path = self.file_system.path.join(root, file)

                if tags:
                    if self.is_binary_file(file_path):
                        # Skip binary files
                        # print(f"DEBUG: Skipping binary file {file_path}")
                        continue

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    except UnicodeDecodeError:
                        try:
                            # Try reading with a different encoding if utf-8 fails
                            with open(file_path, 'r', encoding='latin-1') as f:
                                content = f.read()
                        except UnicodeDecodeError:
                            # Skip the file if it still fails
                            # print(f"DEBUG: Skipping file {file_path} due to encoding issues")
                            continue

                    # Ensure all tags are in content
                    if not all(tag in content for tag in tags):
                        # print(f"DEBUG: Skipping file {file_path} due to missing tags")
                        continue

                for classifier in Classifier.ordered_classifiers():
                    if file.endswith(f".{classifier}"):
                        files_by_classifier[classifier].append(file_path)

        return files_by_classifier

    def print_classified_files(self, files_by_classifier):
        for classifier, files in files_by_classifier.items():
            if files:
                print(f"{classifier.capitalize()} files:")
                for file in files:
                    print(f"  - {file}")
                print()