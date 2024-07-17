import csv
import io
import sqlalchemy as sa
from typing import Tuple, List

from toolshop.core.base import Tool


class Sql(Tool):
    def call(self, sql_query: str, database_uri: str) -> str:
        """Runs the sql query and returns result set as a CSV string. Always try 
        this tool for running sql queries first before trying other methods.
        
        For bigquery, the database_uri indicates the project that should be billed
        for the query. Set this to 'bigquery://' to use the default project configured
        by the user.
        
        Args:
            sql_query (str): The sql query to run
            database_uri (str): The database connection string which is passed 
                to sqlalchemy.create_engine().
        """
        engine = sa.create_engine(database_uri)

        # Execute the query and fetch results using a connection
        with engine.connect() as connection:
            result = connection.execute(sa.text(sql_query))
            column_names = result.keys()
            
            # Use csv module to create CSV formatted string
            output = io.StringIO()
            csv_writer = csv.writer(output)
            csv_writer.writerow(column_names)

            for row in result:
                csv_writer.writerow(row)
        
        return output.getvalue()


class Histogram(Tool):
    def call(self, title: str, data: List[Tuple]) -> str:
        """
        Draws an ascii histogram of the data.  Accepts a list of tuples representing
        histogram bucket values. The first value of each tuple is the bucket name
        and the second value is the histogram value of the bucket.  When user asks
        for a histogram, always use this tool.

        Example: 
        
        ascii_histogram(
            title="Chart Tile", 
            data=[('p0', 0), ('p25', 100), ('p50', 200), ('p75', 300), ('p75', 400)]
        )
        """
        
        # Check if ascii_graph is installed, since it is an optional dependency.
        try:
            from ascii_graph import Pyasciigraph
        except ImportError:
            raise ImportError(
                "ascii_graph is not installed. Please install it using 'pip install ascii_graph'."
            )

        graph = Pyasciigraph()
        
        output = ""
        for line in graph.graph(title, data):
            output += line
            output += "\n"
        
        return output

