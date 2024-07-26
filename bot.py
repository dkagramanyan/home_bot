from aiogram import Bot, Dispatcher, executor, types
import nest_asyncio
import os

import requests as req
from bs4 import BeautifulSoup

import os
import signal
import subprocess
import psutil

nest_asyncio.apply()

with open('token.txt') as file:
    API_TOKEN=file.readline()
    
users = [287157997]
 
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def status(supp_text=''):
    
    url = 'https://bestdavid.ru'
    resp = req.get(url, verify=False)
    soup = BeautifulSoup(resp.text, "html.parser")

    title=soup.find_all('title')
    flag=None
    error=None
    try:
        t = title[0].text
        if 'Jupyter Server'==t:
            flag=True
        else:
            flag=False
    except Exception as e:
        flag=False
        error=e
    
    # res=subprocess.run('wsl -e bash -c " ps ax | grep "/bin/bash ./jupyter_start.sh"" ', capture_output=True)
    res=subprocess.run('wsl -e bash -c " ps ax | grep "./jupyter_start.sh"" ', capture_output=True)
    stdout=res.stdout.decode('utf-8')
    grep_flag=False

    if "/bin/bash ./jupyter_start.sh" in stdout:
        grep_flag=True
        
    if flag:
        text='Jupyter server web status: WORKS\n'
    else:
        text=f'Jupyter server web status: BROKEN\nError{error}\n'
    
    text=text+f'Jupyter server process status: {grep_flag}\n'
    text=text+'\n'+stdout
    
    return text
                
@dp.message_handler(commands=['status'])
async def send_status(message: types.Message, supp_text=''):
    
    if message.chat.id not in users:
        await message.answer('Access restricted')
    else:
        text=status()
        await message.answer(text)

            

        
@dp.message_handler(commands=['start'])
async def send_start(message: types.Message):
    if message.chat.id not in users:
        await message.answer('Access restricted')
    else:
        process=subprocess.Popen(f'jupyter_wsl.bat', cwd='D:/python/home_bot/')
        text=status()
        await message.answer('Server started')
        await message.answer(text)
        
        
@dp.message_handler(commands=['stop'])
async def send_stop(message: types.Message):
    if message.chat.id not in users:
        await message.answer('Access restricted')
    else:
        with open('wsl_jupyter_stop.txt') as file:
            commands=file.readline()
        subprocess.run(commands)
        
        text=status()
        await message.answer('Server stopped')
        await message.answer(text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)