strings = {
    'sending1': "Sending code",
    'sending2': "Sending OTP request 📲",
    'ask_pass': "Now send me your 2 factor password 🔏",
    'ask_phone': "Share contact 📞 using the button to continue",
    'wrong_phone': "This isn't your phone 📵",
    'ask_code': "Please enter the OTP you recived from [Telegram](tg://user?id=777000):\n",
    'ask_ok': "Is this correct?: ",
    'need_login': "U have to /login again or /add_session before using ❕",
    'session_invalid': "The session is invalid or expired ‼️. please /login again or /add_session",
    'msg_404': "Target message not found 🔍❌",
    'code_invalid': "The OTP is invalid ❌",
    'pass_invalid': "The 2 factor password you entered is invalid ❌",
    'howto_add_session': "You can add the string session (telethon) using below syntax\n/add_session <your_string_session>",
    'login_success': "The login was successful ✅",
    'hello': "Hello 👋, I can download restricted content by logging into your account\nClick /help to know me and how to use me",
    'str_session_ok': "The string session is valid and successfully added ✅",
    'checking_str_session': "Validating the String Session ⏳",
    'logged_out': "Logged out successfully ☑️",
    'logout_sure': "Are you sure you want to log out?",
    'not_logged_out': "Logout cancelled!",
    'help': "🔐 __AUTHORIZATION__\nThis bot requires to access your account by /login into it. This is because we can't access your chats in other ways.\nYou have to share your contact and provide the OTP for logging in (in case of 2-factor authentication is active, you have to provide your password too)\n\n📝 __HOW TO USE__\n1. if you can copy the link for the required message, then you can copy it and send to me\n\n2. in case you can't get link, you have to send me the chat_id and the message_id required using following syntax:\n    <chat_id>.<message_id>\n\n3. if you don't have above, then you can run /activate command. it gives you 60 seconds ⏰ to navigate to the chat you want and reply `/dl` to the message for saving it 👍\n\nthats all\nhave fun 👊\n\nPrivacy policy: /privacy_policy",
    'privacy_policy': "⚠️ Warning ⚠️\nAll the media downloaded are obtained from your account. we don't care what you upload, and also we don't log them.\nYou solely bear all the consequenses after the /logout you need to check in Telegram Settings>Devices if extra session is active remove it..It Was Generated By you\nDont use Bot Frequently Coz Telegram Watch You How Fair you Do Give some rest to the bot otherwise your acount may got banned🚫",
    'timeout_start': "You got 60 seconds ⏰ to find the message you want and reply to it with `{}`\nhurry up ⏳",
    'timed_out': "time's up ⏳",
    'not_is_reply': "You need to send this as a reply",
    'dl_sent': "task added to bot",
    'already_logged_in': "You are already logged in.\nIf you want to login again, /logout to proceed.",
    'settings_home': "Customize settings ⚙️",
    'ask_new_dlcmd': "Send new download command ✍️",
    'ask_new_dlmsg': "Send new download message ✍️",
    'ask_new_dltime': "Send a delay ⏰ before deleting status message ✍️\nonly 0-5 in seconds\nor send 999 to not delete",
    'dlcmd_saved': "New download command saved successfully ✅",
    'dlmsg_saved': "New download command saved successfully ✅",
    'non_match_pattern': "The text dosen't match the requested format ☝️\nplease retry",
    'already_activated': "There's an already running instance, no need to activate 👍",
    'about':"I am SaveRestrictContent Bot\nPlatform : Render\nDev :[💥TRUMBOTS💥](https://t.me/movie_time_botonly)\nVersion :V1.0§ Beta"
}
direct_reply = {
    '/tb': strings['hello'],
    '/help': strings['help'],
    '/add_session': strings['howto_add_session'],
    '/privacy_policy': strings['privacy_policy'],
}
