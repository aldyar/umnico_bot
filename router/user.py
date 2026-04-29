from fastapi import APIRouter, Request
from function.ai_function import get_ai_answer,get_image_description
from function.umnico_request import send_umnico_message
from function.messages_func import MessagesFunc
from datetime import datetime
from fastapi import BackgroundTasks
import asyncio
from app.storage import user_timers,processed_ids
from pprint import pprint
from function.lead_func import LeadsFunc
from function.account_func import AccountFunc
from handlers.bot_request import send_chat_log,send_chat_log_status,send_chat_log_photo

router = APIRouter()

@router.post("/webhook")
async def handle_webhook(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    
    event_type = data.get("type")
    if event_type not in ["message.incoming", "message.outgoing"]:
        return {"status": "skipped"}

    msg_root = data.get("message", {})
    msg_id = msg_root.get("messageId")
    lead_id = data.get("leadId")
    source_id = msg_root.get("source", {}).get("realId")
    message_text = msg_root.get("message", {}).get("text") or msg_root.get("message", {}).get("data", {}).get("text")
    client_name = msg_root.get("sender", {}).get("login")

    if event_type == 'message.outgoing':
        msg = await MessagesFunc.get_one_by_msg_id(msg_id)
        if not msg:
            lead = await LeadsFunc.get_one(lead_id)
            if lead.is_active == False:
                return
            await LeadsFunc.update_one(lead_id=lead_id, is_active=False,lead_status='master')
            await send_chat_log_status(lead.client_name,'master')
            print(f'--Lead:{lead_id} деактивирован ')
        return
    
    #Проверка на наличие аккаунта в базе
    sa_info = data.get("message", {}).get("sa", {})
    acc_id = sa_info.get("id")
    acc_type = sa_info.get("type")
    acc_login = sa_info.get("login") 

    acc = await AccountFunc.get_one(acc_id)
    if not acc:
        await AccountFunc.add_one(acc_id,acc_type,acc_login)


    # --- НОВЫЙ БЛОК: Проверка активности лида ---
    if lead_id:
        lead = await LeadsFunc.get_one(lead_id=lead_id)
        if not lead:
            print(f"!!! Новый лид {lead_id}. Добавляем в базу.")
            await LeadsFunc.add_one(lead_id=lead_id,client_name=client_name)
        else:
            if not lead.is_active:
                print(f"--- Лид {lead_id} не активен")
                return {"status": "ai_disabled"}
            
    # --- ПРОВЕРКА №2: Защита от дублей Умнико ---
    if msg_id:
        if msg_id in processed_ids:
            print(f"!!! Опа, дубликат от Умнико! ID {msg_id} уже был. Скипаем.")
            return {"status": "duplicate_ignored"}
        
        # Запоминаем ID
        processed_ids.add(msg_id)
        # Чистим память (храним последние 200 ID)
        if len(processed_ids) > 200:
            processed_ids.pop()
    # --- БЛОК С КАРТИНКОЙ ---
    inner_msg = msg_root.get("message", {}) if isinstance(msg_root.get("message"), dict) else {}
    attachments = inner_msg.get("attachments", [])
    photo_url = next((a["url"] for a in attachments if a["type"] == "photo"), None)
    

    if photo_url:
        #await send_chat_log_photo(client_name,photo_url)
        photo_desc = await get_image_description(photo_url)
        message_text = photo_desc
            
    # --- НАШ ТЕСТОВЫЙ ПРИНТ ---
    print(f"\n>>> ВЕБХУК: Type: {event_type} | Lead: {lead_id} | ID: {msg_id}")
    print(f">>> ТЕКСТ: {message_text}")



        
    if message_text:
        # 1. Сразу записываем сообщение в БД (чтобы история копилась)
        await MessagesFunc.add_message(lead_id=lead_id, role="user", content=message_text,msg_id=msg_id)
        await send_chat_log(message_text,client_name,role='client')
        
        # 2. Ставим метку времени для этого лида
        current_time = datetime.now()
        user_timers[lead_id] = current_time
        
        # 3. Отправляем задачу в "фоновый режим" ожидания
        background_tasks.add_task(wait_and_answer, lead_id, current_time, source_id,client_name,acc_id)
        
        print(f"!!! Сообщение от {lead_id} получено. Ждем паузу в переписке...")

    return {"status": "ok"}

async def wait_and_answer(lead_id: str, task_start_time: datetime, source_id: str,client_name,acc_id):
    # Пауза, чтобы дать пользователю дописать мысль (например, 7 секунд)
    await asyncio.sleep(15)
    
    # ПРОВЕРКА: Если время в словаре совпадает с временем запуска этой задачи,
    # значит новых сообщений за эти 7 секунд не приходило.
    if user_timers.get(lead_id) == task_start_time:
        print(f"!!! Пауза выдержана для {lead_id}. Формируем ответ ИИ.")
        
        # 3. ПРОВЕРКА №2: А не зашел ли мастер, пока мы спали 15 секунд?
        lead = await LeadsFunc.get_one(lead_id=lead_id)
        if lead and not lead.is_active:
            print(f"!!! СТОП. Пока ждали паузу, мастер перехватил чат {lead_id}. ИИ отменяет ответ.")
            user_timers.pop(lead_id, None) # Очищаем таймер, чтобы не висел
            return
        # Вытаскиваем историю (уже со всеми новыми кусками)
        raw_history = await MessagesFunc.get_last_messages(lead_id)
        
        # Формируем список для ИИ
        formatted_history = [
            {"role": msg.role, "content": msg.content} 
            for msg in raw_history][::-1]
        #pprint(f'FORMATES_HISTRY________{formatted_history}')
    
        # Запрос к ИИ
        acc = await AccountFunc.get_one(acc_id)
        ai_response = await get_ai_answer(formatted_history,acc.prompt)
        
        if ai_response:
            ai_text = ai_response.get("answer")
            ai_status = ai_response.get("status")
            print(f"!!! ОТВЕТ ОТ ИИ: {ai_response}")
            #print(f"!!! ОТВЕТ ОТ ИИ: {ai_text} [СТАТУС: {ai_status}]")
            # Отправляем в Umnico
            umnico_data = await send_umnico_message(lead_id=lead_id, text=ai_text, source=source_id)
            sent_msg_id = umnico_data[0].get("messageId")
            await MessagesFunc.add_message(lead_id=lead_id, role="assistant", content=ai_text,msg_id=sent_msg_id)

            #Отправка в телеграмм
            await send_chat_log(ai_text,client_name,role='bot')
            await LeadsFunc.update_one(lead_id=lead_id, lead_status=ai_status)
            if ai_status in ['end', 'priced']:
                await LeadsFunc.update_one(lead_id=lead_id, is_active=False)
                await send_chat_log_status(client_name,ai_status)

                        
        
        # Очищаем таймер для этого пользователя
        user_timers.pop(lead_id, None)
    else:
        # Эта задача устарела, так как пользователь прислал новое сообщение
        print(f"--- Пользователь {lead_id} всё еще пишет, текущая задача отменена.")
