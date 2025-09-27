# AI Calendar – Backend MVP

## ML модела не е качен тук, понеже е над 11GB до момента. В момента се опитвам да кача цялото приложение заедно с модела във Vercel/Huggung Face, за да работи на други машини, а не само локално. Очаквам модела да стане още по-голям понеже има неща, които трябва да се доизпипат.
```bash
Това е готово- Да обуча модела с допълнителни примери като:
Text: Йога клас утре сутринта
Title: Йога
Datetime: 2025-08-18 09:00:00
Tokens: ['Йога', 'клас', 'утре', 'сутринта']
Labels: ['B-TITLE', 'B-TITLE', 'B-WHEN_DAY', 'B-WHEN_DAY']
```
## Инсталация и старт
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt

# start backend
# uvicorn backend.main:app --reload

# start frontend
# cd frontend
# npm run dev