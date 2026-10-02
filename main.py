from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

visits = 0

@app.get("/")
def home():
    global visits
    visits += 1
    return {
        "salom": "Bu Railway'da ishlayotgan haqiqiy backend!",
        "hozirgi_vaqt": datetime.utcnow().isoformat(),
        "nechta_marta_kirishdi": visits,
    }
