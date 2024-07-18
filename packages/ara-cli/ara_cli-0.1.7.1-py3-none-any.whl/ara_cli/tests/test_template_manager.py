from unittest.mock import patch, MagicMock
from pathlib import Path
from ara_cli.classifier import Classifier
from ara_cli.template_manager import SpecificationBreakdownAspects, ArtefactFileManager
from ara_cli.directory_navigator import DirectoryNavigator
from ara_cli.template_manager import TemplatePathManager
from io import StringIO

import pytest
import os



@pytest.fixture(autouse=True)
def navigate_to_ara_directory():
    navigator = DirectoryNavigator("ara")
    original_directory = navigator.navigate_to_target()
    yield
    os.chdir(original_directory)


@pytest.mark.parametrize(
    "file_exists, dir_exists, expected_mkdir_calls, expected_chdir_calls",
    [
        (True, True, 0, 1),
        (True, False, 1, 1),
        (False, False, 0, 0)
    ]
)
def test_create_directory(file_exists, dir_exists, expected_mkdir_calls, expected_chdir_calls):
    artefact_file = 'test_artefact'
    data_dir = 'test_artefact.data'
    sba = ArtefactFileManager()

    with patch('os.path.isfile', return_value=file_exists), \
         patch('os.path.exists', return_value=dir_exists), \
         patch('os.mkdir') as mock_mkdir, \
         patch('os.chdir') as mock_chdir:

        if not file_exists:
            with pytest.raises(ValueError, match=f"File {artefact_file} does not exist. Please create it first."):
                sba.create_directory(artefact_file, data_dir)
        else:
            sba.create_directory(artefact_file, data_dir)

        assert mock_mkdir.call_count == expected_mkdir_calls
        assert mock_chdir.call_count == expected_chdir_calls


@pytest.mark.parametrize(
    "aspect, expect_exception, match_str",
    [
        ("technology", False, None),
        ("", True, f"Template file .* does not exist."),
        ("invalid", True, f"Template file .* does not exist.")
    ]
)
def test_copy_templates_to_directory(aspect, expect_exception, match_str):
    sba = ArtefactFileManager()

    if expect_exception:
        with pytest.raises(FileNotFoundError, match=match_str):
            sba.copy_templates_to_directory(aspect)
    else:
        with patch("ara_cli.template_manager.copy") as mock_copy:
            sba.copy_templates_to_directory(aspect)
            mock_copy.assert_called()


@pytest.mark.parametrize(
    "file_exists, dir_exists, raises, expected_exception, expected_message",
    [
        (True, True, False, None, None),
        (True, False, False, None, None),
        (False, False, True, ValueError, f"File .* does not exist. Please create it first.")
    ]
)
def test_create(file_exists, dir_exists, raises, expected_exception, expected_message):
    artefact_name = 'test_artefact'
    classifier = 'capability'
    aspect = 'technology'
    sba = SpecificationBreakdownAspects()

    with patch('os.path.isfile', return_value=file_exists), \
         patch('os.path.exists', return_value=dir_exists), \
         patch('os.mkdir'), patch('os.chdir'), patch('shutil.copy'):

        if raises:
            with pytest.raises(expected_exception, match=expected_message):
                sba.create(artefact_name, classifier, aspect)
        else:
            sba.create(artefact_name, classifier, aspect)


def test_get_template_content_with_path_mock():
    classifier = "test"
    expected_content = "Hello, this is a test template."
    mock_base_path = MagicMock()

    mock_template_path = MagicMock()
    mock_base_path.__truediv__.return_value = mock_template_path

    mock_file = MagicMock()
    mock_file.read.return_value = expected_content
    mock_template_path.open.return_value.__enter__.return_value = mock_file

    with patch.object(
        TemplatePathManager, 'get_template_base_path_artefacts', return_value=mock_base_path
    ), patch("sys.stdout", new_callable=StringIO) as captured_output:
        manager = TemplatePathManager()

        # We're capturing stdout in as captured_output
        manager.get_template_content(classifier)

        assert captured_output.getvalue().strip() == expected_content


# Add more tests as needed
