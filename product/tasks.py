from celery import shared_task
from time import sleep
from shop_api.celery import app

@app.task()
def download():
    print("START")
    sleep(15)
    print("END")
    return "OK"
