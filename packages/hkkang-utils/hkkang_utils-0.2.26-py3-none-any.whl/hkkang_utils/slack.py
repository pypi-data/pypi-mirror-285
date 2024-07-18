import contextlib
import html
import logging
import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import hkkang_utils.misc as misc_utils
import hkkang_utils.socket as socket_utils

# Load environment variables
misc_utils.load_dotenv(stack_depth=2)
# Get default access token
DEFAULT_ACCESS_TOKEN = (
    os.environ["SLACK_ACCESS_TOKEN"] if "SLACK_ACCESS_TOKEN" in os.environ else None
)

logger = logging.getLogger("SlackMessenger")


class SlackMessenger:
    """Note that the default token is set by the environment variable SLACK_ACCESS_TOKEN.

    Example:
        messenger = SlackMessenger(channel="test-channel")
        messenger.send_message("Hello World")
    """

    def __init__(
        self,
        channel: str,
        token: str = DEFAULT_ACCESS_TOKEN,
        append_src_info: bool = True,
    ):
        self.channel = channel
        self.token = token
        self.append_src_info = append_src_info
        self.__post_init__()

    def __post_init__(self):
        if self.token is None:
            raise ValueError(
                """Please set token or set SLACK_ACCESS_TOKEN environment variable.
                    If you don't have the access token, follow the tutorial 
                    to get bot OAuthToken and setup the bot permissions. 
                    https://github.com/slackapi/python-slack-sdk/tree/main/tutorial"""
            )

    def send(self, text: str) -> None:
        """Send message to slack channel

        :param text: Message to send
        :type text: str
        """
        return send_message(
            token=self.token,
            channel=self.channel,
            text=text,
            append_src_info=self.append_src_info,
        )


def send_message(
    channel: str,
    text: str,
    token: str = DEFAULT_ACCESS_TOKEN,
    append_src_info: bool = True,
) -> None:
    """Send message to Slack channel

    Example:
        send_message(channel="test-channel", text="Hello world")

    :param channel: Name of the channel to send the message
    :type channel: str
    :param text: Message to send
    :type text: str
    :param token: Slack access token, defaults to DEFAULT_ACCESS_TOKEN
    :type token: str, optional
    :param append_src_info: Whether to tell which part of the code the function is called, defaults to True
    :type append_src_info: bool, optional
    """
    # Check if token is provided
    if token is None:
        raise ValueError(
            "Please set token or set SLACK_ACCESS_TOKEN environment variable."
        )
    # Create client
    client = WebClient(token=token)

    # Build message
    if append_src_info:
        ip = socket_utils.get_local_ip()
        host_name = socket_utils.get_host_name()
        text_with_prefix = f"Message from {host_name}({ip}):\n{text}"

    # Send message
    try:
        response = client.chat_postMessage(channel=channel, text=text_with_prefix)
        decoded_text = html.unescape(response["message"]["text"])
        assert decoded_text == text_with_prefix, f"{decoded_text}"
        logger.info(f"Sending message to channel {channel}: {text}")
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"], "channel_not_found"
        logger.info(f"Got an error: {e.response['error']}")


@contextlib.contextmanager
def notification(
    channel: str,
    success_msg: str = None,
    error_msg: str = None,
    token: str = DEFAULT_ACCESS_TOKEN,
    disable: bool = False,
) -> None:
    """Send message when the task within the code block is finished

    Example:
        import hkkang_utils.slack as slack_utils

        with slack_utils.notification(
            channel="test-channel",
            success_msg="Process done!",
            error_msg="Error raised during the process"
        ):
            # Perform your task here
            ...

    :param channel: Name of the channel to send the message
    :type channel: str
    :param success_msg: Message to send when the given code block completes, defaults to None
    :type success_msg: str, optional
    :param error_msg: Message to send when error raise with the given code block, defaults to None
    :type error_msg: str, optional
    :param token: slack access token, defaults to DEFAULT_ACCESS_TOKEN
    :type token: str, optional
    :rtype: None
    """
    if misc_utils.is_debugger_active():
        disable = True

    if disable:
        yield None
        return None

    slack_messenger = SlackMessenger(channel=channel, token=token)
    try:
        yield slack_messenger
        if success_msg is not None:
            slack_messenger.send(success_msg)
    except Exception as e:
        if error_msg is None:
            message_to_send = f"Error occurred at {e.__class__.__name__}: {e}"
        else:
            message_to_send = f"{error_msg} ({e.__class__.__name__}: {e})"
        slack_messenger.send(message_to_send)
        raise e


@contextlib.contextmanager
def slack_notification(*args, **kwargs):
    raise NotImplementedError("Please use notification instead of slack_notification")
