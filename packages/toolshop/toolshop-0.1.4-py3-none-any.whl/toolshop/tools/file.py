"""This module contains tools for reading and writing files."""

import pathlib
import os
from typing import Optional

from ..core.base import Tool, State
from ..core.logging import logger


def make_file_tools(tools: list[str] = None, state: State = None):
    """Creates a set of file tools with shared state.
    
    Args:
        tools (list[str], optional): A list of tool names to include. If None, 
            all tools are included. Defaults to None.
    """
    if state is None:
        state = State()
    
    read_file = ReadFile(state=state)
    read_directory = ReadDirectory(state=state)
    create_file = CreateFile(state=state)
    replace_lines = ReplaceLines(state=state)
    insert_lines = InsertLines(state=state)
    delete_lines = DeleteLines(state=state)
    
    if not tools:
        tools = ["read_file", "read_directory", "create_file", "replace_lines", "insert_lines", "delete_lines"]
    
    x = locals()
    return [x[tool_name] for tool_name in tools]


class ReadFile(Tool):
    def call(
            self,
            path: str, 
            include_line_numbers: bool = True, 
            start_line: int = None, 
            end_line: int = None
    ) -> str:
        """
        Always use this read tool when reading contents of a file. This tool
        is specifically designed for safely reading files and can include line
        numbers in its output for easier reference. This ensures a standardized
        and secure way to access file contents.

        Args:
            path (str): The path to the file.
            include_line_numbers (bool): Whether to include line numbers in the returned contents. Defaults to True.
            start_line (int): The line number to start reading from. Uses one-based indexing.
            end_line (int): The line number to stop reading at. Uses one-based indexing.
        """
        output = _read_helper(
            path, 
            include_line_numbers=include_line_numbers, 
            start_line=start_line-1 if start_line else None, 
            end_line=end_line if end_line else None
        )
        self.state.record_file_read(path)
        
        return output


class ReadDirectory(Tool):
    def call(
        self,
        path,
        files_prefix_allowlist=None,
        files_prefix_ignorelist=['.', '__'],
        files_suffix_allowlist=None,
        files_suffix_ignorelist=None,
        dirs_prefix_allowlist=None,
        dirs_prefix_ignorelist=['.', '__'],
        dirs_suffix_allowlist=None,
        dirs_suffix_ignorelist=None,
        include_line_numbers=True,
        include_contents=True
    ):
        """
        Reads the files in a directory.
        """
        def filter_names(
            names,
            prefix_allowlist=None,
            prefix_ignorelist=None,
            suffix_allowlist=None,
            suffix_ignorelist=None
        ):
            if prefix_allowlist and prefix_ignorelist:
                raise ValueError("Cannot specify both prefix_allowlist and prefix_ignorelist")
            
            if suffix_allowlist and suffix_ignorelist:
                raise ValueError("Cannot specify both suffix_allowlist and suffix_ignorelist")

            if prefix_allowlist:
                names = [
                    n for n in names if any(n.startswith(prefix) for prefix in prefix_allowlist)
                ]
            
            if suffix_allowlist:
                names = [
                    n for n in names if any(n.endswith(suffix) for suffix in suffix_allowlist)
                ]
            
            if prefix_ignorelist:
                names = [
                    n for n in names if not any(n.startswith(prefix) for prefix in prefix_ignorelist)
                ]
            
            if suffix_ignorelist:
                names = [
                    n for n in names if not any(n.endswith(suffix) for suffix in suffix_ignorelist)
                ]
            
            return names

        # Get all files in path and filter out ignored files
        file_paths = []
        for root, dirs, files in os.walk(path):
            dirs[:] = filter_names(
                dirs,
                prefix_allowlist=dirs_prefix_allowlist, 
                prefix_ignorelist=dirs_prefix_ignorelist, 
                suffix_allowlist=dirs_suffix_allowlist, 
                suffix_ignorelist=dirs_suffix_ignorelist
            )
            
            files = filter_names(
                files,
                prefix_allowlist=files_prefix_allowlist,
                prefix_ignorelist=files_prefix_ignorelist,
                suffix_allowlist=files_suffix_allowlist,
                suffix_ignorelist=files_suffix_ignorelist
            )

            file_paths += [os.path.join(root, file) for file in files]

        # Gather all file contents into a single string
        output = ""
        for file_path in file_paths:
            try:
                output += f"===== File: {file_path} =====\n"
                if include_contents:
                    output += _read_helper(
                        file_path, 
                        include_line_numbers=include_line_numbers
                    )
                    output += "\n\n"
            except Exception:
                logger.exception(f"Error reading file: {file_path}")
                output += f"Error reading file: {file_path}\n\n"

        return output


class CreateFile(Tool):
    def call(self, path: str, contents: str) -> str:
        """Creates a new file with the given contents. Fails if the file already exists.

        Args:
            path (str): The name of the file to write to.
            contents (str): The content to write to the file.
        """
        path = os.path.expanduser(path)

        # Raise error if the file already exists
        if os.path.exists(path):
            raise FileExistsError(f'The file "{path}" already exists')

        # Create the file
        file_path = pathlib.Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch(exist_ok=False)

        # Write the contents
        with open(path, "w") as f:
            f.write(contents)
        return f'Successfully wrote "{path}"'


class ReplaceLines(Tool):
    _return_result_to_agent = False

    def call(
        self,
        path: str, 
        text: str, 
        start_line: int, 
        end_line: int,
    ) -> str:
        """Replaces the lines `start_line` to `end_line` with `text` in 
        specified file. Uses one-based indexing, and the `end_line` is inclusive. 
        This operation must replace at least one line. When using `replace_lines()`, always consider the broader
        code context in the lines before and after your replacement. Use appropriate
        indentation in your `text` given the context of the surrounding code. 
        Consider the line that will follow your inserted text when choosing
        `end_line`. NOT THREAD-SAFE. Perform all file modifications in a sequential manner.

        Args:
            path (str): The name of the file to write to.
            text (str): The content to write to the file. Must end with a newline character.
            start_line (int): The line number of the start of the text block to replace.
            end_line (int): The line number of the end of the text block to replace. `end_line` is inclusive.
        """

        self.state.raise_error_if_this_file_has_not_been_read_since_it_was_last_updated(path)
        result = _edit_helper(path, text, start_line - 1, end_line)
        self.state.record_file_update(path)

        return result


class InsertLines(Tool):
    _return_result_to_agent = False

    def call(
        self,
        path: str, 
        text: str, 
        insert_line: int, 
    ) -> str:
        """Inserts `text` at line `insert_line`. Text that was previously on or
        below this line are shifted down. Uses one-based indexing.

        NOT THREAD-SAFE. Perform file modifications in a sequential manner to
        ensure thread safety. Do not modify the same file in parallel or with
        simultaneous asynchronous calls.

        When using `insert_lines()`, always consider the broader
        code context in the lines before and after your replacement. Use appropriate
        indentation in your `text` given the context of the surrounding code.

        Args:
            path (str): The name of the file to write to.
            text (str): The content to write to the file. Must end with a newline character.
            insert_line (int): The line number to insert the content at. -1 will insert at 
                the end of the file.
        """
        self.state.raise_error_if_this_file_has_not_been_read_since_it_was_last_updated(path)
        if insert_line == -1:
            result = _edit_helper(path, text, -1, -1)
        else:
            result = _edit_helper(path, text, insert_line - 1, insert_line - 1)
        self.state.record_file_update(path)

        return result


class DeleteLines(Tool):
    _return_result_to_agent = False
    
    def call(
        self,
        path: str, 
        start_line: int, 
        end_line: int
    ) -> str:
        """Deletes lines `start_line` to `end_line` from the file.
        Uses one-based indexing, and the `end_line` is inclusive.
        
        NOT THREAD-SAFE. Perform file modifications in a sequential manner to
        ensure thread safety. Do not modify the same file in parallel or with
        simultaneous asynchronous calls.            
                    
        Args:
            path (str): The name of the file to delete lines from.
            start_line (int): The start line number of the range to delete.
            end_line (int): The end line number of the range to delete.

        Returns:
            str: The contents of the file after the deletion. Use this return 
                value to verify that your intended changes were correctly apply.
        """

        self.state.raise_error_if_this_file_has_not_been_read_since_it_was_last_updated(path)
        result = _edit_helper(path, "", start_line - 1, end_line)
        self.state.record_file_update(path)

        return result


def _read_helper(
    path: str, 
    start_line: int = None, 
    end_line: int = None, 
    include_line_numbers: bool = True,
    error_if_missing: bool = True
) -> Optional[str]:
    
    path = os.path.expanduser(path)


    if not os.path.exists(path):
        if error_if_missing:
            raise FileNotFoundError(f'The file "{path}" does not exist')
        else:
            return None

    with open(path, "r") as f:
        lines = f.readlines()
        if include_line_numbers:
            lines = [f"{i+1:<4}|{line}" for i, line in enumerate(lines)]
        if start_line and end_line:
            lines = lines[start_line:end_line]
        
        output = "".join(lines)
        return output


def _edit_helper(path: str, text: str, start_line: int, end_line: int):
    """start_line and end_line use pythonic indexing, so the end_line is not inclusive."""
    path = os.path.expanduser(path)

    # Raise error if the file does not exist
    if not os.path.exists(path):
        raise FileExistsError(f'The file "{path}" does not exist')

    if text and not text[-1] == "\n":
        raise ValueError("The text must end with a newline character.")

    # Insert the text
    if not end_line:
        end_line = start_line

    with open(path, "r") as f:
        lines = f.readlines()
        if start_line < 0:
            start_line = len(lines) + start_line + 1

        lines[start_line:end_line] = text.splitlines(True)

    with open(path, "w") as f:
        f.writelines(lines)
    
    with open(path, "r") as f:
        result = f.read()

    return result