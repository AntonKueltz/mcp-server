from unittest import TestCase

from mcp_server.utilities.pagination import PAGE_SIZE, create_next_cursor, parse_cursor


class TestUtilitiesPagination(TestCase):
    def test_next_and_parse_cursor(self):
        cursor = create_next_cursor(None)
        start, end = parse_cursor(cursor)

        self.assertEqual(start, PAGE_SIZE)
        self.assertEqual(end, 2 * PAGE_SIZE)

        cursor = create_next_cursor(cursor)
        start, end = parse_cursor(cursor)

        self.assertEqual(start, 2 * PAGE_SIZE)
        self.assertEqual(end, 3 * PAGE_SIZE)
