import base64
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import hashlib
import html
import os
import re
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from ai_engine import (
    generate_image,
    generate_story_text,
    get_google_cloud_speech_b64,
    get_openai_speech_b64,
    get_speech_b64,
    get_story_note_transcription,
)
from database import delete_story, get_user_stories, save_story, sign_in_user, sign_out_user, update_audio
from styles import apply_styles

BRAND_NAME = "Yum-Yum Stories"
DEFAULT_TTS_PROVIDER = "openai"
SHOW_TTS_PROVIDER_SELECTOR = False
SHOW_INTRO_REPLAY_BUTTON = False
ENABLE_INTRO_OVERLAY = False
MONTHLY_STORY_LIMIT = 30
STANDARD_PLAN_EXTRA_STORIES = 30
FAMILY_PLAN_EXTRA_STORIES = 80
EXTRA_PACK_STORIES = 10
BACKGROUND_EXECUTOR = ThreadPoolExecutor(max_workers=4)

st.set_page_config(
    page_title=BRAND_NAME,
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_styles()


def inject_app_icons():
    return


inject_app_icons()


@st.cache_data(show_spinner=False)
def get_file_b64(path_str):
    path = Path(path_str)
    if not path.exists():
        return None
    return base64.b64encode(path.read_bytes()).decode()


def get_intro_asset():
    candidates = [
        ("intro.mp4", "video", "video/mp4"),
        ("intro.webm", "video", "video/webm"),
        ("intro.mov", "video", "video/quicktime"),
        ("intro.jpg", "image", "image/jpeg"),
        ("intro.jpeg", "image", "image/jpeg"),
        ("intro.png", "image", "image/png"),
    ]

    for filename, kind, mime in candidates:
        file_b64 = get_file_b64(filename)
        if file_b64:
            return {
                "filename": filename,
                "kind": kind,
                "mime": mime,
                "b64": file_b64,
            }

    return None


def render_intro_overlay(copy_pack):
    if not ENABLE_INTRO_OVERLAY:
        return False
    asset = get_intro_asset()
    if not asset:
        return False
    force_show = st.session_state.pop("force_intro", False)

    if asset["kind"] == "video":
        media_markup = (
            f'<video id="nomnom-intro-media" playsinline preload="auto" '
            f'src="data:{asset["mime"]};base64,{asset["b64"]}"></video>'
        )
    else:
        media_markup = (
            f'<img id="nomnom-intro-media" src="data:{asset["mime"]};base64,{asset["b64"]}" '
            f'alt="{BRAND_NAME} intro" />'
        )

    components.html(
        f"""
        <script>
        (function() {{
            let docRef = document;
            try {{
                if (window.parent && window.parent.document) {{
                    docRef = window.parent.document;
                }}
            }} catch (error) {{
                docRef = document;
            }}

            const overlayId = "nomnom-intro-overlay";
            const styleId = "nomnom-intro-style";
            const forceShow = {"true" if force_show else "false"};
            let rootWindow = window;
            try {{
                if (window.parent && window.parent !== window) {{
                    rootWindow = window.parent;
                }}
            }} catch (error) {{
                rootWindow = window;
            }}

            if (forceShow) {{
                rootWindow.__nomnomIntroShown = false;
            }}

            const alreadySeen = !forceShow && rootWindow.__nomnomIntroShown === true;

            if (alreadySeen) {{
                return;
            }}

            const existing = docRef.getElementById(overlayId);
            if (existing) {{
                existing.remove();
            }}

            if (!docRef.getElementById(styleId)) {{
                const style = docRef.createElement("style");
                style.id = styleId;
                style.textContent = `
                    #${{overlayId}} {{
                        position: fixed;
                        inset: 0;
                        z-index: 2147483647;
                        background: #000;
                        overflow: hidden;
                    }}
                    #${{overlayId}} #nomnom-intro-media {{
                        position: absolute;
                        inset: 0;
                        width: 100vw;
                        height: 100vh;
                        object-fit: cover;
                        object-position: center center;
                        background: #000;
                    }}
                    #${{overlayId}} .nomnom-intro-shade {{
                        position: absolute;
                        inset: 0;
                        background:
                            radial-gradient(circle at top, rgba(255, 218, 180, 0.18), transparent 24%),
                            linear-gradient(180deg, rgba(0,0,0,0.08), rgba(0,0,0,0.34));
                        pointer-events: none;
                    }}
                    #${{overlayId}} .nomnom-intro-brand {{
                        position: absolute;
                        left: 50%;
                        bottom: max(28px, env(safe-area-inset-bottom));
                        transform: translateX(-50%);
                        width: min(92vw, 760px);
                        padding: 0 18px;
                        box-sizing: border-box;
                        text-align: center;
                        color: #fff7ef;
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                        text-shadow: 0 4px 22px rgba(0,0,0,0.28);
                    }}
                    #${{overlayId}} .nomnom-intro-title {{
                        font-size: clamp(2rem, 5vw, 4.4rem);
                        font-weight: 800;
                        line-height: 1.08;
                        margin-bottom: 10px;
                        text-wrap: balance;
                    }}
                    #${{overlayId}} .nomnom-intro-copy {{
                        font-size: clamp(1rem, 2vw, 1.25rem);
                        line-height: 1.55;
                        opacity: 0.94;
                        text-wrap: balance;
                    }}
                    #${{overlayId}} .nomnom-intro-skip,
                    #${{overlayId}} .nomnom-intro-hint {{
                        position: absolute;
                        border-radius: 999px;
                        padding: 11px 16px;
                        font-weight: 700;
                        backdrop-filter: blur(10px);
                        box-shadow: 0 12px 26px rgba(0,0,0,0.18);
                    }}
                    #${{overlayId}} .nomnom-intro-skip {{
                        top: max(18px, env(safe-area-inset-top));
                        right: 18px;
                        border: none;
                        background: rgba(255, 248, 240, 0.9);
                        color: #5d3823;
                        cursor: pointer;
                    }}
                    #${{overlayId}} .nomnom-intro-hint {{
                        left: 50%;
                        bottom: 130px;
                        transform: translateX(-50%);
                        background: rgba(18, 12, 9, 0.58);
                        color: #fff7ef;
                        border: 1px solid rgba(255,255,255,0.18);
                        display: none;
                        pointer-events: none;
                    }}
                    @media (max-width: 768px) {{
                        #${{overlayId}} .nomnom-intro-brand {{
                            width: calc(100vw - 28px);
                            bottom: max(20px, env(safe-area-inset-bottom));
                            padding: 18px 18px calc(16px + env(safe-area-inset-bottom)) 18px;
                            border-radius: 24px;
                            background: linear-gradient(180deg, rgba(13, 8, 6, 0.14), rgba(13, 8, 6, 0.38));
                            backdrop-filter: blur(10px);
                        }}
                        #${{overlayId}} .nomnom-intro-title {{
                            font-size: clamp(1.85rem, 10vw, 3rem);
                            line-height: 1.1;
                            margin-bottom: 8px;
                        }}
                        #${{overlayId}} .nomnom-intro-copy {{
                            font-size: 0.92rem;
                            line-height: 1.45;
                            max-width: 100%;
                        }}
                        #${{overlayId}} .nomnom-intro-skip {{
                            top: max(12px, env(safe-area-inset-top));
                            right: 12px;
                            padding: 10px 14px;
                            font-size: 0.92rem;
                        }}
                        #${{overlayId}} .nomnom-intro-hint {{
                            width: calc(100vw - 32px);
                            bottom: calc(110px + env(safe-area-inset-bottom));
                            padding: 10px 14px;
                            font-size: 0.9rem;
                            text-align: center;
                            white-space: normal;
                        }}
                    }}
                `;
                docRef.head.appendChild(style);
            }}

            const overlay = docRef.createElement("div");
            overlay.id = overlayId;
            overlay.innerHTML = `
                {media_markup}
                <div class="nomnom-intro-shade"></div>
                <button class="nomnom-intro-skip">{copy_pack.get("intro_skip", "Skip")}</button>
                <div class="nomnom-intro-hint">{copy_pack.get("intro_tap_sound", "Tap anywhere for sound")}</div>
                <div class="nomnom-intro-brand">
                    <div class="nomnom-intro-title">🌙 {copy_pack.get("title", BRAND_NAME)}</div>
                    <div class="nomnom-intro-copy">{copy_pack.get("intro_copy", "")}</div>
                </div>
            `;
            docRef.body.appendChild(overlay);

            function closeIntro() {{
                rootWindow.__nomnomIntroShown = true;
                const active = docRef.getElementById(overlayId);
                if (active) {{
                    active.remove();
                }}
            }}

            const skipButton = overlay.querySelector(".nomnom-intro-skip");
            if (skipButton) {{
                skipButton.addEventListener("click", closeIntro);
            }}

            const hint = overlay.querySelector(".nomnom-intro-hint");
            const media = overlay.querySelector("#nomnom-intro-media");
            if (!media) {{
                window.setTimeout(closeIntro, 2500);
                return;
            }}

            if (media.tagName === "VIDEO") {{
                media.autoplay = true;
                media.loop = false;
                media.controls = false;
                media.volume = 0.55;
                media.muted = false;
                let soundArmed = false;

                const soundFallback = function() {{
                    media.muted = true;
                    soundArmed = true;
                    if (hint) {{
                        hint.style.display = "block";
                    }}
                    const mutedPlay = media.play();
                    if (mutedPlay) {{
                        mutedPlay.catch(() => {{}});
                    }}
                }};

                const playPromise = media.play();
                if (playPromise) {{
                    playPromise.catch(soundFallback);
                }}

                media.addEventListener("ended", closeIntro);

                overlay.addEventListener("pointerdown", function(event) {{
                    if (!soundArmed) {{
                        return;
                    }}
                    if (skipButton && skipButton.contains(event.target)) {{
                        return;
                    }}
                    try {{
                        media.muted = false;
                        media.volume = 0.75;
                        soundArmed = false;
                        if (hint) {{
                            hint.style.display = "none";
                        }}
                        const replay = media.play();
                        if (replay) {{
                            replay.catch(() => {{
                                soundArmed = true;
                                if (hint) {{
                                    hint.style.display = "block";
                                }}
                            }});
                        }}
                    }} catch (error) {{
                        soundArmed = true;
                        if (hint) {{
                            hint.style.display = "block";
                        }}
                    }}
                }});
            }} else {{
                window.setTimeout(closeIntro, 3200);
            }}
        }})();
        </script>
        """,
        height=0,
    )
    return True


def replay_intro_overlay():
    st.session_state.show_intro = True
    st.session_state.force_intro = True
    st.rerun()


def get_bg_music_b64():
    try:
        with open("bg_music.mp3", "rb") as file:
            return base64.b64encode(file.read()).decode()
    except Exception:
        return None


def mount_bg_music(volume_level=0.36):
    bg_b64 = get_bg_music_b64()
    if not bg_b64:
        return False

    safe_volume = max(0.0, min(float(volume_level), 1.0))

    components.html(
        f"""
        <script>
        (function() {{
            let docRef = document;
            try {{
                if (window.parent && window.parent.document) {{
                    docRef = window.parent.document;
                }}
            }} catch (error) {{
                docRef = document;
            }}

            let bg = docRef.getElementById("nomnom-bg-music");
            if (!bg) {{
                bg = docRef.createElement("audio");
                bg.id = "nomnom-bg-music";
                bg.loop = true;
                bg.preload = "auto";
                bg.style.display = "none";
                docRef.body.appendChild(bg);
            }}

            bg.src = "data:audio/mp3;base64,{bg_b64}";
            bg.volume = {safe_volume};

            function startBg() {{
                try {{
                    const activeBg = docRef.getElementById("nomnom-bg-music");
                    if (!activeBg) {{
                        return;
                    }}
                    activeBg.volume = {safe_volume};
                    const playPromise = activeBg.play();
                    if (playPromise) {{
                        playPromise.catch(() => {{}});
                    }}
                }} catch (error) {{}}
            }}

            if (!docRef.body.dataset.nomnomBgBound) {{
                ["click", "touchstart", "keydown"].forEach(function(eventName) {{
                    docRef.addEventListener(eventName, startBg, {{ passive: true }});
                }});
                docRef.body.dataset.nomnomBgBound = "1";
            }}

            startBg();
        }})();
        </script>
        """,
        height=0,
    )
    return True


def stop_bg_music():
    components.html(
        """
        <script>
        (function() {
            let docRef = document;
            try {
                if (window.parent && window.parent.document) {
                    docRef = window.parent.document;
                }
            } catch (error) {
                docRef = document;
            }

            const bg = docRef.getElementById("nomnom-bg-music");
            if (bg) {
                try {
                    bg.pause();
                    bg.currentTime = 0;
                    bg.remove();
                } catch (error) {}
            }
        })();
        </script>
        """,
        height=0,
    )


def short_story_title(title, fallback_title="Story", max_len=24):
    title = (title or fallback_title).replace("\n", " ").strip()
    return title if len(title) <= max_len else title[: max_len - 1] + "…"


def extract_story_parts(full_text, fallback_title):
    cleaned = (full_text or "").replace("\r\n", "\n").strip()
    cleaned = cleaned.replace(":::writing", "").replace("###", "").strip()
    cleaned = re.sub(r"^#{1,6}\s*", "", cleaned, flags=re.MULTILINE)

    first_line, _, rest = cleaned.partition("\n")
    title = first_line.strip().strip("\"'“”«»")
    title = re.sub(r"^(title|заголовок|titlu)\s*[:\-]\s*", "", title, flags=re.IGNORECASE)
    title = title or fallback_title
    body = rest.strip() if rest.strip() else cleaned

    return title, body


def validate_story_request(child_name, skills, copy_pack):
    errors = []

    if not child_name.strip():
        errors.append(copy_pack.get("error_child_name", "Enter the child's name."))
    if not skills:
        errors.append(copy_pack.get("error_skills", "Choose at least one skill or theme."))

    return errors


def parse_story_created_at(story):
    raw_value = (
        story.get("created_at")
        or story.get("createdAt")
        or story.get("inserted_at")
        or story.get("insertedAt")
    )
    if not raw_value or not isinstance(raw_value, str):
        return None

    try:
        normalized = raw_value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def get_monthly_story_usage(stories, now=None):
    story_items = getattr(stories, "data", None) or []
    if not story_items:
        return 0

    current_dt = now or datetime.now().astimezone()
    monthly_count = 0
    parsed_any_story_date = False

    for story in story_items:
        created_dt = parse_story_created_at(story)
        if created_dt is None:
            continue

        parsed_any_story_date = True

        if created_dt.tzinfo is not None:
            compare_dt = created_dt.astimezone(current_dt.tzinfo)
        else:
            compare_dt = created_dt

        if compare_dt.year == current_dt.year and compare_dt.month == current_dt.month:
            monthly_count += 1

    if not parsed_any_story_date:
        return len(story_items)

    return monthly_count


def get_next_month_reset_date(now=None):
    current_dt = now or datetime.now().astimezone()
    if current_dt.month == 12:
        next_month = current_dt.replace(year=current_dt.year + 1, month=1, day=1)
    else:
        next_month = current_dt.replace(month=current_dt.month + 1, day=1)
    return next_month.strftime("%B %d")


def activate_beta_access(plan_key, copy_pack):
    if plan_key == "extra_pack":
        st.session_state.monthly_story_bonus = st.session_state.get("monthly_story_bonus", 0) + EXTRA_PACK_STORIES
        activated_plan = copy_pack.get("plan_extra_name", "Extra pack")
    elif plan_key == "standard":
        st.session_state.monthly_story_bonus = max(
            st.session_state.get("monthly_story_bonus", 0),
            STANDARD_PLAN_EXTRA_STORIES,
        )
        activated_plan = copy_pack.get("plan_standard_name", "Standard")
    else:
        st.session_state.monthly_story_bonus = max(
            st.session_state.get("monthly_story_bonus", 0),
            FAMILY_PLAN_EXTRA_STORIES,
        )
        activated_plan = copy_pack.get("plan_family_name", "Family")

    st.session_state.billing_notice = copy_pack.get(
        "plan_activation_notice",
        "Beta access activated: {plan}. New limit this month: {limit}.",
    ).format(
        plan=activated_plan,
        limit=MONTHLY_STORY_LIMIT + st.session_state.monthly_story_bonus,
    )
    st.rerun()


def render_access_panel(copy_pack, payment_links):
    live_payments_ready = has_live_payment_links(payment_links)

    st.markdown(
        f"""
        <div class="pricing-shell">
            <div class="section-label">{copy_pack.get("access_panel_title", "Extend access")}</div>
            <div class="pricing-subtitle">{copy_pack.get("access_panel_subtitle", "")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_pack, col_standard, col_family = st.columns(3, gap="medium")

    with col_pack:
        st.markdown(
            f"""
            <div class="plan-card">
                <div class="plan-name">{copy_pack.get("plan_extra_name", "Extra pack")}</div>
                <div class="plan-price">{copy_pack.get("plan_extra_price", "$3.99")}</div>
                <div class="plan-copy">{copy_pack.get("plan_extra_copy", "")}</div>
                <div class="plan-feature">+{EXTRA_PACK_STORIES} stories</div>
                <div class="plan-feature">{copy_pack.get("plan_voice_included", "Narration included")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if live_payments_ready and payment_links.get("extra_pack"):
            st.link_button(
                copy_pack.get("plan_extra_live_btn", "Buy Extra Pack"),
                payment_links["extra_pack"],
                use_container_width=True,
            )
        elif st.button(
            copy_pack.get("plan_extra_btn", "Activate extra pack"),
            key="activate_extra_pack_btn",
            use_container_width=True,
            type="secondary",
        ):
            activate_beta_access("extra_pack", copy_pack)

    with col_standard:
        st.markdown(
            f"""
            <div class="plan-card plan-card-featured">
                <div class="plan-eyebrow">{copy_pack.get("plan_recommended", "Recommended")}</div>
                <div class="plan-name">{copy_pack.get("plan_standard_name", "Standard")}</div>
                <div class="plan-price">{copy_pack.get("plan_standard_price", "$9.99/mo")}</div>
                <div class="plan-copy">{copy_pack.get("plan_standard_copy", "")}</div>
                <div class="plan-feature">+{STANDARD_PLAN_EXTRA_STORIES} stories</div>
                <div class="plan-feature">{copy_pack.get("plan_voice_included", "Narration included")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if live_payments_ready and payment_links.get("standard"):
            st.link_button(
                copy_pack.get("plan_standard_live_btn", "Choose Standard"),
                payment_links["standard"],
                use_container_width=True,
                type="primary",
            )
        elif st.button(
            copy_pack.get("plan_standard_btn", "Activate Standard"),
            key="activate_standard_plan_btn",
            use_container_width=True,
            type="primary",
        ):
            activate_beta_access("standard", copy_pack)

    with col_family:
        st.markdown(
            f"""
            <div class="plan-card">
                <div class="plan-name">{copy_pack.get("plan_family_name", "Family")}</div>
                <div class="plan-price">{copy_pack.get("plan_family_price", "$14.99/mo")}</div>
                <div class="plan-copy">{copy_pack.get("plan_family_copy", "")}</div>
                <div class="plan-feature">+{FAMILY_PLAN_EXTRA_STORIES} stories</div>
                <div class="plan-feature">{copy_pack.get("plan_family_feature", "More stories for the whole family")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if live_payments_ready and payment_links.get("family"):
            st.link_button(
                copy_pack.get("plan_family_live_btn", "Choose Family"),
                payment_links["family"],
                use_container_width=True,
            )
        elif st.button(
            copy_pack.get("plan_family_btn", "Activate Family"),
            key="activate_family_plan_btn",
            use_container_width=True,
            type="secondary",
        ):
            activate_beta_access("family", copy_pack)

    st.caption(
        copy_pack.get(
            "access_panel_live_note" if live_payments_ready else "access_panel_beta_note",
            "This is a beta access screen. Real payments will be connected next.",
        )
    )


def render_story_library(stories, copy_pack, prefix="lib"):
    if not stories or not getattr(stories, "data", None):
        st.caption(copy_pack.get("no_saved_stories", "No saved stories yet"))
        return

    for story in stories.data:
        full_title = story.get("title") or copy_pack.get("story_fallback", "Story")
        short_title = short_story_title(full_title, copy_pack.get("story_fallback", "Story"))

        col_story, col_delete = st.columns([6, 1], gap="small")

        with col_story:
            if st.button(
                short_title,
                key=f"{prefix}_story_{story['id']}",
                use_container_width=True,
                help=full_title,
            ):
                st.session_state.view_story = story
                st.session_state.page_mode = "view"
                st.rerun()

        with col_delete:
            if st.button(
                "🗑",
                key=f"{prefix}_del_{story['id']}",
                help=copy_pack.get("delete_help", "Delete"),
            ):
                if delete_story(story["id"]):
                    if (
                        st.session_state.view_story
                        and st.session_state.view_story.get("id") == story["id"]
                    ):
                        st.session_state.view_story = None
                        st.session_state.page_mode = "form"
                    st.rerun()


def generate_audio_with_provider(tts_provider, story_text, voice_id):
    if not story_text or not voice_id:
        return None, None

    if tts_provider == "openai":
        return get_openai_speech_b64(story_text, voice_id, with_details=True)
    if tts_provider == "google_cloud":
        return get_google_cloud_speech_b64(story_text, voice_id, with_details=True)
    return get_speech_b64(story_text, voice_id, with_details=True)


def prepare_story_media(
    *,
    use_img,
    use_audio,
    tts_provider,
    voice_id,
    title,
    child_name,
    selected_lang,
    skills,
    details,
    story_body,
):
    image_url = None
    audio_b64 = None
    audio_error = None
    futures = {}

    with ThreadPoolExecutor(max_workers=2) as executor:
        if use_img:
            futures["image"] = executor.submit(
                generate_image,
                title=title,
                child_name=child_name,
                lang=selected_lang,
                skills=skills,
                details=details,
            )

        if use_audio and voice_id:
            futures["audio"] = executor.submit(
                generate_audio_with_provider,
                tts_provider,
                story_body,
                voice_id,
            )

        if "image" in futures:
            try:
                image_url = futures["image"].result()
            except Exception:
                image_url = None

        if "audio" in futures:
            try:
                audio_b64, audio_error = futures["audio"].result()
            except Exception as error:
                audio_b64 = None
                audio_error = f"{type(error).__name__}: {error}"

    return image_url, audio_b64, audio_error


def build_story_payload(
    *,
    user_email,
    child_name,
    selected_lang,
    skills,
    details,
    time_val,
    use_img,
):
    full_text = generate_story_text(
        child_name,
        selected_lang,
        skills,
        details,
        time_val,
    )
    if not full_text:
        return {
            "ok": False,
            "error_code": "story_generation_failed",
        }

    title, story_body = extract_story_parts(full_text, "Story")
    image_url = None

    if use_img:
        image_url = generate_image(
            title=title,
            child_name=child_name,
            lang=selected_lang,
            skills=skills,
            details=details,
        )

    result = save_story(
        {
            "user_email": user_email,
            "child_name": child_name,
            "title": title,
            "story_text": story_body,
            "image_url": image_url,
        }
    )

    if not result or not getattr(result, "data", None):
        return {
            "ok": False,
            "error_code": "story_save_failed",
        }

    current_story = result.data[0]
    current_story["title"] = title
    current_story["story_text"] = story_body
    current_story["image_url"] = image_url

    return {
        "ok": True,
        "story": current_story,
        "story_text": story_body,
    }


def get_story_note_language_code(selected_lang):
    return {
        "Русский": "ru",
        "English": "en",
        "Română": "ro",
    }.get(selected_lang, "en")


def apply_pending_story_details():
    pending_text = (st.session_state.pop("pending_details_append", "") or "").strip()
    if not pending_text:
        return

    existing_text = (st.session_state.get("details_input", "") or "").strip()
    st.session_state.details_input = (
        f"{existing_text}\n\n{pending_text}".strip() if existing_text else pending_text
    )


def maybe_process_story_voice_note(voice_note, selected_lang):
    if voice_note is None:
        return

    audio_bytes = voice_note.getvalue()
    if not audio_bytes:
        return

    note_hash = hashlib.sha1(audio_bytes).hexdigest()
    if st.session_state.get("last_processed_voice_note_hash") == note_hash:
        return

    transcript_text, transcript_error = get_story_note_transcription(
        audio_bytes,
        getattr(voice_note, "type", "audio/wav"),
        get_story_note_language_code(selected_lang),
    )

    st.session_state.last_processed_voice_note_hash = note_hash

    if transcript_text:
        st.session_state.pending_details_append = transcript_text
        st.session_state.voice_note_status = "success"
        st.session_state.voice_note_error_message = ""
    else:
        st.session_state.voice_note_status = "error"
        st.session_state.voice_note_error_message = transcript_error or ""

    st.session_state.voice_note_widget_version = st.session_state.get("voice_note_widget_version", 0) + 1
    st.rerun()


def queue_story_voice_note_processing():
    st.session_state.voice_note_pending_process = True


def get_optional_secret_or_env(name, default=""):
    if name in st.secrets and st.secrets[name]:
        return str(st.secrets[name]).strip()

    value = os.getenv(name, default)
    if value:
        return str(value).strip()

    return default


def get_payment_links():
    return {
        "extra_pack": get_optional_secret_or_env("STRIPE_EXTRA_PACK_LINK"),
        "standard": get_optional_secret_or_env("STRIPE_STANDARD_LINK"),
        "family": get_optional_secret_or_env("STRIPE_FAMILY_LINK"),
        "portal": get_optional_secret_or_env("STRIPE_PORTAL_LINK"),
    }


def has_live_payment_links(payment_links):
    return any(payment_links.get(plan_key) for plan_key in ["extra_pack", "standard", "family"])


def start_story_generation_job(
    *,
    user_email,
    child_name,
    selected_lang,
    skills,
    details,
    time_val,
    use_img,
    use_audio,
    voice_id,
    tts_provider,
):
    future = BACKGROUND_EXECUTOR.submit(
        build_story_payload,
        user_email=user_email,
        child_name=child_name,
        selected_lang=selected_lang,
        skills=skills,
        details=details,
        time_val=time_val,
        use_img=use_img,
    )
    st.session_state.story_generation_job = {
        "future": future,
        "use_audio": use_audio,
        "voice_id": voice_id,
        "tts_provider": tts_provider,
    }


def clear_story_generation_job():
    st.session_state.story_generation_job = None


def start_audio_generation_job(story_id, story_text, voice_id, tts_provider):
    future = BACKGROUND_EXECUTOR.submit(
        generate_audio_with_provider,
        tts_provider,
        story_text,
        voice_id,
    )
    st.session_state.audio_generation_job = {
        "future": future,
        "story_id": story_id,
        "story_text": story_text,
        "voice_id": voice_id,
        "tts_provider": tts_provider,
    }


def clear_audio_generation_job():
    st.session_state.audio_generation_job = None


@st.fragment(run_every="2s")
def render_background_job_watcher(copy_pack):
    story_job = st.session_state.get("story_generation_job")
    audio_job = st.session_state.get("audio_generation_job")

    if story_job:
        story_future = story_job.get("future")
        if story_future and story_future.done():
            clear_story_generation_job()
            try:
                result = story_future.result()
            except Exception as error:
                st.session_state.story_generation_error = f"{type(error).__name__}: {error}"
                st.rerun()

            if result.get("ok"):
                current_story = result.get("story")
                if story_job.get("use_audio") and story_job.get("voice_id"):
                    start_audio_generation_job(
                        current_story["id"],
                        result.get("story_text", current_story.get("story_text", "")),
                        story_job.get("voice_id"),
                        story_job.get("tts_provider", DEFAULT_TTS_PROVIDER),
                    )
                st.session_state.view_story = current_story
                st.session_state.page_mode = "view"
                st.rerun()
            else:
                error_code = result.get("error_code", "")
                if error_code == "story_save_failed":
                    st.session_state.story_generation_error = copy_pack.get(
                        "error_save_story",
                        "Failed to save the story.",
                    )
                else:
                    st.session_state.story_generation_error = copy_pack.get(
                        "error_gen_story",
                        "Failed to generate the story text.",
                    )
                st.rerun()

    if audio_job:
        audio_future = audio_job.get("future")
        if audio_future and audio_future.done():
            clear_audio_generation_job()
            try:
                audio_b64, audio_error = audio_future.result()
            except Exception as error:
                audio_b64 = None
                audio_error = f"{type(error).__name__}: {error}"

            if audio_b64:
                update_audio(audio_job["story_id"], audio_b64)
                current_story = st.session_state.get("view_story")
                if current_story and current_story.get("id") == audio_job.get("story_id"):
                    current_story["audio_base64"] = audio_b64
                    st.session_state.view_story = current_story
            elif audio_error:
                st.session_state.audio_generation_error = audio_error

            st.rerun()

    if story_job and story_job.get("future") and not story_job["future"].done():
        st.info(
            copy_pack.get(
                "story_pending_notice",
                "The story is being created in the background. You can keep using the page.",
            )
        )
        st.caption(
            copy_pack.get(
                "story_pending_hint",
                "You can change volume and other settings. Generation will keep going.",
            )
        )
    elif audio_job and audio_job.get("future") and not audio_job["future"].done():
        st.info(copy_pack.get("audio_pending_notice", "Your story is ready. Narration is being added now."))
        st.caption(
            copy_pack.get(
                "audio_pending_hint",
                "You can keep browsing while narration is finishing in the background.",
            )
        )


def reset_authenticated_session():
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.auth_provider = ""
    st.session_state.auth_access_token = ""
    st.session_state.auth_refresh_token = ""
    st.session_state.view_story = None
    st.session_state.page_mode = "form"
    st.session_state.monthly_story_bonus = 0
    st.session_state.billing_notice = ""
    st.session_state.details_input = ""
    st.session_state.last_processed_voice_note_hash = ""
    st.session_state.voice_note_pending_process = False
    st.session_state.voice_note_status = ""
    st.session_state.voice_note_error_message = ""
    st.session_state.story_generation_job = None
    st.session_state.audio_generation_job = None
    st.session_state.story_generation_error = ""
    st.session_state.audio_generation_error = ""


lang_dict = {
    "Русский": {
        "title": BRAND_NAME,
        "subtitle": "Тёплые сказки на ночь, которые мягко развивают важные навыки.",
        "login_badge": "Для родителей",
        "login_subtitle": "Соберите свою спокойную библиотеку историй для сна, поддержки и роста.",
        "login_btn": "Войти",
        "login_error": "Не удалось войти. Проверь email и пароль.",
        "intro_skip": "Пропустить",
        "intro_copy": "Сказки для сна, поддержки и маленьких важных побед.",
        "intro_replay": "Посмотреть заставку снова",
        "intro_sound": "Нажми для звука",
        "intro_tap_sound": "Нажми в любом месте для звука",
        "intro_continue": "Продолжить",
        "intro_hint": "Если видео не запускается само, просто нажми play, а потом Продолжить.",
        "email_label": "Email",
        "password_label": "Пароль",
        "child_name": "Имя ребёнка",
        "child_placeholder": "Например: Даша",
        "default_child_name": "",
        "summary_fallback_child_name": "вашего ребенка",
        "skills_label": "Какие навыки поддержим этой сказкой?",
        "skills_help": "Лучше выбрать 1-2 темы, чтобы история получилась цельной и мягкой.",
        "duration": "Длительность",
        "duration_btn_suffix": "мин",
        "details": "О чём сейчас важно рассказать?",
        "details_placeholder": "Например: ребёнок боится темноты, скучает по детскому саду или учится делиться игрушками.",
        "details_help": "Можно описать ситуацию, любимых животных, настроение ребёнка или желаемый финал.",
        "details_voice_label": "Микрофон для диктовки",
        "details_voice_hint": "Можно писать вручную или нажать микрофон справа и надиктовать сюжет.",
        "details_voice_added": "Голос добавлен прямо в описание сюжета.",
        "spinner_transcribe": "Распознаём голосовую заметку...",
        "warning_transcribe_failed": "Не получилось превратить запись в текст. Попробуй ещё раз.",
        "warning_transcribe_failed_reason": "Причина распознавания",
        "btn_create": "Создать сказку",
        "btn_create_hint": "Мы сделаем историю тёплой, безопасной и подходящей для чтения перед сном.",
        "sidebar_library": "Мои сказки",
        "sidebar_voice": "Выберите голос",
        "sidebar_new": "Новая сказка",
        "sidebar_tagline": "Сказки для сна, близости и маленьких важных побед.",
        "voice_settings": "Голос сказки",
        "ready_story": "Сказка готова",
        "back_btn": "← Назад",
        "empty_story_text": "Текст сказки пустой или не сохранился.",
        "no_saved_stories": "Пока нет сохранённых сказок",
        "section_for_whom": "Для кого сказка",
        "section_language": "Язык истории",
        "section_skill": "Навык или тема",
        "section_format": "Что добавить",
        "section_duration": "Сколько будет длиться чтение",
        "section_details": "Детали сюжета",
        "section_summary": "Что получится",
        "spinner_magic": "Плетём историю...",
        "spinner_voice": "Добавляем голос...",
        "spinner_cover": "Рисуем обложку...",
        "spinner_media": "Готовим иллюстрацию и голос...",
        "story_pending_notice": "Сказка создаётся в фоне. Можно продолжать пользоваться страницей.",
        "story_pending_hint": "Можно менять громкость и другие настройки — процесс не прервётся.",
        "audio_pending_notice": "Сказка уже готова. Озвучка добавляется прямо сейчас.",
        "audio_pending_spinner": "Добавляем озвучку...",
        "audio_pending_hint": "Можно продолжать пользоваться страницей, пока голос догружается.",
        "error_save_story": "Не удалось сохранить сказку.",
        "error_gen_story": "Не удалось сгенерировать текст сказки.",
        "warning_audio_failed": "Не удалось добавить озвучку. Попробуй другой голос.",
        "warning_audio_failed_reason": "Техническая причина",
        "btn_voice_story": "Добавить озвучку",
        "btn_revoice_story": "Озвучить другим голосом",
        "warning_voice_missing": "Сначала выбери голос в левом меню.",
        "story_fallback": "Сказка",
        "delete_help": "Удалить",
        "error_prefix": "Ошибка",
        "account_label": "Аккаунт",
        "logout_btn": "Выйти",
        "manage_billing_btn": "Управлять подпиской",
        "monthly_limit_title": "Лимит месяца",
        "monthly_limit_status": "{used} из {limit} сказок использовано",
        "monthly_limit_left": "Осталось в этом месяце: {left}",
        "monthly_limit_reached": "Лимит этого месяца исчерпан. Скоро подключим дополнительные пакеты и подписку.",
        "monthly_limit_resets": "Сброс лимита: {date}",
        "monthly_bonus_active": "Дополнительно открыто в beta: +{bonus} сказок",
        "music_settings": "Фоновая музыка",
        "music_toggle_show": "♫ Показать громкость",
        "music_toggle_hide": "♫ Скрыть громкость",
        "music_volume": "Громкость музыки",
        "music_hint": "Музыка играет только на экране готовой сказки.",
        "access_panel_title": "Продлить доступ",
        "access_panel_subtitle": "Когда лимит заканчивается, можно сразу открыть дополнительный пакет или план.",
        "access_panel_beta_note": "Пока это beta-механика: кнопки ниже включают доступ без оплаты, чтобы протестировать сценарий продления.",
        "access_panel_live_note": "Когда подключим Stripe-ссылки, эти кнопки будут вести уже на реальную оплату и продление доступа.",
        "plan_recommended": "Рекомендуем",
        "plan_voice_included": "Озвучка включена",
        "plan_extra_name": "Extra Pack",
        "plan_extra_price": "$3.99",
        "plan_extra_copy": "Быстрое продление, если сказки закончились раньше месяца.",
        "plan_extra_btn": "Включить +10",
        "plan_extra_live_btn": "Купить Extra Pack",
        "plan_standard_name": "Standard",
        "plan_standard_price": "$9.99 / мес",
        "plan_standard_copy": "Основной план для ежедневних вечерних сказок.",
        "plan_standard_btn": "Включить Standard",
        "plan_standard_live_btn": "Выбрать Standard",
        "plan_family_name": "Family",
        "plan_family_price": "$14.99 / мес",
        "plan_family_copy": "Больше сказок и более комфортный семейный запас.",
        "plan_family_feature": "Подходит для нескольких детей",
        "plan_family_btn": "Включить Family",
        "plan_family_live_btn": "Выбрать Family",
        "plan_activation_notice": "В beta активирован пакет: {plan}. Новый лимит в этом месяце: {limit}.",
        "section_parent_note": "Каждая история создаётся с мягкой развивающей линией, без жёстких нравоучений и лишней тревоги.",
        "summary_template": "История для {child_name} на {time_val} мин: {skills}.",
        "summary_default_skills": "мягкая поддержка и спокойствие",
        "opt_img": "Добавить иллюстрацию",
        "opt_audio": "Добавить озвучку",
        "voice_hint": "Выберите, каким голосом будет звучать сказка.",
        "tts_provider_label": "Движок озвучки",
        "tts_provider_hint": "Для сравнения можно переключаться между ElevenLabs, OpenAI и Google на одной и той же сказке.",
        "tts_providers": {
            "ElevenLabs": "elevenlabs",
            "OpenAI Voice": "openai",
            "Google Cloud Voice": "google_cloud",
        },
        "openai_voices": {
            "Тёплый мягкий": "marin",
            "Спокойный вечерний": "sage",
            "Светлый нежный": "shimmer",
            "Нейтральный (Alloy)": "alloy",
        },
        "google_cloud_voices": {
            "Женский A (Google)": {"name": "ru-RU-Wavenet-A", "language_code": "ru-RU"},
            "Мужской B (Google)": {"name": "ru-RU-Wavenet-B", "language_code": "ru-RU"},
        },
        "view_hint": "Можно читать самим или включить озвучку, если нужен спокойный ритуал перед сном.",
        "error_child_name": "Напиши имя ребёнка.",
        "error_skills": "Выбери хотя бы один навык или тему.",
        "language_selector": "Язык",
        "voices": {
            "Марина": "ymDCYd8puC7gYjxIamPt",
            "Николай": "8JVbfL6oEdmuxKn5DK2C",
            "Алиса": "EXAVITQu4vr4xnSDxMaL",
            "Новый голос": "vag4Lrn45H8eCOtMyMai",
        },
        "skills": [
            "Честность",
            "Смелость",
            "Доброта",
            "Трудолюбие",
            "Вежливость",
            "Гигиена",
            "Дружба",
            "Усидчивость",
        ],
    },
    "English": {
        "title": BRAND_NAME,
        "subtitle": "Warm bedtime stories that gently support emotional growth and everyday skills.",
        "login_badge": "For parents",
        "login_subtitle": "Build a calm little library of stories for sleep, connection, and confidence.",
        "login_btn": "Log in",
        "login_error": "Login failed. Please check your email and password.",
        "intro_skip": "Skip",
        "intro_copy": "Bedtime stories for calm, closeness, and tiny brave steps.",
        "intro_replay": "Replay the intro",
        "intro_sound": "Tap for sound",
        "intro_tap_sound": "Tap anywhere for sound",
        "intro_continue": "Continue",
        "intro_hint": "If the video does not start automatically, press play and then Continue.",
        "email_label": "Email",
        "password_label": "Password",
        "child_name": "Child's name",
        "child_placeholder": "For example: Emma",
        "default_child_name": "",
        "summary_fallback_child_name": "your child",
        "skills_label": "Which skills should this story gently support?",
        "skills_help": "Choosing 1-2 themes usually creates the most focused and soothing story.",
        "duration": "Duration",
        "duration_btn_suffix": "min",
        "details": "What feels important right now?",
        "details_placeholder": "For example: the child is afraid of the dark, misses preschool, or is learning to share toys.",
        "details_help": "You can mention favorite animals, a current struggle, bedtime mood, or the ending you hope for.",
        "details_voice_label": "Microphone for dictation",
        "details_voice_hint": "You can type manually or tap the mic on the right and dictate the story note.",
        "details_voice_added": "Your voice note was added right into the story details.",
        "spinner_transcribe": "Transcribing your voice note...",
        "warning_transcribe_failed": "We couldn't turn the recording into text. Please try again.",
        "warning_transcribe_failed_reason": "Transcription reason",
        "btn_create": "Create story",
        "btn_create_hint": "We will make it gentle, age-appropriate, and comfortable for bedtime.",
        "sidebar_library": "My stories",
        "sidebar_voice": "Choose a voice",
        "sidebar_new": "New story",
        "sidebar_tagline": "Bedtime stories for closeness, calm, and small brave steps.",
        "voice_settings": "Story voice",
        "ready_story": "Your story is ready",
        "back_btn": "← Back",
        "empty_story_text": "The story text is empty or was not saved.",
        "no_saved_stories": "No saved stories yet",
        "section_for_whom": "Who is this story for",
        "section_language": "Story language",
        "section_skill": "Skill or theme",
        "section_format": "What to include",
        "section_duration": "Reading length",
        "section_details": "Story details",
        "section_summary": "What you'll get",
        "spinner_magic": "Weaving your story...",
        "spinner_voice": "Adding narration...",
        "spinner_cover": "Painting the cover...",
        "spinner_media": "Preparing illustration and narration...",
        "story_pending_notice": "Your story is being created in the background.",
        "story_pending_hint": "You can keep adjusting settings while the generation continues.",
        "audio_pending_notice": "Your story is ready. Narration is being added now.",
        "audio_pending_spinner": "Adding narration...",
        "audio_pending_hint": "You can keep using the app while narration finishes in the background.",
        "error_save_story": "Failed to save the story.",
        "error_gen_story": "Failed to generate the story text.",
        "warning_audio_failed": "We couldn't add narration. Try another voice.",
        "warning_audio_failed_reason": "Technical reason",
        "btn_voice_story": "Add narration",
        "btn_revoice_story": "Narrate with another voice",
        "warning_voice_missing": "First choose a voice in the left sidebar.",
        "story_fallback": "Story",
        "delete_help": "Delete",
        "error_prefix": "Error",
        "account_label": "Account",
        "logout_btn": "Log out",
        "manage_billing_btn": "Manage subscription",
        "monthly_limit_title": "Monthly limit",
        "monthly_limit_status": "{used} of {limit} stories used",
        "monthly_limit_left": "{left} stories left this month",
        "monthly_limit_reached": "This month's limit has been reached. Extra packs and subscriptions are coming soon.",
        "monthly_limit_resets": "Limit resets on {date}",
        "monthly_bonus_active": "Extra beta access unlocked: +{bonus} stories",
        "music_settings": "Background music",
        "music_toggle_show": "♫ Show volume",
        "music_toggle_hide": "♫ Hide volume",
        "music_volume": "Music volume",
        "music_hint": "Music plays only on the finished story screen.",
        "access_panel_title": "Extend access",
        "access_panel_subtitle": "When the monthly limit is used up, you can unlock a pack or plan right away.",
        "access_panel_beta_note": "This is a beta access screen. For now, the buttons below unlock access without payment so we can test the extension flow.",
        "access_panel_live_note": "Once Stripe links are connected, these buttons will open live checkout and subscription management.",
        "plan_recommended": "Recommended",
        "plan_voice_included": "Narration included",
        "plan_extra_name": "Extra Pack",
        "plan_extra_price": "$3.99",
        "plan_extra_copy": "A quick extension when stories run out before the month ends.",
        "plan_extra_btn": "Unlock +10",
        "plan_extra_live_btn": "Buy Extra Pack",
        "plan_standard_name": "Standard",
        "plan_standard_price": "$9.99 / mo",
        "plan_standard_copy": "The core plan for daily bedtime stories.",
        "plan_standard_btn": "Unlock Standard",
        "plan_standard_live_btn": "Choose Standard",
        "plan_family_name": "Family",
        "plan_family_price": "$14.99 / mo",
        "plan_family_copy": "More stories and a more comfortable family buffer.",
        "plan_family_feature": "Built for more than one child",
        "plan_family_btn": "Unlock Family",
        "plan_family_live_btn": "Choose Family",
        "plan_activation_notice": "Beta access activated: {plan}. New limit this month: {limit}.",
        "section_parent_note": "Each story is built to model the chosen skill gently, without fear, shame, or heavy-handed moralizing.",
        "summary_template": "A {time_val}-minute story for {child_name}: {skills}.",
        "summary_default_skills": "gentle support and calm",
        "opt_img": "Add illustration",
        "opt_audio": "Add narration",
        "voice_hint": "Choose how the story should sound.",
        "tts_provider_label": "Narration engine",
        "tts_provider_hint": "For a quick comparison, you can switch between ElevenLabs, OpenAI, and Google on the same story.",
        "tts_providers": {
            "ElevenLabs": "elevenlabs",
            "OpenAI Voice": "openai",
            "Google Cloud Voice": "google_cloud",
        },
        "openai_voices": {
            "Warm and gentle": "marin",
            "Calm evening": "sage",
            "Light and soft": "shimmer",
            "Neutral": "alloy",
        },
        "google_cloud_voices": {
            "Neural2 F (Google)": {"name": "en-US-Neural2-F", "language_code": "en-US"},
            "Neural2 J (Google)": {"name": "en-US-Neural2-J", "language_code": "en-US"},
            "Neural2 D (Google)": {"name": "en-US-Neural2-D", "language_code": "en-US"},
        },
        "view_hint": "You can read it yourself or play the narration when bedtime needs a softer rhythm.",
        "error_child_name": "Please enter the child's name.",
        "error_skills": "Choose at least one skill or theme.",
        "language_selector": "Language",
        "voices": {
            "Alice": "EXAVITQu4vr4xnSDxMaL",
            "Nicholas": "8JVbfL6oEdmuxKn5DK2C",
            "New Voice": "vag4Lrn45H8eCOtMyMai",
        },
        "skills": [
            "Honesty",
            "Bravery",
            "Kindness",
            "Hard work",
            "Politeness",
            "Hygiene",
            "Friendship",
            "Patience",
        ],
    },
    "Română": {
        "title": BRAND_NAME,
        "subtitle": "Povești de seară calde, care sprijină blând emoțiile și obiceiurile bune.",
        "login_badge": "Pentru părinți",
        "login_subtitle": "Construiește o bibliotecă liniștită de povești pentru somn, apropiere și creștere.",
        "login_btn": "Autentificare",
        "login_error": "Autentificarea a eșuat. Verifică emailul și parola.",
        "intro_skip": "Omite",
        "intro_copy": "Povești de seară pentru liniște, apropiere și pași curajoși.",
        "intro_replay": "Redă intro din nou",
        "intro_sound": "Apasă pentru sunet",
        "intro_tap_sound": "Apasă oriunde pentru sunet",
        "intro_continue": "Continuă",
        "intro_hint": "Dacă videoclipul nu pornește automat, apasă play și apoi Continuă.",
        "email_label": "Email",
        "password_label": "Parolă",
        "child_name": "Numele copilului",
        "child_placeholder": "De exemplu: Ana",
        "default_child_name": "",
        "summary_fallback_child_name": "copilul tău",
        "skills_label": "Ce dorim să susținem blând prin această poveste?",
        "skills_help": "Cel mai bine este să alegi 1-2 teme pentru o poveste coerentă și liniștitoare.",
        "duration": "Durată",
        "duration_btn_suffix": "min",
        "details": "Ce este important acum?",
        "details_placeholder": "De exemplu: copilului îi este teamă de întuneric, îi este dor de grădiniță sau învață să împartă jucăriile.",
        "details_help": "Poți menționa animale preferate, o provocare actuală, starea de seară sau finalul dorit.",
        "details_voice_label": "Microfon pentru dictare",
        "details_voice_hint": "Poți scrie manual sau poți apăsa microfonul din dreapta și dicta ideea poveștii.",
        "details_voice_added": "Mesajul vocal a fost adăugat direct în detaliile poveștii.",
        "spinner_transcribe": "Transformăm vocea în text...",
        "warning_transcribe_failed": "Nu am putut transforma înregistrarea în text. Încearcă din nou.",
        "warning_transcribe_failed_reason": "Motivul transcrierii",
        "btn_create": "Creează povestea",
        "btn_create_hint": "Vom crea o poveste caldă, sigură și potrivită pentru seară.",
        "sidebar_library": "Poveștile mele",
        "sidebar_voice": "Alege vocea",
        "sidebar_new": "Poveste nouă",
        "sidebar_tagline": "Povești pentru liniște, apropiere și mici pași curajoși.",
        "voice_settings": "Vocea poveștii",
        "ready_story": "Povestea este gata",
        "back_btn": "← Înapoi",
        "empty_story_text": "Textul poveștii este gol sau nu a fost salvat.",
        "no_saved_stories": "Încă nu există povești salvate",
        "section_for_whom": "Pentru cine este povestea",
        "section_language": "Limba poveștii",
        "section_skill": "Abilitate sau temă",
        "section_format": "Ce includem",
        "section_duration": "Durata lecturii",
        "section_details": "Detalii ale poveștii",
        "section_summary": "Ce vei primi",
        "spinner_magic": "Țesem povestea...",
        "spinner_voice": "Adăugăm vocea...",
        "spinner_cover": "Desenăm coperta...",
        "spinner_media": "Pregătim ilustrația și narațiunea...",
        "story_pending_notice": "Povestea se creează în fundal.",
        "story_pending_hint": "Poți schimba volumul și alte setări fără să oprești procesul.",
        "audio_pending_notice": "Povestea este deja gata. Adăugăm acum și narațiunea.",
        "audio_pending_spinner": "Adăugăm narațiunea...",
        "audio_pending_hint": "Poți continua să folosești aplicația cât timp narațiunea se termină în fundal.",
        "error_save_story": "Povestea nu a putut fi salvată.",
        "error_gen_story": "Textul poveștii nu a putut fi generat.",
        "warning_audio_failed": "Nu am putut adăuga narațiunea. Încearcă altă voce.",
        "warning_audio_failed_reason": "Motiv tehnic",
        "btn_voice_story": "Adaugă narațiune",
        "btn_revoice_story": "Narează cu altă voce",
        "warning_voice_missing": "Alege mai întâi vocea din meniul din stânga.",
        "story_fallback": "Poveste",
        "delete_help": "Șterge",
        "error_prefix": "Eroare",
        "account_label": "Cont",
        "logout_btn": "Ieșire",
        "manage_billing_btn": "Gestionează abonamentul",
        "monthly_limit_title": "Limita lunii",
        "monthly_limit_status": "{used} din {limit} povești folosite",
        "monthly_limit_left": "{left} povești rămase în această lună",
        "monthly_limit_reached": "Limita acestei luni a fost atinsă. În curând vom adăuga pachete extra și abonamente.",
        "monthly_limit_resets": "Limita se resetează la {date}",
        "monthly_bonus_active": "Acces beta extra deblocat: +{bonus} povești",
        "music_settings": "Muzică de fundal",
        "music_toggle_show": "♫ Arată volumul",
        "music_toggle_hide": "♫ Ascunde volumul",
        "music_volume": "Volumul muzicii",
        "music_hint": "Muzica rulează doar pe ecranul poveștii gata.",
        "access_panel_title": "Extinde accesul",
        "access_panel_subtitle": "Când limita lunară se termină, poți activa imediat un pachet sau un plan.",
        "access_panel_beta_note": "Acesta este ecranul beta pentru acces. Deocamdată, butoanele de mai jos activează accesul fără plată ca să testăm fluxul de prelungire.",
        "access_panel_live_note": "După conectarea linkurilor Stripe, aceste butoane vor deschide plata reală și prelungirea accesului.",
        "plan_recommended": "Recomandat",
        "plan_voice_included": "Narațiune inclusă",
        "plan_extra_name": "Extra Pack",
        "plan_extra_price": "$3.99",
        "plan_extra_copy": "O prelungire rapidă când poveștile se termină înainte de sfârșitul lunii.",
        "plan_extra_btn": "Activează +10",
        "plan_extra_live_btn": "Cumpără Extra Pack",
        "plan_standard_name": "Standard",
        "plan_standard_price": "$9.99 / lună",
        "plan_standard_copy": "Planul principal pentru povești de seară zilnice.",
        "plan_standard_btn": "Activează Standard",
        "plan_standard_live_btn": "Alege Standard",
        "plan_family_name": "Family",
        "plan_family_price": "$14.99 / lună",
        "plan_family_copy": "Mai multe povești și un buffer mai confortabil pentru familie.",
        "plan_family_feature": "Potrivit pentru mai mulți copii",
        "plan_family_btn": "Activează Family",
        "plan_family_live_btn": "Alege Family",
        "plan_activation_notice": "În beta a fost activat pachetul: {plan}. Noua limită din această lună este: {limit}.",
        "section_parent_note": "Fiecare poveste modelează blând tema aleasă, fără frică, rușinare sau morală apăsătoare.",
        "summary_template": "O poveste de {time_val} minute pentru {child_name}: {skills}.",
        "summary_default_skills": "sprijin blând și liniște",
        "opt_img": "Adaugă ilustrație",
        "opt_audio": "Adaugă narațiune",
        "voice_hint": "Alege cum vrei să sune povestea.",
        "tts_provider_label": "Motor de narațiune",
        "tts_provider_hint": "Pentru comparație rapidă, poți comuta între ElevenLabs, OpenAI și Google pe aceeași poveste.",
        "tts_providers": {
            "ElevenLabs": "elevenlabs",
            "OpenAI Voice": "openai",
            "Google Cloud Voice": "google_cloud",
        },
        "openai_voices": {
            "Voce caldă și blândă": "marin",
            "Voce calmă de seară": "sage",
            "Voce luminoasă și fină": "shimmer",
            "Voce neutră": "alloy",
        },
        "google_cloud_voices": {
            "Wavenet A (Google)": {"name": "ro-RO-Wavenet-A", "language_code": "ro-RO"},
            "Wavenet B (Google)": {"name": "ro-RO-Wavenet-B", "language_code": "ro-RO"},
        },
        "view_hint": "O poți citi tu sau poți porni narațiunea când seara are nevoie de mai multă liniște.",
        "error_child_name": "Te rog să introduci numele copilului.",
        "error_skills": "Alege cel puțin o abilitate sau o temă.",
        "language_selector": "Limbă",
        "voices": {
            "Alina": "EXAVITQu4vr4xnSDxMaL",
            "Marcel": "8JVbfL6oEdmuxKn5DK2C",
            "Voce noua": "vag4Lrn45H8eCOtMyMai",
        },
        "skills": [
            "Onestitate",
            "Curaj",
            "Bunătate",
            "Hărnicie",
            "Politețe",
            "Igienă",
            "Prietenie",
            "Răbdare",
        ],
    },
}


if "time_val" not in st.session_state:
    st.session_state.time_val = 5
if "view_story" not in st.session_state:
    st.session_state.view_story = None
if "sel_lang" not in st.session_state:
    st.session_state.sel_lang = "English"
if "page_mode" not in st.session_state:
    st.session_state.page_mode = "form"
if "show_intro" not in st.session_state:
    st.session_state.show_intro = ENABLE_INTRO_OVERLAY
if "force_intro" not in st.session_state:
    st.session_state.force_intro = False
if "details_input" not in st.session_state:
    st.session_state.details_input = ""
if "last_processed_voice_note_hash" not in st.session_state:
    st.session_state.last_processed_voice_note_hash = ""
if "voice_note_widget_version" not in st.session_state:
    st.session_state.voice_note_widget_version = 0
if "voice_note_pending_process" not in st.session_state:
    st.session_state.voice_note_pending_process = False
if "bg_music_volume" not in st.session_state:
    st.session_state.bg_music_volume = 42
if "show_music_controls" not in st.session_state:
    st.session_state.show_music_controls = False
if "monthly_story_bonus" not in st.session_state:
    st.session_state.monthly_story_bonus = 0
if "billing_notice" not in st.session_state:
    st.session_state.billing_notice = ""
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "auth_provider" not in st.session_state:
    st.session_state.auth_provider = ""
if "auth_access_token" not in st.session_state:
    st.session_state.auth_access_token = ""
if "auth_refresh_token" not in st.session_state:
    st.session_state.auth_refresh_token = ""
if "story_generation_job" not in st.session_state:
    st.session_state.story_generation_job = None
if "audio_generation_job" not in st.session_state:
    st.session_state.audio_generation_job = None
if "story_generation_error" not in st.session_state:
    st.session_state.story_generation_error = ""
if "audio_generation_error" not in st.session_state:
    st.session_state.audio_generation_error = ""


lang_options = list(lang_dict.keys())
active_copy_pack = lang_dict.get(st.session_state.get("sel_lang", "English"), lang_dict["English"])

if st.session_state.show_intro and render_intro_overlay(active_copy_pack):
    st.session_state.show_intro = False


if not st.session_state.get("logged_in", False):
    stop_bg_music()

    current_lang = st.session_state.get("sel_lang", "English")
    copy_pack = lang_dict.get(current_lang, lang_dict["English"])

    _, center, _ = st.columns([1, 2, 1])
    with center:
        selected_lang = st.selectbox(
            copy_pack.get("language_selector", "Language"),
            lang_options,
            index=lang_options.index(current_lang),
            key="login_lang_selector",
            label_visibility="collapsed",
        )
        if selected_lang != current_lang:
            st.session_state.sel_lang = selected_lang
            st.rerun()

        st.markdown(
            f"""
            <div class="hero-badge">{copy_pack.get("login_badge", "")}</div>
            <div class="hero-title">🌙 {BRAND_NAME}</div>
            <div class="hero-subtitle">{copy_pack.get("login_subtitle", "")}</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        with st.form("login_form"):
            email = st.text_input(copy_pack.get("email_label", "Email"), key="login_email")
            password = st.text_input(
                copy_pack.get("password_label", "Password"),
                type="password",
                key="login_password",
            )

            submitted = st.form_submit_button(
                copy_pack.get("login_btn", "Log in"),
                type="primary",
                use_container_width=True,
            )

        if submitted:
            sign_in_result = sign_in_user(email, password)
            if sign_in_result.get("ok"):
                st.session_state.logged_in = True
                st.session_state.user_email = sign_in_result.get("email", email.strip())
                st.session_state.auth_provider = sign_in_result.get("provider", "")
                st.session_state.auth_access_token = sign_in_result.get("access_token", "")
                st.session_state.auth_refresh_token = sign_in_result.get("refresh_token", "")
                st.session_state.page_mode = "form"
                st.session_state.view_story = None
                st.rerun()
            else:
                st.error(copy_pack.get("login_error", "Login failed"))

else:
    copy_pack = lang_dict.get(st.session_state.sel_lang, lang_dict["English"])
    stories = get_user_stories(st.session_state.user_email)
    payment_links = get_payment_links()
    monthly_story_usage = get_monthly_story_usage(stories)
    effective_monthly_limit = MONTHLY_STORY_LIMIT + st.session_state.monthly_story_bonus
    monthly_stories_left = max(effective_monthly_limit - monthly_story_usage, 0)
    monthly_limit_reached = monthly_stories_left <= 0
    next_reset_date = get_next_month_reset_date()
    billing_notice = st.session_state.pop("billing_notice", "")
    story_generation_error = st.session_state.pop("story_generation_error", "")
    audio_generation_error = st.session_state.pop("audio_generation_error", "")

    with st.sidebar:
        try:
            st.image("logo.jpg", width=88)
        except Exception:
            pass

        st.markdown(
            f"""
            <div class="sidebar-brand">🌙 {copy_pack.get("title", BRAND_NAME)}</div>
            <div class="sidebar-subbrand">{copy_pack.get("sidebar_tagline", "")}</div>
            """,
            unsafe_allow_html=True,
        )

        st.success(f'{copy_pack.get("account_label", "Account")}: {st.session_state.user_email}')
        if st.button(
            copy_pack.get("logout_btn", "Log out"),
            use_container_width=True,
            key="sidebar_logout_btn",
        ):
            sign_out_user(
                st.session_state.get("auth_access_token", ""),
                st.session_state.get("auth_refresh_token", ""),
            )
            reset_authenticated_session()
            st.rerun()

        st.markdown(
            f'<div class="section-label">{copy_pack.get("monthly_limit_title", "Monthly limit")}</div>',
            unsafe_allow_html=True,
        )
        st.progress(min(monthly_story_usage / effective_monthly_limit, 1.0))
        st.caption(
            copy_pack.get("monthly_limit_status", "{used} of {limit} stories used").format(
                used=monthly_story_usage,
                limit=effective_monthly_limit,
            )
        )
        st.caption(
            copy_pack.get("monthly_limit_left", "{left} stories left this month").format(
                left=monthly_stories_left,
            )
        )
        st.caption(
            copy_pack.get("monthly_limit_resets", "Limit resets on {date}").format(
                date=next_reset_date,
            )
        )
        if st.session_state.monthly_story_bonus > 0:
            st.caption(
                copy_pack.get("monthly_bonus_active", "Extra beta access unlocked: +{bonus} stories").format(
                    bonus=st.session_state.monthly_story_bonus,
                )
            )
        if monthly_limit_reached:
            st.warning(
                copy_pack.get(
                    "monthly_limit_reached",
                    "This month's limit has been reached.",
                )
            )
        if billing_notice:
            st.success(billing_notice)
        if payment_links.get("portal"):
            st.link_button(
                copy_pack.get("manage_billing_btn", "Управлять подпиской"),
                payment_links["portal"],
                use_container_width=True,
            )

        with st.expander(copy_pack.get("sidebar_library", "Stories"), expanded=False):
            render_story_library(stories, copy_pack, prefix="side")

        st.divider()

        st.markdown(
            f'<div class="section-label">{copy_pack.get("voice_settings", "Voice settings")}</div>',
            unsafe_allow_html=True,
        )
        provider_options = copy_pack.get(
            "tts_providers",
            {
                "ElevenLabs": "elevenlabs",
                "OpenAI Voice": "openai",
                "Google Cloud Voice": "google_cloud",
            },
        )
        if SHOW_TTS_PROVIDER_SELECTOR:
            st.caption(copy_pack.get("tts_provider_hint", ""))
            provider_name = st.selectbox(
                copy_pack.get("tts_provider_label", "Narration engine"),
                list(provider_options.keys()),
                key="tts_provider_select",
            )
            tts_provider = provider_options.get(provider_name, DEFAULT_TTS_PROVIDER)
        else:
            tts_provider = DEFAULT_TTS_PROVIDER

        st.caption(copy_pack.get("voice_hint", ""))

        if tts_provider == "openai":
            voice_options = copy_pack.get("openai_voices", {})
        elif tts_provider == "google_cloud":
            voice_options = copy_pack.get("google_cloud_voices", {})
        else:
            voice_options = copy_pack.get("voices", {})
        voice_name = st.selectbox(
            copy_pack.get("sidebar_voice", "Voice"),
            list(voice_options.keys()),
            key=f"voice_select_{tts_provider}",
        )
        voice_id = voice_options.get(voice_name)

        st.markdown(
            f'<div class="section-label">{copy_pack.get("music_settings", "Background music")}</div>',
            unsafe_allow_html=True,
        )
        if st.button(
            copy_pack.get(
                "music_toggle_hide" if st.session_state.show_music_controls else "music_toggle_show",
                "Adjust music",
            ),
            use_container_width=True,
            key="toggle_music_controls_btn",
        ):
            st.session_state.show_music_controls = not st.session_state.show_music_controls
            st.rerun()

        if st.session_state.show_music_controls:
            st.slider(
                copy_pack.get("music_volume", "Music volume"),
                min_value=0,
                max_value=100,
                step=1,
                key="bg_music_volume",
            )
            st.caption(copy_pack.get("music_hint", ""))

        if SHOW_INTRO_REPLAY_BUTTON:
            if st.button(
                copy_pack.get("intro_replay", "Replay intro"),
                use_container_width=True,
                key="replay_intro_btn",
            ):
                replay_intro_overlay()

        if st.button(
            copy_pack.get("sidebar_new", "New story"),
            use_container_width=True,
            type="primary",
            key="sidebar_new_story_btn",
        ):
            st.session_state.view_story = None
            st.session_state.page_mode = "form"
            st.rerun()

    render_background_job_watcher(copy_pack)
    if story_generation_error:
        st.error(story_generation_error)
    if audio_generation_error:
        st.warning(copy_pack.get("warning_audio_failed", "Narration was not generated. Please try again."))
        st.caption(
            f"{copy_pack.get('warning_audio_failed_reason', 'Technical reason')}: {audio_generation_error}"
        )

    if st.session_state.page_mode == "view" and st.session_state.view_story:
        story = st.session_state.view_story
        bg_music_ready = mount_bg_music(st.session_state.bg_music_volume / 100)
        audio_job = st.session_state.get("audio_generation_job")
        audio_pending_for_current_story = bool(
            audio_job
            and audio_job.get("story_id") == story.get("id")
            and audio_job.get("future")
            and not audio_job["future"].done()
        )

        top_left, top_right = st.columns([1, 6])

        with top_left:
            if st.button(
                copy_pack.get("back_btn", "← Back"),
                use_container_width=True,
                key="back_story_btn",
            ):
                st.session_state.view_story = None
                st.session_state.page_mode = "form"
                st.rerun()

        with top_right:
            st.markdown(
                f"""
                <div class="hero-badge">{copy_pack.get("ready_story", "Story ready")}</div>
                <div class="hero-title story-title">{html.escape(story.get("title", copy_pack.get("story_fallback", "Story")))}</div>
                <div class="hero-subtitle">{copy_pack.get("view_hint", "")}</div>
                """,
                unsafe_allow_html=True,
            )

        story_text = (story.get("story_text") or "").strip()

        voice_button_label = (
            copy_pack.get("btn_revoice_story", "Re-narrate with current voice")
            if story.get("audio_base64")
            else copy_pack.get("btn_voice_story", "Narrate this story")
        )
        if st.button(
            voice_button_label,
            type="secondary",
            use_container_width=True,
            key=f"voice_current_story_{story.get('id', 'current')}",
            disabled=audio_pending_for_current_story,
        ):
            if not voice_id:
                st.warning(copy_pack.get("warning_voice_missing", "First choose a voice in the left sidebar."))
            elif not story_text:
                st.warning(copy_pack.get("empty_story_text", "Story text is empty."))
            else:
                start_audio_generation_job(story["id"], story_text, voice_id, tts_provider)
                st.rerun()

        if story.get("audio_base64"):
            try:
                st.audio(base64.b64decode(story["audio_base64"]))
            except Exception:
                pass

        if story.get("image_url"):
            st.image(story["image_url"], use_container_width=True)

        if story_text:
            safe_story = html.escape(story_text).replace("\n", "<br>")
            st.markdown(
                f"""
                <div class="story-shell">
                    <div class="story-output">
                        {safe_story}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.warning(copy_pack.get("empty_story_text", "Story text is empty."))

        if not bg_music_ready:
            st.caption("Чтобы играла фоновая музыка, положи файл `bg_music.mp3` рядом с `app.py`.")

    else:
        stop_bg_music()

        _, center, _ = st.columns([1, 2, 1])

        with center:
            st.markdown(
                f"""
                <div class="hero-badge">{copy_pack.get("title", BRAND_NAME)}</div>
                <div class="hero-title">🌙 {BRAND_NAME}</div>
                <div class="hero-subtitle">{copy_pack.get("subtitle", "")}</div>
                """,
                unsafe_allow_html=True,
            )
            st.caption(copy_pack.get("section_parent_note", ""))

            st.markdown(
                f'<div class="section-label">{copy_pack.get("section_for_whom", "For whom")}</div>',
                unsafe_allow_html=True,
            )
            child_name = st.text_input(
                copy_pack.get("child_name", "Child's name"),
                value="",
                placeholder=copy_pack.get("child_placeholder", ""),
            )

            st.markdown(
                f'<div class="section-label">{copy_pack.get("section_language", "Language")}</div>',
                unsafe_allow_html=True,
            )
            new_lang = st.selectbox(
                copy_pack.get("language_selector", "Language"),
                lang_options,
                index=lang_options.index(st.session_state.sel_lang),
                key="lang_selector_center",
                label_visibility="collapsed",
            )
            if new_lang != st.session_state.sel_lang:
                st.session_state.sel_lang = new_lang
                st.rerun()

            st.markdown(
                f'<div class="section-label">{copy_pack.get("section_skill", "Skill")}</div>',
                unsafe_allow_html=True,
            )
            skills = st.multiselect(
                copy_pack.get("skills_label", "Skills"),
                copy_pack.get("skills", []),
                default=[copy_pack.get("skills", [""])[0]] if copy_pack.get("skills") else [],
                label_visibility="collapsed",
            )
            st.caption(copy_pack.get("skills_help", ""))

            st.markdown(
                f'<div class="section-label">{copy_pack.get("section_format", "Format")}</div>',
                unsafe_allow_html=True,
            )
            format_left, format_right = st.columns(2)
            with format_left:
                use_img = st.checkbox(
                    copy_pack.get("opt_img", "Add illustration"),
                    value=True,
                    key="use_img_checkbox",
                )
            with format_right:
                use_audio = st.checkbox(
                    copy_pack.get("opt_audio", "Add narration"),
                    value=True,
                    key="use_audio_checkbox",
                )

            st.markdown(
                f'<div class="section-label">{copy_pack.get("section_duration", "Duration")}</div>',
                unsafe_allow_html=True,
            )
            duration_columns = st.columns(3)
            for index, minutes in enumerate([3, 5, 10]):
                if duration_columns[index].button(
                    f'{minutes} {copy_pack.get("duration_btn_suffix", "min")}',
                    key=f"duration_btn_{minutes}",
                    type="primary" if st.session_state.time_val == minutes else "secondary",
                    use_container_width=True,
                ):
                    st.session_state.time_val = minutes
                    st.rerun()

            st.markdown(
                f'<div class="section-label">{copy_pack.get("section_details", "Details")}</div>',
                unsafe_allow_html=True,
            )
            apply_pending_story_details()
            voice_note_key = f"details_voice_note_{st.session_state.voice_note_widget_version}"

            details_col, mic_col = st.columns([7, 1], gap="small")
            with details_col:
                details = st.text_area(
                    copy_pack.get("details", "Story details"),
                    key="details_input",
                    label_visibility="collapsed",
                    placeholder=copy_pack.get("details_placeholder", ""),
                )
            with mic_col:
                voice_note = st.audio_input(
                    copy_pack.get("details_voice_label", "Microphone for dictation"),
                    label_visibility="collapsed",
                    key=voice_note_key,
                    on_change=queue_story_voice_note_processing,
                )

            st.caption(copy_pack.get("details_help", ""))
            st.caption(copy_pack.get("details_voice_hint", ""))

            voice_note_status = st.session_state.pop("voice_note_status", None)
            voice_note_error_message = st.session_state.pop("voice_note_error_message", "")

            if st.session_state.pop("voice_note_pending_process", False):
                pending_voice_note = st.session_state.get(voice_note_key)
                if pending_voice_note is not None:
                    with st.spinner(copy_pack.get("spinner_transcribe", "Transcribing your voice note...")):
                        maybe_process_story_voice_note(pending_voice_note, st.session_state.sel_lang)

            if voice_note_status == "success":
                st.success(copy_pack.get("details_voice_added", "Your voice note was added right into the story details."))
            elif voice_note_status == "error":
                st.warning(
                    copy_pack.get(
                        "warning_transcribe_failed",
                        "We couldn't turn the recording into text. Please try again.",
                    )
                )
                if voice_note_error_message:
                    st.caption(
                        f"{copy_pack.get('warning_transcribe_failed_reason', 'Transcription reason')}: {voice_note_error_message}"
                    )

            selected_skills = ", ".join(skills) if skills else copy_pack.get("summary_default_skills", "")
            story_summary = copy_pack.get("summary_template", "{skills}").format(
                child_name=child_name.strip() or copy_pack.get("summary_fallback_child_name", "your child"),
                time_val=st.session_state.time_val,
                skills=selected_skills,
            )
            st.markdown(
                f'<div class="soft-info-chip">{html.escape(story_summary)}</div>',
                unsafe_allow_html=True,
            )

            st.caption(copy_pack.get("btn_create_hint", ""))
            story_generation_in_progress = bool(st.session_state.get("story_generation_job"))
            if monthly_limit_reached:
                st.warning(
                    copy_pack.get(
                        "monthly_limit_reached",
                        "This month's limit has been reached.",
                    )
                )
                render_access_panel(copy_pack, payment_links)

            if st.button(
                copy_pack.get("btn_create", "Create story"),
                type="primary",
                use_container_width=True,
                key="create_story_btn",
                disabled=monthly_limit_reached or story_generation_in_progress,
            ):
                errors = validate_story_request(child_name, skills, copy_pack)
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    start_story_generation_job(
                        user_email=st.session_state.user_email,
                        child_name=child_name.strip(),
                        selected_lang=st.session_state.sel_lang,
                        skills=skills,
                        details=details.strip(),
                        time_val=st.session_state.time_val,
                        use_img=use_img,
                        use_audio=use_audio,
                        voice_id=voice_id,
                        tts_provider=tts_provider,
                    )
                    st.rerun()
