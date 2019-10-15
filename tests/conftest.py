import sys
import os

import pytest

VERSION = "{}".format(sys.version_info[0])

# TODO: switch to pytest-filedata


def expected_docs(ext):
    expected_path = os.path.join(
        os.path.dirname(__file__),
        "data",
        VERSION,
        "gencodedocs.expected.{}".format(ext),
    )

    with open(expected_path, "r") as fh:
        return fh.read()


@pytest.fixture
def expected_docs_md():
    return expected_docs("md")


@pytest.fixture
def expected_docs_doc_func_md():
    return expected_docs("doc_func.md")


@pytest.fixture
def expected_docs_doc_class_md():
    return expected_docs("doc_class.md")


@pytest.fixture
def expected_docs_html():
    return expected_docs("html")


@pytest.fixture
def expected_docs_list():
    output = expected_docs("md")
    return output.split("\n")
