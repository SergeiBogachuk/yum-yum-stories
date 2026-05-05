import streamlit as st


def apply_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Manrope:wght@400;500;600;700;800&display=swap');

	        :root {
	            --bg-0: #fffdf8;
	            --bg-1: #f8eee2;
	            --bg-2: #ead8c2;
	            --panel: rgba(255, 252, 247, 0.9);
	            --panel-strong: rgba(255, 251, 246, 0.98);
	            --panel-soft: rgba(255, 246, 236, 0.82);
            --sidebar-0: #221c18;
            --sidebar-1: #2b221d;
            --sidebar-2: #3b2d26;
            --ink: #231d18;
            --ink-soft: #5f5247;
            --ink-muted: #8a7968;
            --line: rgba(78, 56, 37, 0.13);
            --line-strong: rgba(125, 91, 58, 0.24);
            --accent: #bf7a44;
            --accent-strong: #9e5e31;
            --accent-soft: #f6e2cb;
            --accent-soft-2: #fff1e0;
            --danger-soft: #f5b69f;
            --success-soft: #dfe9cf;
            --shadow-lg: 0 28px 70px rgba(65, 42, 22, 0.14);
            --shadow-md: 0 18px 36px rgba(65, 42, 22, 0.1);
            --shadow-sm: 0 10px 22px rgba(65, 42, 22, 0.08);
            --radius-xl: 34px;
            --radius-lg: 24px;
            --radius-md: 18px;
            --radius-sm: 14px;
        }

        html, body, [class*="css"] {
            font-family: "Manrope", sans-serif;
        }

	        .stApp {
	            color: var(--ink) !important;
	            background:
	                radial-gradient(circle at 18% 8%, rgba(255, 226, 194, 0.22), transparent 26%),
	                radial-gradient(circle at 82% 4%, rgba(231, 242, 241, 0.52), transparent 30%),
	                radial-gradient(circle at 50% 105%, rgba(169, 116, 77, 0.08), transparent 36%),
	                linear-gradient(135deg, #fffdf9 0%, #f7efe5 54%, #efe1d1 100%) !important;
	            position: relative;
	            overflow-x: hidden;
	            min-height: 100svh !important;
	        }

        [data-testid="stAppViewContainer"] {
            position: relative;
            z-index: 0;
        }

        [data-testid="stSidebar"] {
            position: relative;
            z-index: 20 !important;
        }

        @media (min-width: 769px) {
            [data-testid="stSidebar"] {
                display: block !important;
                visibility: visible !important;
                transform: translateX(0) !important;
                opacity: 1 !important;
                min-width: 292px !important;
                width: 292px !important;
                max-width: 292px !important;
            }

            [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
                padding-top: 1rem !important;
                padding-bottom: 1rem !important;
            }
        }

        #MainMenu,
        footer,
	        [data-testid="stDecoration"],
	        [data-testid="stStatusWidget"] {
	            display: none !important;
	            visibility: hidden !important;
	            height: 0 !important;
	            min-height: 0 !important;
	        }

	        header[data-testid="stHeader"] {
	            display: block !important;
	            visibility: visible !important;
	            height: 0 !important;
	            min-height: 0 !important;
	            background: transparent !important;
	            overflow: visible !important;
	            pointer-events: none !important;
	            z-index: 2147482000 !important;
	        }

        [data-testid="stToolbar"] {
            display: flex !important;
            visibility: visible !important;
            height: 0 !important;
            min-height: 0 !important;
            background: transparent !important;
            pointer-events: none !important;
            overflow: visible !important;
        }

        [data-testid="stAppViewContainer"] {
            background: transparent !important;
        }

        section[data-testid="stMain"] {
            background: transparent !important;
            min-height: 0 !important;
            padding-bottom: 0 !important;
        }

        section[data-testid="stMain"] > div,
        [data-testid="stAppViewContainer"] > .main {
            padding-bottom: 0 !important;
        }

        [data-testid="stBottomBlockContainer"],
        [data-testid="stBottomBlockContainer"] * {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
        }

	        [data-testid="collapsedControl"],
	        [data-testid="stExpandSidebarButton"],
	        [data-testid="stSidebarCollapsedControl"],
	        [data-testid="stSidebarCollapseButton"] {
	            display: flex !important;
	            visibility: visible !important;
	            position: fixed !important;
	            top: max(12px, env(safe-area-inset-top)) !important;
	            left: max(12px, env(safe-area-inset-left)) !important;
	            width: 44px !important;
	            height: 44px !important;
	            align-items: center !important;
	            justify-content: center !important;
	            background: rgba(255, 248, 240, 0.92) !important;
	            border: 1px solid var(--line) !important;
	            border-radius: 14px !important;
            box-shadow: var(--shadow-sm) !important;
            color: var(--ink) !important;
            pointer-events: auto !important;
            opacity: 1 !important;
            z-index: 2147483000 !important;
        }

        [data-testid="collapsedControl"] *,
        [data-testid="collapsedControl"] svg,
        [data-testid="stExpandSidebarButton"] *,
        [data-testid="stExpandSidebarButton"] svg,
        [data-testid="stSidebarCollapsedControl"] *,
        [data-testid="stSidebarCollapsedControl"] svg,
        [data-testid="stSidebarCollapseButton"] *,
        [data-testid="stSidebarCollapseButton"] svg {
            color: var(--ink) !important;
            fill: var(--ink) !important;
            stroke: var(--ink) !important;
        }

	        .block-container,
	        [data-testid="block-container"],
	        [data-testid="stMainBlockContainer"] {
	            max-width: min(880px, calc(100vw - 44px)) !important;
	            margin-left: auto !important;
	            margin-right: auto !important;
	            margin-top: 14px !important;
	            margin-bottom: 0 !important;
	            padding: 1.45rem 1.55rem 0.75rem 1.55rem !important;
	            background:
	                linear-gradient(180deg, rgba(255, 252, 247, 0.9), rgba(255, 248, 241, 0.78)) !important;
	            border: 1px solid rgba(120, 89, 58, 0.11) !important;
	            border-radius: var(--radius-xl) !important;
	            box-shadow: 0 24px 58px rgba(65, 42, 22, 0.1) !important;
	            backdrop-filter: blur(18px) !important;
	        }

	        [data-testid="block-container"]:has(.story-form-marker),
	        .block-container:has(.story-form-marker),
	        [data-testid="stMainBlockContainer"]:has(.story-form-marker) {
	            max-width: min(720px, calc(100vw - 44px)) !important;
	            padding: 0.85rem 1rem 0.25rem 1rem !important;
	            border-radius: 28px !important;
	            background:
	                linear-gradient(180deg, rgba(255, 253, 248, 0.94), rgba(255, 249, 241, 0.86)) !important;
	        }

        [data-testid="stVerticalBlock"]:has(.story-form-marker),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.story-form-marker),
        div:has(> .st-key-story_form_shell) {
            max-width: min(700px, calc(100vw - 44px)) !important;
            margin-left: auto !important;
            margin-right: auto !important;
            padding-bottom: 0 !important;
        }

	        [data-testid="block-container"]:has(.story-form-marker) > div,
	        .block-container:has(.story-form-marker) > div {
	            gap: 0.28rem !important;
	        }

        .st-key-story_form_shell {
            max-width: min(700px, calc(100vw - 44px)) !important;
            margin: 0 auto !important;
            padding: 0.05rem 0 0 !important;
        }

        .st-key-story_form_shell [data-testid="stVerticalBlock"] {
            gap: 0.28rem !important;
        }

        .st-key-story_form_shell .stTextInput,
        .st-key-story_form_shell .stSelectbox,
        .st-key-story_form_shell .stMultiSelect,
        .st-key-story_form_shell .stTextArea {
            margin-bottom: 0.14rem !important;
        }

        .st-key-story_form_shell .stTextInput input {
            min-height: 38px !important;
            padding: 0.42rem 0.78rem !important;
        }

        .st-key-story_form_shell div[data-baseweb="select"] > div {
            min-height: 38px !important;
        }

        .st-key-story_form_shell [data-testid="stTextAreaRootElement"] {
            border-radius: 16px !important;
        }

        .st-key-story_form_shell .stTextArea textarea {
            min-height: 92px !important;
            padding: 0.62rem 0.78rem !important;
            line-height: 1.48 !important;
        }

        .st-key-story_form_shell div.stButton > button {
            min-height: 40px !important;
            border-radius: 14px !important;
        }

        .st-key-story_form_shell .stCheckbox {
            padding: 8px 12px !important;
            border-radius: 14px !important;
        }

        .st-key-story_form_shell .stCaptionContainer,
        .st-key-story_form_shell .stCaptionContainer p {
            line-height: 1.45 !important;
            margin-top: -0.05rem !important;
        }

        [data-testid="block-container"]:has(.login-page-marker) {
            max-width: min(1040px, calc(100vw - 38px)) !important;
            padding-bottom: 1.65rem !important;
        }

        [data-testid="block-container"]:has(.login-page-marker) .stSelectbox {
            max-width: 720px !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }

        [data-testid="block-container"]:has(.login-page-marker) [data-testid="stForm"],
        [data-testid="block-container"]:has(.login-page-marker) div[data-testid="stHorizontalBlock"] {
            max-width: 720px !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }

        [data-testid="block-container"]:has(.login-page-marker) [data-testid="stForm"] {
            padding: 1rem 1rem 1.05rem 1rem !important;
            border-radius: 24px !important;
            background:
                linear-gradient(180deg, rgba(255, 251, 245, 0.88), rgba(248, 239, 226, 0.64)) !important;
            border: 1px solid rgba(123, 91, 58, 0.18) !important;
            box-shadow: 0 18px 44px rgba(67, 43, 25, 0.08) !important;
        }

        [data-testid="stSidebar"] {
            background:
                radial-gradient(circle at 22% 0%, rgba(255, 209, 151, 0.22), transparent 30%),
                linear-gradient(180deg, #1b1512 0%, #291f1a 48%, #38261f 100%) !important;
            border-right: 1px solid rgba(255, 234, 212, 0.16) !important;
            box-shadow:
                inset -1px 0 0 rgba(255,255,255,0.07),
                18px 0 56px rgba(42, 28, 19, 0.16) !important;
        }

        [data-testid="stSidebar"] * {
            color: #fff7ed !important;
        }

        [data-testid="stSidebar"] .stCaptionContainer,
        [data-testid="stSidebar"] .stCaptionContainer p {
            color: rgba(255, 247, 237, 0.78) !important;
        }

        [data-testid="stSidebar"] .stAlert {
            border-radius: var(--radius-md) !important;
            border: 1px solid rgba(255, 227, 194, 0.12) !important;
            background: rgba(246, 224, 198, 0.1) !important;
            box-shadow: none !important;
        }

        [data-testid="stSidebar"] a {
            color: #ffe1b7 !important;
            font-weight: 800 !important;
        }

        [data-testid="stSidebar"] .section-label {
            color: #d8a26e !important;
            text-shadow: 0 1px 0 rgba(0, 0, 0, 0.18);
        }

        h1, h2, h3 {
            color: var(--ink) !important;
            font-family: "Fraunces", serif !important;
            letter-spacing: -0.03em !important;
        }

        .hero-badge {
            width: fit-content;
            margin: 0 auto 14px auto;
            padding: 9px 16px;
            border-radius: 999px;
            background: rgba(255, 241, 222, 0.9);
            color: #8b562d;
            border: 1px solid rgba(196, 145, 89, 0.24);
            box-shadow: 0 10px 24px rgba(120, 76, 36, 0.08);
            font-size: 0.92rem;
            font-weight: 800;
            letter-spacing: 0.01em;
        }

        .hero-title {
            text-align: center;
            font-family: "Fraunces", serif;
            font-size: clamp(2.8rem, 4.6vw, 4.5rem);
            font-weight: 700;
            line-height: 0.98;
            color: var(--ink);
            text-wrap: balance;
            margin-bottom: 0.7rem;
        }

        .story-title {
            font-size: clamp(2.2rem, 4vw, 3.3rem);
        }

	        .hero-subtitle {
	            text-align: center;
	            color: var(--ink-soft);
	            font-size: 1.05rem;
            line-height: 1.75;
            margin: 0 auto 1.55rem auto;
            max-width: 700px;
	            text-wrap: balance;
	        }

	        [data-testid="block-container"]:has(.story-form-marker) .hero-badge,
	        .block-container:has(.story-form-marker) .hero-badge,
	        .st-key-story_form_shell .hero-badge {
	            margin-bottom: 9px;
	            padding: 7px 13px;
	            font-size: 0.82rem;
	        }

	        [data-testid="block-container"]:has(.story-form-marker) .hero-title,
	        .block-container:has(.story-form-marker) .hero-title,
	        .st-key-story_form_shell .hero-title {
	            font-size: clamp(2rem, 3vw, 3.05rem) !important;
	            line-height: 0.96;
	            margin-bottom: 0.28rem;
	        }

	        [data-testid="block-container"]:has(.story-form-marker) .hero-subtitle,
	        .block-container:has(.story-form-marker) .hero-subtitle,
	        .st-key-story_form_shell .hero-subtitle {
	            max-width: 560px;
	            margin-bottom: 0.48rem;
	            font-size: 0.9rem;
	            line-height: 1.44;
	        }

        .login-benefits {
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
            max-width: 820px;
            margin: 0 auto 1.35rem auto;
        }

        .login-benefit {
            padding: 10px 14px;
            border-radius: 999px;
            background:
                linear-gradient(135deg, rgba(255, 251, 246, 0.96), rgba(255, 239, 219, 0.9));
            border: 1px solid rgba(151, 102, 61, 0.18);
            box-shadow: 0 12px 26px rgba(83, 54, 31, 0.07);
            color: #725238;
            font-size: 0.92rem;
            font-weight: 800;
            white-space: nowrap;
        }

        .support-compact {
            max-width: 720px;
            margin: 1.55rem auto 0.65rem auto;
            padding-top: 0.95rem;
            border-top: 1px solid rgba(105, 77, 49, 0.12);
        }

        .support-compact .section-label {
            margin-top: 0;
            margin-bottom: 6px;
            opacity: 0.86;
        }

        .support-compact p {
            margin: 0;
            color: var(--ink-muted);
            font-size: 0.92rem;
            line-height: 1.65;
        }

        .sidebar-brand {
            font-family: "Fraunces", serif;
            font-size: 1.45rem;
            font-weight: 700;
            color: #fff6ea;
            margin-top: 10px;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }

        .sidebar-subbrand {
            font-size: 0.96rem;
            line-height: 1.72;
            color: rgba(248, 240, 230, 0.76);
            margin-bottom: 20px;
        }

	        .section-label {
	            margin-top: 8px;
	            margin-bottom: 7px;
	            font-size: 0.8rem;
	            font-weight: 800;
	            letter-spacing: 0.08em;
	            text-transform: uppercase;
	            color: #7f6247 !important;
	        }

	        [data-testid="block-container"]:has(.story-form-marker) .section-label,
	        .block-container:has(.story-form-marker) .section-label,
	        .st-key-story_form_shell .section-label {
	            margin-top: 0.38rem;
	            margin-bottom: 0.22rem;
	            font-size: 0.76rem;
	            letter-spacing: 0.09em;
	        }

        .soft-info-chip {
            width: fit-content;
            margin: 16px auto 18px auto;
            padding: 11px 16px;
            border-radius: 999px;
            background: linear-gradient(135deg, rgba(255, 242, 226, 0.96), rgba(255, 247, 238, 0.96));
            border: 1px solid rgba(196, 145, 89, 0.22);
            color: #7b5430;
            font-weight: 700;
            box-shadow: 0 12px 24px rgba(120, 76, 36, 0.06);
        }

        .pricing-shell {
            margin-top: 12px;
            margin-bottom: 10px;
        }

        .pricing-subtitle {
            color: var(--ink-soft);
            font-size: 0.98rem;
            line-height: 1.65;
            margin-bottom: 12px;
        }

        .plan-card {
            min-height: 210px;
            padding: 18px 18px 16px 18px;
            border-radius: 24px;
            background: linear-gradient(180deg, rgba(255, 251, 246, 0.98), rgba(255, 247, 240, 0.96));
            border: 1px solid rgba(113, 82, 52, 0.12);
            box-shadow: 0 14px 30px rgba(120, 76, 36, 0.06);
            margin-bottom: 12px;
        }

        .plan-card-featured {
            border-color: rgba(191, 122, 68, 0.28);
            box-shadow: 0 18px 36px rgba(191, 122, 68, 0.1);
            background: linear-gradient(180deg, rgba(255, 247, 236, 1), rgba(255, 243, 229, 0.98));
        }

        .plan-eyebrow {
            display: inline-block;
            margin-bottom: 10px;
            padding: 6px 10px;
            border-radius: 999px;
            background: rgba(191, 122, 68, 0.12);
            color: #965d32;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        .plan-name {
            font-family: "Fraunces", serif;
            font-size: 1.32rem;
            font-weight: 700;
            color: var(--ink);
            margin-bottom: 6px;
        }

        .plan-price {
            font-size: 1.45rem;
            font-weight: 800;
            color: #8c542b;
            margin-bottom: 10px;
        }

        .plan-copy {
            color: var(--ink-soft);
            line-height: 1.62;
            margin-bottom: 12px;
        }

        .plan-feature {
            color: var(--ink);
            font-weight: 700;
            margin-top: 6px;
        }

        p, label, span, div {
            color: var(--ink);
        }

        .stCaptionContainer,
        .stCaptionContainer p {
            color: var(--ink-muted) !important;
            line-height: 1.7 !important;
        }

        [data-testid="InputInstructions"] {
            display: none !important;
        }

	        div[data-baseweb="input"] > div,
	        div[data-baseweb="select"] > div,
	        [data-testid="stTextAreaRootElement"] {
	            background: rgba(255, 251, 246, 0.96) !important;
	            border: 1px solid rgba(113, 82, 52, 0.14) !important;
	            border-radius: 16px !important;
	            color: var(--ink) !important;
	            box-shadow:
	                inset 0 1px 0 rgba(255,255,255,0.78),
	                0 8px 18px rgba(120, 76, 36, 0.04) !important;
	            transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease !important;
	        }

        div[data-baseweb="input"] > div:focus-within,
        div[data-baseweb="select"] > div:focus-within,
        [data-testid="stTextAreaRootElement"]:focus-within {
            border-color: rgba(191, 122, 68, 0.58) !important;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.88),
                0 0 0 4px rgba(191, 122, 68, 0.1),
                0 14px 30px rgba(120, 76, 36, 0.08) !important;
            transform: translateY(-1px);
        }

	        .stTextInput input,
	        .stTextArea textarea {
	            color: var(--ink) !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
	            outline: none !important;
	        }

	        .stTextInput input {
	            min-height: 42px !important;
	            padding: 0.54rem 0.9rem !important;
	        }

	        div[data-baseweb="select"] > div {
	            min-height: 42px !important;
	        }

        .stTextInput input::placeholder,
        .stTextArea textarea::placeholder {
            color: #a49382 !important;
        }

	        .stTextArea textarea {
	            min-height: 122px !important;
	            line-height: 1.6 !important;
	            padding: 0.76rem 0.95rem !important;
	        }

        div[data-baseweb="select"] * {
            color: var(--ink) !important;
        }

        div[data-baseweb="popover"],
        div[data-baseweb="popover"] > div,
        div[data-baseweb="select-dropdown"],
        div[data-baseweb="menu"] {
            background: #fffaf5 !important;
            color: var(--ink) !important;
            border-radius: 18px !important;
            z-index: 2147483000 !important;
        }

        ul[role="listbox"],
        div[role="listbox"] {
            background: #fffaf5 !important;
            border: 1px solid rgba(113, 82, 52, 0.16) !important;
            border-radius: 18px !important;
            box-shadow: 0 18px 44px rgba(70, 46, 24, 0.14) !important;
            padding-top: 8px !important;
            padding-bottom: 8px !important;
        }

        li[role="option"],
        div[role="option"] {
            background: #fffaf5 !important;
            color: var(--ink) !important;
        }

        li[role="option"] *,
        div[role="option"] *,
        ul[role="listbox"] *,
        div[role="listbox"] * {
            color: var(--ink) !important;
            fill: var(--ink) !important;
            stroke: var(--ink) !important;
            opacity: 1 !important;
        }

        li[role="option"][aria-selected="true"],
        div[role="option"][aria-selected="true"] {
            background: rgba(246, 226, 203, 0.96) !important;
            color: #7b5430 !important;
        }

        li[role="option"]:hover,
        div[role="option"]:hover,
        li[role="option"][data-highlighted="true"],
        div[role="option"][data-highlighted="true"] {
            background: rgba(255, 244, 230, 1) !important;
            color: var(--ink) !important;
        }

        div[data-baseweb="tab-list"] {
            background: rgba(255, 249, 241, 0.96) !important;
            border: 1px solid rgba(113, 82, 52, 0.12) !important;
            border-radius: 22px !important;
            padding: 6px !important;
            box-shadow: 0 10px 22px rgba(120, 76, 36, 0.045) !important;
        }

	        button[role="tab"] {
	            min-height: 44px !important;
	            border-radius: 14px !important;
            color: var(--ink) !important;
            opacity: 1 !important;
            font-weight: 800 !important;
            background: transparent !important;
            transition: background 0.18s ease, color 0.18s ease, box-shadow 0.18s ease !important;
        }

        button[role="tab"] *,
        button[role="tab"] p,
        button[role="tab"] span,
        button[role="tab"] div {
            color: var(--ink) !important;
            opacity: 1 !important;
        }

        button[role="tab"]:hover {
            background: rgba(255, 244, 230, 0.96) !important;
            color: var(--ink) !important;
        }

        button[role="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, var(--accent) 0%, var(--accent-strong) 100%) !important;
            color: #fffaf5 !important;
            box-shadow: 0 12px 24px rgba(191, 122, 68, 0.18) !important;
        }

        button[role="tab"][aria-selected="true"] *,
        button[role="tab"][aria-selected="true"] p,
        button[role="tab"][aria-selected="true"] span,
        button[role="tab"][aria-selected="true"] div {
            color: #fffaf5 !important;
        }

	        div[data-baseweb="button-group"] {
	            background: rgba(255, 249, 241, 0.96) !important;
	            border: 1px solid rgba(113, 82, 52, 0.12) !important;
	            border-radius: 18px !important;
	            padding: 5px !important;
	            box-shadow: 0 10px 22px rgba(120, 76, 36, 0.045) !important;
	        }

	        div[data-baseweb="button-group"] button[role="radio"] {
	            min-height: 42px !important;
	            border-radius: 13px !important;
            background: rgba(255, 251, 246, 0.96) !important;
            color: var(--ink) !important;
            opacity: 1 !important;
            font-weight: 800 !important;
            box-shadow: none !important;
            border: none !important;
        }

        div[data-baseweb="button-group"] button[role="radio"] *,
        div[data-baseweb="button-group"] button[role="radio"] p,
        div[data-baseweb="button-group"] button[role="radio"] span,
        div[data-baseweb="button-group"] button[role="radio"] div {
            color: var(--ink) !important;
            opacity: 1 !important;
        }

        div[data-baseweb="button-group"] button[role="radio"]:hover {
            background: rgba(255, 244, 230, 0.98) !important;
            color: var(--ink) !important;
        }

        div[data-baseweb="button-group"] button[role="radio"][aria-checked="true"] {
            background: linear-gradient(135deg, var(--accent) 0%, var(--accent-strong) 100%) !important;
            color: #fffaf5 !important;
            box-shadow: 0 12px 24px rgba(191, 122, 68, 0.18) !important;
        }

        div[data-baseweb="button-group"] button[role="radio"][aria-checked="true"] *,
        div[data-baseweb="button-group"] button[role="radio"][aria-checked="true"] p,
        div[data-baseweb="button-group"] button[role="radio"][aria-checked="true"] span,
        div[data-baseweb="button-group"] button[role="radio"][aria-checked="true"] div {
            color: #fffaf5 !important;
        }

	        .stCheckbox {
	            background: rgba(255, 249, 241, 0.86) !important;
	            padding: 10px 14px !important;
	            border-radius: 16px !important;
            border: 1px solid rgba(113, 82, 52, 0.12) !important;
            box-shadow: 0 10px 20px rgba(120, 76, 36, 0.05) !important;
        }

        .stCheckbox:hover {
            border-color: rgba(191, 122, 68, 0.28) !important;
        }

        div[data-baseweb="tag"] {
            background: linear-gradient(135deg, #d98257, #c96c40) !important;
            border-radius: 999px !important;
            border: none !important;
            color: white !important;
            font-weight: 700 !important;
            box-shadow: 0 8px 18px rgba(191, 122, 68, 0.18) !important;
        }

        div[data-baseweb="tag"] span {
            color: white !important;
        }

	        div.stButton > button {
	            min-height: 44px !important;
	            border-radius: 16px !important;
            font-weight: 800 !important;
            letter-spacing: -0.01em !important;
            transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease !important;
        }

        div.stButton > button[kind="primary"],
        button[kind="primaryFormSubmit"] {
            background: linear-gradient(135deg, var(--accent) 0%, var(--accent-strong) 100%) !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 16px 30px rgba(191, 122, 68, 0.22) !important;
        }

        div.stButton > button[kind="primary"]:hover,
        button[kind="primaryFormSubmit"]:hover {
            transform: translateY(-1px);
            box-shadow: 0 18px 34px rgba(191, 122, 68, 0.26) !important;
        }

        div.stButton > button[kind="secondary"] {
            background: rgba(255, 250, 243, 0.96) !important;
            color: var(--ink) !important;
            border: 1px solid rgba(113, 82, 52, 0.14) !important;
            box-shadow: 0 10px 22px rgba(120, 76, 36, 0.045) !important;
        }

        div.stButton > button[kind="secondary"]:hover {
            border-color: rgba(191, 122, 68, 0.32) !important;
            transform: translateY(-1px);
        }

	        div.stLinkButton > a,
	        .stLinkButton a {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
	            min-height: 44px !important;
	            border-radius: 16px !important;
            font-weight: 800 !important;
            letter-spacing: -0.01em !important;
            text-decoration: none !important;
            background: rgba(255, 250, 243, 0.96) !important;
            color: var(--ink) !important;
            border: 1px solid rgba(113, 82, 52, 0.14) !important;
            box-shadow: 0 10px 22px rgba(120, 76, 36, 0.045) !important;
            transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease !important;
        }

        div.stLinkButton > a:hover,
        .stLinkButton a:hover {
            border-color: rgba(191, 122, 68, 0.32) !important;
            transform: translateY(-1px) !important;
            color: var(--ink) !important;
            text-decoration: none !important;
        }

        [data-testid="stSidebar"] div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #d8874f 0%, #c26739 100%) !important;
            box-shadow: 0 16px 28px rgba(191, 122, 68, 0.16) !important;
        }

        [data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
            background: rgba(255, 250, 243, 0.96) !important;
            color: var(--ink) !important;
            border: 1px solid rgba(113, 82, 52, 0.14) !important;
            box-shadow: 0 10px 22px rgba(120, 76, 36, 0.045) !important;
        }

        [data-testid="stSidebar"] div.stButton > button[kind="secondary"] p,
        [data-testid="stSidebar"] div.stButton > button[kind="secondary"] span,
        [data-testid="stSidebar"] div.stButton > button[kind="secondary"] div {
            color: var(--ink) !important;
        }

        [data-testid="stSidebar"] div.stLinkButton > a,
        [data-testid="stSidebar"] .stLinkButton a {
            background: rgba(255, 250, 243, 0.96) !important;
            color: var(--ink) !important;
            border: 1px solid rgba(113, 82, 52, 0.14) !important;
            box-shadow: 0 10px 22px rgba(120, 76, 36, 0.045) !important;
        }

        [data-testid="stSidebar"] div.stLinkButton > a *,
        [data-testid="stSidebar"] .stLinkButton a *,
        [data-testid="stSidebar"] div.stLinkButton > a span,
        [data-testid="stSidebar"] .stLinkButton a span,
        [data-testid="stSidebar"] div.stLinkButton > a p,
        [data-testid="stSidebar"] .stLinkButton a p,
        [data-testid="stSidebar"] div.stLinkButton > a div,
        [data-testid="stSidebar"] .stLinkButton a div {
            color: var(--ink) !important;
            opacity: 1 !important;
        }

        [data-testid="stSidebar"] div.stLinkButton > a:hover,
        [data-testid="stSidebar"] .stLinkButton a:hover {
            border-color: rgba(191, 122, 68, 0.32) !important;
            color: var(--ink) !important;
        }

        [data-testid="stExpander"] {
            border: 1px solid rgba(255, 229, 197, 0.12) !important;
            border-radius: 18px !important;
            background: rgba(255, 248, 240, 0.06) !important;
            overflow: hidden !important;
        }

        [data-testid="stExpander"] summary {
            background: rgba(255, 248, 240, 0.04) !important;
            border-radius: 16px !important;
        }

        [data-testid="stSidebar"] [data-testid="stExpander"] .stButton button {
            background: rgba(255, 249, 240, 0.06) !important;
            color: #fff3e3 !important;
            border: 1px solid rgba(255, 227, 194, 0.12) !important;
            box-shadow: none !important;
        }

        [data-testid="stSidebar"] [data-testid="stExpander"] .stButton button:hover {
            background: rgba(255, 249, 240, 0.12) !important;
            border-color: rgba(255, 227, 194, 0.2) !important;
        }

        .story-output {
            background:
                linear-gradient(180deg, rgba(255, 252, 248, 0.98), rgba(255, 248, 241, 0.98)) !important;
            color: #34281f !important;
            padding: 32px !important;
            border-radius: 28px !important;
            font-size: 1.08rem !important;
            line-height: 1.95 !important;
            border: 1px solid rgba(113, 82, 52, 0.12) !important;
            box-shadow: var(--shadow-md) !important;
        }

        .story-output,
        .story-output p,
        .story-output span,
        .story-output div,
        .story-output strong,
        .story-output em {
            color: #34281f !important;
        }

        [data-testid="stImage"] img {
            border-radius: 24px !important;
            box-shadow: 0 18px 42px rgba(70, 46, 24, 0.14) !important;
        }

        audio {
            width: 100% !important;
            margin-top: 10px !important;
            margin-bottom: 16px !important;
            border-radius: 18px !important;
        }

        .stInfo, .stSuccess, .stWarning, .stError {
            border-radius: 18px !important;
            border: 1px solid rgba(113, 82, 52, 0.12) !important;
        }

        .stSuccess {
            background: linear-gradient(135deg, rgba(223, 233, 207, 0.92), rgba(232, 242, 219, 0.92)) !important;
            color: #324426 !important;
        }

        .stWarning {
            background: linear-gradient(135deg, rgba(255, 246, 201, 0.92), rgba(255, 240, 177, 0.9)) !important;
            color: #6a5428 !important;
        }

        .stError {
            background: linear-gradient(135deg, rgba(251, 224, 216, 0.96), rgba(247, 211, 200, 0.94)) !important;
            color: #6f3521 !important;
        }

        .stInfo {
            background: linear-gradient(135deg, rgba(239, 231, 221, 0.95), rgba(245, 239, 231, 0.95)) !important;
            color: #53453a !important;
        }

        hr {
            border-color: rgba(113, 82, 52, 0.08) !important;
        }

	        @media (max-width: 768px) {
	            .stApp,
	            [data-testid="stAppViewContainer"],
	            section[data-testid="stMain"] {
                min-height: 100svh !important;
                height: auto !important;
            }

            [data-testid="collapsedControl"],
            [data-testid="stExpandSidebarButton"],
            [data-testid="stSidebarCollapsedControl"],
            [data-testid="stSidebarCollapseButton"] {
                display: flex !important;
                visibility: visible !important;
                position: fixed !important;
                top: max(12px, env(safe-area-inset-top)) !important;
                left: max(12px, env(safe-area-inset-left)) !important;
                width: 46px !important;
                height: 46px !important;
                align-items: center !important;
                justify-content: center !important;
                background: rgba(255, 250, 243, 0.98) !important;
                border: 1px solid rgba(113, 82, 52, 0.22) !important;
                border-radius: 16px !important;
                box-shadow: 0 14px 34px rgba(42, 28, 19, 0.2) !important;
                opacity: 1 !important;
            }

            [data-testid="stSidebar"] {
                min-width: min(88vw, 340px) !important;
                width: min(88vw, 340px) !important;
                max-width: min(88vw, 340px) !important;
                box-shadow: 24px 0 70px rgba(18, 12, 8, 0.42) !important;
            }

            [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
                padding-top: 1rem !important;
                padding-bottom: 1.5rem !important;
            }

	            .block-container,
	            [data-testid="block-container"],
	            [data-testid="stMainBlockContainer"] {
	                max-width: calc(100vw - 14px) !important;
	                padding: 0.86rem 0.78rem 0.7rem 0.78rem !important;
	                border-radius: 22px !important;
	                margin-top: 8px !important;
	                margin-bottom: 0 !important;
	                min-height: auto !important;
	            }

	            [data-testid="block-container"]:has(.login-page-marker),
	            .block-container:has(.login-page-marker),
	            [data-testid="stMainBlockContainer"]:has(.login-page-marker),
	            [data-testid="block-container"]:has(.story-form-marker),
	            .block-container:has(.story-form-marker),
	            [data-testid="stMainBlockContainer"]:has(.story-form-marker),
	            .st-key-story_form_shell {
	                max-width: calc(100vw - 14px) !important;
	                padding-left: 0.78rem !important;
	                padding-right: 0.78rem !important;
	            }

            .st-key-story_form_shell {
                padding-top: 0 !important;
                padding-bottom: 0 !important;
            }

            .st-key-story_form_shell [data-testid="stHorizontalBlock"] {
                gap: 0.55rem !important;
            }

	            .hero-title {
	                font-size: 2rem !important;
	            }

            .story-title {
                font-size: 2.05rem !important;
            }

	            .hero-subtitle {
	                font-size: 0.98rem !important;
	                line-height: 1.48 !important;
	            }

	            .stTextInput input,
	            div[data-baseweb="select"] > div,
	            div.stButton > button,
	            div.stLinkButton > a,
	            .stLinkButton a {
	                min-height: 40px !important;
	            }

	            .stTextArea textarea {
	                min-height: 96px !important;
	            }

            .login-benefits {
                flex-direction: column;
                align-items: stretch;
                gap: 8px;
                margin-bottom: 1.05rem;
            }

            .login-benefit {
                text-align: center;
                white-space: normal;
            }

            .support-compact {
                margin-top: 1.25rem;
            }

            .story-output {
                padding: 22px !important;
                border-radius: 22px !important;
            }

            .plan-card {
                min-height: 0;
            }

        }
        </style>
        """,
        unsafe_allow_html=True,
    )
