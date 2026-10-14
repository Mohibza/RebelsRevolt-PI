import requests
import time
import json

CV = "vc_435_vn_3.0.435_a"
E_AUTH_V = "e1"
E_AUTH_K = "PgdtSBeR0MumR7fO"


def _make_headers_names(api_id, country_code):
    return {
        "User-Agent": "Dalvik/2.2.0 (Linux; U; Android 11; GM2022 Build/QKQ5.198916.030)",
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive",
        "e-auth-v": E_AUTH_V,
        "e-auth-c": str(country_code),
        "e-auth": str(api_id),
        "e-auth-k": E_AUTH_K,
        "content-type": "application/x-www-form-urlencoded",
        "Host": "api.eyecon-app.com"
    }


def _make_headers_fb(api_id, country_code):
    return {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10; GM1903 Build/QKQ1.190716.003)",
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive",
        "e-auth-v": E_AUTH_V,
        "e-auth-c": str(country_code),
        "e-auth": str(api_id),
        "e-auth-k": E_AUTH_K,
        "Host": "api.eyecon-app.com"
    }


def try_one_credential(number, credential):
    """
    Try searching a number with ONE credential.
    Returns (names_list, raw_response_text, error_str)
    names_list is [] if not found or on error.
    """
    api_id = credential['api_id']
    country = credential['country_code']

    url = (
        "https://api.eyecon-app.com/app/getnames.jsp"
        f"?cli={number}&lang=en&is_callerid=false&is_ic=false"
        f"&cv={CV}&requestApi=URLconnection&source=Other&is_search=true"
    )

    headers = _make_headers_names(api_id, country)

    try:
        session = requests.Session()
        resp = session.post(url, headers=headers, timeout=12)
        raw = resp.text[:500] if resp.text else ''

        if resp.status_code == 200:
            # Try to parse JSON
            try:
                data = resp.json()
                if isinstance(data, list):
                    names = [x['name'] for x in data if isinstance(x, dict) and 'name' in x]
                    return names, raw, None
                elif isinstance(data, dict):
                    # Sometimes wrapped: {"result": [...]}
                    for key in ('result', 'names', 'data', 'contacts'):
                        if key in data and isinstance(data[key], list):
                            names = [x['name'] for x in data[key] if isinstance(x, dict) and 'name' in x]
                            return names, raw, None
                    return [], raw, None
                return [], raw, None
            except Exception as e:
                return [], raw, f"JSON parse error: {e}"
        else:
            return [], raw, f"HTTP {resp.status_code}"
    except requests.exceptions.Timeout:
        return [], '', 'Timeout'
    except Exception as e:
        return [], '', str(e)


def try_facebook(number, credential):
    """
    Try Facebook picture lookup for a number with ONE credential.
    Returns (fb_id, fb_link) or (None, None)
    """
    api_id = credential['api_id']
    country = credential['country_code']

    fburl = (
        "https://api.eyecon-app.com/app/pic"
        f"?cli={number}&is_callerid=true&is_ic=true&size=big&type=0"
        f"&cancelfresh=0&cv={CV}&requestApi=URLconnection&source=Other"
    )

    headers = _make_headers_fb(api_id, country)

    try:
        session = requests.Session()
        fbres = session.get(fburl, headers=headers, timeout=12, allow_redirects=True)
        final_url = fbres.url

        if "https://graph." in final_url or "graph.facebook.com" in final_url:
            fb_link = str(final_url.replace('graph.', '').split("/picture?")[0])
            fb_id = fb_link.replace("https://facebook.com/", "").strip("/")
            return fb_id, fb_link
        return None, None
    except Exception:
        return None, None


def search_number(number, credentials_list, start_index=0):
    """
    Search a number trying credentials round-robin starting at start_index.
    If the first credential returns empty names, tries ALL remaining credentials
    before giving up — ensures maximum chance of finding a result.

    Returns dict:
      names: list of name strings
      names_str: comma-joined or 'Not Found'
      fb_id: str or None
      fb_link: str or None
      credential_used: label of credential that found result
      attempts: number of credentials tried
      raw_response: last raw response for debugging
    """
    n_creds = len(credentials_list)
    if n_creds == 0:
        return {
            'names': [], 'names_str': 'No Credentials',
            'fb_id': None, 'fb_link': None,
            'credential_used': None, 'attempts': 0, 'raw_response': ''
        }

    found_names = []
    used_label = None
    raw_resp = ''
    attempts = 0

    # Try starting from start_index, wrap around all credentials
    for i in range(n_creds):
        idx = (start_index + i) % n_creds
        cred = credentials_list[idx]
        attempts += 1

        names, raw, err = try_one_credential(number, cred)
        raw_resp = raw

        if names:  # Found something!
            found_names = names
            used_label = cred.get('label', f'Key {idx+1}')
            break
        elif i < n_creds - 1:
            # Not found with this key, try next (small delay to avoid rate limit)
            time.sleep(0.3)

    if not used_label and credentials_list:
        used_label = credentials_list[start_index % n_creds].get('label', 'Key 1')

    # Facebook lookup — use same credential that found names (or first)
    fb_cred_idx = start_index % n_creds
    # Try FB with the credential that gave names, if any
    if found_names and used_label:
        for i in range(n_creds):
            idx = (start_index + i) % n_creds
            if credentials_list[idx].get('label') == used_label:
                fb_cred_idx = idx
                break

    fb_id, fb_link = try_facebook(number, credentials_list[fb_cred_idx])

    names_str = ', '.join(found_names) if found_names else 'Not Found'

    return {
        'names': found_names,
        'names_str': names_str,
        'fb_id': fb_id,
        'fb_link': fb_link,
        'credential_used': used_label,
        'attempts': attempts,
        'raw_response': raw_resp
    }
