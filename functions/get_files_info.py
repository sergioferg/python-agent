import os
import subprocess

from config import MAX_CHARS


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
