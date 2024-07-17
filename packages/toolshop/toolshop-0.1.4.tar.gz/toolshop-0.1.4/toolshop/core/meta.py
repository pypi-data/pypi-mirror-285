from toolshop.core.base import Tool

class EnableResultToFile(Tool):
    def call(
            self,
            path: str
    ) -> str:
        """
        After this tool is called, the output of the following tool call will be written 
            to the specified file.

        Args:
            path (str): The path to the file where the output will be written.
        """
        self.path = path

    def post_call_hook(self):
        self.state.enable_result_to_file(self.path)


