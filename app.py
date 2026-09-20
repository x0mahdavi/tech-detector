import streamlit as st
import requests
import re

st.set_page_config(
    page_title="Tech Detector Pro",
    page_icon="🕵️",
    layout="wide"
)

# ====================== Advanced Technology Signatures ======================
TECH_SIGNATURES = {
    "CMS & Site Builders": {
        "WordPress": {"html": [r"wp-content", r"wp-includes", r"/wp-json/", r"wordpress"], "meta": [r"generator.*wordpress"]},
        "Joomla": {"html": [r"joomla", r"/media/jui/"], "meta": [r"generator.*joomla"]},
        "Drupal": {"html": [r"drupal", r"sites/default/files"], "headers": {"x-generator": "Drupal", "x-drupal-cache": ""}},
        "Ghost": {"html": [r"ghost\.org", r"ghost-"], "headers": {"x-ghost": ""}},
        "Shopify": {"html": [r"cdn\.shopify\.com", r"Shopify\.theme"], "headers": {"x-shopify-stage": ""}},
        "Wix": {"html": [r"wix\.com", r"static\.wixstatic\.com"]},
        "Squarespace": {"html": [r"squarespace\.com", r"static\.squarespace"]},
        "Webflow": {"html": [r"webflow\.com", r"wf-"]},
        "Blogger": {"html": [r"blogger\.com", r"blogspot"], "meta": [r"generator.*blogger"]},
        "PrestaShop": {"html": [r"prestashop"]},
        "Magento": {"html": [r"Magento_", r"skin/frontend", r"mage/"]},
        "OpenCart": {"html": [r"catalog/view/theme"]},
        "Bitrix": {"html": [r"bitrix"]},
        "TYPO3": {"html": [r"typo3"]},
        "Contentful": {"html": [r"contentful"]},
        "Strapi": {"html": [r"strapi"]},
        "Sanity": {"html": [r"sanity\.io"]},
    },

    "JavaScript Frameworks": {
        "React": {"html": [r"react", r"data-reactroot", r"__NEXT_DATA__", r"react-dom"]},
        "Next.js": {"html": [r"__NEXT_DATA__", r"_next/static"], "headers": {"x-powered-by": "Next.js"}},
        "Vue.js": {"html": [r"vue\.js", r"data-v-", r"__vue", r"Vue\."]},
        "Nuxt.js": {"html": [r"__NUXT__", r"_nuxt/"]},
        "Angular": {"html": [r"ng-version", r"angular", r"ng-app", r"ng-controller"]},
        "Svelte": {"html": [r"svelte"]},
        "SvelteKit": {"html": [r"__sveltekit"]},
        "Ember.js": {"html": [r"emberjs", r"ember"]},
        "Alpine.js": {"html": [r"alpinejs", r"x-data"]},
        "Stimulus": {"html": [r"data-controller", r"stimulus"]},
        "Solid.js": {"html": [r"solid-js"]},
        "Qwik": {"html": [r"qwik", r"qk-"]},
        "Astro": {"html": [r"astro", r"astro-"]},
        "Remix": {"html": [r"__remix"]},
        "Gatsby": {"html": [r"gatsby", r"___gatsby"]},
    },

    "UI Frameworks": {
        "Tailwind CSS": {"html": [r"tailwind", r"cdn\.tailwindcss\.com"]},
        "Bootstrap": {"html": [r"bootstrap"]},
        "Material UI": {"html": [r"material-ui", r"@mui", r"mui"]},
        "Ant Design": {"html": [r"antd", r"ant-design"]},
        "Chakra UI": {"html": [r"chakra-ui"]},
        "Bulma": {"html": [r"bulma"]},
        "Foundation": {"html": [r"foundation"]},
        "Semantic UI": {"html": [r"semantic-ui"]},
        "Vuetify": {"html": [r"vuetify"]},
        "Quasar": {"html": [r"quasar"]},
        "Shadcn/ui": {"html": [r"shadcn"]},
        "Mantine": {"html": [r"mantine"]},
    },

    "JavaScript Libraries": {
        "jQuery": {"html": [r"jquery"]},
        "Lodash": {"html": [r"lodash"]},
        "Axios": {"html": [r"axios"]},
        "Moment.js": {"html": [r"moment\.js", r"moment\.min\.js"]},
        "Day.js": {"html": [r"dayjs"]},
        "Chart.js": {"html": [r"chart\.js"]},
        "D3.js": {"html": [r"d3\.js", r"d3\.min\.js"]},
        "Three.js": {"html": [r"three\.js"]},
        "GSAP": {"html": [r"gsap", r"TweenMax"]},
        "Zone.js": {"html": [r"zone\.js"]},
        "RxJS": {"html": [r"rxjs"]},
        "Underscore.js": {"html": [r"underscore"]},
        "Polymer": {"html": [r"polymer"]},
        "Backbone.js": {"html": [r"backbone"]},
        "Knockout.js": {"html": [r"knockout"]},
        "Mustache.js": {"html": [r"mustache"]},
        "Handlebars": {"html": [r"handlebars"]},
    },

    "Backend Frameworks": {
        "Laravel": {"headers": {"set-cookie": "laravel_session"}, "html": [r"laravel"]},
        "Django": {"headers": {"set-cookie": "csrftoken"}, "html": [r"csrfmiddlewaretoken"]},
        "Express": {"headers": {"x-powered-by": "Express"}},
        "NestJS": {"html": [r"nestjs"]},
        "ASP.NET": {"headers": {"x-powered-by": "ASP.NET", "x-aspnet-version": ""}, "html": [r"__VIEWSTATE"]},
        "Ruby on Rails": {"headers": {"x-runtime": "", "server": "Phusion Passenger"}},
        "Spring Boot": {"headers": {"x-application-context": ""}, "html": [r"jsessionid"]},
        "Flask": {"headers": {"server": "Werkzeug"}},
        "FastAPI": {"headers": {"server": "uvicorn"}},
        "Phoenix": {"headers": {"server": "Cowboy"}},
        "Symfony": {"html": [r"symfony"]},
        "CodeIgniter": {"html": [r"codeigniter"]},
        "CakePHP": {"html": [r"cakephp"]},
        "Yii": {"html": [r"yii"]},
    },

    "Programming Languages": {
        "PHP": {"headers": {"x-powered-by": "php"}},
        "Python": {"headers": {"server": r"gunicorn|uvicorn|werkzeug"}},
        "Node.js": {"headers": {"x-powered-by": r"Express|Next\.js"}},
        "Ruby": {"headers": {"server": r"Passenger|Puma|WEBrick"}},
        "Java": {"html": [r"jsessionid"]},
        "Go": {"headers": {"server": r"Go|golang"}},
    },

    "Web Servers & Hosting": {
        "Nginx": {"headers": {"server": "nginx"}},
        "Apache": {"headers": {"server": "apache"}},
        "IIS": {"headers": {"server": "microsoft-iis"}},
        "Cloudflare": {"headers": {"server": "cloudflare", "cf-ray": ""}},
        "AWS CloudFront": {"headers": {"via": "cloudfront", "x-amz-cf-id": ""}},
        "Fastly": {"headers": {"via": "fastly"}},
        "Akamai": {"headers": {"server": "akamai"}},
        "LiteSpeed": {"headers": {"server": "litespeed"}},
        "Caddy": {"headers": {"server": "caddy"}},
        "Vercel": {"headers": {"server": "vercel", "x-vercel-id": ""}},
        "Netlify": {"headers": {"server": "netlify"}},
        "GitHub Pages": {"headers": {"server": "GitHub\.com"}},
        "Heroku": {"headers": {"via": "vegur"}},
    },

    "Security & WAF": {
        "Cloudflare": {"headers": {"cf-ray": "", "cf-mitigated": ""}},
        "Sucuri": {"headers": {"x-sucuri-id": ""}},
        "Wordfence": {"html": [r"wordfence"]},
        "ModSecurity": {"headers": {"server": "mod_security"}},
        "Imperva": {"headers": {"x-iinfo": ""}},
        "AWS WAF": {"headers": {"x-amzn-requestid": ""}},
    },

    "Analytics & Marketing": {
        "Google Analytics": {"html": [r"google-analytics\.com", r"gtag\(", r"G-[A-Z0-9]{8,}", r"UA-\d+"]},
        "Google Tag Manager": {"html": [r"googletagmanager\.com"]},
        "Hotjar": {"html": [r"hotjar\.com"]},
        "Microsoft Clarity": {"html": [r"clarity\.ms"]},
        "Facebook Pixel": {"html": [r"connect\.facebook\.net", r"fbq\("]},
        "Yandex Metrica": {"html": [r"mc\.yandex\.ru"]},
        "Mixpanel": {"html": [r"mixpanel"]},
        "Segment": {"html": [r"segment\.com|analytics\.js"]},
        "Plausible": {"html": [r"plausible\.io"]},
        "Matomo": {"html": [r"matomo|piwik"]},
        "Amplitude": {"html": [r"amplitude"]},
        "Heap": {"html": [r"heap-"]},
    },

    "Live Chat & Support": {
        "Intercom": {"html": [r"intercom", r"widget\.intercom"]},
        "Zendesk": {"html": [r"zendesk|zdassets"]},
        "Crisp": {"html": [r"crisp\.chat"]},
        "Tawk.to": {"html": [r"tawk\.to"]},
        "Goftino": {"html": [r"goftino"]},
        "Raychat": {"html": [r"raychat"]},
        "JivoChat": {"html": [r"jivosite"]},
        "LiveChat": {"html": [r"livechatinc"]},
        "Drift": {"html": [r"drift\.com"]},
        "HubSpot Chat": {"html": [r"js\.hs-scripts\.com"]},
    },

    "Authentication": {
        "Google Sign-In": {"html": [r"accounts\.google\.com/gsi", r"google-signin"]},
        "Auth0": {"html": [r"auth0\.com"]},
        "Firebase Auth": {"html": [r"firebase|identitytoolkit"]},
        "Okta": {"html": [r"okta\.com"]},
        "Keycloak": {"html": [r"keycloak"]},
        "Clerk": {"html": [r"clerk\.com|clerk\."]},
        "Supabase Auth": {"html": [r"supabase"]},
    },

    "Miscellaneous": {
        "PWA": {"html": [r"manifest\.json", r"serviceWorker", r"sw\.js"]},
        "Open Graph": {"html": [r"og:title|og:image|property=\"og:"]},
        "Twitter Cards": {"html": [r"twitter:card|twitter:title"]},
        "Sentry": {"html": [r"sentry\.io|sentry\."]},
        "Google Fonts": {"html": [r"fonts\.googleapis\.com|fonts\.gstatic\.com"]},
        "Font Awesome": {"html": [r"font-awesome|fontawesome"]},
        "reCAPTCHA": {"html": [r"recaptcha|google\.com/recaptcha"]},
        "hCaptcha": {"html": [r"hcaptcha"]},
        "Stripe": {"html": [r"js\.stripe\.com"]},
        "PayPal": {"html": [r"paypal\.com|paypalobjects"]},
        "Cloudinary": {"html": [r"cloudinary\.com"]},
        "imgix": {"html": [r"imgix\.net"]},
        "Cookiebot": {"html": [r"cookiebot"]},
        "OneTrust": {"html": [r"onetrust|cookielaw"]},
        "HubSpot": {"html": [r"hs-scripts|hubspot"]},
        "Mailchimp": {"html": [r"mailchimp|list-manage"]},
    }
}


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def fetch_site(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        return {
            "success": True,
            "url": response.url,
            "status": response.status_code,
            "headers": {k.lower(): v for k, v in response.headers.items()},
            "html": response.text,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def detect_technologies(data: dict) -> dict:
    if not data.get("success"):
        return {}

    html_lower = data["html"].lower()
    headers = data["headers"]
    detected = {}

    for category, techs in TECH_SIGNATURES.items():
        found = []
        for tech_name, rules in techs.items():
            matched = False

            if "html" in rules:
                for pattern in rules["html"]:
                    if re.search(pattern, html_lower, re.IGNORECASE):
                        matched = True
                        break

            if not matched and "headers" in rules:
                for h_key, h_val in rules["headers"].items():
                    if h_key in headers:
                        if h_val == "" or re.search(h_val, headers[h_key], re.IGNORECASE):
                            matched = True
                            break

            if not matched and "meta" in rules:
                for pattern in rules["meta"]:
                    if re.search(pattern, html_lower, re.IGNORECASE):
                        matched = True
                        break

            if matched:
                found.append(tech_name)

        if found:
            detected[category] = sorted(list(set(found)))

    return detected


# ====================== UI ======================
st.title("🕵️ Tech Detector Pro")
st.markdown("Advanced website technology detection tool")
st.markdown("---")

url_input = st.text_input("Enter website URL:", placeholder="example.com or https://example.com")

if st.button("🔍 Start Scan", use_container_width=False):
    if not url_input.strip():
        st.warning("Please enter a URL.")
    else:
        with st.spinner("Scanning website... Please wait"):
            target = normalize_url(url_input)
            data = fetch_site(target)

            if not data["success"]:
                st.error(f"Failed to connect: `{data.get('error')}`")
            else:
                results = detect_technologies(data)

                st.success("Scan completed successfully")

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Final URL:** `{data['url']}`")
                with col2:
                    st.markdown(f"**Status Code:** `{data['status']}`")

                st.markdown("---")
                st.subheader("Detected Technologies")

                if not results:
                    st.warning("No technologies detected.")
                else:
                    for category, techs in results.items():
                        with st.expander(f"📦 {category}  ({len(techs)})", expanded=True):
                            cols = st.columns(3)
                            for idx, tech in enumerate(techs):
                                with cols[idx % 3]:
                                    st.markdown(f"**✅ {tech}**")

                with st.expander("🧾 Important Response Headers"):
                    important = [
                        "server", "x-powered-by", "x-generator", "via", "cf-ray",
                        "content-type", "x-frame-options", "strict-transport-security",
                        "content-security-policy"
                    ]
                    for h in important:
                        if h in data["headers"]:
                            st.code(f"{h}: {data['headers'][h]}")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; font-size: 0.9em;'>
    Created by <b>Hossein Mahdavi</b><br><br>
    <a href="https://hosseinmahdave.ir/" target="_blank">Website</a> •
    <a href="https://github.com/x0mahdavi" target="_blank">GitHub</a> •
    <a href="https://x.com/x0mahdavi" target="_blank">X</a> •
    <a href="https://www.instagram.com/x0mahdavi/" target="_blank">Instagram</a> •
    <a href="https://www.linkedin.com/in/x0mahdavi" target="_blank">LinkedIn</a> •
    <a href="https://t.me/x0mahdavi" target="_blank">Telegram</a>
</div>
""", unsafe_allow_html=True)