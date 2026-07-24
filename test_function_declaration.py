import unittest

from call_function import available_functions
from functions.get_file_content import schema_get_file_content
from functions.get_files_info import schema_get_files_info
from functions.run_python_file import schema_run_python_file
from functions.write_file import schema_write_file


class TestFunctionDeclaration(unittest.TestCase):
    def test_get_files_info_schema(self) -> None:
        function_schema = schema_get_files_info["function"]
        properties = function_schema["parameters"]["properties"]

        self.assertEqual(schema_get_files_info["type"], "function")
        self.assertEqual(function_schema["name"], "get_files_info")
        self.assertEqual(function_schema["parameters"]["type"], "object")
        self.assertIn("directory", properties)
        self.assertNotIn("working_directory", properties)

    def test_get_file_content_schema(self) -> None:
        function_schema = schema_get_file_content["function"]
        parameters = function_schema["parameters"]

        self.assertEqual(function_schema["name"], "get_file_content")
        self.assertEqual(parameters["properties"]["file_path"]["type"], "string")
        self.assertEqual(parameters["required"], ["file_path"])
        self.assertNotIn("working_directory", parameters["properties"])

    def test_run_python_file_schema(self) -> None:
        function_schema = schema_run_python_file["function"]
        parameters = function_schema["parameters"]
        properties = parameters["properties"]

        self.assertEqual(function_schema["name"], "run_python_file")
        self.assertEqual(parameters["required"], ["file_path"])
        self.assertEqual(properties["file_path"]["type"], "string")
        self.assertEqual(properties["args"]["type"], "array")
        self.assertEqual(properties["args"]["items"], {"type": "string"})
        self.assertNotIn("args", parameters["required"])
        self.assertNotIn("working_directory", properties)

    def test_write_file_schema(self) -> None:
        function_schema = schema_write_file["function"]
        parameters = function_schema["parameters"]
        properties = parameters["properties"]

        self.assertEqual(function_schema["name"], "write_file")
        self.assertEqual(properties["file_path"]["type"], "string")
        self.assertEqual(properties["content"]["type"], "string")
        self.assertEqual(parameters["required"], ["file_path", "content"])
        self.assertNotIn("working_directory", properties)

    def test_available_functions_contains_all_four_schemas(self) -> None:
        self.assertEqual(
            available_functions,
            [
                schema_get_files_info,
                schema_get_file_content,
                schema_run_python_file,
                schema_write_file,
            ],
        )


if __name__ == "__main__":
    unittest.main()
