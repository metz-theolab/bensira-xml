"""Command Line Interface to transform the raw files into a standardized format.
"""

import click
from pathlib import Path
from tei_transformer import TEITransformer


@click.command()
@click.option(
    "--input",
    "-i",
    "input_files",
    required=True,
    type=click.Path(exists=True, dir_okay=True, file_okay=False, resolve_path=True),
    help="The path to the input files to transform.",
)
@click.option(
    "--output",
    "-o",
    "output_files",
    required=True,
    type=click.Path(exists=True, dir_okay=True, file_okay=False, resolve_path=True),
    help="The path to the generated output files.",
)
def transform_files(input_files: Path, output_files: Path) -> None:
    """Transform the input files into a standardized format.

    Args:
        input_files (str): The path to the input files to transform.
    """
    for file in Path(input_files).glob('*.xml'):
        click.echo(f"Transforming the input files: {file.name}")
        TEITransformer(file).dump(Path(output_files) / file.name)