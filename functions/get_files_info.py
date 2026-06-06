import os
import subprocess

from google.genai import types

from config import MAX_CHARS

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)

def get_files_info(working_directory: str, directory: str = "."):
    try:
        work_dir_abs = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(work_dir_abs, directory))

        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'

        common = os.path.commonpath([work_dir_abs, target_dir])
        if common != work_dir_abs:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        items_list = []
        dir_list = os.listdir(target_dir)
        for item in dir_list:
            full_path = os.path.join(target_dir, item)
            items_list.append(f"- {item}: file_size={os.path.getsize(full_path)} bytes, is_dir={os.path.isdir(full_path)}")

        return "\n".join(items_list)

    except Exception as e:
        return f"Error: {e}"

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Returns the contents of a file in a specified directory relative to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to retrieve information from",
            ),
        },
    ),
)

def get_file_content(working_directory: str, file_path: str) -> str:
    try:
        work_dir_abs = os.path.abspath(working_directory)

        target_dir = os.path.normpath(os.path.join(work_dir_abs, file_path))

        common = os.path.commonpath([work_dir_abs, target_dir])
        if common != work_dir_abs:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(target_dir):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(target_dir, mode='r') as file:
            file_content = file.read(MAX_CHARS)
            if file.read(1):
                file_content += f' [..File "{file_path}" truncated at {MAX_CHARS} characters]'

        return file_content

    except Exception as e:
        return f"Error: {e}"

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content into a specified file, returns success or error",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to write content into",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content itself to write into the file",
            ),
        },
    ),
)

def write_file(working_directory: str, file_path: str, content: str) -> str:
    try:
        work_dir_abs = os.path.abspath(working_directory)

        target_dir = os.path.normpath(os.path.join(work_dir_abs, file_path))

        common = os.path.commonpath([work_dir_abs, target_dir])
        if common != work_dir_abs:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        if os.path.isdir(target_dir):
            return f'Error: Cannot write to "{file_path}" as it is a directory'

        abs_file_path = os.path.abspath(file_path)
        os.makedirs(os.path.dirname(abs_file_path), exist_ok=True)

        with open(abs_file_path, mode='w') as file:
            file.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

    except Exception as e:
        return f"Error: {e}"

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a python file with an optional list of arguments. Returns captured STDOUT or STERR in case of having. Also returns exit code in case of failure.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to run file from.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                ),
                description="List of strings containing parameters to be added to the python call, can be None.",
            ),
        },
        required=["file_path"],
    ),
)

def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    try:
        work_dir_abs = os.path.abspath(working_directory)

        target_dir = os.path.normpath(os.path.join(work_dir_abs, file_path))

        common = os.path.commonpath([work_dir_abs, target_dir])
        if common != work_dir_abs:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(target_dir):
            return f'Error: "{file_path}" does not exist or is not a regular file'

        if not file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'

        command = ["python", target_dir]
        if args:
            command.extend(args)

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=work_dir_abs
        )
        output = []
        if result.returncode != 0:
            output.append(f"Process exited with code {result.returncode}")

        if result.stdout:
            output.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")
        if not result.stdout and not result.stderr:
            output.append("No output produced")

        return "\n".join(output)

    except Exception as e:
        return f"Error: executing Python file: {e}"
