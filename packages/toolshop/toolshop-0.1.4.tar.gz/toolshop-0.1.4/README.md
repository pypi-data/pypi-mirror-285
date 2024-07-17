# Toolshop
A Tool Framework for AI Agents

# Description
Toolshop is a general framework for developing tools used by LLM Agents. The
library ships with a standard set of tools that can be used by agents that
support tool-calling. Additionally, build your own custom tools by extending the
`Tool` class. By developing your tools with Toolshop, your tools inherit several
helpful features.
* __Configuration__: Toolshop tools are classes, not functions. This enables
  users to configure their tools for a particular session before passing them to
  the agent.
* __Confirmations__: Toolshop makes it easy to add required user confirmations
  to tool calls. Examples might include an agent editing sensitive files or
  provisioning cloud resources.
* __Constraints__: Tools can share state. This allows users to enforce
  constraints that require more context than the tool call arguments alone.
  Examples might include prevention of multiple parallel edits to the same file,
  requiring file reads before file edits, and cost-based limits on tool usage.

# Quick Start
Toolshop ships with a text-based assistant equipped with all of Toolshop's tools
and designed for developer productivity.

To install and chat, run:
```
pip install toolshop
ts chat
```

# Python Usage
```
from toolshop import all_tools
from marvin.beta import Application

app = Application(
    tools=all_tools()
)

app.say("Write mergesort.py")
app.say("Test mergesort.py")
```

# Motivation
Toolshop seeks to provide a tool development platform for AI engineers. The
motivation for this project is the belief that tool development is the best
place for AI developers to invest their time. Conversely, time spent augmenting
the reasoning and planning of existing assistant services is a risky area to
invest as a 3rd party developer.  This is simply because the reasoning and
planning capabilities of agentic AI, offered "out of the box" by companies such
as OpenAI and Anthropic, will continue to improve over time. Focusing
development time on enhancing these capabilities is potentially risky, as 
improvements to the base assistant services themselves will quickly render this work
obsolete.

The shift of companies like
[OpenAI](https://platform.openai.com/docs/guides/text-generation/completions-api)
and [Anthropic](https://docs.anthropic.com/claude/reference/complete_post) away
from simple text-completion models towards tool-enabled chat assistants
abstracts more from the user, thereby increasing the surface area for AI R&D. We
should expect these companies to continually improve their flagship assistant
services, with enhancements in reasoning and planning being obvious avenues for
development.

In contrast, tool development seems like a safe area for investment, and
Toolshop provides a solid foundation for this purpose. An agent will always
require a means to affect its environment or access information it was not
trained on. The tool-calling paradigm has emerged as a simple and effective
pattern to support these needs. Smarter models are able to use tools more
correctly and efficiently, so investments in solid tools will pay dividends as
models improve. Additionally, by enforcing guardrails in the tools rather than
in the process, the planning and reasoning process native to the underlying
agent remains unhindered.