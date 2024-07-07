# tests/test_code_management.py

import unittest
import os
import ast
from unittest.mock import MagicMock
from core import code_management as cm

class TestCodeManagement(unittest.TestCase):

    def test_generate_code_from_description(self):
        cm.assist = MagicMock()
        cm.assist.ask_question_memory.return_value = "<code>\n```python\nprint('Hello, World!')\n```"
        description = "prints 'Hello, World!'"
        code = cm.generate_code_from_description(description)
        self.assertIn("print('Hello, World!')", code)

    def test_update_code(self):
        cm.assist = MagicMock()
        cm.assist.ask_question_memory.return_value = "<code>\n```python\nprint('Hello, World!')\n```"
        description = "prints 'Hello, World!'"
        filename = 'test_file.py'
        cm.update_code(description, filename)
        with open(filename, 'r') as file:
            code = file.read()
        self.assertIn("print('Hello, World!')", code)
        os.remove(filename)

    def test_create_file(self):
        cm.assist = MagicMock()
        cm.assist.ask_question_memory.return_value = "<code>\n```python\nprint('Hello, World!')\n```"
        description = "prints 'Hello, World!'"
        filename = 'test_create_file.py'
        result = cm.create_file(description, filename)
        self.assertTrue(os.path.exists(filename))
        with open(filename, 'r') as file:
            content = file.read()
        self.assertIn("print('Hello, World!')", content)
        os.remove(filename)

    def test_check_syntax_errors(self):
        code = "print('Hello, World!')"
        errors = cm.check_syntax_errors(code)
        self.assertEqual(errors, [])

        code_with_error = "print('Hello, World!'"
        errors = cm.check_syntax_errors(code_with_error)
        self.assertNotEqual(errors, [])

    def test_suggest_fixes_for_errors(self):
        cm.assist = MagicMock()
        cm.assist.ask_question_memory.return_value = "<code>\n```python\nprint('Hello, World!')\n```"
        code_with_error = "print('Hello, World!'"
        errors = cm.check_syntax_errors(code_with_error)
        fixed_code = cm.suggest_fixes_for_errors(errors, code_with_error)
        self.assertNotIn("SyntaxError", fixed_code)

    def test_check_and_fix_file(self):
        cm.assist = MagicMock()
        cm.assist.ask_question_memory.return_value = "<code>\n```python\nprint('Hello, World!')\n```"
        filename = 'test_check_and_fix_file.py'
        with open(filename, 'w') as file:
            file.write("print('Hello, World!'")
        recorder = MagicMock()
        recorder.text.return_value = "yes"
        result = cm.check_and_fix_file(filename, recorder)
        self.assertIn("Errors in test_check_and_fix_file.py have been fixed.", result)
        os.remove(filename)

    def test_check_and_fix_project(self):
        cm.assist = MagicMock()
        cm.assist.ask_question_memory.return_value = "<code>\n```python\nprint('Hello, World!')\n```"
        filename1 = 'test_file1.py'
        filename2 = 'test_file2.py'
        with open(filename1, 'w') as file:
            file.write("print('Hello, World!'")
        with open(filename2, 'w') as file:
            file.write("print('Hello, World!'")
        recorder = MagicMock()
        recorder.text.return_value = "yes"
        result = cm.check_and_fix_project(recorder)
        self.assertIn("Errors in test_file1.py have been fixed.", result)
        self.assertIn("Errors in test_file2.py have been fixed.", result)
        os.remove(filename1)
        os.remove(filename2)

if __name__ == '__main__':
    unittest.main()
