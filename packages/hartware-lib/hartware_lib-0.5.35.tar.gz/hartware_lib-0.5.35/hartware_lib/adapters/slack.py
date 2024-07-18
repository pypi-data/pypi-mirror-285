import logging

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web.slack_response import SlackResponse

from hartware_lib.settings import SlackBotSettings

logger = logging.getLogger("hartware_lib.slack")


class SlackAdapter:
    def __init__(self, settings: SlackBotSettings):
        self.settings = settings
        self.client = WebClient(token=self.settings.api_token)

    def send(self, message: str, channel: str | None = None) -> SlackResponse:
        try:
            return self.client.chat_postMessage(
                channel=channel or self.settings.default_channel, text=message
            )
        except SlackApiError as exc:
            logger.warning(str(exc))

            raise exc
