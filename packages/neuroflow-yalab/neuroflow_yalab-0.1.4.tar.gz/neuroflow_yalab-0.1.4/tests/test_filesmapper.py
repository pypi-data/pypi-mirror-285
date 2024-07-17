"""
This file contains the tests for the filesmapper module.
"""

from neuroflow.files_mapper.files_mapper import FilesMapper


def test_files_mapper_subject_session():
    """
    Test the FilesMapper class.
    """
    path = "data/0001/1"
    mapper = FilesMapper(path)
    assert mapper.subject == "0001"
    assert mapper.session == "1"
