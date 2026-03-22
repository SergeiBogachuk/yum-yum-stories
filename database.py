import os

import streamlit as st
from supabase import create_client


class EmptyResult:
    data = []


def _secret_or_env(name):
    if name in st.secrets and st.secrets[name]:
        return st.secrets[name]

    value = os.getenv(name)
    if value:
        return value

    raise RuntimeError(f"Missing required secret: {name}")


def _create_supabase_client():
    return create_client(
        _secret_or_env("SUPABASE_URL"),
        _secret_or_env("SUPABASE_KEY"),
    )


@st.cache_resource(show_spinner=False)
def get_supabase():
    return _create_supabase_client()


def check_user(email, password):
    try:
        result = (
            get_supabase()
            .table("users")
            .select("id")
            .eq("email", email.strip())
            .eq("password", password)
            .limit(1)
            .execute()
        )
        return len(result.data) > 0
    except Exception:
        return False


def sign_in_user(email, password):
    normalized_email = (email or "").strip()
    auth_error_message = ""

    try:
        auth_client = _create_supabase_client()
        auth_response = auth_client.auth.sign_in_with_password(
            {
                "email": normalized_email,
                "password": password,
            }
        )
        auth_user = getattr(auth_response, "user", None)
        auth_session = getattr(auth_response, "session", None)

        if auth_user and getattr(auth_user, "email", None):
            return {
                "ok": True,
                "email": auth_user.email.strip(),
                "provider": "supabase_auth",
                "access_token": getattr(auth_session, "access_token", "") or "",
                "refresh_token": getattr(auth_session, "refresh_token", "") or "",
            }
    except Exception as error:
        auth_error_message = str(error)

    if check_user(normalized_email, password):
        return {
            "ok": True,
            "email": normalized_email,
            "provider": "legacy_table",
            "access_token": "",
            "refresh_token": "",
        }

    return {
        "ok": False,
        "error": auth_error_message,
    }


def sign_out_user(access_token="", refresh_token=""):
    if not access_token or not refresh_token:
        return False

    try:
        auth_client = _create_supabase_client()
        auth_client.auth.set_session(access_token, refresh_token)
        auth_client.auth.sign_out()
        return True
    except Exception:
        return False


def get_user_stories(email):
    try:
        return (
            get_supabase()
            .table("stories")
            .select("*")
            .eq("user_email", email.strip())
            .order("id", desc=True)
            .execute()
        )
    except Exception:
        return EmptyResult()


def save_story(story_data):
    payload = {
        "user_email": story_data.get("user_email"),
        "child_name": story_data.get("child_name"),
        "title": story_data.get("title"),
        "story_text": story_data.get("story_text"),
        "image_url": story_data.get("image_url"),
    }

    try:
        return get_supabase().table("stories").insert(payload).execute()
    except Exception:
        return None


def update_audio(story_id, audio_b64):
    try:
        return (
            get_supabase()
            .table("stories")
            .update({"audio_base64": audio_b64})
            .eq("id", story_id)
            .execute()
        )
    except Exception:
        return None


def delete_story(story_id):
    try:
        get_supabase().table("stories").delete().eq("id", story_id).execute()
        return True
    except Exception:
        return False
