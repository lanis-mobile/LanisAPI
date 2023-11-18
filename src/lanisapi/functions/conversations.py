"""This script includes classes and functions about the 'Nachrichten - Beta-Version' page."""

import json
from dataclasses import dataclass
from datetime import datetime, timedelta

from selectolax.parser import HTMLParser

from ..constants import LOGGER, URL
from ..helpers.cryptor import Cryptor
from ..helpers.request import Request


@dataclass
class Conversation:
    """A conversation.

    Parameters
    ----------
    id : str
        The `Uniquid` (as Lanis calls it) of a conversation.
    title : str
        The title.
    teacher : str
        The teacher in full name.
    creation_date : str
        When the conversation was created.
    newest_date : str
        When the newest comment was created.
    unread : bool
        If the user already marked it as `read`.
    special_receivers : list[str]
        Often these are groups of specific people,
        like `Alle SuS` or special People, like `Admin`.
    receivers : list[str]
        People with their full name and sometimes class.
    content : str
        The content.
    comments : None
        Currently always None because it wasn't implemented yet.
    """

    id: str
    title: str
    teacher: str
    creation_date: datetime
    newest_date: datetime
    unread: bool
    special_receivers: list[str]
    receivers: list[str]
    content: str
    comments = None


def _parse_date(date: str) -> datetime:
    """Sometimes Lanis doesn't return a full date but rather it returns 'heute UHRZEIT' oder 'gestern UHRZEIT'."""
    if "heute" in date:
        _today = datetime.now()
        parsed_newest_date = datetime.strptime(date, "heute %H:%M")
        parsed_newest_date = parsed_newest_date.replace(
            _today.year, _today.month, _today.day
        )
    elif "gestern" in date:
        _yesterday = datetime.now() - timedelta(1)
        parsed_newest_date = datetime.strptime(date, "gestern %H:%M")
        parsed_newest_date = parsed_newest_date.replace(
            _yesterday.year, _yesterday.month, _yesterday.day
        )
    else:
        parsed_newest_date = datetime.strptime(date, "%d.%m.%Y %H:%M")

    return parsed_newest_date


def _get_single_conversation(cryptor: Cryptor, id: str) -> dict[str, any]:
    """Get creation date and content of the conversation.

    Parameters
    ----------
    cryptor : Cryptor
        The class to encrypt or decrypt data.
    id : str
        The `Uniquid`. Cool typo.

    Returns
    -------
    dict[str, any]
        The data.

    Todo
    ----
    Get comments.
    """
    single_message_response = Request.post(
        URL.conversations,
        data={"a": "read", "uniqid": cryptor.encrypt(id)},
        params={"a": "read", "msg": id},
        headers={"X-Requested-With": "XMLHttpRequest"},
    )

    if not single_message_response:
        return None

    single_message = json.loads(
        cryptor.decrypt(single_message_response.json()["message"])
    )

    creation_date = _parse_date(single_message["Datum"])

    content = HTMLParser(single_message["Inhalt"]).text()

    LOGGER.info("Get single conversation: Success.")

    return {"creation_date": creation_date, "content": content}


def _get_conversations(cryptor: Cryptor, number: int = 5) -> list[Conversation]:
    """Return conversations from the "Nachrichten - Beta-Version".

    Parameters
    ----------
    cryptor : Cryptor
        The class to encrypt or decrypt data.
    number : int, optional
        The number of conversations to return, by default 5.
        To get all conversations use -1 but this will take a while and spam Lanis servers.

    Returns
    -------
    list[Conversation]
        The conversations in Conversation.
    """
    # script: /module/nachrichten/js/start.js
    response = Request.post(
        URL.conversations,
        data={"a": "headers", "getType": "visibleOnly", "last": "0"},
        headers={"X-Requested-With": "XMLHttpRequest"},
    )

    parsed_response: dict[str, any] = response.json()

    parsed_conversations: list[dict[str, any]] = json.loads(
        cryptor.decrypt(parsed_response["rows"])
    )

    conversations_list: list[Conversation] = []

    if number == -1:
        number = parsed_response["total"]

    for i in range(number):
        parsed_conversation = parsed_conversations[i]

        # Get full teacher name
        parsed_teacher = HTMLParser(parsed_conversation["SenderName"]).text()

        teacher = None

        # Sometimes there is just " , " for some reason so we need to get rid of it.
        if parsed_teacher != " , ":
            teacher = HTMLParser(parsed_conversation["SenderName"]).text().strip()

        # Get special receivers
        special_receivers = None
        try:
            if parsed_conversation["WeitereEmpfaenger"]:
                special_receivers = (
                    HTMLParser(parsed_conversation["WeitereEmpfaenger"])
                    .text()
                    .strip()
                    .split("   ")
                )
        except (IndexError, KeyError):
            # Just skip if none are found.
            pass

        # Get all receivers
        receivers = []

        for receiver in parsed_conversation["empf"]:
            parsed_receiver = HTMLParser(receiver).text().strip()

            # Sometimes receivers are empty so we need to skip them.
            if parsed_receiver:
                receivers.append(parsed_receiver)

        single_message_data = _get_single_conversation(
            cryptor, parsed_conversation["Uniquid"]
        )

        try:
            conversation = Conversation(
                id=parsed_conversation["Uniquid"],
                title=parsed_conversation["Betreff"],
                teacher=teacher,
                creation_date=single_message_data["creation_date"],
                newest_date=_parse_date(parsed_conversation["Datum"]),
                unread=bool(parsed_conversation["unread"]),
                special_receivers=special_receivers,
                receivers=receivers,
                content=single_message_data["content"],
            )
        except KeyError as err:
            LOGGER.error(f"Get conversations: KeyError found, most likely it's 'unread', idk why this happens, try again.\nMore details: {parsed_conversation}")
            raise err

        conversations_list.append(conversation)

    return conversations_list
