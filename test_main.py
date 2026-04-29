# from fastapi import FastAPI, Request
# import uvicorn

# app = FastAPI()

# @app.post("/webhook")
# async def handle_webhook(request: Request):
#     data = await request.json()
#     print("!!! ПРИШЛИ ДАННЫЕ ОТ UMNICO !!!")
#     print(data)
#     return {"status": "ok"}

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=5500)


from fastapi import FastAPI, Request
import uvicorn
import json

app = FastAPI()

@app.post("/webhook")
async def handle_webhook(request: Request):
    data = await request.json()
    
    # Форматируем JSON в красивую строку с отступами
    pretty_json = json.dumps(data, indent=4, ensure_ascii=False)
    
    print("\n" + "="*80)
    print(pretty_json)
    print("="*80 + "\n")
    
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5500)