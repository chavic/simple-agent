import unittest
from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace
from unittest.mock import Mock, patch

import call_function as call_function_module
from call_function import call_function


def make_tool_call(
    function_name: str, arguments: str = "{}", tool_call_id: str = "call-1"
) -> SimpleNamespace:
    return SimpleNamespace(
        id=tool_call_id,
        function=SimpleNamespace(name=function_name, arguments=arguments),
    )


class TestCallFunction(unittest.TestCase):
    def test_dispatches_function_and_injects_working_directory(self) -> None:
        function = Mock(return_value="directory contents")
        tool_call = make_tool_call(
            "get_files_info", '{"directory": "pkg"}', "call-123"
        )
        output = StringIO()

        with (
            patch.dict(
                call_function_module.function_map,
                {"get_files_info": function},
            ),
            redirect_stdout(output),
        ):
            result = call_function(tool_call, verbose=True)

        function.assert_called_once_with(
            directory="pkg", working_directory="./calculator"
        )
        self.assertEqual(
            result,
            {
                "role": "tool",
                "tool_call_id": "call-123",
                "content": "directory contents",
            },
        )
        self.assertEqual(
            output.getvalue(),
            " - Calling function: get_files_info({'directory': 'pkg'})\n",
        )

    def test_working_directory_cannot_be_overridden(self) -> None:
        function = Mock(return_value="safe")
        tool_call = make_tool_call(
            "get_file_content",
            '{"file_path": "main.py", "working_directory": "/tmp"}',
        )

        with (
            patch.dict(
                call_function_module.function_map,
                {"get_file_content": function},
            ),
            redirect_stdout(StringIO()),
        ):
            call_function(tool_call)

        function.assert_called_once_with(
            file_path="main.py", working_directory="./calculator"
        )

    def test_unknown_function_returns_tool_error(self) -> None:
        tool_call = make_tool_call("delete_everything", tool_call_id="call-404")
        output = StringIO()

        with redirect_stdout(output):
            result = call_function(tool_call)

        self.assertEqual(
            result,
            {
                "role": "tool",
                "tool_call_id": "call-404",
                "content": "Error: Unknown function: delete_everything",
            },
        )
        self.assertEqual(
            output.getvalue(),
            " - Calling function: delete_everything\n",
        )


if __name__ == "__main__":
    unittest.main()
