from __future__ import annotations
import os
import yaml
from schemon.common import parse_yaml
from schemon.model import Session
from typing import Tuple
from schemon.dao import (
    get_latest_registry_schema,
    get_registry_schema_by_entity,
    get_registry_fields_by_entity,
)
from schemon.validator import (
    ValidationResult,
    compare_fields,
    compare_schema,
    compare_config,
    compare_expectation,
    ValidationResultItem,
    ValidationTypeEnum,
    ValidationResultItemStatusEnum,
    handle_validation_results,
)
from prettytable import PrettyTable
from schemon.notification.ado import create_pr_thread
from schemon.notification.composer import generate_validation_report


from schemon.env import loadenv


loadenv()


def validate_cli(
    filepaths: list[str],
    notification: str,
    platform: str = None,
    repo_id: str = None,
    pr_id: str = None,
):
    """
    Validates the given filepaths and prints the validation results.

    Args:
        filepaths (list[str]): A list of filepaths to be validated.
        notification (str): The notification destination to be sent to.
        platform (str, optional): The git repository platform.
        repo_id (str, optional): The repository ID.
        pr_id (str, optional): The pull request ID.

    Returns:
        ValidationResultEnum: The validation result.

    """
    notification_items = []
    validation_passed = True

    for filepath in filepaths:
        table = PrettyTable()
        table.align = "l"
        table.field_names = [
            "Passed",
            "Warning",
            "Name",
            "Type",
            "Validation Type",
            "Message",
        ]
        validation_result_items, curr_version, new_version = validate(filepath)

        if any(
            item.status == ValidationResultItemStatusEnum.FAILED
            for item in validation_result_items
        ):
            validation_passed = False

        print("\n")
        handle_validation_results(
            filepath,
            curr_version,
            new_version,
            validation_result_items,
            notification_items,
            table,
        )
        print(table)

    if notification == "pr":
        report = generate_validation_report(notification_items)
        if platform == "ado":
            org = os.getenv("ADO_ORG")
            project = os.getenv("ADO_PROJECT")
            pat = os.getenv("ADO_PAT")

            print("Sending notification to Azure DevOps...")
            response = create_pr_thread(org, project, repo_id, pr_id, pat, report)
            print("Azure Devops response", response)

    if not validation_passed:
        print("Validation failed")
        return 1
    print("Validation passed")
    return 0


def validate(filepath: str) -> Tuple[list[ValidationResultItem], str, str]:
    """Validate YAML with registry database.

    Args:
        filepath (str): The path to the YAML file to be validated.

    Returns:
        Tuple[list[ValidationResultItem], str, str]: A tuple containing the validation results,
        the current version, and the new version.

    """

    validation_result_items = []
    parsed = parse_yaml(filepath)
    entity_name = parsed["entity"]["name"]
    stage = parsed["stage"]
    env = os.getenv("ENV")
    session = Session()
    rs = get_registry_schema_by_entity(session, entity_name, stage, env)

    if rs:
        validation_result_items = compare(session, parsed)
    else:
        validation_result_items.append(
            ValidationResultItem(
                entity_name,
                "entity",
                True,
                False,
                ValidationResultItemStatusEnum.PASSEDWITHNEW,
                ValidationTypeEnum.NEW,
                f"no previous registry schema data for entity [{entity_name}]",
            )
        )
    curr_version, new_version = get_new_version(session, validation_result_items)
    return validation_result_items, curr_version, new_version


def compare(
    session: Session,  # type: ignore
    source: dict[str:dict],
) -> list[ValidationResultItem]:
    """
    Compares the source schema, fields, config, and expectations with the target schema, fields, config, and expectations.

    Args:
        session (Session): The database session.
        source (dict[str:dict]): The source schema, fields, config, and expectations.

    Returns:
        list[ValidationResultItem]: A list of validation results.
    """

    entity_name = source["entity"]["name"]
    stage = source["stage"]
    env = os.getenv("ENV")

    # compare schema
    rs = get_registry_schema_by_entity(session, entity_name, stage, env)
    full_content = yaml.safe_load(rs.content)
    source_schema_dict = {
        "stage": source["stage"],
        "entity_name": source["entity"]["name"],
        "entity_description": source["entity"]["description"],
        "owner_name": source["owner"]["name"],
        "owner_email": source["owner"]["email"],
        "platform": source["platform"],
        "format": source["format"],
        "type": source["type"],
    }
    target_schema_dict = {
        "stage": rs.stage,
        "entity_name": rs.entity_name,
        "entity_description": rs.entity_description,
        "owner_name": rs.owner_name,
        "owner_email": rs.owner_email,
        "platform": rs.platform,
        "format": rs.format,
        "type": rs.type,
    }
    validation_result_items = compare_schema(source_schema_dict, target_schema_dict)

    # compare fields
    source_field_dict = source
    target = get_registry_fields_by_entity(session, entity_name, stage, env)
    target_field_dict = {d.name: vars(d) for d in target}
    validation_result_items.extend(compare_fields(source_field_dict, target_field_dict))

    # compare config
    source_config_dict = source.get("config")
    target_config_dict = full_content.get("config")
    validation_result_items.extend(
        compare_config(source_config_dict, target_config_dict)
    )

    # compare expectation
    source_expectation_dict = source.get("expectations")
    target_expectation_dict = full_content.get("expectations")
    validation_result_items.extend(
        compare_expectation(source_expectation_dict, target_expectation_dict)
    )

    return validation_result_items


def get_new_version(session: Session, validation_result_items: list[ValidationResult]) -> Tuple[str, str]:  # type: ignore
    """
    Determines the new version based on the validation results.

    Args:
        session (Session): The session object used for retrieving the latest schema.
        validation_result_items (list[ValidationResult]): A list of validation results.

    Returns:
        Tuple[str, str]: A tuple containing the current version and the new version.

    Raises:
        None

    """
    default_version = "1.0"
    is_major = None

    latest_schema = get_latest_registry_schema(session)
    if latest_schema is not None:
        curr_version = latest_schema.version

    if not validation_result_items:
        return curr_version, curr_version
    elif (
        len(validation_result_items) == 1
        and validation_result_items[0].validation_type == ValidationTypeEnum.NEW
    ):
        return "New entity", default_version
    elif any(not result.passed for result in validation_result_items):
        is_major = True
    elif any(result.passed and result.warning for result in validation_result_items):
        is_major = False
    else:
        return "INVALID_VERSION"

    return curr_version, increment_version(is_major, curr_version)


def increment_version(is_major: bool, curr_version: str) -> str:
    """
    Increments the version number based on the given parameters.

    Args:
        is_major (bool): A boolean value indicating whether to increment the major version.
        curr_version (str): The current version number in the format "major.minor".

    Returns:
        str: The new version number after incrementing.

    """
    major, minor = map(int, curr_version.split("."))

    if is_major:
        major += 1
        minor = 0
    else:
        minor += 1

    new_version = f"{major}.{minor}"
    return new_version


if __name__ == "__main__":
    validate_cli(
        ["/d/prog/schemon/sample-yaml/bronze/bronze_delta_cms_stope_comment.yaml"]
    )
