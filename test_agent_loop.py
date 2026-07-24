import unittest
from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from call_function import available_functions
from main import run_agent


def make_response(message, usage=None) -> SimpleNamespace:
    return SimpleNamespace(
        choices=[SimpleNamespace(message=message)],
        usage=usage,
    )


def make_client(responses: list, histories: list[list]) -> SimpleNamespace:
    remaining_responses = responses.copy()

    def create(**kwargs):
        histories.append(list(kwargs["messages"]))
        return remaining_responses.pop(0)

    return SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=create),
        )
    )


class TestAgentLoop(unittest.TestCase):
    def test_appends_assistant_then_tool_message_before_next_call(self) -> None:
        tool_call = SimpleNamespace(
            id="call-1",
            function=SimpleNamespace(
                name="get_files_info",
                arguments='{"directory": "pkg"}',
            ),
        )
        assistant_tool_message = SimpleNamespace(
            content=None,
            tool_calls=[tool_call],
        )
        assistant_final_message = SimpleNamespace(
            content="The pkg directory contains calculator.py.",
            tool_calls=None,
        )
        histories: list[list] = []
        client = make_client(
            [
                make_response(assistant_tool_message),
                make_response(assistant_final_message),
            ],
            histories,
        )
        initial_messages = [
            {"role": "system", "content": "system"},
            {"role": "user", "content": "list pkg"},
        ]
        tool_message = {
            "role": "tool",
            "tool_call_id": "call-1",
            "content": "calculator.py",
        }
        output = StringIO()

        with (
            patch("main.call_function", return_value=tool_message),
            redirect_stdout(output),
        ):
            succeeded = run_agent(client, initial_messages)

        self.assertTrue(succeeded)
        self.assertEqual(
            histories[1],
            [
                {"role": "system", "content": "system"},
                {"role": "user", "content": "list pkg"},
                assistant_tool_message,
                tool_message,
            ],
        )
        self.assertEqual(
            initial_messages,
            [
                {"role": "system", "content": "system"},
                {"role": "user", "content": "list pkg"},
                assistant_tool_message,
                tool_message,
                assistant_final_message,
            ],
        )
        self.assertEqual(
            output.getvalue(),
            "Final response:\n"
            "The pkg directory contains calculator.py.\n",
        )

    def test_passes_tools_on_every_iteration(self) -> None:
        final_message = SimpleNamespace(content="Done", tool_calls=None)
        calls = []

        def create(**kwargs):
            calls.append(kwargs)
            return make_response(final_message)

        client = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=create),
            )
        )

        with redirect_stdout(StringIO()):
            run_agent(client, [])

        self.assertIs(calls[0]["tools"], available_functions)

    def test_verbose_mode_prints_tool_result(self) -> None:
        tool_call = SimpleNamespace(
            id="call-1",
            function=SimpleNamespace(name="write_file", arguments="{}"),
        )
        tool_message = SimpleNamespace(content=None, tool_calls=[tool_call])
        final_message = SimpleNamespace(content="Done", tool_calls=None)
        client = make_client(
            [make_response(tool_message), make_response(final_message)],
            [],
        )
        result_message = {
            "role": "tool",
            "tool_call_id": "call-1",
            "content": "wrote file",
        }
        output = StringIO()

        with (
            patch("main.call_function", return_value=result_message),
            redirect_stdout(output),
        ):
            run_agent(client, [], verbose=True)

        self.assertIn("-> wrote file\n", output.getvalue())

    def test_empty_tool_result_raises(self) -> None:
        tool_call = SimpleNamespace(
            id="call-1",
            function=SimpleNamespace(name="get_files_info", arguments="{}"),
        )
        tool_message = SimpleNamespace(content=None, tool_calls=[tool_call])
        client = make_client([make_response(tool_message)], [])

        with patch(
            "main.call_function",
            return_value={
                "role": "tool",
                "tool_call_id": "call-1",
                "content": "",
            },
        ):
            with self.assertRaisesRegex(
                RuntimeError, "Function call returned empty content"
            ):
                run_agent(client, [])

    def test_stops_after_iteration_limit(self) -> None:
        tool_call = SimpleNamespace(
            id="call-1",
            function=SimpleNamespace(name="get_files_info", arguments="{}"),
        )
        tool_message = SimpleNamespace(content=None, tool_calls=[tool_call])
        client = make_client(
            [make_response(tool_message), make_response(tool_message)],
            [],
        )
        result_message = {
            "role": "tool",
            "tool_call_id": "call-1",
            "content": "still working",
        }
        output = StringIO()

        with (
            patch("main.call_function", return_value=result_message),
            redirect_stdout(output),
        ):
            succeeded = run_agent(client, [], max_iterations=2)

        self.assertFalse(succeeded)
        self.assertEqual(
            output.getvalue(),
            "Error: Agent did not produce a final response after "
            "2 iterations\n",
        )


if __name__ == "__main__":
    unittest.main()
