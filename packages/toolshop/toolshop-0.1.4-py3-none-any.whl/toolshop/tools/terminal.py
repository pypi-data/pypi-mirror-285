import httpx
import subprocess
from typing import List

from toolshop.core.logging import logger
from toolshop.core.base import Tool


class PythonExec(Tool): 
    def call(self, code: str, vars: List[str]):
        """
        Executes python code on your local machine using exec().  Returns 
        the requested variables from the scope used by exec().
        
        Args:
            code (str): String of python code to execute
            vars (List[str]): List of variable names to return from the scope

        ```
        >>> get_vars_from_exec("a = 1+1", ["a"])
        {'a': 2}
        ```
        """   
        scope = {}
        exec(code, scope)
        return {k: v for k, v in scope.items() if k in vars}


class Shell(Tool):
    def call(self, command: str):
        """
        Execute the given shell command and return output. If you 
        get errors, try using the --help flag on the command you 
        are running.

        Args:
            command (str): A shell command to execute.

        """
        output = shell_helper(
            command, 
            log_lines=True,
            include_exit_code=True
        )

        return output


def shell_helper(
    command: str, 
    log_lines: bool = False, 
    include_exit_code: bool = False
):
    # Create the subprocess with both stdout and stderr being piped
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output = ''

    # Stream stdout
    for line in iter(process.stdout.readline, b''):
        decoded_line = line.decode()
        if log_lines:
            if decoded_line[-1] == '\n':
                decoded_line = decoded_line[:-1]
                
            logger.info(decoded_line)
        output += decoded_line

    process.stdout.close()

    # Capture stderr
    error = process.stderr.read().decode()
    if error:
        if log_lines:
            logger.info(error)
        output += error

    process.stderr.close()

    # Wait for the process to finish and get the exit code
    return_code = process.wait()

    if include_exit_code:
        # Add explicit exit code notice to the output
        exit_message = f"[exit code {return_code}]"
        logger.info(exit_message)
        output += exit_message + '\n'


    return output

class Browse(Tool):
    def call(self, url: str):
        """
        Fetch the contents of a webpage.

        Args:
            url (str): The URL of the webpage to fetch.

        """

        logger.info("=== browse() ===")
        logger.info(f"url: {url}")
        response = httpx.get(url)

        logger.info("response:")
        logger.info(response.text)
        logger.info("================")

        return response.text
