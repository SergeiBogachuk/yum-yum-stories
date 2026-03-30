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


def get_child_profiles(email):
    try:
        return (
            get_supabase()
            .table("child_profiles")
            .select("*")
            .eq("user_email", email.strip())
            .order("child_name")
            .execute()
        )
    except Exception:
        return EmptyResult()


def save_child_profile(profile_data):
    normalized_email = (profile_data.get("user_email") or "").strip()
    child_name = (profile_data.get("child_name") or "").strip()

    if not normalized_email or not child_name:
        return None

    payload = {
        "user_email": normalized_email,
        "child_name": child_name,
        "age_band": profile_data.get("age_band") or None,
        "story_goal": profile_data.get("story_goal") or None,
        "favorite_hero": (profile_data.get("favorite_hero") or "").strip() or None,
    }

    try:
        existing = (
            get_supabase()
            .table("child_profiles")
            .select("id")
            .eq("user_email", normalized_email)
            .eq("child_name", child_name)
            .limit(1)
            .execute()
        )

        if getattr(existing, "data", None):
            child_profile_id = existing.data[0]["id"]
            result = (
                get_supabase()
                .table("child_profiles")
                .update(payload)
                .eq("id", child_profile_id)
                .execute()
            )
        else:
            result = get_supabase().table("child_profiles").insert(payload).execute()

        if getattr(result, "data", None):
            return result.data[0]
        return None
    except Exception:
        return None


def delete_child_profile(profile_id):
    try:
        get_supabase().table("child_profiles").delete().eq("id", profile_id).execute()
        return True
    except Exception:
        return False


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


def track_event(event_name, user_email="", properties=None):
    payload = {
        "event_name": (event_name or "").strip(),
        "user_email": (user_email or "").strip() or None,
        "properties": properties or {},
    }

    if not payload["event_name"]:
        return False

    try:
        get_supabase().table("analytics_events").insert(payload).execute()
        return True
    except Exception:
        return False
