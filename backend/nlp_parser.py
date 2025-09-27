import re
import dateparser

def parse_event_text(text: str):
    raw_text = text.strip()

    # 1) Извличаме час ("от 20", "от 18:30")
    hour, minute = None, 0
    hour_match = re.search(r'от\s*(\d{1,2})(?::(\d{2}))?', raw_text)
    if hour_match:
        hour = int(hour_match.group(1))
        if hour_match.group(2):
            minute = int(hour_match.group(2))

    # 2) Премахваме "от 20" от текста, за да остане само датата
    date_part = re.sub(r'от\s*\d{1,2}(:\d{2})?', '', raw_text, flags=re.IGNORECASE).strip()

    # 3) Заглавие (без дата/часови части)
    title = re.sub(r'(този|следващия|утре|днес|понеделник|вторник|сряда|четвъртък|петък|събота|неделя)', '', date_part, flags=re.IGNORECASE).strip()
    if not title:
        title = "Събитие"

    # 4) Парсваме датата (без часа)
    date_only = dateparser.parse(
        date_part,
        languages=['bg'],
        settings={'PREFER_DATES_FROM': 'future'}
    )

    if not date_only:
        return None, None

    # 5) Ако имаме и час – добавяме го
    if hour is not None:
        date_only = date_only.replace(hour=hour, minute=minute)

    return title, date_only
