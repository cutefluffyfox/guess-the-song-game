from __future__ import annotations

import re
import hashlib
from datetime import datetime, timedelta

from scripts.game_rules import TEXT_TO_EMOTE


class MessageProcessor:
    keyword: str
    link: str

    def __init__(self, keyword: str, link: str):
        self.keyword = keyword
        self.link = link

    def process(self, text: str) -> str:
        raise NotImplementedError('Each processor must be implemented')

    def __len__(self) -> int:
        return len(self.keyword)


class CharacterReplaceProcessor(MessageProcessor):
    """Replaces all occurrences of `keyword` in text. Including sub-words"""
    def process(self, text: str) -> str:
        return text.replace(self.keyword, self.link)


class WordReplaceProcessor(MessageProcessor):
    """Replaces all occurrences of `keyword` in text. Only if it's a separate word"""

    punctuation: str = '\n\t ,.?![](){}:\''

    def __init__(self, keyword: str, link: str):
        super().__init__(keyword=keyword, link=link)

    def process(self, text: str) -> str:
        # TODO: optimize this abomination
        text = ' ' + text + ' '  # TODO: swap back to regex & make it case-insensitive
        for start in self.punctuation:
            for end in self.punctuation:
                while start + self.keyword + end in text:
                    text = text.replace(start + self.keyword + end, start + self.link + end)
        return text.strip()


class Message:
    text: str
    time: datetime
    author: str
    kind: str
    visible: bool

    def __init__(self, text: str, username: str, kind: str = 'message'):
        self.text = text
        self.author = username
        self.kind = kind
        self.time = datetime.now()
        self.visible = True
        if self.text is None or self.author is None:
            raise ValueError(f'WHAT: {username} & {text}')

    @property
    def id(self) -> int:
        return hash(self)

    def __hash__(self) -> int:
        return int(hashlib.sha256((self.author + self.text + str(self.time.timestamp())).encode('utf-8')).hexdigest(), 16)

    def __eq__(self, other: int or Message) -> bool:
        return hash(self) == hash(other)  # hash(int) == int

    def __str__(self) -> str:
        return self.text


class Chat:
    messages: list[Message]
    processors: list[MessageProcessor]

    def __init__(self):
        self.messages = list()

        # initialize processors from TEXT_TO_EMOTE variable
        self.processors = []
        for keyword, link in sorted(TEXT_TO_EMOTE.items(), key=len, reverse=True):
            html = f'<img class="emo-ticon" src="{link}" title="{keyword}">'
            if isinstance(keyword, str):
                self.processors.append(CharacterReplaceProcessor(keyword=keyword, link=html))
            else:
                raise NotImplementedError('Non-string keywords are not supported yet')

    def add_message(self, text: str, username: str, kind: str = 'message') -> Message:
        message = Message(text=text, username=username, kind=kind)
        self.messages.append(message)
        return message

    def process(self, message: Message or str, safe: bool = False) -> str:
        message = str(message)
        if safe:
            message = message.replace('<', '&lt;').replace('>', '&gt;')
        for processor in self.processors:
            message = processor.process(message)
        return message

    def find_message(self, message_id: int) -> Message or None:
        for message in self.messages:
            if message.id == message_id:
                return message

    def get_last_messages(self, username: str, time_window: timedelta = timedelta(minutes=10)) -> list[Message]:
        now = datetime.now()
        messages: list[Message] = []
        for message in self.messages[::-1]:
            if message.time + time_window < now:
                break
            if message.author == username:
                messages.append(message)
        return messages[::-1]
