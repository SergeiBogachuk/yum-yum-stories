import base64
from io import BytesIO
import json
import os
import re

import requests
import streamlit as st
from openai import OpenAI

try:
    import boto3
except ImportError:
    boto3 = None

try:
    from google.cloud import texttospeech
    from google.oauth2 import service_account
except ImportError:
    texttospeech = None
    service_account = None


def _secret_or_env(name):
    if name in st.secrets and st.secrets[name]:
        return st.secrets[name]

    value = os.getenv(name)
    if value:
        return value

    raise RuntimeError(f"Missing required secret: {name}")


def _optional_secret_or_env(name, default=None):
    if name in st.secrets and st.secrets[name]:
        return st.secrets[name]

    value = os.getenv(name)
    if value:
        return value

    return default


@st.cache_resource(show_spinner=False)
def get_openai_client():
    return OpenAI(api_key=_secret_or_env("OPENAI_API_KEY"))


@st.cache_resource(show_spinner=False)
def get_aws_polly_client():
    if boto3 is None:
        return None

    region = _optional_secret_or_env("AWS_DEFAULT_REGION", "us-east-1")
    aws_access_key_id = _optional_secret_or_env("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = _optional_secret_or_env("AWS_SECRET_ACCESS_KEY")
    aws_session_token = _optional_secret_or_env("AWS_SESSION_TOKEN")

    client_kwargs = {
        "service_name": "polly",
        "region_name": region,
    }

    if aws_access_key_id and aws_secret_access_key:
        client_kwargs["aws_access_key_id"] = aws_access_key_id
        client_kwargs["aws_secret_access_key"] = aws_secret_access_key

    if aws_session_token:
        client_kwargs["aws_session_token"] = aws_session_token

    try:
        return boto3.client(**client_kwargs)
    except Exception:
        return None


@st.cache_resource(show_spinner=False)
def get_google_tts_client():
    if texttospeech is None:
        return None

    try:
        if "gcp_service_account" in st.secrets:
            service_account_info = dict(st.secrets["gcp_service_account"])
            credentials = service_account.Credentials.from_service_account_info(
                service_account_info
            )
            return texttospeech.TextToSpeechClient(credentials=credentials)

        service_account_json = _optional_secret_or_env("GOOGLE_TTS_SERVICE_ACCOUNT_JSON")
        if service_account_json:
            service_account_info = json.loads(service_account_json)
            credentials = service_account.Credentials.from_service_account_info(
                service_account_info
            )
            return texttospeech.TextToSpeechClient(credentials=credentials)

        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            return texttospeech.TextToSpeechClient()
    except Exception:
        return None

    return None


def _estimate_word_target(time_val):
    targets = {
        3: "350-500 words",
        5: "550-800 words",
        10: "900-1300 words",
    }
    return targets.get(time_val, "600-900 words")


def generate_story_text(child_name, lang, skills, details, time_val):
    skills_text = ", ".join(skills) if skills else "gentle confidence, calm, and kindness"
    story_context = details or "Create an original cozy bedtime situation that fits a young child."
    word_target = _estimate_word_target(time_val)
    model = os.getenv("OPENAI_MODEL") or (
        st.secrets["OPENAI_MODEL"] if "OPENAI_MODEL" in st.secrets else "gpt-5.3-chat-latest"
    )

    system_prompt = (
        "You are a warm children's bedtime storyteller with a strong understanding of gentle child "
        "development. You write emotionally safe fairy tales that model skills through story, not through "
        "lecturing. Keep everything soothing, imaginative, and appropriate for young children."
    )

    user_prompt = f"""
Write a complete bedtime fairy tale in {lang}.

Story requirements:
- The child's name is: {child_name}
- Gently support these themes or skills: {skills_text}
- Story context to include when helpful: {story_context}
- Target reading time: about {time_val} minutes ({word_target})
- The first line must be a short, beautiful title only
- After the title, write the story in short, readable paragraphs
- End with a short closing paragraph addressed directly to {child_name}
- In that closing, gently reinforce the main lesson and invite the child to practice it in real life again and again
- The closing may include one soft reflective question or loving reminder, but it must never sound harsh, guilty, or preachy

Tone and safety requirements:
- Warm, magical, tender, and calming
- Show the skill through the character's journey instead of preaching
- No scary villains, humiliation, shame, or harsh punishment
- No sarcasm, cynicism, or overstimulation
- End with felt safety, emotional relief, and a gentle sense of growth

Writing quality:
- Make the child feel seen, capable, and comforted
- Use sensory details, but keep the pacing soft enough for bedtime
- Keep the plot coherent and complete
- Do not use markdown, bullet points, or section labels

Return only:
1. Title on the first line
2. The full story after that
""".strip()

    response = get_openai_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    full_text = response.choices[0].message.content or ""
    return full_text.replace(":::writing", "").replace("###", "").strip()


def generate_image(title, child_name=None, lang=None, skills=None, details=None):
    try:
        skills_text = ", ".join(skills or [])
        details_text = details or "a calm and magical bedtime moment"
        prompt = f"""
Create a warm storybook cover illustration for a children's bedtime fairy tale.

Visual direction:
- soft painterly lighting
- gentle magical atmosphere
- expressive but calm character emotions
- cozy, imaginative composition for young children
- no text, no letters, no watermark

Story context:
- title: {title}
- child's name: {child_name or "child"}
- language context: {lang or "neutral"}
- themes: {skills_text or "kindness and emotional safety"}
- plot hints: {details_text}
""".strip()

        response = get_openai_client().images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
        )
        return response.data[0].url
    except Exception:
        return None


def _chunk_tts_text(text, max_chars=3800):
    clean_text = (text or "").replace("\r\n", "\n").strip()
    if not clean_text:
        return []

    chunks = []
    current = ""
    paragraphs = [part.strip() for part in clean_text.split("\n") if part.strip()]

    if not paragraphs:
        paragraphs = [clean_text]

    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
            continue

        if current:
            chunks.append(current)
            current = ""

        if len(paragraph) <= max_chars:
            current = paragraph
            continue

        sentences = re.split(r"(?<=[.!?…])\s+", paragraph)
        sentence_bucket = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            sentence_candidate = (
                f"{sentence_bucket} {sentence}".strip() if sentence_bucket else sentence
            )

            if len(sentence_candidate) <= max_chars:
                sentence_bucket = sentence_candidate
            else:
                if sentence_bucket:
                    chunks.append(sentence_bucket)
                sentence_bucket = sentence

        if sentence_bucket:
            current = sentence_bucket

    if current:
        chunks.append(current)

    return chunks


def get_speech_b64(text, voice_id, with_details=False):
    api_key = _secret_or_env("ELEVENLABS_API_KEY")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    try:
        response = requests.post(
            url,
            json={
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.45,
                    "similarity_boost": 0.75,
                },
            },
            headers={
                "xi-api-key": api_key,
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
            },
            timeout=60,
        )

        if response.status_code == 200:
            audio_b64 = base64.b64encode(response.content).decode()
            return (audio_b64, None) if with_details else audio_b64

        error_detail = f"ElevenLabs {response.status_code}: {response.text[:220]}"
        return (None, error_detail) if with_details else None
    except Exception as error:
        error_detail = f"{type(error).__name__}: {error}"
        return (None, error_detail) if with_details else None


def get_openai_speech_b64(text, voice="marin", with_details=False):
    model = os.getenv("OPENAI_TTS_MODEL") or (
        st.secrets["OPENAI_TTS_MODEL"] if "OPENAI_TTS_MODEL" in st.secrets else "gpt-4o-mini-tts"
    )
    chunks = _chunk_tts_text(text)
    if not chunks:
        return None

    instructions = (
        "Read this as a warm bedtime storyteller for a young child. "
        "Keep the tone calm, tender, emotionally safe, and gently expressive. "
        "Avoid sounding robotic, rushed, or overly dramatic."
    )

    audio_parts = []
    try:
        for chunk in chunks:
            request_params = {
                "model": model,
                "voice": voice,
                "input": chunk,
                "response_format": "mp3",
            }

            if model not in {"tts-1", "tts-1-hd"}:
                request_params["instructions"] = instructions

            response = get_openai_client().audio.speech.create(**request_params)
            audio_parts.append(response.content)

        if not audio_parts:
            return (None, "OpenAI returned empty audio.") if with_details else None

        audio_b64 = base64.b64encode(b"".join(audio_parts)).decode()
        return (audio_b64, None) if with_details else audio_b64
    except Exception as error:
        error_detail = f"{type(error).__name__}: {error}"
        return (None, error_detail) if with_details else None


def get_story_note_transcription(audio_bytes, mime_type="audio/wav", language=None):
    if not audio_bytes:
        return None, "No audio was recorded."

    model = os.getenv("OPENAI_TRANSCRIBE_MODEL") or (
        st.secrets["OPENAI_TRANSCRIBE_MODEL"]
        if "OPENAI_TRANSCRIBE_MODEL" in st.secrets
        else "gpt-4o-mini-transcribe"
    )

    try:
        file_ext = "wav"
        mime_text = (mime_type or "").lower()
        if "mp4" in mime_text or "m4a" in mime_text:
            file_ext = "m4a"
        elif "mpeg" in mime_text or "mp3" in mime_text:
            file_ext = "mp3"
        elif "webm" in mime_text:
            file_ext = "webm"

        audio_file = BytesIO(audio_bytes)
        audio_file.name = f"story-note.{file_ext}"

        request_params = {
            "model": model,
            "file": audio_file,
        }
        if language:
            request_params["language"] = language

        transcript = get_openai_client().audio.transcriptions.create(**request_params)
        transcript_text = transcript if isinstance(transcript, str) else getattr(transcript, "text", "")
        transcript_text = (transcript_text or "").strip()

        if not transcript_text:
            return None, "OpenAI returned empty transcription."

        return transcript_text, None
    except Exception as error:
        error_detail = f"{type(error).__name__}: {error}"
        return None, error_detail


def get_aws_polly_speech_b64(text, voice_id, with_details=False):
    client = get_aws_polly_client()
    if client is None:
        detail = "AWS Polly client is not configured. Check boto3 and AWS keys."
        return (None, detail) if with_details else None

    chunks = _chunk_tts_text(text, max_chars=2400)
    if not chunks:
        detail = "The text is empty."
        return (None, detail) if with_details else None

    audio_parts = []
    for chunk in chunks:
        response = None
        try:
            response = client.synthesize_speech(
                Text=chunk,
                OutputFormat="mp3",
                VoiceId=voice_id,
                Engine="neural",
                TextType="text",
            )
        except Exception:
            try:
                response = client.synthesize_speech(
                    Text=chunk,
                    OutputFormat="mp3",
                    VoiceId=voice_id,
                    Engine="standard",
                    TextType="text",
                )
            except Exception as error:
                error_detail = f"{type(error).__name__}: {error}"
                return (None, error_detail) if with_details else None

        audio_stream = response.get("AudioStream") if response else None
        if not audio_stream:
            detail = "AWS Polly returned no audio stream."
            return (None, detail) if with_details else None

        audio_parts.append(audio_stream.read())
        try:
            audio_stream.close()
        except Exception:
            pass

    if not audio_parts:
        detail = "AWS Polly returned empty audio."
        return (None, detail) if with_details else None

    audio_b64 = base64.b64encode(b"".join(audio_parts)).decode()
    return (audio_b64, None) if with_details else audio_b64


def get_google_cloud_speech_b64(text, voice_config, with_details=False):
    client = get_google_tts_client()
    if client is None or texttospeech is None:
        detail = "Google Cloud Text-to-Speech client is not configured. Check library install and Google credentials."
        return (None, detail) if with_details else None

    if isinstance(voice_config, str):
        voice_config = {"name": voice_config, "language_code": "en-US"}

    if not isinstance(voice_config, dict):
        detail = "Invalid Google voice configuration."
        return (None, detail) if with_details else None

    chunks = _chunk_tts_text(text, max_chars=1800)
    if not chunks:
        detail = "The text is empty."
        return (None, detail) if with_details else None

    language_code = voice_config.get("language_code", "en-US")
    voice_name = voice_config.get("name")
    speaking_rate = voice_config.get("speaking_rate", 0.95)

    audio_parts = []
    try:
        voice_params = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=speaking_rate,
        )

        for chunk in chunks:
            response = client.synthesize_speech(
                input=texttospeech.SynthesisInput(text=chunk),
                voice=voice_params,
                audio_config=audio_config,
            )
            audio_parts.append(response.audio_content)

        if not audio_parts:
            detail = "Google Cloud returned empty audio."
            return (None, detail) if with_details else None

        audio_b64 = base64.b64encode(b"".join(audio_parts)).decode()
        return (audio_b64, None) if with_details else audio_b64
    except Exception as error:
        error_detail = f"{type(error).__name__}: {error}"
        return (None, error_detail) if with_details else None
