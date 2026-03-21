import sys
from unittest.mock import Mock

import pytest

import wyoming_openai.__main__ as main_module
from wyoming_openai.__main__ import main


@pytest.mark.asyncio
async def test_main_rejects_non_object_stt_extra_body_env(monkeypatch, capsys):
    monkeypatch.setenv("STT_EXTRA_BODY", '["not-an-object"]')
    monkeypatch.setattr(sys, "argv", ["wyoming_openai"])

    with pytest.raises(SystemExit) as exc_info:
        await main()

    assert exc_info.value.code == 2
    assert "Invalid STT extra body: expected a JSON object" in capsys.readouterr().err


@pytest.mark.asyncio
async def test_main_rejects_invalid_tts_extra_body_cli(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["wyoming_openai", "--tts-extra-body", '{"stream":'])

    with pytest.raises(SystemExit) as exc_info:
        await main()

    assert exc_info.value.code == 2
    assert "Invalid TTS extra body" in capsys.readouterr().err


class _FakeClient:
    def __init__(self):
        self.backend = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def list_supported_voices(self, *args, **kwargs):
        return []


class _CapturingServer:
    async def run(self, handler_factory):
        handler_factory(Mock(name="reader"), Mock(name="writer"))


@pytest.mark.asyncio
async def test_main_allows_unused_tts_response_format_in_stt_only_mode(monkeypatch):
    async def fake_factory(*args, **kwargs):
        return _FakeClient()

    for env_var in ("TTS_MODELS", "TTS_STREAMING_MODELS", "TTS_VOICES"):
        monkeypatch.delenv(env_var, raising=False)

    monkeypatch.setattr(
        main_module.CustomAsyncOpenAI,
        "create_autodetected_factory",
        staticmethod(lambda: fake_factory),
    )
    monkeypatch.setattr(
        main_module.AsyncServer,
        "from_uri",
        staticmethod(lambda uri: _CapturingServer()),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wyoming_openai",
            "--stt-models",
            "whisper-1",
            "--tts-extra-body",
            '{"response_format":"mp3"}',
        ],
    )

    await main()


@pytest.mark.asyncio
async def test_main_allows_unused_stt_response_format_in_tts_only_mode(monkeypatch):
    async def fake_factory(*args, **kwargs):
        return _FakeClient()

    for env_var in ("STT_MODELS", "STT_STREAMING_MODELS"):
        monkeypatch.delenv(env_var, raising=False)

    monkeypatch.setattr(
        main_module.CustomAsyncOpenAI,
        "create_autodetected_factory",
        staticmethod(lambda: fake_factory),
    )
    monkeypatch.setattr(
        main_module.AsyncServer,
        "from_uri",
        staticmethod(lambda uri: _CapturingServer()),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "wyoming_openai",
            "--tts-models",
            "tts-1",
            "--tts-voices",
            "alloy",
            "--stt-extra-body",
            '{"response_format":"text"}',
        ],
    )

    await main()
