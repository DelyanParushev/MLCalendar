from ml.nlp_parser_ml import parse_text
from datetime import datetime
import calendar

def print_next_month_calendar():
    now = datetime.now()
    # Print current month's calendar
    print(f"\nCalendar for debugging:")
    cal = calendar.monthcalendar(now.year, now.month)
    print("Mo Tu We Th Fr Sa Su")
    for week in cal:
        print(" ".join(f"{day:2d}" if day != 0 else "  " for day in week))

def test_weekday_parsing():
    test_cases = [
        "Футбол неделя от 19",
        "Среща в петък от 14",
        "Обяд събота от 13",
        "Тренировка във вторник от 18",
        "Кино с приятели в събота от 20"
    ]
    
    print("\nTest results:")
    
    for text in test_cases:
        result = parse_text(text)
        print(f"\nInput: {text}")
        print(f"Raw result: {result}")
        print(f"Title: {result.get('title')}")
        print(f"DateTime: {result.get('datetime')}")
        print(f"Tokens: {result.get('tokens')}")
        print(f"Labels: {result.get('labels')}")
        
        dt = result.get('datetime')
        if dt:
            print(f"Is future: {dt > datetime.now()}")
            print(f"Day of week (number): {dt.weekday()}")
            print(f"Day of week (name): {dt.strftime('%A')}")
            print(f"Full date: {dt.strftime('%Y-%m-%d %H:%M %A')}")
            
        # Show debugging info
        if result.get('debug'):
            print(f"Debug info: {result['debug']}")
            
        # Let's analyze the individual tokens
        tokens = result.get('tokens', [])
        labels = result.get('labels', [])
        if tokens and labels:
            print("\nToken analysis:")
            for t, l in zip(tokens, labels):
                print(f"Token: '{t}' -> Label: '{l}'")

if __name__ == "__main__":
    test_weekday_parsing()
