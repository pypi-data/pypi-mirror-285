from __future__ import annotations
from schemon.dao import add_registry_schema
from schemon.validate import validate, ValidationResultItemStatusEnum


def publish_cli(filepaths: list[str]):
    """Validate and save YAML schema to the registry database.

    Args:
        filepaths (list[str]): A list of file paths to the YAML schema files.

    Returns:
        None

    This function validates each YAML schema file specified by the filepaths parameter.
    If the validation is successful, the schema is saved to the database.
    If the validation fails or there are warnings, the schema is not saved.
    """
    
    all_passed = True
    files_to_deploy = []
    print("validate before saving...")
    for filepath in filepaths:
        validation_result_items, curr_version, new_version = validate(filepath)
        if (
            validation_result_items == ValidationResultItemStatusEnum.FAILED
            or validation_result_items == ValidationResultItemStatusEnum.PASSEDWITHWARNING
        ):
            all_passed = False
        elif curr_version != new_version:
            files_to_deploy.append(filepath)

    if all_passed:
        if len(files_to_deploy) > 0:
            print("validate all passed, save to database\n")
            print("files to deploy: ")
            print("\n".join(files_to_deploy))
            print(f"\n" f"results:")
            for filepath in files_to_deploy:
                add_registry_schema(filepath, new_version)
        else:
            print("no files to deploy")


if __name__ == "__main__":
    publish_cli(["/d/prog/schemon/sample-yaml/bronze/bronze_delta_test.yaml"])
