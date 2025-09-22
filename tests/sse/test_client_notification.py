from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock

from mcp_server.context import RequestContext
from mcp_server.sse.client_notifications import progress_notification


class TestSSE_ClientNotification(IsolatedAsyncioTestCase):
    async def test_progress_notification_no_token(self):
        context = RequestContext(Mock(), Mock())
        self.assertIsNone(await progress_notification(context, 50, 100))
