
from pathlib import Path
from prompt_toolkit import PromptSession
from rich.prompt import Confirm
from marvin.beta import Application
from marvin.utilities.asyncio import run_async, run_sync
from marvin.beta.assistants import Run
from typing import Union
import marvin

from toolshop.agent.instructions import get_coder_instructions
from toolshop.tools.terminal import shell_helper
from toolshop.tools.misc import all_tools

marvin.settings.openai.assistants.model = "gpt-4o"


class Agent(Application):
    def __init__(
        self, 
        coder_is_interactive: bool = True,
        context_path = None
    ):
        if context_path:
            with open(context_path, 'r') as f:
                user_context = f.read()
        else:
            user_context = ""

        instructions = get_coder_instructions(
            coder_is_interactive=coder_is_interactive,
            user_context=user_context
        )

        super().__init__(
            name="Agent",
            instructions=instructions,
            tools=all_tools(),  
        )

    def do(self, message: str = None, use_reflection: bool = True):
        self.say(message)
        
        if use_reflection:
            response = "made fixes"

            while "made fixes" in response.lower():
                thread = self.say(
                    "Re-read the files you have modified and fix any issues. If " 
                    "you had to fix any issues, respond 'made fixes'."
                )

                response = thread.messages[-1].content[0].text.value


    # for better type hinting
    def chat(
        self,
        initial_message: str = None,
        assistant_dir: Union[Path, str, None] = None,
        **kwargs,
    ):
        print(f'model: {self.model}')
        """Start a chat session with the assistant."""
        return run_sync(self.chat_async(initial_message, assistant_dir, **kwargs))

    async def chat_async(
        self,
        initial_message: str = None,
        assistant_dir: Union[Path, str, None] = None,
        **kwargs,
    ):
        """Async method to start a chat session with the assistant."""
        session = PromptSession()
        # send an initial message, if provided
        if initial_message is not None:
            await self.say_async(initial_message, **kwargs)
        while True:
            try:
                message = await run_async(
                    session.prompt,
                    message="➤ ",
                )

                # if the user types >, run the command in the shell
                if message == "":
                    continue
                elif message[0] == '>':
                    shell_helper(message.replace('>', ''), log_lines=True)
                # if the user types exit, ask for confirmation
                elif message in ["exit", "!exit", ":q", "!quit"]:
                    if Confirm.ask("[red]Are you sure you want to exit?[/]"):
                        break
                    continue
                # if the user types exit -y, quit right away
                elif message in ["exit -y", ":q!"]:
                    break
                else:
                    await self.say_async(message, **kwargs)
            except KeyboardInterrupt:
                break


    def post_run_hook(self, run: Run):
        if False:
            print('=== run.assistant.instructions ===')
            print(run.assistant.instructions)
            print('========================')
