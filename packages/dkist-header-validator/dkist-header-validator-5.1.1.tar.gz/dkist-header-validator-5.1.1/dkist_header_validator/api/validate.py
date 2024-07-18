import typer

from dkist_header_validator.spec_validators import spec122_validator
from dkist_header_validator.spec_validators import Spec122ValidationException
from dkist_header_validator.spec_validators import spec214_validator
from dkist_header_validator.spec_validators import Spec214ValidationException

app = typer.Typer(help="CLI for the dkist-header-validator package")
"""
Command Line Interface for the dkist-header-validator package
"""


@app.command("validate122")
def validate122(
    filename: str = typer.Argument(help="Location of the FITS file on disk", default=None)
):
    """
    Validate a FITS file for SPEC-0122 compliance.

    SPEC failures are:
        - Extra keywords not included in SPEC-0122
        - Keywords with values of the wrong type (float instead of string, for example)
        - SPEC-0122 keywords that are missing
        - SPEC-0122 keywords with invalid values compared to the valid list given in the SPEC
    """
    try:
        spec122_validator.validate(filename, extra=False)
        print(f"No validation errors found in file {filename}")
    except Spec122ValidationException as e:
        print(f"Validation errors in file {filename}")
        for key, value in e.errors.items():
            print(f"{key}: {value}")


@app.command("validate214")
def validate214(
    filename: str = typer.Argument(help="Location of the FITS file on disk", default=None)
):
    """
    Validate a FITS file for SPEC-0214 compliance.

    SPEC failures are:
        - Extra keywords not included in SPEC-0214
        - Keywords with values of the wrong type (float instead of string, for example)
        - SPEC-0214 keywords that are missing
        - SPEC-0214 keywords with invalid values compared to the valid list given in the SPEC
    """
    try:
        spec214_validator.validate(filename, extra=False)
        print(f"No validation errors found in file {filename}")
    except Spec214ValidationException as e:
        print(f"Validation errors in file {filename}")
        for key, value in e.errors.items():
            print(f"{key}: {value}")


def main():
    """
    CLI for the dkist-header-validator package
    """
    app()


if __name__ == "__main__":
    main()
