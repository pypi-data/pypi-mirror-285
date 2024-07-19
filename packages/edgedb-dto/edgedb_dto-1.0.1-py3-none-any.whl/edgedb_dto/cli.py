import argparse
from .generator import generate_dtos


def cli():
    parser = argparse.ArgumentParser(
        description="Generate DTO classes using pipeline function"
    )
    parser.add_argument(
        "--source-directory",
        "-s",
        help="Source directory containing codegen files",
        default=".",
    )
    parser.add_argument(
        "--output-directory",
        "-o",
        help="Output directory for generated DTO classes",
        default=None,
    )
    # parser.add_argument(
    #     "--init",
    #     "-i",
    #     help="Generate init file for generated DTO classes",
    #     action="store_true",
    #     default=False,
    # )

    args = parser.parse_args()

    source_directory = args.source_directory
    output_directory = args.output_directory
    # init_file = args.init

    generate_dtos(source_directory, output_directory)
