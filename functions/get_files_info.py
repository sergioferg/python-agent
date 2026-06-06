import os

from google.genai import types

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
        required=["directory"],
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
