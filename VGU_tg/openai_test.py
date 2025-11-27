import os
import socks
import socket
from openai import OpenAI

# Настраиваем Socks5 прокси
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1080)  # измените на ваши данные
socket.socket = socks.socksocket

with open('../.env', 'r', encoding='UTF-8') as f:
    code = f.readline()

client = OpenAI(
    api_key=code
)

response = client.responses.create(
    model="gpt-5-nano",
    input="что ты знаешь о блокчейне",
    store=False,
)

print(response.output_text)
