from aiogram import Bot, Dispatcher, executor, types
import nest_asyncio
import os

import requests as req
from bs4 import BeautifulSoup

import os
import signal
import subprocess
import psutil
import time
from datetime import datetime, timedelta
from subprocess import check_output, STDOUT
import re

nest_asyncio.apply()

with open('token.txt') as file:
    API_TOKEN=file.readline()
    
users = [287157997]
CHAT_ID=users[0]
 
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

commands='/status\n/start\n/stop\n/reboot'

def status(supp_text=''):
    
    url = 'https://bestdavid.ru'
    flag=None
    error=None
    try:
        resp = req.get(url, verify=False)
        soup = BeautifulSoup(resp.text, "html.parser")

        title=soup.find_all('title')
        t = title[0].text
        if 'Jupyter Server'==t:
            flag=True
            
    except Exception as e:
        flag=False
        error=e
    
    # res=subprocess.run('wsl -e bash -c " ps ax | grep "/bin/bash ./jupyter_start.sh"" ', capture_output=True)
    res=subprocess.run('wsl -e bash -c " ps ax | grep "./jupyter_start.sh"" ', capture_output=True)
    stdout=res.stdout.decode('utf-8')
    grep_flag=False

    if "/bin/bash ./jupyter_start.sh" in stdout:
        grep_flag=True
        

    text=f'Https web status:      {flag}\n'
    text=text+f'Jupyter server process status:      {grep_flag}\n'
    text=text+'\nProcesses:\n\n'+stdout
    
    text=text+f'\nErrors: {error}\n'
    
    d = timedelta(seconds= time.time() - psutil.boot_time() )
    text=text + f'\nUptime windows {d.days:02d}:{d.seconds//3600:02d}:{(d.seconds//60)%60:02d}:{d.seconds % 60:02}\n'
    
    res=subprocess.run('wmic ComputerSystem get TotalPhysicalMemory', capture_output=True).stdout.decode('utf-8')
    res=int(re.sub("[^0-9]", "", res))
    total_memory=int(res)/(1024**3)
    
    res=subprocess.run('wmic OS get FreePhysicalMemory', capture_output=True).stdout.decode('utf-8')
    res=int(re.sub("[^0-9]", "", res))
    available_memory=int(res)/(1024**2)
    
    available_windows_memory=total_memory-available_memory
    
    text=text+ f'\nTotal windows memory: {total_memory:.2f} GiB'
    text=text+ f'\nAvailable  windows memory: {available_memory:.2f} GiB'
    text=text+ f'\nUsed  windows memory: {available_windows_memory:.2f} GiB\n'
    
    res=subprocess.run('wsl -e bash -c "echo $(($(getconf _PHYS_PAGES) * $(getconf PAGE_SIZE) / (1024 * 1024)))" ', capture_output=True)
    total_memory=int(res.stdout.decode('utf-8'))/1024
    
    res=subprocess.run('wsl -e bash -c "echo $(($(getconf _AVPHYS_PAGES) * $(getconf PAGE_SIZE) / (1024 * 1024)))" ', capture_output=True)
    available_memory=int(res.stdout.decode('utf-8'))/1024
    
    text=text+ f'\nTotal wsl memory: {total_memory:.2f} GiB'
    text=text+ f'\nAvailable  wsl memory: {available_memory:.2f} GiB'
    text=text+ f'\nUsed  wsl memory: {(total_memory-available_memory):.2f} GiB\n'
    
    text=text+ f'\nOnly windows used memory: {(available_windows_memory-total_memory+available_memory):.2f} GiB\n'
    
    text=text+ f'\n{commands}\n'
    
    return text
                
@dp.message_handler(commands=['status'])
async def send_status(message: types.Message, supp_text=''):
    
    if message.chat.id not in users:
        await message.answer('Access restricted')
    else:
        await message.answer('Collecting status info')
        text=status()
        await message.answer(text)

        
@dp.message_handler(commands=['start'])
async def send_start(message: types.Message):
    if message.chat.id not in users:
        await message.answer('Access restricted')
    else:
        await message.answer('Server starting')
        process=subprocess.Popen(f'jupyter_wsl.bat', cwd='D:/python/home_bot/')
        time.sleep(2)
        text=status()
        await message.answer('Server started')
        await message.answer(text)
        
        
@dp.message_handler(commands=['stop'])
async def send_stop(message: types.Message):
    if message.chat.id not in users:
        await message.answer('Access restricted')
    else:
        await message.answer('Server stopping')
        with open('wsl_jupyter_stop.txt') as file:
            commands=file.readline()
        subprocess.run(commands)
        
        text=status()
        await message.answer('Server stopped')
        await message.answer(text)
        
@dp.message_handler(commands=['reboot'])
async def send_reboot(message: types.Message):
    if message.chat.id not in users:
        await message.answer('Access restricted')
    else:
        await message.answer('Windows machine is rebooting. Expected time to turn on the bot 5 min')
        subprocess.run('shutdown /r /t 0')
        await message.answer('Reboot command is successful')

        
async def on_startup(dp):
    # Send a message when the bot starts
    text="Bot has started"
    text=text+ f'\n\n{commands}\n'
    await bot.send_message(chat_id=CHAT_ID, text=text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)