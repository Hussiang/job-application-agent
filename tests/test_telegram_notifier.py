import requests

from src.notifications.telegram_notifier import TelegramNotifier


def test_missing_credentials_returns_false(monkeypatch):
    monkeypatch.setattr(
        "src.notifications.telegram_notifier.load_dotenv",
        lambda *_: None,
    )
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

    notifier = TelegramNotifier()

    assert notifier.send_message("test") is False


def test_network_timeout_returns_false(monkeypatch):
    monkeypatch.setattr(
        "src.notifications.telegram_notifier.load_dotenv",
        lambda *_: None,
    )
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "test-chat")

    def raise_timeout(*args, **kwargs):
        raise requests.Timeout("simulated timeout")

    monkeypatch.setattr(
        "src.notifications.telegram_notifier.requests.post",
        raise_timeout,
    )

    notifier = TelegramNotifier()

    assert notifier.send_message("test") is False


def test_telegram_api_rejection_returns_false(monkeypatch):
    monkeypatch.setattr(
        "src.notifications.telegram_notifier.load_dotenv",
        lambda *_: None,
    )
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "test-chat")

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"ok": False, "description": "Rejected"}

    monkeypatch.setattr(
        "src.notifications.telegram_notifier.requests.post",
        lambda *args, **kwargs: FakeResponse(),
    )

    notifier = TelegramNotifier()

    assert notifier.send_message("test") is False


def test_successful_telegram_response_returns_true(monkeypatch):
    monkeypatch.setattr(
        "src.notifications.telegram_notifier.load_dotenv",
        lambda *_: None,
    )
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "test-chat")

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"ok": True, "result": {"message_id": 1}}

    monkeypatch.setattr(
        "src.notifications.telegram_notifier.requests.post",
        lambda *args, **kwargs: FakeResponse(),
    )

    notifier = TelegramNotifier()

    assert notifier.send_message("test") is True
