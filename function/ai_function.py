from openai import AsyncOpenAI
import os
from config import AI_TOKEN
import base64
import httpx
import json

# Ключ лучше держать в .env, но для теста можно подставить напрямую
client = AsyncOpenAI(api_key=AI_TOKEN)

# async def get_ai_answer( msg_history: list):
#     try:
#         # 1. Начинаем с системного промпта
#         messages = [
#             {"role": "system", "content": "Ты мастер по удалению вмятин PDR. Отвечай вежливо и коротко."}
#         ]
        
#         # 2. Добавляем историю (она уже в нужном формате [{"role": "...", "content": "..."}])
#         messages.extend(msg_history)
        
#         response = await client.chat.completions.create(
#             model="gpt-4o",
#             messages=messages
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         print(f"Ошибка OpenAI: {e}")
#         return "Извините, произошла техническая ошибка. Попробуйте позже."


# 1. Общая роль (кто это)
GENERAL_ROLE = """
Ты — эксперт по беспокрасочному удалению вмятин (PDR) с 10-летним стажем. Твой стиль: вежливость, профессионализм и лаконичность.
Твоя главная цель — получить фото повреждения. 
- Если клиент просто поздоровался, просто поздоровайся в ответ, не нужно сразу переходить к делу.
- Если клиент описывает вмятину словами, дай примерную оценку (например: 'По описанию похоже на работу на 2-3 часа, от 5000 руб'), но сразу уточняй, что точный расчет возможен только по фото.
- Настойчиво, но мягко предлагай прислать фотографию под углом.
- Если фото уже есть, оценивай его уверенно, используя термины: 'растянутый металл', 'слом', 'доступ изнутри'."""

# Конкретный алгоритм и формат
SPECIFIC_INSTRUCTIONS = """
Ты должен отвечать СТРОГО в формате JSON с двумя полями: "answer" и "status".

Статусы (status):
1. "priced" — если в этом или прошлых сообщениях была названа цена.
2. "end" — если диалог явно завершается (клиент сказал "спасибо", "я подумаю", "до свидания" или "понял").
3. "chatting" — во всех остальных случаях, пока идет уточнение деталей.

Пример ответа:
{"answer": "Добрый день! Чем могу помочь?", "status": "chatting"}
"""

async def get_ai_answer(msg_history: list,prompt):
    try:
        # Собираем системный промпт из двух частей
        full_system_prompt = f"{prompt}\n\n{SPECIFIC_INSTRUCTIONS}"
        
        messages = [
            {"role": "system", "content": full_system_prompt}
        ]
        
        # Добавляем историю сообщений
        messages.extend(msg_history)
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.7 # Добавил немного "человечности" для диалога
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Ошибка OpenAI: {e}")
        return "Извините, произошла техническая ошибка. Попробуйте позже."

async def get_image_description(photo_url: str) -> str:
    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(photo_url)
        if response.status_code != 200: return "[Ошибка загрузки фото]"
        img_b64 = base64.b64encode(response.content).decode('utf-8')

    res = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Что изображено на этом фото? Опиши словам максимально точно."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
            ]
        }]
    )
    return f'photo: {res.choices[0].message.content}'