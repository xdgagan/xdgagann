import re
import os

from telethon import events, Button
from telethon import __version__ as tlhver
from pyrogram import __version__ as pyrover
from NoinoiRobot.events import register as MEMEK
from NoinoiRobot import telethn as tbot

PHOTO = "https://telegra.ph/file/113b9daeef77b928b9077.jpg"

@MEMEK(pattern=("/alive"))
async def awake(event):
  tai = event.sender.first_name
  LUNA = "**HELLO I AM NOINOI!** \n\n"
  LUNA += "✨ **I'M WORKING PROPERLY** \n\n"
  LUNA += "✨ **MY MASTER : [BAZIGAR](https://T.ME/BAZIGARYT)** \n\n"
  LUNA += f"✨ **Telethon Version : {tlhver}** \n\n"
  LUNA += f"✨ **PYROGRAM VERSION : {pyrover}** \n\n"
  LUNA += "**THANS FOR ADDING ME HEAR ❤️**"
  BUTTON = [[Button.url("ʜᴇʟᴘ", "https://t.me/NOINOI_BOT?start=help"), Button.url("sᴜᴘᴘᴏʀᴛ", "https://t.me/NOINOISUPPORT")]]
  await tbot.send_file(event.chat_id, PHOTO, caption=LUNA,  buttons=BUTTON)

@MEMEK(pattern=("/cmd"))
async def reload(event):
  tai = event.sender.first_name
  LUNA = "✅ **𝗛𝗘𝗔𝗥 𝗧𝗛𝗘 𝗦𝗢𝗠𝗘 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 𝗙𝗢𝗥 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 & 𝗩𝗜𝗗𝗘𝗢 & 𝗘𝗫𝗧𝗔𝗥𝗡𝗔𝗟 𝗙𝗘𝗔𝗧𝗨𝗥𝗘𝗦 📌**"
  buttons = [
    [
        InlineKeyboardButton(text="𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚", callback_data="luna_"),
    ],
            ]
  await tbot.send_file(event.chat_id, PHOTO, caption=LUNA,  buttons=BUTTON)
