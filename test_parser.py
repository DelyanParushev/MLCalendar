from ml.nlp_parser_ml import parse_text

examples = [
    "Обяд от 15 събота с приятели",
    "Вечеря с Гери в Неделя от 18",
    "Среща в офиса в петък 14:45",
    "Йога клас утре сутринта",
    "Покупки в мола в събота следобед",
    "На 20ти от 21 Разходка",
    "Футбол неделя от 19 до 21"
]

for ex in examples:
    parsed = parse_text(ex)
    print(f"Text: {ex}")
    print(f"Title: {parsed.get('title')}")
    print(f"Datetime: {parsed.get('datetime')}")
    print(f"Tokens: {parsed.get('tokens')}")
    print(f"Labels: {parsed.get('labels')}")
    print("-" * 50)
