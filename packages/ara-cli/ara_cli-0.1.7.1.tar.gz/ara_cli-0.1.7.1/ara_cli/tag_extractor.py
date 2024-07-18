import os


class TagExtractor:

    def __init__(self, file_system=None):
        self.file_system = file_system or os

    def extract_tags(self, navigate_to_target=False):
        from ara_cli.template_manager import DirectoryNavigator
        from ara_cli.file_classifier import FileClassifier

        navigator = DirectoryNavigator()
        if navigate_to_target:
            navigator.navigate_to_target()

        file_classifier = FileClassifier(self.file_system)
        classified_files = file_classifier.classify_files()

        files = set().union(*classified_files.values())

        unique_tags = set()

        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    first_line = file.readline().strip()
                    tags = first_line.split(' ')
                    tags = list(filter(lambda x: x.startswith('@'), tags))
                    tags = [tag[1:] for tag in tags]
                    unique_tags.update(tags)
            except (UnicodeDecodeError, IOError) as e:
                print(f"Error reading {file_path}: {e}")

        sorted_tags = sorted(unique_tags)
        return sorted_tags
