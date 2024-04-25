import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from AnonXMusic import YouTube, app
from AnonXMusic.core.call import Anony
from AnonXMusic.misc import SUDOERS, db
from AnonXMusic.utils.database import (
    get_active_chats,
    get_lang,
    get_upvote_count,
    is_active_chat,
    is_music_playing,
    is_nonadmin_chat,
    music_off,
    music_on,
    set_loop,
)
from AnonXMusic.utils.decorators.language import languageCB
from AnonXMusic.utils.formatters import seconds_to_min
from AnonXMusic.utils.inline import close_markup, stream_markup, stream_markup_timer
from AnonXMusic.utils.thumbnails import get_thumb
from config import (
    BANNED_USERS,
    SUPPORT_CHAT,
    SOUNCLOUD_IMG_URL,
    STREAM_IMG_URL,
    TELEGRAM_AUDIO_URL,
    TELEGRAM_VIDEO_URL,
    adminlist,
    confirmer,
    votemode,
)

# تعريف العميل
app = Client("message.from_user.mention")

# عند بدء المحادثة الصوتية
@app.on_raw_update()
async def on_raw_update(client, update):
    # التحقق مما إذا كان التحديث يشير إلى بداية أو نهاية المحادثة الصوتية
    if isinstance(update, types.UpdateGroupCall):
        if isinstance(update.call, types.GroupCallDiscarded):
            # بداية المحادثة الصوتية
            print("↢ تم بدء المحادثة الصوتية..⚘")
        elif isinstance(update.call, types.GroupCallDiscarded):
            # نهاية المحادثة الصوتية
            print("- تم إنهاء مكالمة")

# ابدأ العميل
app.start()


checker = {}
upvoters = {}


@app.on_callback_query(filters.regex("ADMIN") & ~BANNED_USERS)
@languageCB
async def del_back_playlist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    command, chat = callback_request.split("|")
    if "_" in str(chat):
        bet = chat.split("_")
        chat = bet[0]
        counter = bet[1]
    chat_id = int(chat)
    if not await is_active_chat(chat_id):
        return await CallbackQuery.answer(_["general_5"], show_alert=True)
    mention = CallbackQuery.from_user.mention
    if command == "UpVote":
        if chat_id not in votemode:
            votemode[chat_id] = {}
        if chat_id not in upvoters:
            upvoters[chat_id] = {}

        voters = (upvoters[chat_id]).get(CallbackQuery.message.id)
        if not voters:
            upvoters[chat_id][CallbackQuery.message.id] = []

        vote = (votemode[chat_id]).get(CallbackQuery.message.id)
        if not vote:
            votemode[chat_id][CallbackQuery.message.id] = 0

        if CallbackQuery.from_user.id in upvoters[chat_id][CallbackQuery.message.id]:
            (upvoters[chat_id][CallbackQuery.message.id]).remove(
                CallbackQuery.from_user.id
            )
            votemode[chat_id][CallbackQuery.message.id] -= 1
        else:
            (upvoters[chat_id][CallbackQuery.message.id]).append(
                CallbackQuery.from_user.id
            )
            votemode[chat_id][CallbackQuery.message.id] += 1
        upvote = await get_upvote_count(chat_id)
        get_upvotes = int(votemode[chat_id][CallbackQuery.message.id])
        if get_upvotes >= upvote:
            votemode[chat_id][CallbackQuery.message.id] = upvote
            try:
                exists = confirmer[chat_id][CallbackQuery.message.id]
                current = db[chat_id][0]
            except:
                return await CallbackQuery.edit_message_text(f"ғᴀɪʟᴇᴅ.")
            try:
                if current["vidid"] != exists["vidid"]:
                    return await CallbackQuery.edit_message.text(_["admin_35"])
                if current["file"] != exists["file"]:
                    return await CallbackQuery.edit_message.text(_["admin_35"])
            except:
                return await CallbackQuery.edit_message_text(_["admin_36"])
            try:
                await CallbackQuery.edit_message_text(_["admin_37"].format(upvote))
            except:
                pass
            command = counter
            mention = "ᴜᴘᴠᴏᴛᴇs"
        else:
            if (
                CallbackQuery.from_user.id
                in upvoters[chat_id][CallbackQuery.message.id]
            ):
