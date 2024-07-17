import io
import math
from base64 import b64encode
from enum import Enum
from pathlib import Path

import pylibmagic  # noqa: F401
import magic
import pydicom

import rich
import typer

from ..core.bootstrap.system import SystemBootstrapper, OS, MachineType

help_msg = "Skyler CLI: The multitool I always wanted to build myself"
app = typer.Typer(
    help=help_msg,
    no_args_is_help=True,
)


@app.command()
def setup_configs(
    os: OS = typer.Option(..., prompt="Select your OS"),
    machine_type: MachineType = typer.Option(
        ..., prompt="What type of machine is this?"
    ),
    personal_machine: bool = typer.Option(
        ..., prompt="Is this a personal machine (as opposed to one for work)"
    ),
    dryrun: bool = typer.Option(False, is_flag=True),
):
    bootstrapper = SystemBootstrapper(os, machine_type, is_personal=personal_machine)
    if dryrun:
        print(
            f"Dryrun! Would have set up the system with: {os=} {machine_type=} {personal_machine=}"
        )
        return

    bootstrapper.bootstrap_system()


class OutputFormat(Enum):
    PPRINT = "pprint"
    JSON = "json"


@app.command(help="Parse a single dicom file, and pretty print the file metadata")
def dicom(
    in_file: Path,
    fmt: OutputFormat = typer.Option(default="pprint"),
    pixel_data_len: int = typer.Option(
        32,
        "--pixel_data_len",
        "-n",
        help="How many bytes of pixel data to return for each fragment (if there is "
        "any pixel data at all). Set to -1 to include all the data",
    ),
):
    dicom_data = pydicom.dcmread(in_file)
    pixel_data_tag = 0x7FE00010
    has_pixel_data = pixel_data_tag in dicom_data
    if fmt == OutputFormat.PPRINT:
        rich.print(repr(dicom_data))
        if has_pixel_data:
            summarize_pixel_data(dicom_data[pixel_data_tag].value, pixel_data_len)
    elif fmt == OutputFormat.JSON:
        result_dict = dicom_data.to_json_dict()
        if "7FE00010" in result_dict:
            pixel_data_fragments = parse_encapsulated_dicom_data(
                dicom_data[pixel_data_tag].value
            )
            if pixel_data_len >= 0:
                pixel_data_fragments = [
                    f[: min(pixel_data_len, len(f))] for f in pixel_data_fragments
                ]
            b64_fragments = [b64encode(f).decode() for f in pixel_data_fragments]
            result_pixel_data_dict = result_dict["7FE00010"]
            result_pixel_data_dict["fragments"] = b64_fragments
            if "InlineBinary" in result_pixel_data_dict:
                del result_pixel_data_dict["InlineBinary"]
        rich.print_json(data=result_dict)
    else:
        print(f"Unsupported output format: {fmt}")


def summarize_pixel_data(pixel_data: bytes, head_len: int):
    fragments = parse_encapsulated_dicom_data(pixel_data)
    summaries = []
    idx_len = math.ceil(math.log10(len(fragments)))
    for i, fragment in enumerate(fragments):
        fragment_type = magic.from_buffer(fragment)
        if fragment:
            if head_len >= 0:
                hl = min(len(fragment), head_len)
                fragment_head = fragment[:hl].hex()
            else:
                fragment_head = fragment.hex()
        else:
            fragment_head = ""
        idx = str(i).zfill(idx_len)
        summaries.append(
            f"{idx}: {len(fragment)} bytes\n\ttype: {fragment_type}\n\thead (hex): {fragment_head}"
        )
    print("=" * 10)
    print(
        f"{len(summaries)} pixel data fragments found. The 0th is likely a (possibly empty) offset table:"
    )
    print("\n".join(summaries))


def parse_encapsulated_dicom_data(raw_bytes: bytes) -> list[bytes]:
    fragments = []
    with io.BytesIO(raw_bytes) as raw_data:
        while raw_data.tell() < len(raw_bytes):
            tag = raw_data.read(4)
            assert tag == bytes.fromhex("FEFF00E0")
            length = int.from_bytes(raw_data.read(4), byteorder="little")
            fragments.append(raw_data.read(length))
    return fragments


if __name__ == "__main__":
    app()
