from __future__ import annotations
import os
import ast
from enum import Enum


class ValidationTypeEnum(Enum):
    NEW = 0
    ADDED = 1
    REMOVED = 2
    MODIFIED = 3


class ValidationResultItemStatusEnum(Enum):
    FAILED = 0
    PASSED = 1
    PASSEDWITHWARNING = 2
    PASSEDWITHNEW = 3
    INVALID = 99


class ValidationReportStatusEnum(Enum):
    FAILED = 0
    PASSED = 1
    PASSEDWITHWARNING = 2
    INVALID = 99


class ValidationResult:
    def __init__(self, result: ValidationResultItemStatusEnum, new_version: str):
        self.result = result
        self.new_version = new_version


class ValidationResultItem:
    def __init__(
        self,
        name: str,
        type: str,
        passed: bool,
        warning: bool,
        status: ValidationResultItemStatusEnum,
        validation_type: ValidationTypeEnum,
        message: str,
    ):
        self.name = name
        self.type = type
        self.passed = passed
        self.warning = warning
        self.status = status
        self.validation_type = validation_type
        self.message = message


def compare_schema(
    source: dict[str:str], target: dict[str:str]
) -> list[ValidationResultItem]:
    """
    Compare two schema dictionaries and return a list of ValidationResultItem objects.

    Args:
        source (dict[str:str]): The source schema dictionary.
        target (dict[str:str]): The target schema dictionary.

    Returns:
        list[ValidationResultItem]: A list of ValidationResultItem objects representing the differences between the two schemas.
    """
    validationResults = []

    entity_name = source["entity_name"]

    for k in target:
        if source[k] != target[k] and (
            k == "owner_name"
            or k == "owner_email"
            or k == "entity_description"
            or k == "entity_description"
        ):
            validationResults.append(
                ValidationResultItem(
                    f"{entity_name}[{k}]",
                    "schema header",
                    True,
                    True,
                    ValidationResultItemStatusEnum.PASSEDWITHWARNING,
                    ValidationTypeEnum.MODIFIED,
                    f"schema header [{k}] type changed from [{target[k]}] to [{source[k]}]",
                )
            )
        elif source[k] != target[k] and (
            k == "platform" or k == "format" or k == "table"
        ):
            validationResults.append(
                ValidationResultItem(
                    f"{entity_name}[{k}]",
                    "schema header",
                    False,
                    True,
                    ValidationResultItemStatusEnum.FAILED,
                    ValidationTypeEnum.MODIFIED,
                    f"schema header [{k}] type changed from [{target[k]}] to [{source[k]}]",
                )
            )

    return validationResults


def compare_fields(
    source: dict[str:dict], target: dict[str:dict]
) -> list[ValidationResultItem]:
    """
    Compare registry fields (old version) with yaml fields (new version).
    Report errors if:
    1. Fields are added.
    2. Fields are deleted.
    3. Field types are changed.

    Args:
        source (dict[str:dict]): The source dictionary containing the old version of fields.
        target (dict[str:dict]): The target dictionary containing the new version of fields.

    Returns:
        list[ValidationResultItem]: A list of ValidationResultItem objects representing the validation results.
    """
    validationResults = []

    source_fields: dict = source["fields"]
    if (
        "transformation_config" in source["config"]
        and source["config"]["transformation_config"] is not None
        and "append_config" in source["config"]["transformation_config"]
    ):
        source_fields.update(source["config"]["transformation_config"]["append_config"])

    target_fields: dict = target

    new = {k: source_fields[k] for k in source_fields if k not in target_fields}
    deleted = {k: target_fields[k] for k in target_fields if k not in source_fields}

    if new:
        for k, v in new.items():
            validationResults.append(
                ValidationResultItem(
                    k,
                    "field",
                    True,
                    True,
                    ValidationResultItemStatusEnum.PASSEDWITHWARNING,
                    ValidationTypeEnum.ADDED,
                    f"field [{k}] added",
                )
            )

    # TODO: deleted fields should be checked if there is downstream usage.
    # if there is downstream usage, it should be a warning with passed=False
    # if no downstream usage, it should be a passed=True
    if deleted:
        for k, v in deleted.items():
            validationResults.append(
                ValidationResultItem(
                    k,
                    "field",
                    False,
                    True,
                    ValidationResultItemStatusEnum.FAILED,
                    ValidationTypeEnum.REMOVED,
                    f"field [{k}] removed",
                )
            )

    for field_name, d in target.items():
        if field_name in source_fields:
            field_props = [
                "type",
                "required",
                "nullable",
                "unique",
                "key",
                "pd_default",
                "default",
                "description",
                "regex",
                "example",
            ]
            for field_prop in field_props:
                if field_prop not in source_fields[field_name] and (
                    d[field_prop] == None or d[field_prop] == "null"
                ):
                    continue
                elif field_prop in source_fields[field_name] and (
                    d[field_prop] == None or d[field_prop] == "null"
                ):
                    validationResults.append(
                        ValidationResultItem(
                            f"{field_name}[{field_prop}]",
                            "field prop",
                            True,
                            True,
                            ValidationResultItemStatusEnum.PASSEDWITHWARNING,
                            ValidationTypeEnum.ADDED,
                            f"field [{field_name}] prop [{field_prop}] added",
                        )
                    )
                elif field_prop not in source_fields[field_name] and (
                    d[field_prop] != None and d[field_prop] != "null"
                ):
                    validationResults.append(
                        ValidationResultItem(
                            f"{field_name}[{field_prop}]",
                            "field prop",
                            True,
                            True,
                            ValidationResultItemStatusEnum.PASSEDWITHWARNING,
                            ValidationTypeEnum.REMOVED,
                            f"field [{field_name}] prop [{field_prop}] removed",
                        )
                    )
                elif (
                    type(source_fields[field_name][field_prop]) == list
                    and source_fields[field_name][field_prop]
                    != ast.literal_eval(d[field_prop])
                ) or (
                    type(source_fields[field_name][field_prop]) != list
                    and source_fields[field_name][field_prop] != d[field_prop]
                ):
                    passed = True
                    status = ValidationResultItemStatusEnum.PASSEDWITHWARNING
                    if (
                        field_prop == "type"
                        or field_prop == "required"
                        or field_prop == "nullable"
                        or field_prop == "regex"
                    ):
                        passed = False
                        status = ValidationResultItemStatusEnum.FAILED
                    validationResults.append(
                        ValidationResultItem(
                            f"{field_name}[{field_prop}]",
                            "field prop",
                            passed,
                            True,
                            status,
                            ValidationTypeEnum.MODIFIED,
                            f"field [{field_name}] prop [{field_prop}] changed from [{d[field_prop]}] to [{source_fields[field_name][field_prop]}]",
                        )
                    )

    return validationResults


def compare_config(
    source: dict[str:dict], target: dict[str:dict]
) -> list[ValidationResultItem]:
    """
    Compare the configuration between the source and target dictionaries.

    Args:
        source (dict[str:dict]): The source dictionary containing the configuration.
        target (dict[str:dict]): The target dictionary containing the configuration.

    Returns:
        list[ValidationResultItem]: A list of validation result items.

    """
    validationResults = []
    validationResults = compare_dicts(source, target, "config")

    return validationResults


def compare_expectation(
    source: dict[str:dict], target: dict[str:dict]
) -> list[ValidationResultItem]:
    """
    Compare the expectation between the source and target dictionaries.

    Args:
        source (dict[str:dict]): The source dictionary.
        target (dict[str:dict]): The target dictionary.

    Returns:
        list[ValidationResultItem]: A list of validation result items.
    """
    validationResults = []
    validationResults = compare_dicts(source, target, "expectation")

    return validationResults


# Helper function to compare lists without considering order
def compare_lists(lst1, lst2, section, path):
    """
    Compare two lists and generate a list of validation results.

    Args:
        lst1 (list): The first list to compare.
        lst2 (list): The second list to compare.
        section (str): The section name for the validation results.
        path (str): The path of the lists being compared.

    Returns:
        list: A list of ValidationResultItem objects representing the validation results.
    """
    ValidationResult = []
    unique_key = "rule"
    dict1 = {
        item[unique_key]: item
        for item in lst1
        if isinstance(item, dict) and unique_key in item
    }
    dict2 = {
        item[unique_key]: item
        for item in lst2
        if isinstance(item, dict) and unique_key in item
    }

    # Check for keys that are only in one of the lists
    keys1 = set(dict1.keys())
    keys2 = set(dict2.keys())
    for key in keys1 - keys2:
        ValidationResult.append(
            ValidationResultItem(
                path,
                section,
                True,
                True,
                ValidationResultItemStatusEnum.PASSEDWITHWARNING,
                ValidationTypeEnum.ADDED,
                f"List item unique key {key} in the path [{path}] added",
            )
        )
    for key in keys2 - keys1:
        ValidationResult.append(
            ValidationResultItem(
                path,
                section,
                True,
                True,
                ValidationResultItemStatusEnum.PASSEDWITHWARNING,
                ValidationTypeEnum.REMOVED,
                f"List item unique key {key} in the path [{path}] removed",
            )
        )
    # Recursively compare the items with the same unique key
    for key in keys1 & keys2:
        new_path = f"{path}[{unique_key}={key}]"
        ValidationResult.extend(
            compare_dicts(dict1[key], dict2[key], section, new_path)
        )

    return ValidationResult


def compare_dicts(d1, d2, section, path=""):
    """
    Compare two dictionaries recursively and generate a list of validation results.

    Args:
        d1 (dict): The first dictionary to compare.
        d2 (dict): The second dictionary to compare.
        section (str): The section name for the validation results.
        path (str, optional): The current path in the dictionary. Defaults to "".

    Returns:
        list: A list of ValidationResultItem objects representing the validation results.
    """

    ValidationResult = []

    # If both are not dictionaries or lists, directly compare them
    if not isinstance(d1, (dict, list)) or not isinstance(d2, (dict, list)):
        if d1 != d2:
            ValidationResult.append(
                ValidationResultItem(
                    path,
                    section,
                    True,
                    True,
                    ValidationResultItemStatusEnum.PASSEDWITHWARNING,
                    ValidationTypeEnum.MODIFIED,
                    f"Key in the path [{path}] changed from [{d2}] to [{d1}]",
                )
            )
        return ValidationResult

    # If both are lists, compare them without considering order
    if isinstance(d1, list) and isinstance(d2, list):
        ValidationResult.extend(compare_lists(d1, d2, section, path))
        return ValidationResult

    # If one is a list and the other is not, they are different
    if isinstance(d1, list) or isinstance(d2, list):
        ValidationResult.append(
            ValidationResultItem(
                path,
                section,
                True,
                True,
                ValidationResultItemStatusEnum.PASSEDWITHWARNING,
                ValidationTypeEnum.MODIFIED,
                f"Item in the path [{path}] changed from [{d2}] to [{d1}]",
            )
        )
        return ValidationResult

    # Check for keys that are only in one of the dictionaries
    keys_d1 = set(d1.keys())
    keys_d2 = set(d2.keys())
    for key in keys_d1 - keys_d2:
        ValidationResult.append(
            ValidationResultItem(
                path,
                section,
                True,
                True,
                ValidationResultItemStatusEnum.PASSEDWITHWARNING,
                ValidationTypeEnum.ADDED,
                f"Key in the path [{path}.{key}] added",
            )
        )
    for key in keys_d2 - keys_d1:
        ValidationResult.append(
            ValidationResultItem(
                path,
                section,
                True,
                True,
                ValidationResultItemStatusEnum.PASSEDWITHWARNING,
                ValidationTypeEnum.REMOVED,
                f"Key in the path [{path}.{key}] removed",
            )
        )

    # Recursively compare the values of the keys
    for key in keys_d1 & keys_d2:
        new_path = f"{path}.{key}" if path else key
        ValidationResult.extend(compare_dicts(d1[key], d2[key], section, new_path))

    return ValidationResult


def print_validation_result(filepath, status):
    if status == ValidationReportStatusEnum.PASSED:
        print(f"{filepath} validation passed")
    elif status == ValidationReportStatusEnum.FAILED:
        print(f"{filepath} validation failed")
    elif status == ValidationReportStatusEnum.PASSEDWITHWARNING:
        print(f"{filepath} validation passed with warning")


def add_to_notification_items(
    filepath,
    curr_version,
    new_version,
    status,
    validation_result_items,
    notification_items,
):
    notification_items.append(
        {
            "entity": os.path.basename(filepath),
            "curr_version": curr_version,
            "new_version": new_version,
            "status": status,
            "result": validation_result_items,
        }
    )


def add_to_table(table, validation_result_items):
    for resultItem in validation_result_items:
        table.add_row(
            [
                resultItem.passed,
                resultItem.warning,
                resultItem.name,
                resultItem.type,
                resultItem.validation_type,
                resultItem.message,
            ]
        )


def determine_status_overall(validation_result_items):
    if not validation_result_items:
        return ValidationReportStatusEnum.PASSED
    elif (
        len(validation_result_items) == 1
        and validation_result_items[0].validation_type == ValidationTypeEnum.NEW
    ):
        return ValidationReportStatusEnum.PASSED
    elif any(not item.passed for item in validation_result_items):
        return ValidationReportStatusEnum.FAILED
    elif any(item.passed and item.warning for item in validation_result_items):
        return ValidationReportStatusEnum.PASSEDWITHWARNING
    return ValidationReportStatusEnum.PASSED


def handle_validation_results(
    filepath,
    curr_version,
    new_version,
    validation_result_items,
    notification_items,
    table,
):
    status = determine_status_overall(validation_result_items)
    entity_name = (
        validation_result_items[0].name
        if validation_result_items and status == ValidationReportStatusEnum.PASSED
        else None
    )
    print_validation_result(filepath, status)
    add_to_notification_items(
        filepath,
        curr_version,
        new_version,
        status,
        validation_result_items,
        notification_items,
    )

    if status in [
        ValidationReportStatusEnum.FAILED,
        ValidationReportStatusEnum.PASSEDWITHWARNING,
    ] or (status == ValidationReportStatusEnum.PASSED and entity_name):
        add_to_table(table, validation_result_items)
