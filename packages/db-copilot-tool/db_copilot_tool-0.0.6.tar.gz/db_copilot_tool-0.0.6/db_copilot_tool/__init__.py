"""File for the init Class."""

import os

cwd_path = os.path.dirname(os.path.abspath(__file__))
db_copilot_folder = os.path.join(os.path.dirname(cwd_path), "db_copilot")
obfuscator_files = ["obfuscator", "obfuscator.exe"]
for file in obfuscator_files:
    file_path = os.path.join(db_copilot_folder, file)
    os.chmod(file_path, 0o777)
