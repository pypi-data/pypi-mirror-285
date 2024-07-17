import argparse
from typing import Optional

from ons_metadata_validation.outputs.excel_outputs import (
    outputs_main,
)
from ons_metadata_validation.processing.processing import (
    MetadataProcessor,
)


def main(
    md_filepath: str,
    variable_check_set: str = "cmar",
    save_report: bool = True,
    save_corrected_copy: bool = False,
    save_commented_copy: bool = True,
    destination_folder: Optional[str] = None,
):
    # setup_logger(__file__, 2)

    processor = MetadataProcessor(
        md_filepath,
        variable_check_set=variable_check_set,
        save_report=save_report,
        save_corrected_copy=save_corrected_copy,
    )
    processor.main_process()
    return outputs_main(
        processor=processor,
        save_folder=destination_folder,
        save_commented_copy=save_commented_copy,
    )


def main_cli() -> None:
    parser = argparse.ArgumentParser(description="validate metadata template")
    parser.add_argument(
        "md_filepath", type=str, help="the filepath to the metdata template"
    )
    parser.add_argument(
        "variable_check_set",
        default="cmar",
        const="cmar",
        nargs="?",
        choices=["cmar", "full"],
        type=str,
        help="the role config to apply",
    )
    parser.add_argument(
        "save_report",
        default=True,
        nargs="?",
        type=bool,
        help="save the validation report",
    )
    parser.add_argument(
        "save_corrected_copy",
        default=False,
        nargs="?",
        type=bool,
        help="create a corrected version of the template",
    )
    parser.add_argument(
        "save_commented_copy",
        default=True,
        nargs="?",
        type=bool,
        help="create a commented version of the template",
    )
    parser.add_argument(
        "destination_folder",
        default=None,
        nargs="?",
        type=str,
        help="save report in directory, defaults to same location as metadata file",
    )

    args = parser.parse_args()

    main(
        args.md_filepath,
        args.variable_check_set,
        args.save_report,
        args.save_corrected_copy,
        args.save_commented_copy,
        args.destination_folder,
    )


if __name__ == "__main__":
    main_cli()
