def all_tools(framework='marvin'):
    from toolshop.tools.terminal import Shell, PythonExec, Browse
    from toolshop.tools.data import Sql, Histogram
    from toolshop.tools.file import make_file_tools
    from toolshop.core.meta import EnableResultToFile
    from toolshop.core.base import State
    from toolshop.tools.gcp import AuthenticateToGCP

    state = State()

    tools = [
        Shell(state=state),
        PythonExec(state=state),
        Browse(state=state),
        Sql(state=state),
        Histogram(state=state),
        EnableResultToFile(state=state),
        AuthenticateToGCP(state=state),
        *make_file_tools(state=state),
    ]
    
    if framework == 'marvin':
        return [t.to_marvin() for t in tools]
