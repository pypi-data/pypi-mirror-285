from dataclasses import dataclass
from typing import List

import pytest

from tecton.cli.environment import UploadPart
from tecton.cli.environment import get_upload_parts
from tecton.cli.environment_utils import EnvironmentDependencies
from tecton.cli.environment_utils import is_valid_environment_name
from tecton.cli.upload_utils import DEFAULT_UPLOAD_PART_SIZE_MB


SAMPLE_LOCK_JSON = {
    "locked_resolves": [
        {
            "locked_requirements": [
                {
                    "project_name": "attrs",
                    "requires_dists": [
                        "attrs[tests-mypy]; extra == 'tests-no-zope'",
                        "hypothesis; extra == 'tests-no-zope'",
                    ],
                    "version": "23.2.0",
                },
                {"project_name": "boto3", "requires_dists": ["botocore<1.35.0,>=1.34.87"], "version": "1.34.87"},
                {"project_name": "pytest", "requires_dists": [], "version": "8.1.1"},
            ]
        }
    ],
    "requirements": ["attrs==23.2.0", "boto3==1.34.87", "pytest"],
}


@dataclass
class FileSplit__TestCase:
    name: str
    file_size: int
    expected_parts: List[UploadPart]


FILE_SPLIT_TEST_CASES = [
    FileSplit__TestCase(
        name="single_file",
        file_size=DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024 - 1,
        expected_parts=[UploadPart(part_number=1, offset=0, part_size=DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024 - 1)],
    ),
    FileSplit__TestCase(
        name="exact_multiple_parts",
        file_size=DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024 * 5,
        expected_parts=[
            UploadPart(
                part_number=i,
                offset=(i - 1) * DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024,
                part_size=DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024,
            )
            for i in range(1, 6)
        ],
    ),
    FileSplit__TestCase(
        name="multiple_parts_with_last_part_smaller",
        file_size=(DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024 * 2) + (DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024 // 2),
        expected_parts=[
            UploadPart(part_number=1, offset=0, part_size=DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024),
            UploadPart(
                part_number=2,
                offset=DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024,
                part_size=DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024,
            ),
            UploadPart(
                part_number=3,
                offset=2 * DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024,
                part_size=DEFAULT_UPLOAD_PART_SIZE_MB * 1024 * 1024 // 2,
            ),
        ],
    ),
    FileSplit__TestCase(
        name="zero_size_file",
        file_size=0,
        expected_parts=[],
    ),
]


@pytest.fixture
def temporary_requirements_file(tmp_path):
    requirements_text = "package1\n# package2\npackage3\n"
    requirements_path = tmp_path / "requirements.txt"
    requirements_path.write_text(requirements_text)
    return requirements_path


@pytest.mark.parametrize("test_case", FILE_SPLIT_TEST_CASES, ids=[tc.name for tc in FILE_SPLIT_TEST_CASES])
def test_get_upload_parts(test_case):
    parts = get_upload_parts(test_case.file_size)
    assert len(parts) == len(test_case.expected_parts)
    for part, expected_part in zip(parts, test_case.expected_parts):
        assert part.part_size == expected_part.part_size
        assert part.part_number == expected_part.part_number
        assert part.offset == expected_part.offset


@pytest.mark.parametrize(
    "name, expected",
    [
        ("env123", True),
        ("env_123", True),
        ("ENV-123", True),
        ("env*123", False),
        ("env?123", False),
        ("env!123", False),
        ("", False),
        ("env 123", False),
    ],
)
def test_environments(name, expected):
    assert is_valid_environment_name(name) == expected


@pytest.fixture
def environment_dependencies():
    return EnvironmentDependencies(SAMPLE_LOCK_JSON)


@pytest.mark.parametrize(
    "package_name, expected_version",
    [("attrs", "23.2.0"), ("boto3", "1.34.87"), ("pytest", "8.1.1"), ("nonexistent", None)],
)
def test_get_version(environment_dependencies, package_name, expected_version):
    assert environment_dependencies.get_version(package_name) == expected_version


@pytest.mark.parametrize(
    "package_name, expected_presence", [("attrs", True), ("boto3", True), ("pytest", True), ("nonexistent", False)]
)
def test_is_dependency_present(environment_dependencies, package_name, expected_presence):
    assert environment_dependencies.is_dependency_present(package_name) == expected_presence


@pytest.mark.parametrize(
    "package_name, expected_extras", [("attrs", ["tests-no-zope"]), ("boto3", []), ("pytest", []), ("nonexistent", [])]
)
def test_get_dependency_extras(environment_dependencies, package_name, expected_extras):
    extras = environment_dependencies.get_dependency_extras(package_name)
    assert extras == expected_extras
