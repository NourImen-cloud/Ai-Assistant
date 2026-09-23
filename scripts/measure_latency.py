import time
import httpx

URL = "http://127.0.0.1:8000/chat"

def measure(message: str, timeout: float = 120.0):
    start = time.time()
    try:
        r = httpx.post(URL, json={"message": message}, timeout=timeout)
        elapsed = time.time() - start
        print(f"Elapsed: {elapsed:.2f}s | Status: {r.status_code} | Body: {r.text}")
    except Exception as e:
        elapsed = time.time() - start
        print(f"Elapsed: {elapsed:.2f}s | ERROR: {e}")


if __name__ == "__main__":
    print("Cold request")
    measure("hello cold")
    print("Warm request")
    measure("hello warm")
