from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, Mock

from parameterized import parameterized
from pydantic import AnyUrl

from mcp_server.resources.file_system import read_file, _determine_mime_type
from mcp_server.resources.model import TextContent


class TestResourcesFileSystem(TestCase):
    @parameterized.expand(
        [
            (Path("/etc/foo.py"), "text/x-python"),
            (Path("/etc/foo.rs"), "text/x-rust"),
            (Path("/etc/foo"), "text/plain"),
            (Path("/etc/foo.txt"), "text/plain"),
        ]
    )
    def test_determine_mime_type(self, path: Path, expected: str):
        actual = _determine_mime_type(path)
        self.assertEqual(actual, expected)

    def test_read_file(self):
        file = Path.cwd() / "tmp.txt"
        uri = AnyUrl(f"file://{file}")

        try:
            content = "foobar"
            expected = TextContent(mime_type="text/plain", text=content)

            with file.open(mode="w") as f:
                f.write(content)

            with patch("mcp_server.resources.file_system.all_resources", {uri: Mock()}):
                actual = read_file(uri)
                self.assertEqual(actual, expected)
        finally:
            file.unlink()

    def test_read_file_not_in_resources(self):
        with self.assertRaises(ValueError):
            read_file(AnyUrl("file:///not/in/resources.txt"))

    def test_read_file_not_on_filesystem(self):
        file = AnyUrl("file:///not/on/filesystem.txt")

        with patch("mcp_server.resources.file_system.all_resources", {file: Mock()}):
            with self.assertRaises(ValueError):
                read_file(file)
