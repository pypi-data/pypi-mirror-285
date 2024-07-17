import click
from toolshop.agent.agent import Agent

@click.group()
@click.pass_context
def toolshop(ctx):
    """Toolshop Command Line Interface"""
    if ctx.invoked_subcommand is None:
        click.echo("Welcome to Toolshop!")

@toolshop.command()
@click.option('--context', help='Path to context file', default=None)
def chat(context: str = None):
    """Start the chat with Agent."""
    app = Agent(coder_is_interactive=True, context_path=context)
    app.chat()

@toolshop.command()
@click.argument('instructions')
def do(instructions: str):
    """Send instructions for Agent to execute non-interactively."""
    app = Agent(coder_is_interactive=False)
    app.do(instructions)
