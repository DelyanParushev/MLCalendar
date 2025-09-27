import requests
import json

BASE_URL = "https://dex7er999-calendar-nlp-api.hf.space/api"

def test_parse():
    text = "среща утре в 15 часа"
    response = requests.post(
        f"{BASE_URL}/parse",
        json={"text": text},
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
    print("\nParse Test:")
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))

def test_create_event():
    text = "среща утре в 15 часа"
    response = requests.post(
        f"{BASE_URL}/events",
        json={"text": text},
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
    print("\nCreate Event Test:")
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))

def test_get_events():
    response = requests.get(f"{BASE_URL}/events")
    print("\nGet Events Test:")
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    test_parse()
    test_create_event()
    test_get_events()
