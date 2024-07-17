"""Package setup File for the db copilot tool."""

import email.parser
import glob
import os
import shutil

from packaging.requirements import Requirement
from setuptools import find_packages, setup
from wheel.wheelfile import WheelFile

db_copilot_wheel = glob.glob(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "dbcopilot",
        "dist",
        "dbcopilot-*.whl",
    )
)[0]


def unpack_db_copilot():
    """Unpack the db copilot tool."""
    target_folder = os.path.abspath(os.path.dirname(__file__))
    db_copilot_folder = os.path.join(target_folder, "db_copilot")
    if os.path.exists(db_copilot_folder):
        shutil.rmtree(db_copilot_folder)
    print(f"unpacking db copilot: {db_copilot_wheel} to {target_folder}")
    WheelFile(db_copilot_wheel).extractall(target_folder)
    for root, dirs, _ in os.walk(db_copilot_folder):
        for dir_name in dirs:
            init_file = os.path.join(root, dir_name, "__init__.py")
            if not os.path.exists(init_file):
                with open(init_file, "w") as f:
                    f.write(
                        "# This file is required to make Python treat the directory as a package."
                    )
    obfuscator_files = ["obfuscator", "obfuscator.exe"]
    for file in obfuscator_files:
        file_path = os.path.join(db_copilot_folder, file)
        os.chmod(file_path, 0o777)
        print(f"change mode of {file_path}")
    print("unpacked db copilot")


def db_copilot_dependencies():
    meta_file_template = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "dbcopilot-*.dist-info/METADATA"
    )
    print(meta_file_template)
    meta_file = glob.glob(meta_file_template)[0]
    with open(meta_file, "r") as f:
        metadata_str = f.read()
        metadata = email.parser.Parser().parsestr(metadata_str)

        all_requires = metadata.get_all("Requires-Dist")
        return [
            str(Requirement(require.split(";")[0]))
            for require in all_requires
            if not 'extra == "extensions"' in require
        ]


unpack_db_copilot()
db_copilot_package_name = "db_copilot"
package_name = "db_copilot_tool"
required_packages = db_copilot_dependencies() + [
    "diskcache",
    "azureml-core",
    "retrying",
    "azureml-telemetry",
]
setup(
    name=package_name,
    version=(
        "0.0.6"
        if not os.environ.get("RELEASE_VERSION")
        else os.environ.get("RELEASE_VERSION")
    ),
    packages=find_packages(
        include=[
            package_name,
            f"{package_name}.*",
            db_copilot_package_name,
            f"{db_copilot_package_name}.*",
        ]
    ),
    entry_points={
        "package_tools": [
            f"{package_name} = {package_name}.tools.tools_manager:list_package_tools"
        ]
    },
    package_data={
        package_name: [
            "_telemetry.json",
            "tools/yamls/*yaml",
            "db_copilot/obfuscator",
            "db_copilot/db_provider/utils/lemma.map.txt",
        ],
        db_copilot_package_name: ["*", "*/*/*"],
    },
    install_requires=required_packages,
    author="Microsoft Corporation",
    author_email="xiangrao@microsoft.com",
    description="nl2sql tool for prompt flow",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.8",
)
