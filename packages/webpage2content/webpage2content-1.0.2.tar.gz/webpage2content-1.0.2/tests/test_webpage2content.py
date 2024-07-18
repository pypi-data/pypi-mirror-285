# Make the unit test runner be able to find the package.
# It's a dirty solution but it's fine for small projects.
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from unittest.mock import patch, MagicMock
from webpage2content.webpage2content_impl import webpage2content


class TestWebpage2Content(unittest.TestCase):

    @patch("webpage2content.webpage2content_impl._get_page_as_markdown")
    @patch("webpage2content.webpage2content_impl._call_gpt")
    def test_exit_if_markdown_is_empty(self, mock_call_gpt, mock_get_page_as_markdown):
        # Arrange
        mock_get_page_as_markdown.return_value = ""
        mock_openai_client = MagicMock()

        # Act
        result = webpage2content("https://www.example.com", mock_openai_client)

        # Assert
        self.assertIsNone(result)
        self.assertEqual(mock_call_gpt.call_count, 0)

    @patch("webpage2content.webpage2content_impl._get_page_as_markdown")
    @patch("webpage2content.webpage2content_impl._call_gpt")
    def test_exit_if_not_human_readable(self, mock_call_gpt, mock_get_page_as_markdown):
        # Arrange
        mock_get_page_as_markdown.return_value = "Sample markdown content"
        mock_call_gpt.side_effect = [
            "Page description response",
            "No",
            "1. Line 1 content\n2. Line 2 content discard\n3. Line 3 content",
        ]
        mock_openai_client = MagicMock()

        # Act
        result = webpage2content("https://www.example.com", mock_openai_client)

        # Assert
        self.assertIsNone(result)
        self.assertEqual(mock_call_gpt.call_count, 2)

    @patch("webpage2content.webpage2content_impl._get_page_as_markdown")
    @patch("webpage2content.webpage2content_impl._call_gpt")
    def test_filter_by_line_number(self, mock_call_gpt, mock_get_page_as_markdown):
        # Arrange
        mock_get_page_as_markdown.return_value = """
Foo
Bar
Baz
Qux

Zeep
Threep
"""
        mock_call_gpt.side_effect = [
            "Page description response",
            "Yes",
            """
1. Content - keep
2. Noise - discard
3. Noise - discard
4. Content - keep
6. Content - keep
7. Content - keep
""",
        ]
        mock_openai_client = MagicMock()

        # Act
        result = webpage2content("https://www.example.com", mock_openai_client)

        # Assert
        self.assertEqual(result, "Foo\n\nQux\n\nZeep\nThreep")
        self.assertEqual(mock_call_gpt.call_count, 3)


if __name__ == "__main__":
    unittest.main()
