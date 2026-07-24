import os
import subprocess


schema_run_python_file = {
    "type": "function",
    "function": {
        "name": "run_python_file",
        "description": (
            "Executes a Python file within the working directory and returns "
            "its output"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": (
                        "Path of the Python file to execute, relative to the "
                        "working directory"
                    ),
                },
                "args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Optional command-line arguments to pass to the "
                        "Python file"
                    ),
                },
            },
            "required": ["file_path"],
        },
    },
}


def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    try:
        working_dir_abs = os.path.abspath(working_directory)
        absolute_file_path = os.path.abspath(
            os.path.join(working_dir_abs, file_path)
        )

        if (
            os.path.commonpath([working_dir_abs, absolute_file_path])
            != working_dir_abs
        ):
            return (
                f'Error: Cannot execute "{file_path}" as it is outside '
                "the permitted working directory"
            )

        if not os.path.isfile(absolute_file_path):
            return (
                f'Error: "{file_path}" does not exist or is not a regular file'
            )

        if not file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        command = ["python", absolute_file_path]
        if args:
            command.extend(args)

        completed_process = subprocess.run(
            command,
            cwd=working_dir_abs,
            capture_output=True,
            text=True,
            timeout=30,
        )

        output = []

        if completed_process.stdout:
            output.append(f"STDOUT:\n{completed_process.stdout}")

        if completed_process.stderr:
            output.append(f"STDERR:\n{completed_process.stderr}")

        if completed_process.returncode != 0:
            output.append(
                f"Process exited with code {completed_process.returncode}"
            )

        if not completed_process.stdout and not completed_process.stderr:
            output.append("No output produced")

        return "\n".join(output)
    except Exception as e:
        return f"Error: executing Python file: {e}"
