"""This script includes the HTMLLogger for handy html bug reports."""
import os
from time import time


class HTMLLogger:
    """Provide various logging functions to send html code for bug reports."""

    @classmethod
    def init(cls) -> None:
        """Create a initial html_logs.txt file and checks if saving is allowed."""
        if not os.path.exists("html_logs.txt"):
            with open("html_logs.txt", "w", encoding="utf-8") as file:
                file.writelines(
                    [
                        "## Info ################################################################################################\n",
                        "# This file has various html data WHICH MAY CONTAIN SENSITIVE DATA but it's very useful for debugging! #\n",
                        "# This file will be uploaded by you to the GitHub errors page if any warning or error occurred!         #\n"
                        "########################################################################################################\n",
                        "\n",
                        "## Format ############################################################################################\n"
                        "# timestamp-library function name-(if multiple data) id of html element-name of wanted data: Message #\n"
                        "######################################################################################################\n",
                    ]
                )

    @classmethod
    def log_missing_element(
        cls,
        html: str,
        function_name: str,
        element_index: str,
        attribute_name: str,
    ) -> None:
        """Log a missing html element.

        Parameters
        ----------
        html : str
            The pure html of the element
        function_name : str
            The name of the causative function.
        element_index : str
            The index of a element if the functions tries to get a set of data.
        attribute_name : str
            The name of the wanted data.
        """
        log = f"""
#--Start------------------------#
{int(time())}-{function_name}-{element_index}-{attribute_name}: Missing element!

*~~Element-HTML~~~~~~~~~~~~*

{html}
#--End--------------------------#

"""

        with open("html_logs.txt", "a", encoding="utf-8") as file:
            file.write(log)
