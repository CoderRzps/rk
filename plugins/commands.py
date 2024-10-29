import os
import logging
import random, string
import asyncio
import time
import datetime
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait, ButtonDataInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id, delete_files
from database.users_chats_db import db
from info import STICKERS_IDS,SUPPORT_GROUP ,INDEX_CHANNELS, ADMINS, IS_VERIFY, VERIFY_TUTORIAL, VERIFY_EXPIRE, TUTORIAL, SHORTLINK_API, SHORTLINK_URL, AUTH_CHANNEL, DELETE_TIME, SUPPORT_LINK, UPDATES_LINK, LOG_CHANNEL, PICS, PROTECT_CONTENT, IS_STREAM, IS_FSUB, PAYMENT_QR
from utils import get_settings, get_size, is_subscribed, is_check_admin, get_shortlink, get_verify_status, update_verify_status, save_group_settings, temp, get_readable_time, get_wish, get_seconds
import requests
from telegraph import upload_file
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import string

# PM_FILE_DELETE_TIME ko define karna
PM_FILE_DELETE_TIME = 3600  # Example value

# Jab aap use kar rahe hain
time = get_readable_time(PM_FILE_DELETE_TIME)



@Client.on_message(filters.command("ask") & filters.incoming)
async def aiRes(_, message):
    if message.chat.id == SUPPORT_GROUP:
        try:
            # Puchhe gaye sawal ko split aur check karte hain
            asked = message.text.split(None, 1)[1]
        except IndexError:
            return await message.reply("Bhai kuch puch to le /ask k baad !")

        thinkStc = await message.reply_sticker(sticker=random.choice(STICKERS_IDS))

        # API request
        url = "https://bisal-ai-api.vercel.app/biisal"
        try:
            res = requests.post(url, data={'query': asked})
            res.raise_for_status()  # Agar error status aaye toh exception raise karega
            response = res.json().get("response")
            await thinkStc.delete()
            await message.reply(f"<b>hey {message.from_user.mention()},\n{response.strip()}</b>")  # Strip to remove extra spaces
        except (requests.RequestException, ValueError):
            await thinkStc.delete()
            await message.reply("Mausam kharab hai ! Thode der mein try kre !\nor Report to Developer.")
    else:
        btn = [[
            InlineKeyboardButton('💡 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ 💡', url=SUPPORT_LINK)
        ]]
        await message.reply(
            f"<b>hey {message.from_user.mention()},\n\nPlease use this command in support group.</b>", 
            reply_markup=InlineKeyboardMarkup(btn)
            )
        
"""@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    botid = client.me.id
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            username = f'@{message.chat.username}' if message.chat.username else 'Private'
            await client.send_message(LOG_CHANNEL, script.NEW_GROUP_TXT.format(message.chat.title, message.chat.id, username, total))       
            await db.add_chat(message.chat.id, message.chat.title)
        wish = get_wish()
        btn = [[
            InlineKeyboardButton('⚡️ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ ⚡️', url=UPDATES_LINK),
            InlineKeyboardButton('💡 Support Group 💡', url=SUPPORT_LINK)
        ]]
        await message.reply(text=f"<b>ʜᴇʏ {message.from_user.mention}, <i>{wish}</i>\nʜᴏᴡ ᴄᴀɴ ɪ ʜᴇʟᴘ ʏᴏᴜ??</b>", reply_markup=InlineKeyboardMarkup(btn))
        return 
        
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.NEW_USER_TXT.format(message.from_user.mention, message.from_user.id))

    verify_status = await get_verify_status(message.from_user.id)
    if verify_status['is_verified'] and VERIFY_EXPIRE < (time.time() - verify_status['verified_time']):
        await update_verify_status(message.from_user.id, is_verified=False)
    
    if (len(message.command) != 2) or (len(message.command) == 2 and message.command[1] == 'start'):
        buttons = [[
            InlineKeyboardButton('⤬ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ ⤬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('ℹ️ ᴜᴘᴅᴀᴛᴇs', url=UPDATES_LINK),
                    InlineKeyboardButton('🧑‍💻 sᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
                ],[
                    InlineKeyboardButton('👨‍🚒 ʜᴇʟᴘ', callback_data='help'),
                    InlineKeyboardButton('📚 ᴀʙᴏᴜᴛ', callback_data='about')
                ],[
                    InlineKeyboardButton('💰 ᴇᴀʀɴ ᴜɴʟɪᴍɪᴛᴇᴅ ᴍᴏɴᴇʏ ʙʏ ʙᴏᴛ 💰', callback_data='earn')
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, get_wish()),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return


    mc = message.command[1]

    if mc.startswith('verify'):
        _, token = mc.split("_", 1)
        verify_status = await get_verify_status(message.from_user.id)
        if verify_status['verify_token'] != token:
            return await message.reply("Your verify token is invalid.")
        expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=VERIFY_EXPIRE)
        await update_verify_status(message.from_user.id, is_verified=True, verified_time=time_now(), expire_time=expiry_time)
        if verify_status["link"] == "":
            reply_markup = None
        else:
            btn = [[
                InlineKeyboardButton("📌 Get File 📌", url=f'https://t.me/{temp.U_NAME}?start={verify_status["link"]}')
            ]]
            reply_markup = InlineKeyboardMarkup(btn)
        await message.reply(f"✅ You successfully verified until: {get_readable_time(VERIFY_EXPIRE)}", reply_markup=reply_markup, protect_content=True)
        return
    
    verify_status = await get_verify_status(message.from_user.id)
    if not await db.has_premium_access(message.from_user.id):
        if IS_VERIFY and not verify_status['is_verified']:
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            await update_verify_status(message.from_user.id, verify_token=token, link="" if mc == 'inline_verify' else mc)
            link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f'https://t.me/{temp.U_NAME}?start=verify_{token}')
            btn = [[
                InlineKeyboardButton("🧿 Verify 🧿", url=link)
            ],[
                InlineKeyboardButton('🗳 Tutorial 🗳', url=VERIFY_TUTORIAL)
            ]]
            await message.reply("You not verified today! Kindly verify now. 🔐", reply_markup=InlineKeyboardMarkup(btn), protect_content=True)
            return

    settings = await get_settings(int(mc.split("_", 2)[1]))
    if not await db.has_premium_access(message.from_user.id):
        if settings['fsub']:
            btn = await is_subscribed(client, message, settings['fsub'])
            if btn:
                btn.append(
                    [InlineKeyboardButton("🔁 Try Again 🔁", callback_data=f"checksub#{mc}")]
                )
                reply_markup = InlineKeyboardMarkup(btn)
                await message.reply_photo(
                    photo=random.choice(PICS),
                    caption=f"👋 Hello {message.from_user.mention},\n\nPlease join my 'Updates Channel' and try again. 😇",
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.HTML
                )
                return 
        
        _, grp_id, key = mc.split("_", 2)
        files = temp.FILES.get(key)
        if not files:
            return await message.reply('No Such All Files Exist!')
        settings = await get_settings(int(grp_id))
        file_ids = []
        total_files = await message.reply(f"<b><i>🗂 Total files - <code>{len(files)}</code></i></b>")
        for file in files:
            CAPTION = settings['caption']
            f_caption = CAPTION.format(
                file_name=file.file_name,
                file_size=get_size(file.file_size),
                file_caption=file.caption
            )      
            if settings.get('is_stream', IS_STREAM):
                btn = [[
                    InlineKeyboardButton("✛ ᴡᴀᴛᴄʜ & ᴅᴏᴡɴʟᴏᴀᴅ ✛", callback_data=f"stream#{file.file_id}")
                ],[
                    InlineKeyboardButton('⚡️ ᴜᴘᴅᴀᴛᴇs', url=UPDATES_LINK),
                    InlineKeyboardButton('💡 ꜱᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
                ],[
                    InlineKeyboardButton('⁉️ ᴄʟᴏsᴇ ⁉️', callback_data='close_data')
                ]]
            else:
                btn = [[
                    InlineKeyboardButton('⚡️ ᴜᴘᴅᴀᴛᴇs', url=UPDATES_LINK),
                    InlineKeyboardButton('💡 ꜱᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
                ],[
                    InlineKeyboardButton('⁉️ ᴄʟᴏsᴇ ⁉️', callback_data='close_data')
                ]]

            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file.file_id,
                caption=f_caption,
                protect_content=False if await db.has_premium_access(message.from_user.id) else True,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            file_ids.append(msg.id)

        time = get_readable_time(PM_FILE_DELETE_TIME)
        vp = await message.reply(f"Nᴏᴛᴇ: Tʜɪs ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇ ɪɴ {time} ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛs. Sᴀᴠᴇ ᴛʜᴇ ғɪʟᴇs ᴛᴏ sᴏᴍᴇᴡʜᴇʀᴇ ᴇʟsᴇ")
        await asyncio.sleep(PM_FILE_DELETE_TIME)
        buttons = [[InlineKeyboardButton('ɢᴇᴛ ғɪʟᴇs ᴀɢᴀɪɴ', callback_data=f"get_del_send_all_files#{grp_id}#{key}")]] 
        await client.delete_messages(
            chat_id=message.chat.id,
            message_ids=file_ids + [total_files.id]
        )
        await vp.edit("Tʜᴇ ғɪʟᴇ ʜᴀs ʙᴇᴇɴ ɢᴏɴᴇ ! Cʟɪᴄᴋ ɢɪᴠᴇɴ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪᴛ ᴀɢᴀɪɴ.", reply_markup=InlineKeyboardMarkup(buttons))
        return

    type_, grp_id, file_id = mc.split("_", 2)
    files_ = await get_file_details(file_id)
    if not files_:
        return await message.reply('No Such File Exist!')
    files = files_[0]
    settings = await get_settings(int(grp_id))
    if type_ != 'shortlink' and settings['shortlink']:
        if not await db.has_premium_access(message.from_user.id):
            link = await get_shortlink(settings['url'], settings['api'], f"https://t.me/{temp.U_NAME}?start=shortlink_{grp_id}_{file_id}")
            btn = [[
                InlineKeyboardButton("♻️ Get File ♻️", url=link)
            ],[
                InlineKeyboardButton("📍 ʜᴏᴡ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋ 📍", url=settings['tutorial'])
            ]]
            await message.reply(f"[{get_size(files.file_size)}] {files.file_name}\n\nYour file is ready, Please get using this link. 👍", reply_markup=InlineKeyboardMarkup(btn), protect_content=True)
            return
            
    CAPTION = settings['caption']
    f_caption = CAPTION.format(
        file_name = files.file_name,
        file_size = get_size(files.file_size),
        file_caption=files.caption
    )
    if settings.get('is_stream', IS_STREAM):
        btn = [[
            InlineKeyboardButton("✛ ᴡᴀᴛᴄʜ & ᴅᴏᴡɴʟᴏᴀᴅ ✛", callback_data=f"stream#{file_id}")
        ],[
            InlineKeyboardButton('⚡️ ᴜᴘᴅᴀᴛᴇs', url=UPDATES_LINK),
            InlineKeyboardButton('💡 ꜱᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
        ],[
            InlineKeyboardButton('⁉️ ᴄʟᴏsᴇ ⁉️', callback_data='close_data')
        ]]
    else:
        btn = [[
            InlineKeyboardButton('⚡️ ᴜᴘᴅᴀᴛᴇs', url=UPDATES_LINK),
            InlineKeyboardButton('💡 ꜱᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
        ],[
            InlineKeyboardButton('⁉️ ᴄʟᴏsᴇ ⁉️', callback_data='close_data')
        ]]
    vp = await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=False if await db.has_premium_access(message.from_user.id) else True,
        reply_markup=InlineKeyboardMarkup(btn)
    )
    time = get_readable_time(PM_FILE_DELETE_TIME)
    msg = await vp.reply(f"Nᴏᴛᴇ: Tʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇ ɪɴ {time} ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛs. Sᴀᴠᴇ ᴛʜᴇ ғɪʟᴇ ᴛᴏ sᴏᴍᴇᴡʜᴇʀᴇ ᴇʟsᴇ")
    await asyncio.sleep(PM_FILE_DELETE_TIME)
    btns = [[
        InlineKeyboardButton('ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ', callback_data=f"get_del_file#{grp_id}#{file_id}")
    ]]
    await msg.delete()
    await vp.delete()
    await vp.reply("Tʜᴇ ғɪʟᴇ ʜᴀs ʙᴇᴇɴ ɢᴏɴᴇ ! Cʟɪᴄᴋ ɢɪᴠᴇɴ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪᴛ ᴀɢᴀɪɴ.", reply_markup=InlineKeyboardMarkup(btns))"""

# .on_message decorator se start command handle karte hain
@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    botid = client.me.id
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            username = f'@{message.chat.username}' if message.chat.username else 'Private'
            await client.send_message(LOG_CHANNEL, script.NEW_GROUP_TXT.format(message.chat.title, message.chat.id, username, total))       
            await db.add_chat(message.chat.id, message.chat.title)
        wish = get_wish()
        btn = [[
            InlineKeyboardButton('⚡️ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ ⚡️', url=UPDATES_LINK),
            InlineKeyboardButton('💡 Support Group 💡', url=SUPPORT_LINK)
        ]]
        await message.reply(text=f"<b>ʜᴇʏ {message.from_user.mention}, <i>{wish}</i>\nʜᴏᴡ ᴄᴀɴ ɪ ʜᴇʟᴘ ʏᴏᴜ??</b>", reply_markup=InlineKeyboardMarkup(btn))
        return 
        
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.NEW_USER_TXT.format(message.from_user.mention, message.from_user.id))

    verify_status = await get_verify_status(message.from_user.id)
    if verify_status['is_verified'] and VERIFY_EXPIRE < (time.time() - verify_status['verified_time']):
        await update_verify_status(message.from_user.id, is_verified=False)
    
    if (len(message.command) != 2) or (len(message.command) == 2 and message.command[1] == 'start'):
        buttons = [[
            InlineKeyboardButton('⤬ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ ⤬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('ℹ️ ᴜᴘᴅᴀᴛᴇs', url=UPDATES_LINK),
                    InlineKeyboardButton('🧑‍💻 sᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
                ],[
                    InlineKeyboardButton('👨‍🚒 ʜᴇʟᴘ', callback_data='help'),
                    InlineKeyboardButton('📚 ᴀʙᴏᴜᴛ', callback_data='about')
                ],[
                    InlineKeyboardButton('💰 ᴇᴀʀɴ ᴜɴʟɪᴍɪᴛᴇᴅ ᴍᴏɴᴇʏ ʙʏ ʙᴏᴛ 💰', callback_data='earn')
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, get_wish()),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return

    mc = message.command[1]

    if mc.startswith('verify'):
        _, token = mc.split("_", 1)
        verify_status = await get_verify_status(message.from_user.id)
        if verify_status['verify_token'] != token:
            return await message.reply("Your verify token is invalid.")
        expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=VERIFY_EXPIRE)
        await update_verify_status(message.from_user.id, is_verified=True, verified_time=time_now(), expire_time=expiry_time)
        if verify_status["link"] == "":
            reply_markup = None
        else:
            btn = [[
                InlineKeyboardButton("📌 Get File 📌", url=f'https://t.me/{temp.U_NAME}?start={verify_status["link"]}')
            ]]
            reply_markup = InlineKeyboardMarkup(btn)
        await message.reply(f"✅ You successfully verified until: {get_readable_time(VERIFY_EXPIRE)}", reply_markup=reply_markup, protect_content=True)
        return
    
    verify_status = await get_verify_status(message.from_user.id)
    if not await db.has_premium_access(message.from_user.id):
        if IS_VERIFY and not verify_status['is_verified']:
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            await update_verify_status(message.from_user.id, verify_token=token, link="" if mc == 'inline_verify' else mc)
            link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f'https://t.me/{temp.U_NAME}?start=verify_{token}')
            btn = [[
                InlineKeyboardButton("🧿 Verify 🧿", url=link)
            ],[
                InlineKeyboardButton('🗳 Tutorial 🗳', url=VERIFY_TUTORIAL)
            ]]
            await message.reply("You not verified today! Kindly verify now. 🔐", reply_markup=InlineKeyboardMarkup(btn), protect_content=True)
            return

    settings = await get_settings(int(mc.split("_", 2)[1]))
    if not await db.has_premium_access(message.from_user.id):
        if settings['fsub']:
            btn = await is_subscribed(client, message, settings['fsub'])
            if btn:
                btn.append(
                    [InlineKeyboardButton("🔁 Try Again 🔁", callback_data=f"checksub#{mc}")]
                )
                reply_markup = InlineKeyboardMarkup(btn)
                await message.reply_photo(
                    photo=random.choice(PICS),
                    caption=f"👋 Hello {message.from_user.mention},\n\nPlease join my 'Updates Channel' and try again. 😇",
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.HTML
                )
                return 
        
        _, grp_id, key = mc.split("_", 2)
        files = temp.FILES.get(key)
        if not files:
            return await message.reply('No Such All Files Exist!')
        settings = await get_settings(int(grp_id))
        file_ids = []
        total_files = await message.reply(f"<b><i>🗂 Total files - <code>{len(files)}</code></i></b>")
        for file in files:
            CAPTION = settings['caption']
            f_caption = CAPTION.format(
                file_name=file.file_name,
                file_size=get_size(file.file_size),
                file_caption=file.caption
            )      
            if settings.get('is_stream', IS_STREAM):
                btn = [[
                    InlineKeyboardButton("✛ ᴡᴀᴛᴄʜ & ᴅᴏᴡɴʟᴏᴀᴅ ✛", callback_data=f"stream#{file.file_id}")
                ],[
                    InlineKeyboardButton('⚡️ ᴜᴘᴅᴀᴛᴇs', url=UPDATES_LINK),
                    InlineKeyboardButton('💡 ꜱᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
                ],[
                    InlineKeyboardButton('⁉️ ᴄʟᴏsᴇ ⁉️', callback_data='close_data')
                ]]
            else:
                btn = [[
                    InlineKeyboardButton('⚡️ ᴜᴘᴅᴀᴛᴇs', url=UPDATES_LINK),
                    InlineKeyboardButton('💡 ꜱᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
                ],[
                    InlineKeyboardButton('⁉️ ᴄʟᴏsᴇ ⁉️', callback_data='close_data')
                ]]

            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file.file_id,
                caption=f_caption,
                protect_content=False if await db.has_premium_access(message.from_user.id) else True,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            file_ids.append(msg.id)

        time = get_readable_time(PM_FILE_DELETE_TIME)
        vp = await message.reply(f"Nᴏᴛᴇ: Tʜɪs ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇ ɪɴ {time} ᴛᴏ ᴀᴠᴏɪᴅ ᴄᴏᴘʏʀɪɢʜᴛs. Sᴀᴠᴇ ᴛʜᴇᴍ ᴏᴜᴛsɪᴅᴇ ɪf yᴏᴜ ʟɪᴋᴇ ᴜsɪɴɢ ᴛʜᴇ ʙᴏᴛ.", reply_to_message_id=total_files.id)

        # Cleanup old messages
        await asyncio.sleep(PM_FILE_DELETE_TIME)
        for file_id in file_ids:
            try:
                await client.delete_messages(chat_id=message.from_user.id, message_ids=file_id)
            except Exception as e:
                print(e)

        await client.delete_messages(chat_id=message.from_user.id, message_ids=vp.id)

@Client.on_message(filters.command('index_channels') & filters.user(ADMINS))
async def channels_info(bot, message):
    """Send basic information of index channels"""
    ids = INDEX_CHANNELS
    if not ids:
        return await message.reply("Not set INDEX_CHANNELS")

    text = '**Indexed Channels:**\n\n'
    for i, id in enumerate(ids, start=1):
        try:
            chat = await bot.get_chat(id)
            text += f'{i}. {chat.title}\n'
        except Exception as e:
            text += f'{i}. [ID: {id}] - Could not retrieve information: {e}\n'
    text += f'\n**Total:** {len(ids)}'

    await message.reply(text)

@Client.on_message(filters.command('stats') & filters.user(ADMINS))
async def stats(bot, message):
    msg = await message.reply('Please Wait...')
    files = await Media.count_documents()
    users = await db.total_users_count()
    chats = await db.total_chat_count()
    u_size = get_size(await db.get_db_size())
    f_size = get_size(536870912 - await db.get_db_size())
    uptime = get_readable_time(time.time() - temp.START_TIME)
    STATUS_TXT = "Files: {}\nUsers: {}\nChats: {}\nUser Size: {}\nFile Size: {}\nUptime: {}"
    await msg.edit(STATUS_TXT.format(files, users, chats, u_size, f_size, uptime))

@Client.on_message(filters.command('settings'))
async def settings(client, message):
    try:
        # यूज़र आईडी की जांच करें
        userid = message.from_user.id if message.from_user else None
        if not userid:
            return await message.reply("<b>You are Anonymous admin; you can't use this command!</b>")
        
        # यह कमांड केवल ग्रुप या सुपरग्रुप में ही चल सकती है
        chat_type = message.chat.type
        if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            return await message.reply_text("Please use this command in a group.")
        
        grp_id = message.chat.id

        # ऐडमिन चेक
        if not await is_check_admin(client, grp_id, message.from_user.id):
            return await message.reply_text("You are not an admin in this group.")
        
        # ग्रुप सेटिंग्स प्राप्त करें
        settings = await get_settings(grp_id)
        if settings is None:
            return await message.reply_text("Error: Could not retrieve settings.")

        # बटन सेटअप
        buttons = [
            [
                InlineKeyboardButton("Auto Filter", callback_data=f"setgs#auto_filter#{settings.get('auto_filter', False)}#{grp_id}"),
                InlineKeyboardButton("✅ Yes" if settings.get("auto_filter", False) else "❌ No", callback_data=f"setgs#auto_filter#{settings.get('auto_filter', False)}#{grp_id}")
            ],
            [
                InlineKeyboardButton("File Secure", callback_data=f"setgs#file_secure#{settings.get('file_secure', False)}#{grp_id}"),
                InlineKeyboardButton("✅ Yes" if settings.get("file_secure", False) else "❌ No", callback_data=f"setgs#file_secure#{settings.get('file_secure', False)}#{grp_id}")
            ],
            [
                InlineKeyboardButton("IMDb Poster", callback_data=f"setgs#imdb#{settings.get('imdb', False)}#{grp_id}"),
                InlineKeyboardButton("✅ Yes" if settings.get("imdb", False) else "❌ No", callback_data=f"setgs#imdb#{settings.get('imdb', False)}#{grp_id}")
            ],
            [
                InlineKeyboardButton("Spelling Check", callback_data=f"setgs#spell_check#{settings.get('spell_check', False)}#{grp_id}"),
                InlineKeyboardButton("✅ Yes" if settings.get("spell_check", False) else "❌ No", callback_data=f"setgs#spell_check#{settings.get('spell_check', False)}#{grp_id}")
            ],
            [
                InlineKeyboardButton("Auto Delete", callback_data=f"setgs#auto_delete#{settings.get('auto_delete', False)}#{grp_id}"),
                InlineKeyboardButton(f"{get_readable_time(DELETE_TIME)}" if settings.get("auto_delete", False) else "❌ No", callback_data=f"setgs#auto_delete#{settings.get('auto_delete', False)}#{grp_id}")
            ],
            [
                InlineKeyboardButton("Welcome", callback_data=f"setgs#welcome#{settings.get('welcome', False)}#{grp_id}"),
                InlineKeyboardButton("✅ Yes" if settings.get("welcome", False) else "❌ No", callback_data=f"setgs#welcome#{settings.get('welcome', False)}#{grp_id}")
            ],
            [
                InlineKeyboardButton("Shortlink", callback_data=f"setgs#shortlink#{settings.get('shortlink', False)}#{grp_id}"),
                InlineKeyboardButton("✅ Yes" if settings.get("shortlink", False) else "❌ No", callback_data=f"setgs#shortlink#{settings.get('shortlink', False)}#{grp_id}")
            ],
            [
                InlineKeyboardButton("Result Page", callback_data=f"setgs#links#{settings.get('links', False)}#{grp_id}"),
                InlineKeyboardButton("⛓ Link" if settings.get("links", False) else "🧲 Button", callback_data=f"setgs#links#{settings.get('links', False)}#{grp_id}")
            ],
            [
                InlineKeyboardButton("Fsub", callback_data=f"setgs#is_fsub#{settings.get('is_fsub', IS_FSUB)}#{grp_id}"),
                InlineKeyboardButton("✅ On" if settings.get("is_fsub", IS_FSUB) else "❌ Off", callback_data=f"setgs#is_fsub#{settings.get('is_fsub', IS_FSUB)}#{grp_id}")
            ],
            [
                InlineKeyboardButton("Stream", callback_data=f"setgs#is_stream#{settings.get('is_stream', IS_STREAM)}#{grp_id}"),
                InlineKeyboardButton("✅ On" if settings.get("is_stream", IS_STREAM) else "❌ Off", callback_data=f"setgs#is_stream#{settings.get('is_stream', IS_STREAM)}#{grp_id}")
            ],
            [
                InlineKeyboardButton("❌ Close ❌", callback_data="close_data")
            ]
        ]

        # जवाब भेजें
        await message.reply_text(
            text=f"Change your settings for <b>'{message.chat.title}'</b> as you wish. ⚙",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )

    except Exception as e:
        # Error Handling
        await message.reply_text(f"An error occurred: {e}")

from pyrogram import Client, filters, enums

@Client.on_message(filters.command('set_template'))
async def save_template(client, message):
    # User ID ki check
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("<b>You are Anonymous admin; you can't use this command!</b>")
    
    # Chat type ki check
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("Please use this command in a group.")

    grp_id = message.chat.id
    title = message.chat.title

    # Admin check
    if not await is_check_admin(client, grp_id, userid):
        return await message.reply_text("You are not an admin in this group.")
    
    # Template receive karna
    try:
        template = message.text.split(" ", 1)[1]
        if not template:
            raise ValueError("Template is empty.")
    except IndexError:
        return await message.reply_text("Command incomplete! Please provide a template after the command.")
    except ValueError as e:
        return await message.reply_text(str(e))
    
    # Group settings me template save karna
    await save_group_settings(grp_id, 'template', template)
    await message.reply_text(f"Successfully changed template for <b>{title}</b> to:\n\n{template}", parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command('set_caption'))
async def save_caption(client, message):
    # User ID ki check
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("<b>You are Anonymous admin; you can't use this command!</b>")

    # Chat type ki check
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("Please use this command in a group.")
    
    grp_id = message.chat.id
    title = message.chat.title

    # Admin check
    if not await is_check_admin(client, grp_id, userid):
        return await message.reply_text("You are not an admin in this group.")
    
    # Caption receive karna
    try:
        caption = message.text.split(" ", 1)[1]
        if not caption:
            raise ValueError("Caption is empty.")
    except IndexError:
        return await message.reply_text("Command incomplete! Please provide a caption after the command.")
    except ValueError as e:
        return await message.reply_text(str(e))
    
    # Group settings me caption save karna
    await save_group_settings(grp_id, 'caption', caption)
    await message.reply_text(f"Successfully changed caption for <b>{title}</b> to:\n\n{caption}", parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command('set_shortlink'))
async def save_shortlink(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("<b>You are Anonymous admin you can't use this command !</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("Use this command in group.")    
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('You not admin in this group.')
    try:
        _, url, api = message.text.split(" ", 2)
    except:
        return await message.reply_text("<b>Command Incomplete:-\n\ngive me a shortlink & api along with the command...\n\nEx:- <code>/shortlink mdisklink.link 5843c3cc645f5077b2200a2c77e0344879880b3e</code>")   
    try:
        await get_shortlink(url, api, f'https://t.me/{temp.U_NAME}')
    except:
        return await message.reply_text("Your shortlink API or URL invalid, Please Check again!")   
    await save_group_settings(grp_id, 'url', url)
    await save_group_settings(grp_id, 'api', api)
    await message.reply_text(f"Successfully changed shortlink for {title} to\n\nURL - {url}\nAPI - {api}")

@Client.on_message(filters.command('get_custom_settings'))
async def get_custom_settings(client, message):
    # User ID ki check
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("<b>You are Anonymous admin; you can't use this command!</b>")

    # Chat type ki check
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("Please use this command in a group.")

    grp_id = message.chat.id
    title = message.chat.title

    # Admin check
    if not await is_check_admin(client, grp_id, userid):
        return await message.reply_text("You are not an admin in this group...")

    # Custom settings fetch karna
    settings = await get_settings(grp_id)
    if settings is None:
        return await message.reply_text("No custom settings found for this group.")

    # Settings ka text banana
    text = f"""Custom settings for: <b>{title}</b>

Shortlink URL: {settings.get("url", "Not Set")}
Shortlink API: {settings.get("api", "Not Set")}

IMDb Template: {settings.get('template', 'Not Set')}

File Caption: {settings.get('caption', 'Not Set')}

Welcome Text: {settings.get('welcome_text', 'Not Set')}

Tutorial Link: {settings.get('tutorial', 'Not Set')}

Force Channels: {', '.join(settings.get('fsub', [])) if settings.get('fsub') else 'Not Set'}"""

    # Close button ka inline keyboard
    btn = [[
        InlineKeyboardButton(text="Close", callback_data="close_data")
    ]]
    
    # Settings reply karna
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML, disable_web_page_preview=True)


@Client.on_message(filters.command('set_welcome'))
async def save_welcome(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("<b>You are Anonymous admin you can't use this command !</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("Use this command in group.")      
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('You not admin in this group.')
    try:
        welcome = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("Command Incomplete!")    
    await save_group_settings(grp_id, 'welcome_text', welcome)
    await message.reply_text(f"Successfully changed welcome for {title} to\n\n{welcome}")
        
@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete_file(bot, message):
    try:
        query = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("Command Incomplete!\nUsage: /delete query")
    msg = await message.reply_text('Searching...')
    total, files = await delete_files(query)
    if int(total) == 0:
        return await msg.edit('Not have files in your query')
    btn = [[
        InlineKeyboardButton("YES", callback_data=f"delete_{query}")
    ],[
        InlineKeyboardButton("CLOSE", callback_data="close_data")
    ]]
    await msg.edit(f"Total {total} files found in your query {query}.\n\nDo you want to delete?", reply_markup=InlineKeyboardMarkup(btn))
 
@Client.on_message(filters.command('delete_all') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    btn = [[
        InlineKeyboardButton(text="YES", callback_data="delete_all")
    ],[
        InlineKeyboardButton(text="CLOSE", callback_data="close_data")
    ]]
    files = await Media.count_documents()
    if int(files) == 0:
        return await message.reply_text('Not have files to delete')
    await message.reply_text(f'Total {files} files have.\nDo you want to delete all?', reply_markup=InlineKeyboardMarkup(btn))

@Client.on_message(filters.command('set_tutorial'))
async def set_tutorial(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("<b>You are Anonymous admin you can't use this command !</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("Use this command in group.")       
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('You not admin in this group.')
    try:
        tutorial = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("Command Incomplete!")   
    await save_group_settings(grp_id, 'tutorial', tutorial)
    await message.reply_text(f"Successfully changed tutorial for {title} to\n\n{tutorial}")

@Client.on_message(filters.command('set_fsub'))
async def set_fsub(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("<b>You are Anonymous admin you can't use this command !</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("Use this command in group.")      
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, message.from_user.id):
        return await message.reply_text('You not admin in this group.')
    vp = message.text.split(" ", 1)[1]
    if vp.lower() in ["Off", "off", "False", "false", "Turn Off", "turn off"]:
        await save_group_settings(grp_id, 'is_fsub', False)
        return await message.reply_text("Successfully Turned Off !")
    elif vp.lower() in ["On", "on", "True", "true", "Turn On", "turn on"]:
        await save_group_settings(grp_id, 'is_fsub', True)
        return await message.reply_text("Successfully Turned On !")
    try:
        ids = message.text.split(" ", 1)[1]
        fsub_ids = list(map(int, ids.split()))
    except IndexError:
        return await message.reply_text("Command Incomplete!\n\nCan multiple channel add separate by spaces. Like: /set_fsub id1 id2 id3")
    except ValueError:
        return await message.reply_text('Make sure ids is integer.')        
    channels = "Channels:\n"
    for id in fsub_ids:
        try:
            chat = await client.get_chat(id)
        except Exception as e:
            return await message.reply_text(f"{id} is invalid!\nMake sure this bot admin in that channel.\n\nError - {e}")
        if chat.type != enums.ChatType.CHANNEL:
            return await message.reply_text(f"{id} is not channel.")
        channels += f'{chat.title}\n'
    await save_group_settings(grp_id, 'fsub', fsub_ids)
    await message.reply_text(f"Successfully set force channels for {title} to\n\n{channels}")

@Client.on_message(filters.command('telegraph'))
async def telegraph(bot, message):
    reply_to_message = message.reply_to_message
    if not reply_to_message:
        return await message.reply('Reply to any photo or video.')
    file = reply_to_message.photo or reply_to_message.video or None
    if file is None:
        return await message.reply('Invalid media.')
    if file.file_size >= 5242880:
        await message.reply_text(text="Send less than 5MB")   
        return
    text = await message.reply_text(text="ᴘʀᴏᴄᴇssɪɴɢ....")   
    media = await reply_to_message.download()  
    try:
        response = upload_file(media)
    except Exception as e:
        await text.edit_text(text=f"Error - {e}")
        return    
    try:
        os.remove(media)
    except:
        pass
    await text.edit_text(f"<b>❤️ ʏᴏᴜʀ ᴛᴇʟᴇɢʀᴀᴘʜ ʟɪɴᴋ ᴄᴏᴍᴘʟᴇᴛᴇᴅ 👇</b>\n\n<code>https://telegra.ph/{response[0]}</code></b>")

@Client.on_message(filters.command('ping'))
async def ping(client, message):
    start_time = time.monotonic()
    msg = await message.reply("👀")
    end_time = time.monotonic()
    await msg.edit(f'{round((end_time - start_time) * 1000)} ms')
    
@Client.on_message(filters.command("add_premium"))
async def give_premium_cmd_handler(client, message):
    if message.from_user.id not in ADMINS:
        return
    if len(message.command) == 3:
        user_id = int(message.command[1])  # Convert the user_id to integer
        time = message.command[2]        
        seconds = await get_seconds(time)
        if seconds > 0:
            expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
            user_data = {"id": user_id, "expiry_time": expiry_time} 
            await db.update_user(user_data)  # Use the update_user method to update or insert user data
            await message.reply_text("Premium access added to the user.")
            
            await client.send_message(
                chat_id=user_id,
                text=f"<b>ᴘʀᴇᴍɪᴜᴍ ᴀᴅᴅᴇᴅ ᴛᴏ ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ꜰᴏʀ {time} ᴇɴᴊᴏʏ 😀\n</b>",                
            )
        else:
            await message.reply_text("Invalid time format. Please use '1day for days', '1hour for hours', or '1min for minutes', or '1month for months' or '1year for year'")
    else:
        await message.reply_text("<b>Usage: /add_premium user_id time \n\nExample /add_premium 1252789 10day \n\n(e.g. for time units '1day for days', '1hour for hours', or '1min for minutes', or '1month for months' or '1year for year')</b>")
        
@Client.on_message(filters.command("remove_premium"))
async def remove_premium_cmd_handler(client, message):
    if message.from_user.id not in ADMINS:
        return
    if len(message.command) == 2:
        user_id = int(message.command[1])  # Convert the user_id to integer
      #  time = message.command[2]
        time = "1s"
        seconds = await get_seconds(time)
        if seconds > 0:
            expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
            user_data = {"id": user_id, "expiry_time": expiry_time}  # Using "id" instead of "user_id"
            await db.update_user(user_data)  # Use the update_user method to update or insert user data
            await message.reply_text("Premium access removed to the user.")
            await client.send_message(
                chat_id=user_id,
                text=f"<b>premium removed by admins \n\n Contact Admin if this is mistake \n\n 👮 Admin : @Rk_botowner \n</b>",                
            )
        else:
            await message.reply_text("Invalid time format.'")
    else:
        await message.reply_text("Usage: /remove_premium user_id")
        
@Client.on_message(filters.command("plan"))
async def plans_list(client, message):
    btn = [[
        InlineKeyboardButton("ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ 🧾", url=OWNER_USERNAME)
    ],[
        InlineKeyboardButton("⚠️ ᴄʟᴏsᴇ / ᴅᴇʟᴇᴛᴇ ⚠️", callback_data="close_data")
    ]]
    reply_markup = InlineKeyboardMarkup(btn)
    await message.reply_photo(
        photo=PAYMENT_QR,
        caption=script.PREMIUM_PLAN_TEXT.format(OWNER_UPI_ID),
        reply_markup=reply_markup
    )
        
@Client.on_message(filters.command("my_plan"))
async def check_plans_cmd(client, message):
    user_id  = message.from_user.id
    if await db.has_premium_access(user_id):         
        remaining_time = await db.check_remaining_uasge(user_id)             
        expiry_time = remaining_time + datetime.datetime.now()
        await message.reply_text(f"**Your plans details are :\n\nRemaining Time : {remaining_time}\n\nExpirytime : {expiry_time}**")
    else:
        btn = [ 
            [InlineKeyboardButton("ɢᴇᴛ ғʀᴇᴇ ᴛʀᴀɪʟ ғᴏʀ 𝟻 ᴍɪɴᴜᴛᴇꜱ ☺️", callback_data="get_trail")],
            [InlineKeyboardButton("ʙᴜʏ sᴜʙsᴄʀɪᴘᴛɪᴏɴ : ʀᴇᴍᴏᴠᴇ ᴀᴅs", callback_data="buy_premium")],
            [InlineKeyboardButton("⚠️ ᴄʟᴏsᴇ / ᴅᴇʟᴇᴛᴇ ⚠️", callback_data="close_data")]
        ]
        reply_markup = InlineKeyboardMarkup(btn)
        m=await message.reply_sticker("CAACAgIAAxkBAAIBTGVjQbHuhOiboQsDm35brLGyLQ28AAJ-GgACglXYSXgCrotQHjibHgQ")         
        await message.reply_text(f"**😢 You Don't Have Any Premium Subscription.\n\n Check Out Our Premium /plans**",reply_markup=reply_markup)
        await asyncio.sleep(2)
        await m.delete()

@Client.on_message(filters.private & filters.command("set_pm_search"))
async def set_pm_search(client, message):
    user_id = message.from_user.id
    bot_id = client.me.id
    if user_id not in ADMINS:
        await message.delete()
        return
    try:
        option = (message.text).split(" ", 1)[1].lower()
    except IndexError:
        return await message.reply_text("<b>💔 Invalid option. Please send me 'on' or 'off' / 'true' or 'false' after the command.</b>")
    if option in ['on', 'true']:
        await db.update_pm_search_status(bot_id, enable=True)
        await message.reply_text("<b>✅️ ᴘᴍ ꜱᴇᴀʀᴄʜ ᴇɴᴀʙʟᴇᴅ ꜰʀᴏᴍ ɴᴏᴡ ᴜꜱᴇʀꜱ ᴀʙʟᴇ ᴛᴏ ꜱᴇᴀʀᴄʜ ᴍᴏᴠɪᴇ ɪɴ ʙᴏᴛ ᴘᴍ.</b>")
    elif option in ['off', 'false']:
        await db.update_pm_search_status(bot_id, enable=False)
        await message.reply_text("<b>❌️ ᴘᴍ ꜱᴇᴀʀᴄʜ ᴅɪꜱᴀʙʟᴇᴅ, ɴᴏ ᴏɴᴇ ᴜꜱᴇʀꜱ ᴀʙʟᴇ ᴛᴏ ꜱᴇᴀʀᴄʜ ᴍᴏᴠɪᴇ ɪɴ ʙᴏᴛ ᴘᴍ.</b>")
    else:
        await message.reply_text("<b>💔 Invalid option. Please send me 'on' or 'off' / 'true' or 'false' after the command.</b>")

@Client.on_message(filters.command('set_fsub'))
async def set_fsub(client, message):
    user_id = message.from_user.id
    if not user_id:
        return await message.reply("<b>You are Anonymous admin you can't use this command !</b>")
    chat_type = message.chat.type
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("Use this command in group.")      
    grp_id = message.chat.id
    title = message.chat.title
    if not await is_check_admin(client, grp_id, user_id):
        return await message.reply_text('You not admin in this group.')
    try:
        ids = message.text.split(" ", 1)[1]
        fsub_ids = list(map(int, ids.split()))
    except IndexError:
        return await message.reply_text("Command Incomplete!\n\nCan multiple channel add separate by spaces. Like: /set_fsub id1 id2 id3")
    except ValueError:
        return await message.reply_text('Make sure ids is integer.')        
    channels = "Channels:\n"
    for id in fsub_ids:
        try:
            chat = await client.get_chat(id)
        except Exception as e:
            return await message.reply_text(f"<code>{id}</code> is invalid!\nMake sure this bot admin in that channel.\n\nError - {e}")
        if chat.type != enums.ChatType.CHANNEL:
            return await message.reply_text(f"<code>{id}</code> is not channel.")
        channels += f'{chat.title}\n'
    await save_group_settings(grp_id, 'fsub', fsub_ids)
    await message.reply_text(f"Successfully set force channels for {title} to\n\n<code>{channels}</code>")

@Client.on_message(filters.command('remove_fsub'))
async def remove_fsub(client, message):
    grp_id = message.chat.id
    settings = await get_settings(int(grp_id))
    user_id = message.from_user.id
    chat_type = message.chat.type
    if not user_id:
        return await message.reply("<b>You are Anonymous admin you can't use this command !</b>")
    if chat_type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return await message.reply_text("Use this command in group.")
    if not await is_check_admin(client, grp_id, user_id):
        return await message.reply_text('You not admin in this group.')
    if not settings['fsub']:
        await query.answer("ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ᴄʜᴀɴɴᴇʟ...", show_alert=True)
        return
    await save_group_settings(grp_id, 'fsub', None)
    await message.reply_text("<b>Successfully removed your force channel id...</b>")
