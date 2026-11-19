
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]


class TelegramNotifier:
    def __init__(self):
        load_dotenv(BASE_DIR / ".env")

        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

        self.api_url = (
            f"https://api.telegram.org/bot"
            f"{self.bot_token}/sendMessage"
            if self.bot_token
            else None
        )

    def send_message(self, message: str) -> bool:
        if not self.bot_token or not self.chat_id:
            print(
                "Telegram notification skipped: "
                "credentials are not configured."
            )
            return False

        try:
            response = requests.post(
                self.api_url,
                json={
                    "chat_id": self.chat_id,
                    "text": message,
                },
                timeout=15,
            )
            response.raise_for_status()

            result = response.json()

            if not result.get("ok", False):
                print(
                    "Telegram API rejected the notification."
                )
                return False

            return True

        except requests.RequestException as exc:
            print(
                "Telegram notification failed due to "
                f"a network or HTTP error: {exc}"
            )
            return False

        except ValueError:
            print(
                "Telegram notification failed: "
                "invalid API response."
            )
            return False
