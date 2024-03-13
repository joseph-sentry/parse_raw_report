import argparse
import base64
import json
import os
import zlib

from pathlib import Path


def process(raw_report_location, destination_dir, no_limit):
    counter = 0
    files = dict()

    try:
        os.mkdir(
            destination_dir,
        )
    except FileExistsError:
        pass

    with open(
        raw_report_location,
        "r",
    ) as f:
        json_obj = json.loads(f.read())
        key = ""
        if "coverage_files" in json_obj.keys():
            key = "coverage_files"
        elif "test_results_files" in json_obj.keys():
            key = "test_results_files"
        else:
            print(
                "Error: raw report JSON does not contain coverage_files or test_results_files key"
            )
        for file in json_obj[key]:
            filename = file["filename"]

            if filename.startswith("/"):
                filename = filename[1:]

            data = str(zlib.decompress(base64.b64decode(file["data"])), "utf8")
            counter += len(data)
            files[filename] = data.replace(
                "\n",
                """
""",
            )

            destination_path = Path(destination_dir, filename)

            destination_path.parent.mkdir(parents=True, exist_ok=True)
            with open(destination_path, "w") as f:
                f.write(files[filename])
            if not no_limit and counter > 10000:
                break


parser = argparse.ArgumentParser(description="Turn raw report into readable files")
parser.add_argument("raw_report_location")
parser.add_argument("--destination-dir", dest="dest", default="raw_report_files")
parser.add_argument(
    "--no-limit",
    dest="no_limit",
    action=argparse.BooleanOptionalAction,
    default=False,
)
args = parser.parse_args()

process(args.raw_report_location, args.dest, args.no_limit)
