import os
from pathlib import Path

import requests
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]


class TelegramNotifier:

    def __init__(self):
        load_dotenv(
            BASE_DIR / ".env"
        )

        self.bot_token = os.getenv(
            "TELEGRAM_BOT_TOKEN"
        )

        self.chat_id = os.getenv(
            "TELEGRAM_CHAT_ID"
        )

        if not self.bot_token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN is not configured."
            )

        if not self.chat_id:
            raise ValueError(
                "TELEGRAM_CHAT_ID is not configured."
            )

        self.api_url = (
            f"https://api.telegram.org/bot"
            f"{self.bot_token}/sendMessage"
        )

    def send_message(
        self,
        message: str,
    ) -> bool:

        response = requests.post(
            self.api_url,
            json={
                "chat_id": self.chat_id,
                "text": message,
            },
            timeout=15,
        )

        if response.ok:
            return True

        print(
            "Telegram notification failed:"
        )
        print(response.text)

        return False