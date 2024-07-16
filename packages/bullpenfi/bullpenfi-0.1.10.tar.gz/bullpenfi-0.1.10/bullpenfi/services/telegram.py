from datetime import datetime, timedelta, timezone
import emoji
import json
import logging
import sys
import re
import unicodedata
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import (
    MessageEntityBold,
    MessageEntityItalic,
    MessageEntityTextUrl,
    MessageEntityCustomEmoji,
    MessageEntityUnderline,
    MessageEntityStrike,
    MessageEntityCode,
    MessageEntityPre,
)
from bullpenfi.auth import authenticator

# Configure the root logger to display logs of INFO level and above
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)  # Add StreamHandler to output to stdout
    ],
)

logger = logging.getLogger(__name__)


class TelegramService:
    """A class to interact with Telegram API."""

    def __init__(self, api_key, api_id, api_hash, phone, username):
        """
        Initialize the TelegramService.

        Args:
            api_key (str): The API key for authentication.
            api_id (str): The Telegram API ID.
            api_hash (str): The Telegram API hash.
            phone (str): The phone number associated with the Telegram account.
            username (str): The username of the Telegram account.
        """
        authenticator.authenticate(api_key)
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.username = username
        self.client = TelegramClient(phone, api_id, api_hash)

    class DateTimeEncoder(json.JSONEncoder):
        """Custom JSON encoder for datetime objects."""

        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()

            if isinstance(o, bytes):
                return list(o)

            return json.JSONEncoder.default(self, o)

    async def get_tg_messages_for_account(
        self, telegram_url: str, timeframe_hours: int
    ):
        """
        Retrieves Telegram messages for a given account within a specified timeframe.

        Args:
            telegram_url (str): The URL of the Telegram channel or user.
            timeframe_hours (int): The number of hours to look back for messages.

        Returns:
            list: A list of dictionaries containing the retrieved messages.
        """
        async with self.client:
            await self.client.start()
            logger.info("Client Created")

            if not await self.client.is_user_authorized():
                await self.client.send_code_request(self.phone)
                try:
                    await self.client.sign_in(self.phone, input("Enter the code: "))
                except SessionPasswordNeededError:
                    await self.client.sign_in(password=input("Password: "))

            entity = telegram_url if telegram_url.isdigit() else telegram_url
            my_channel = await self.client.get_entity(entity)

            offset_id = 0
            limit = 100
            all_messages = []
            total_messages = 0
            try:
                timeframe_hours = int(timeframe_hours)
            except ValueError:
                logger.error(
                    "Invalid timeframe_hours: %s. Using default of 24 hours.",
                    timeframe_hours,
                )
                timeframe_hours = 24

            cutoff_date = datetime.now(timezone.utc) - timedelta(hours=timeframe_hours)

            while True:
                logger.info(
                    "Current Offset ID is: %d; Total Messages limit (0 for no limit): %d",
                    offset_id,
                    total_messages,
                )
                history = await self.client(
                    GetHistoryRequest(
                        peer=my_channel,
                        offset_id=offset_id,
                        offset_date=None,
                        add_offset=0,
                        limit=limit,
                        max_id=0,
                        min_id=0,
                        hash=0,
                    )
                )
                if not history.messages:
                    break
                messages = history.messages
                for message in messages:
                    if message.date < cutoff_date:
                        logger.info(
                            "Reached cutoff date. Total messages: %d", total_messages
                        )
                        return all_messages
                    message_dict = message.to_dict()
                    if message.entities:
                        message_dict["text"] = self.remove_unicode_characters(
                            self.reconstruct_message_with_links(message)
                        )
                    all_messages.append(message_dict)
                    total_messages += 1
                if len(messages) < limit:
                    break
                offset_id = messages[len(messages) - 1].id

            logger.info(
                "Finished retrieving messages. Total messages: %d", total_messages
            )

            return all_messages

    def reconstruct_message_with_links(self, message):
        """Reconstructs the message text with embedded links and formatting in Markdown format.

        Args:
            message (Message): The message object from Telegram.

        Returns:
            str: The message text with embedded links and formatting in Markdown format.
        """
        text = message.message
        entities = sorted(message.entities or [], key=lambda e: e.offset)

        markdown_parts = []
        last_offset = 0
        emoji_offset = 0

        # Pre-calculate emoji offsets
        emoji_positions = [e["match_start"] for e in emoji.emoji_list(text)]

        for entity in entities:
            logger.debug("Processing entity: %s", type(entity).__name__)
            logger.debug("Entity offset: %d, length: %d", entity.offset, entity.length)

            # Calculate emoji offset for this entity
            emoji_offset = sum(1 for pos in emoji_positions if pos < entity.offset)

            # Add text before the entity
            markdown_parts.append(text[last_offset : entity.offset - emoji_offset])

            # Extract entity text
            entity_text = text[
                entity.offset
                - emoji_offset : entity.offset
                - emoji_offset
                + entity.length
            ]

            # Process the entity
            if isinstance(entity, MessageEntityBold):
                markdown_parts.append(f"**{entity_text}**")
            elif isinstance(entity, MessageEntityItalic):
                markdown_parts.append(f"*{entity_text}*")
            elif isinstance(entity, MessageEntityUnderline):
                markdown_parts.append(f"<u>{entity_text}</u>")
            elif isinstance(entity, MessageEntityStrike):
                markdown_parts.append(f"~~{entity_text}~~")
            elif isinstance(entity, MessageEntityCode):
                markdown_parts.append(f"`{entity_text}`")
            elif isinstance(entity, MessageEntityPre):
                markdown_parts.append(f"```\n{entity_text}\n```")
            elif isinstance(entity, MessageEntityTextUrl):
                # Preserve newlines within the link text
                link_text = entity_text.replace("\n", "\\n")
                markdown_parts.append(f"[{link_text}]({entity.url})")
            elif isinstance(entity, MessageEntityCustomEmoji):
                markdown_parts.append(entity_text)
                emoji_offset += 1  # Add 1 more to the offset for custom emojis
            else:
                markdown_parts.append(entity_text)

            last_offset = entity.offset + entity.length - emoji_offset

        # Add any remaining text
        markdown_parts.append(text[last_offset:])

        markdown_text = "".join(markdown_parts)

        # Replace new line characters with Markdown line breaks, including those within links
        markdown_text = markdown_text.replace("\n", "<br />").replace("\\n", "<br />")

        logger.debug("Final markdown text: %s...", markdown_text[:100])

        return markdown_text

    def remove_unicode_characters(self, text):
        """
        Remove Unicode characters and escape sequences from a string.

        Args:
            text (str): The input text.

        Returns:
            str: The text with Unicode characters and escape sequences removed.
        """
        # Remove Unicode escape sequences
        text = re.sub(r"\\u[0-9a-fA-F]{4}", "", text)

        # Remove actual Unicode characters
        text = "".join(char for char in text if ord(char) < 128)

        # Optional: Normalize remaining text (e.g., convert accented characters)
        text = (
            unicodedata.normalize("NFKD", text)
            .encode("ASCII", "ignore")
            .decode("ASCII")
        )

        return text
