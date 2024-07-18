# app/main.py
from fastapi import FastAPI
from .routers import items
from data_base.main import init_db_pool, close_db_pol
import configparser

# 创建 configparser 对象
db_config = configparser.ConfigParser()
db_config.read('config.ini')
app = FastAPI()

DB_HOST = db_config['DATABASE']['DB_HOST']
DB_PORT = db_config.getint('DATABASE', 'DB_PORT')
DB_USER = db_config['DATABASE']['DB_USER']
DB_PASSWORD = db_config['DATABASE']['DB_PASSWORD']
DB_NAME = db_config['DATABASE']['DB_NAME']


# 启动事件
@app.on_event('startup')
async def startup():
    await init_db_pool(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, db=DB_NAME)
# 关闭事件
@app.on_event('shutdown')
async def shutdown():
    await close_db_pol()

app.include_router(items.router)