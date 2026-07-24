import os
from config import MAX_CHARS


schema_get_file_content = {
    "type": "function",
    "function": {
        "name": "get_file_content",
        "description": (
            "Reads the contents of a file at a path relative to the working "
            "directory"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": (
                        "Path of the file to read, relative to the working "
                        "directory"
                    ),
                },
            },
            "required": ["file_path"],
        },
    },
}


def get_file_content(working_directory: str, file_path: str) -> str:
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_path = os.path.normpath(os.path.join(working_dir_abs, file_path))

        # Will be True or False
        valid_target_path = (
            os.path.commonpath([working_dir_abs, target_path]) == working_dir_abs
        )

        if not valid_target_path:
            return (
                f'Error: Cannot read "{file_path}" as it is outside '
                "the permitted working directory"
            )

        if not os.path.isfile(target_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(target_path) as file:
            contents = file.read(MAX_CHARS)

            if file.read(1):
                contents += (
                    f'[...File "{file_path}" truncated at '
                    f"{MAX_CHARS} characters]"
                )

        return contents
    except Exception as e:
        return f"Error: {e}"
