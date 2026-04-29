import httpx
import logging
from config import UMNICO_TOKEN
# Твой токен и ID пользователя в Umnico
UMNICO_USER_ID = 2481621  # Возьми свой ID из личного кабинета или вебхука

async def send_umnico_message(lead_id: int, text: str, source: int):
    url = f"https://api.umnico.com/v1.3/messaging/{lead_id}/send"
    
    headers = {
        "Authorization": f"Bearer {UMNICO_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "message": {
            "text": text
        },
        "source": source,
        "userId": UMNICO_USER_ID
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # print(f"\n>>> ПОЛНЫЙ ОТВЕТ ОТ UMNICO: {data}\n")
                # print(f"Успешно отправлено в чат {lead_id}")
                return response.json()
            else:
                print(f"Ошибка отправки: {response.status_code}, {response.text}")
                return None
        except Exception as e:
            print(f"Ошибка при запросе к Umnico: {e}")
            return None