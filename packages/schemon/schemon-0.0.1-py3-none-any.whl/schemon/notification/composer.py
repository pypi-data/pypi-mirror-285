from __future__ import annotations
from schemon.validator import (
    ValidationResultItemStatusEnum,
    ValidationReportStatusEnum,
)


def generate_validation_report(items: list[dict]) -> str:
    """
    Generate a validation report based on the provided items.

    Args:
        items (list[dict]): A list of dictionaries representing the validation items.

    Returns:
        str: The generated validation report.

    """
    report = "## Validation Report\n\n"

    # Determine the overall status
    if all(item["status"] == ValidationReportStatusEnum.PASSED for item in items):
        status = "Passed ✅"
    elif any(item["status"] == ValidationReportStatusEnum.FAILED for item in items):
        status = "Failed ❌"
    elif any(
        item["status"] == ValidationReportStatusEnum.PASSEDWITHWARNING for item in items
    ):
        status = "Passed with warning ⚠️"

    report += f"### Status: {status}\n\n"
    report += "---\n"
    report += "### Details\n"

    for item in items:
        entity_name = item["entity"]
        status = item["status"]
        curr_version = item["curr_version"]
        new_version = item["new_version"]
        result_items = item["result"]

        report += f"- **{entity_name}**\n"
        if not result_items:
            report += "\t✅ All good! No version change.\n"

        if (
            status == ValidationReportStatusEnum.PASSEDWITHWARNING
            or status == ValidationReportStatusEnum.FAILED
        ):
            report += f"\t⬆️ Version will be changed from **{curr_version}** to **{new_version}**\n"

        for result_item in result_items:
            if result_item.status == ValidationResultItemStatusEnum.PASSED:
                report += f"\t✅ All good! No version change.\n"
            elif result_item.status == ValidationResultItemStatusEnum.PASSEDWITHNEW:
                report += f"\t🆕 New entity.\n"
            elif result_item.status == ValidationResultItemStatusEnum.PASSEDWITHWARNING:
                report += f"\t⚠️ A {result_item.type} **{result_item.name}** is **{result_item.validation_type.name.lower()}** with message - {result_item.message}\n"
            elif result_item.status == ValidationResultItemStatusEnum.FAILED:
                report += f"\t❌ A {result_item.type} **{result_item.name}** is **{result_item.validation_type.name.lower()}** with message - {result_item.message}\n"

        report += "\n"

    print(report)

    return report
