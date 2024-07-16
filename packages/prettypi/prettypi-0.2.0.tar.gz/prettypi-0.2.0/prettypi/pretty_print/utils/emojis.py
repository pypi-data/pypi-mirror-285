""" This module contains the Emoji enum class. """

from enum import Enum


class Emoji(Enum):
    """This class contains emojis that can be used in the pretty print module.

    **Example:**

    .. code-block:: python

            from pretty_print import Emoji
            print(f"{Emoji.SMILE} This is a smile emoji")

    """

    SMILE = "😊"
    SAD = "😢"
    HEART = "❤️"
    STAR = "⭐"
    FIRE = "🔥"
    THUMBS_UP = "👍"
    THUMBS_DOWN = "👎"
    CLAP = "👏"
    PARTY = "🎉"
    ROCKET = "🚀"
    BEER = "🍺"
    COFFEE = "☕"
    BOOK = "📖"
    COMPUTER = "💻"
    MONEY = "💰"
    LOCK = "🔒"
    KEY = "🔑"
    WARNING = "⚠️"
    CHECK = "✅"
    CROSS = "❌"
    QUESTION = "❓"
    EXCLAMATION = "❗"
    PLUS = "➕"
    MINUS = "➖"
    DIVIDE = "➗"
    MULTIPLY = "✖️"
    INFINITY = "♾️"
    HOURGLASS = "⌛"
    CALENDAR = "📅"
    CLOCK = "⏰"
    BELL = "🔔"
    MAGNIFYING_GLASS = "🔍"
    PENCIL = "✏️"
    PAPER = "📝"
    SCISSORS = "✂️"
    PAPERCLIP = "📎"
    ENVELOPE = "✉️"
    MAILBOX = "📬"
    TELEPHONE = "☎️"
    MOBILE_PHONE = "📱"
    CAMERA = "📷"
    VIDEO_CAMERA = "📹"
    TELEVISION = "📺"
    RADIO = "📻"
    COMPUTER_DISK = "💽"
    FLOPPY_DISK = "💾"
    CD = "💿"
    DVD = "📀"
    CAMERA_WITH_FLASH = "📸"
    MOVIE_CAMERA = "🎥"
    PROJECTOR = "📽️"
    FILM_FRAMES = "🎞️"
    TELEPHONE_RECEIVER = "📞"
    MOBILE_PHONE_RECEIVER = "📲"
    BELL_WITH_SLASH = "🔕"
    SPEAKER = "🔈"
    MUTE = "🔇"
    LOUDSPEAKER = "📢"
    MEGAPHONE = "📣"
    RADIO_BUTTON = "🔘"
    VIBRATION_MODE = "📳"
    MOBILE_PHONE_OFF = "📴"
    ANTENNA_BARS = "📶"
    PACKAGE = "📦"
    PYTHON = "🐍"
    INFORMATION = "ℹ️"

    def __str__(self):
        return self.value
