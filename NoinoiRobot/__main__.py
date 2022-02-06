import importlib
import time
import re
from sys import argv
from typing import Optional

from NoinoiRobot import (
    ALLOW_EXCL,
    CERT_PATH,
    DONATION_LINK,
    LOGGER,
    OWNER_ID,
    PORT,
    SUPPORT_CHAT,
    TOKEN,
    URL,
    WEBHOOK,
    SUPPORT_CHAT,
    dispatcher,
    StartTime,
    telethn,
    pbot,
    updater,
)

# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from NoinoiRobot.queues import QUEUE
from pyrogram import Client, filters
from NoinoiRobot.modules import ALL_MODULES
from NoinoiRobot.modules.helper_funcs.chat_status import is_user_admin
from NoinoiRobot.modules.helper_funcs.misc import paginate_modules
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop, run_async
from telegram.utils.helpers import escape_markdown


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time

NOINOI_IMG = "https://telegra.ph/file/a439299736dc1fe3928e3.jpg"

PM_START_TEXT = """
**ɪ ᴀᴍ ɴᴏɪɴᴏɪ🌸🤖t** [ㅤ](https://telegra.ph/file/a439299736dc1fe3928e3.jpg)
️➖➖➖➖➖➖➖➖➖➖➖➖➖
**sᴜᴘᴇʀғᴀsᴛ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ 🌸. ғᴇᴇʟ ғʀᴇᴇ ᴛᴏ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘs!!**
️➖➖➖➖➖➖➖➖➖➖➖➖➖
☉ **ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ғᴏʀ ᴍᴏʀᴇ.**
"""

buttons = [
    [
        InlineKeyboardButton(text="Update", url="http://t.me/BAZIGARXD"),
        InlineKeyboardButton(text="Support", url="https://t.me/CFC_BOT_SUPPORT"),
    ],
    [
        InlineKeyboardButton(text="Help", callback_data="noi_"),
        InlineKeyboardButton(
            text="Noinoi", callback_data="noi_source"
        ),
    ],
    [
        
        InlineKeyboardButton(text="Aᴅᴅ ᴍᴇ ᴛᴏ ɢʀᴏᴜᴘ ", url="http://t.me/NOINOI_BOT?startgroup=true"),
    ],
]


HELP_STRINGS = """
**Main commands:**  [ㅤ](https://telegra.ph/file/a439299736dc1fe3928e3.jpg)
❂ /start: sᴛᴀʀᴛ ᴍᴇ ʏᴏᴜ ʜᴀᴠᴇ ᴘʀᴏʙᴀʙʟʏ ᴀʟʀᴇᴀᴅʏ ᴜsᴇᴅ ᴛʜɪs..
❂ /help: sᴇɴᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ɪ ᴡɪʟʟ ᴛᴇʟʟ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ᴍʏsᴇʟғ.

ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ᴇɪᴛʜᴇʀ ʙᴇ ᴜsᴇᴅ ᴇɪᴛʜᴇʀ / ᴏʀ  ! ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʀᴇᴘᴏʀᴛ ᴀɴʏ ʙᴜɢs ᴏʀ ɴᴇᴇᴅ ʜᴇʟᴘ ᴡɪᴛʜ sᴇᴛᴛɪɴɢ ᴜᴘ ʀᴇᴀᴄʜ ᴜs ᴀᴛ ʜᴇᴀʀ"""



DONATE_STRING = """ʜᴇʜᴇ ʏᴏᴜ ᴄᴀɴ ᴅᴏɴᴇᴛ ғʀᴏᴍ ʜᴇᴀʀ!
 [NOINOI](https://t.me/BAZIGARXD) ❤️
"""

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("NoinoiRobot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


@run_async
def test(update: Update, context: CallbackContext):
    # pprint(eval(str(update)))
    # update.effective_message.reply_text("Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("This person edited a message")
    print(update.effective_message)


@run_async
def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="help_back")]]
                    ),
                )

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            update.effective_message.reply_text(
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )
    else:
        update.effective_message.reply_photo(
            NOINOI_IMG, caption= "I'm awake already!\n<b>Haven't slept since:</b> <code>{}</code>".format(
                uptime
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Sᴜᴘᴘᴏʀᴛ", url="https://t.me/CFC_BOT_SUPPORT")]]
            ),
        )
        
def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


@run_async
def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "Here is the help for the *{}* module:\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="help_back")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass

## ///////////////////////////////////////////   N O I N O I   -   H E L P   -     S E T U P     ///////////////////////////////////////////////////

@run_async
def noi_about_callback(update, context):
    query = update.callback_query
    if query.data == "noi_":
        query.message.edit_text(
            text= " ❍ Hey i am Noinoi Robot and i am superfast music player & group managment bot.\n ❍ You can cheak my all commands by tap on below button.\n ❍ i make diff section for diffrent commands so you get easy to use our bot.\n ❍ Give me all admin rights in group i am trusted bot from CFC comunity.\n ❍ i have many featurs to use me and one of safe bot on telegram.\n ❍ i can play music on voice chat & many commands of group manager. \n\n ❍ Powed by @BAZIGARXD",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Basic", callback_data="noi_basic"
                        ),
                        
                        InlineKeyboardButton(
                            text="Admin", callback_data="noi_admin"
                        ),
                        InlineKeyboardButton(
                            text="Setup", callback_data="noi_setup"
                        ),
                        ],
                    [
                        InlineKeyboardButton(
                            text="Music", callback_data="noi_music"
                        ),
                        
                        InlineKeyboardButton(
                            text="Advance", callback_data="noi_advance"
                        ),
                        InlineKeyboardButton(
                            text="Extra", callback_data="noi_extra"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="Funs", callback_data="noi_funs"
                        ),
                        
                        InlineKeyboardButton(
                            text="All ", callback_data="help_back"
                        ),
                        InlineKeyboardButton(
                            text="Setting ", callback_data="noi_setting"
                        ),
                    ],
                    [InlineKeyboardButton(text="📍 Home", callback_data="noi_back")],
                ]
            ),
        )
    elif query.data == "noi_back":
        query.message.edit_text(
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=False,
        )

## ///////////////////////////////////////////   N O I N O I   -   B A S I C   -     S E T U P     ///////////////////////////////////////////////////
        
    elif query.data == "noi_basic":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗕𝗔𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ Hey this feature has many commands, & this feature is knnown as basic command.\n❍ this feature is also help you to manage your group \n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                    InlineKeyboardButton("Group", callback_data="noi_group"),
                    InlineKeyboardButton("Locks", callback_data="noi_lock"),
                    InlineKeyboardButton("Rules", callback_data="noi_rule"),
                    ],
                    [
                    InlineKeyboardButton("Welcome", callback_data="noi_welcome"),
                    InlineKeyboardButton("Filter", callback_data="noi_filter"),
                    InlineKeyboardButton("Disable", callback_data="noi_disable"),
                    ],
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_"),
                 
                 ]
                ]
            ),
        )
        
    elif query.data == "noi_group":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗚𝗥𝗢𝗨𝗣 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /setgtitle <text>: set group title."
            f"\n\n❍ /setgpic Reply to any image to set group photo."
            f"\n\n❍ /setdesc: Set group description."
            f"\n\n❍ /setsticker: Set group sticker. \n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",

            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_basic"),
                 
                 ]
                ]
            ),
        )
        
    elif query.data == "noi_lock":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗟𝗢𝗖𝗞𝗦 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ If anyone share links or media unwanted if you want to do lock your group then u can use this command."
            f"\n\n❍ /locktypes : Lists all possible locktypes."
            f"\n\n❍ /unlock : if you want unlock your group."
            f"\n\n❍ /lock : if you want to lock your group."
            f"\n\n❍ /locks : current list of locks in group. \n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",

            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_basic"),
                 
                 ]
                ]
            ),
        )
        
    elif query.data == "noi_rule":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗥𝗨𝗟𝗘𝗦 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍  /rules: get the rules for this chat."
            f"\n\n❍ /setrules <your rules here>: set the rules for this chat."
            f"\n\n❍ /clearrules: clear the rules for this chat.\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_basic"),
                 
                 ]
                ]
            ),
        )
        
    elif query.data == "noi_welcome":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /welcome <on/off>: enable/disable welcome."
            f"\n\n❍ /goodbye: same usage and args as /welcome."
            f"\n\n❍ /setwelcome <sometext>: set a custom welcome message."
            f"\n\n❍ /setgoodbye <sometext>: set a custom goodbye."
            f"\n\n❍ /resetwelcome: reset to the default welcome message."
            f"\n\n❍ /resetgoodbye: reset to the default goodbye message."
            f"\n\n❍ /welcomemutehelp: gives information about welcome mutes.."
            f"\n\n❍ /cleanservice <on/off: deletes telegrams welcome/left service messages."
            f"\n\n❍ /welcomehelp: view more formatting information for custom welcome/goodbye messages."
            f"\n\n❍ /cleanwelcome <on/off>: On new member, try to delete the previous welcome message to avoid spamming the chat.\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_basic"),
                 
                 ]
                ]
            ),
        )     
        
    elif query.data == "noi_filter":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗙𝗜𝗟𝗧𝗘𝗥𝗦 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /filters: List all active filters saved in the chat."
            f"\n\n❍ /stop <filter keyword>: Stop that filter.."
            f"\n\n❍ /removeallfilters: Remove all chat filters at once."
            f"\n\n❍ Check /markdownhelp to know more.\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_basic"),
                 
                 ]
                ]
            ),
        )     
        
    elif query.data == "noi_disable":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗗𝗜𝗦𝗔𝗕𝗟𝗘 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /cmds: check the current status of disabled commands."
            f"\n\n❍ /enable <cmd name>: enable that command."
            f"\n\n❍ /disable <cmd name>: disable that command."
            f"\n\n❍ /enablemodule <module name>: enable all commands in that module."
            f"\n\n❍ /disablemodule <module name>: disable all commands in that module."
            f"\n\n❍ /listcmds: list all possible toggleable commands.\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_basic"),
                 
                 ]
                ]
            ),
        )     
        
 # //////////////////////////////////////////  N O I   -   A D M I N   -    H E L P     ///////////////////////////////////////////////////////////////////////

    elif query.data == "noi_admin":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ Hey this feature has many commands, & this feature is knnown as admin command.\n❍ this feature is also help you to manage your group \n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                    InlineKeyboardButton("Admin", callback_data="noi_admins"),
                    InlineKeyboardButton("Ban", callback_data="noi_ban"),
                    InlineKeyboardButton("Mute", callback_data="noi_mute"),
                    ],
                    [
                    InlineKeyboardButton("Zombie", callback_data="noi_zombie"),
                    ],
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_"),
                 
                 ]
                ]
            ),
        )

    elif query.data == "noi_admins":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /admins: list of admins in the chat."
            f"\n\n❍ /pinned: to get the current pinned message."
            f"\n\n❍ /pin: silently pins the message replied to."
            f"\n\n❍ /unpin: unpins the currently pinned message."
            f"\n\n❍ /invitelink: gets invitelink."
            f"\n\n❍ /fullpromote: promotes the user replied to with full rights."
            f"\n\n❍ /demote: demotes the user replied to."
            f"\n\n❍ /admincache: force refresh the admins list."
            f"\n\n❍ /del: deletes the message you replied to."
            f"\n\n❍ /demote: demotes the user replied to."
            f"\n\n❍ /purge: deletes all messages between this and the replied to message.."
            f"\n\n❍ /demote: demotes the user replied to."
            f"\n\n❍ /title <title here>: sets a custom title for an admin that the bot promoted."
            f"\n\n❍ /promote: promotes the user replied to.\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_admin"),
                 
                 ]
                ]
            ),
        )    
        
    elif query.data == "noi_ban":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗕𝗔𝗡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /kickme: kicks the user who issued the command."
            f"\n\n❍ /ban <userhandle>: bans a user. (via handle, or reply)."
            f"\n\n❍ /sban <userhandle>: Silently ban a user. Deletes command, Replied message and doesn't reply. (via handle, or reply)."
            f"\n\n❍ /tban <userhandle> x(m/h/d): bans a user for x time. (via handle, or reply). m = minutes, h = hours, d = days."
            f"\n\n❍ /unban <userhandle>: unbans a user. (via handle, or reply)."
            f"\n\n❍ /kick <userhandle>: kicks a user out of the group, (via handle, or reply)\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_admin"),
                 
                 ]
                ]
            ),
        )     
        
    elif query.data == "noi_mute":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗧𝗘 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /mute <userhandle>: silences a user. Can also be used as a reply, muting the replied to user."
            f"\n\n❍ /tmute <userhandle> x(m/h/d): mutes a user for x time. (via handle, or reply). m = minutes, h = hours, d = days."
            f"\n\n❍ /unmute <userhandle>: unmutes a user. Can also be used as a reply, muting the replied to user.\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_admin"),
                 
                 ]
                ]
            ),
        )  
              
    elif query.data == "noi_zombie":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗭𝗢𝗠𝗕𝗜𝗘 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /zombies: searches deleted accounts."
            f"\n\n❍ /zombies clean: removes deleted accounts from the group."
            f"\n\n❍ /snipe <chatid> <string>: Make me send a message to a specific chat.\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_admin"),
                 
                 ]
                ]
            ),
        )  
        
 # //////////////////////////////////////////  N O I   -   A D M I N   -    H E L P     ///////////////////////////////////////////////////////////////////////


    elif query.data == "noi_promotes":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗦𝗨𝗗𝗢 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ Hey this feature has many commands, & this feature is knnown as promote command.\n❍ this feature is also help you to manage your group \n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                    InlineKeyboardButton("Full", callback_data="noi_full"),
                    InlineKeyboardButton("Half", callback_data="noi_half"),
                    ],
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_"),
                 
                 ]
                ]
            ),
        )

    elif query.data == "noi_full":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗙𝗨𝗟𝗟 𝗣𝗥𝗢𝗠𝗢𝗧𝗘 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /fullpromote : for promote with full rights in groups.\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_full"),
                 
                 ]
                ]
            ),
        )  

    elif query.data == "noi_half":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗚 𝗕𝗔𝗡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /halfpromote : for promote bot with limited rights.\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_half"),
                 
                 ]
                ]
            ),
        ) 

## ************************************************************************************************************************************************


    elif query.data == "noi_music":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ Hey this feature has many commands, & this feature is knnown as music command.\n❍ this feature is also help you to manage your group \n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                    InlineKeyboardButton("Music", callback_data="noi_musics"),
                    InlineKeyboardButton("Join", callback_data="noi_join"),
                    InlineKeyboardButton("Auth", callback_data="noi_auth"),
                    ],
                    [
                    InlineKeyboardButton("Blacklist", callback_data="noi_blacklist"),
                    InlineKeyboardButton("Ping", callback_data="noi_ping"),
                    InlineKeyboardButton("Lyrics", callback_data="noi_lyrics"),
                    ],
                    [
                    InlineKeyboardButton("<<", callback_data="noi_next"),
                    InlineKeyboardButton("↪ Back", callback_data="noi_"),
                    InlineKeyboardButton(">>", callback_data="noi_next"),
                    ],
                ]
            ),
        )

    elif query.data == "noi_next":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ Hey this feature has many commands, & this feature is knnown as music command.\n❍ this feature is also help you to manage your group \n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                    InlineKeyboardButton("Theame", callback_data="noi_theame"),
                    InlineKeyboardButton("Server", callback_data="noi_server"),
                    InlineKeyboardButton("Song", callback_data="noi_song"),
                    ],
                    [
                    InlineKeyboardButton("Speedtest", callback_data="noi_speed"),
                    InlineKeyboardButton("Stats", callback_data="noi_stats"),
                    InlineKeyboardButton("Assistant", callback_data="noi_assist"),
                    ],
                    [
                    InlineKeyboardButton("<<", callback_data="noi_music"),
                    InlineKeyboardButton("↪ Back", callback_data="noi_"),
                    InlineKeyboardButton(">>", callback_data="noi_music"),
                    ],
                ]
            ),
        )

        
    elif query.data == "noi_musics":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /play : for play music on voice chat."
            f"\n\n❍ /pause : for pause music on voice chat."
            f"\n\n❍ /resume : for resume music on voice chat."
            f"\n\n❍ /skip : for skip music on voice chat."
            f"\n\n❍ /mute : for mute music on voice chat."
            f"\n\n❍ /unmute : unmute play music on voice chat."
            f"\n\n❍ /end : for end music on voice chat.\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_music"),
                 
                 ]
                ]
            ),
        ) 

    elif query.data == "noi_join":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /join : for join the voice chat."
            f"\n\n❍ /leave : for leave the voice chat."
            f"\n\n❍ /leaveassistant : for leave assistant from voice chat.\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_music"),
                 
                 ]
                ]
            ),
        ) 

    elif query.data == "noi_auth":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /join : for join the voice chat."
            f"\n\n❍ /leave : for leave the voice chat."
            f"\n\n❍ /leaveassistant : for leave assistant from voice chat.\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_music"),
                 
                 ]
                ]
            ),
        ) 

    elif query.data == "noi_blacklist":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /chatbl : for blacklist any chat."
            f"\n\n❍ /charwl : for remove blacklist chats."
            f"\n\n❍ /blchats : for cheak black list chats.\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_music"),
                 
                 ]
                ]
            ),
        ) 

    elif query.data == "noi_ping":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /ping : for cheak bot working or dead.\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_music"),
                 
                 ]
                ]
            ),
        ) 
        
    elif query.data == "noi_lyrics":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /lyrics : for get song lyrics.\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_music"),
                 
                 ]
                ]
            ),
        )
        
    elif query.data == "noi_theame":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /theme : - Set a theme for thumbnails"
            f"\n\n❍ /settheame : - Set a theme for thumbnails.\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_next"),
                 
                 ]
                ]
            ),
        )
        
    elif query.data == "noi_server":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /logs : 100 logs line"
            f"\n\n❍ /vars : config vars from heroku"
            f"\n\n❍ /delvars : del any vars or env"
            f"\n\n❍ /setvars : set any var or update"
            f"\n\n❍ /usage : get dyno usage"
            f"\n\n❍ /update : update your bot"
            f"\n\n❍ /restart : restart your bot.\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_next"),
                 
                 ]
                ]
            ),
        )
        

    elif query.data == "noi_song":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /song : - for download song.\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_next"),
                 
                 ]
                ]
            ),
        )
        
    elif query.data == "noi_speed":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /speedtest : - for cheak speed of bot.\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_next"),
                 
                 ]
                ]
            ),
        )
        
    elif query.data == "noi_stats":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /stats : - for cheak stats of bot.\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_next"),
                 
                 ]
                ]
            ),
        )
        
    elif query.data == "noi_assist":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ /setassistant : - for set the bot assistant."
            f"\n\n❍ /changeassistant : - for change the bot assistant.\n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_next"),
                 
                 ]
                ]
            ),
        )
        
## ////////////////////////////////////////// A D V A N C E - C O M M A N D S  ///////////////////////////////////////////////////////////////////        
        
    elif query.data == "noi_advance":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗕𝗔𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ Hey this feature has many commands, & this feature is knnown as Advance command.\n❍ this feature is also help you to manage your group \n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                    InlineKeyboardButton("Logo", callback_data="noi_logo"),
                    InlineKeyboardButton("Channel", callback_data="noi_channel"),
                    InlineKeyboardButton("Search", callback_data="noi_search"),
                    ],
                    [
                    InlineKeyboardButton("Tagall", callback_data="noi_tagall"),
                    InlineKeyboardButton("Translate", callback_data="noi_translate"),
                    InlineKeyboardButton("Promote", callback_data="noi_promote"),
                    ],
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_"),
                 
                 ]
                ]
            ),
        )
        
    elif query.data == "noi_logo":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗩𝗜𝗗𝗘𝗢 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──**"
            f"\n❍ /logo [ name ] : for make name logo. \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="↪ Back", callback_data="noi_advance")]]
            ),
        )
        
    elif query.data == "noi_search":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗩𝗜𝗗𝗘𝗢 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──**"
            f"\n❍ /google <query>: Perform a google search."
            f"\n❍ /image <query>: Search Google for images and returns them."
            f"\n❍ /app <appname>: Searches for an app in Play Store and returns its details."
            f"\n❍ /reverse: Does a reverse image search of the media which it was replied to."
            f"\n❍ /gps <location>: Get gps location"
            f"\n❍ /country <country name>: Gathering info about given country"
            f"\n❍ /imdb <Movie name>: Get full info about a movie with imdb.com"
            f"\n❍ github <username>: Get information about a GitHub user. \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="↪ Back", callback_data="noi_advance")]]
            ),
        )
        
    elif query.data == "noi_tagall":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗩𝗜𝗗𝗘𝗢 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──**"
            f"\n❍ /mentionall : to mention all membbers in group."
            f"\n❍ /cancel : to stop mention \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="↪ Back", callback_data="noi_advance")]]
            ),
        )
        
    elif query.data == "noi_translate":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗩𝗜𝗗𝗘𝗢 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──**"
            f"\n❍ /tr : reply to any msg for translate."
            f"\n❍ /tts : for make message to voice message. \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="↪ Back", callback_data="noi_advance")]]
            ),
        )
        
## /////////////////////////////////////// E X T R A -  C O M M A N D S  ////////////////////////////////////////////////

    elif query.data == "noi_extra":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗕𝗔𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ Hey this feature has many commands, & this feature is knnown as Extra command.\n❍ this feature is also help you to manage your group \n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                    InlineKeyboardButton("Afk", callback_data="noi_afk"),
                    InlineKeyboardButton("Animation", callback_data="noi_animation"),
                    InlineKeyboardButton("Anime", callback_data="noi_anime"),
                    ],
                    [
                    InlineKeyboardButton("Couples", callback_data="noi_couples"),
                    InlineKeyboardButton("Telegraph", callback_data="noi_telegraph"),
                    InlineKeyboardButton("Fun", callback_data="noi_fun"),
                    ],
                    [
                    InlineKeyboardButton("Info", callback_data="noi_info"),
                    InlineKeyboardButton("Text", callback_data="noi_text"),
                    InlineKeyboardButton("Weather", callback_data="noi_weather"),
                    ],
                [
                    InlineKeyboardButton(text="↪ Back", callback_data="noi_"),
                 
                 ]
                ]
            ),
        )

    elif query.data == "noi_afk":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗔𝗞𝗙 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──**"
            f"\n❍ /afk [ reason ] : mark yourself as you afk."
            f"\n❍ /brb : dame as the afk command. \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="↪ Back", callback_data="noi_advance")]]
            ),
        )
        
    elif query.data == "noi_animation":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗔𝗡𝗜𝗠𝗔𝗧𝗜𝗢𝗡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──**"
            f"\n❍ /love : send love animatoion."
            f"\n❍ /bomb : send bomb animation."
            f"\n❍ /hack : send hack animation. \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="↪ Back", callback_data="noi_advance")]]
            ),
        )
        
    elif query.data == "noi_anime":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗔𝗡𝗜𝗠𝗘 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──**"
            f"\n❍ /anime <anime>: returns information about the."
            f"\n❍ /whatanime: returns source of anime when replied to photo or gif.."
            f"\n❍ /character <character>: returns information about the character."
            f"\n❍ /manga <manga>: returns information about the manga."
            f"\n❍ /user <user>: returns information about a MyAnimeList user."
            f"\n❍ /upcoming: returns a list of new anime in the upcoming seasons."
            f"\n❍ /airing <anime>: returns anime airing info."
            f"\n❍ /whatanime <anime>: reply to gif or photo."
            f"\n❍ /kaizoku <anime>: search an anime on."
            f"\n❍ /kayo <anime>: search an anime."
            f"\n❍ /animequotes: for anime quotes randomly as photos. \n❍ /quote: send quotes randomly as text \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="↪ Back", callback_data="noi_advance")]]
            ),
        )

    elif query.data == "noi_couples":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗖𝗢𝗨𝗣𝗟𝗘𝗦 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──**"
            f"\n❍ /couples : get couples of today. \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="↪ Back", callback_data="noi_advance")]]
            ),
        )        
        
    elif query.data == "noi_telegraph":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗧𝗘𝗟𝗘𝗚𝗥𝗔𝗣𝗛 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──**"
            f"\n❍ /tm : to convert any image to telegraph link."
            f"\n❍ /txt : any text change to telegraph link. \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="↪ Back", callback_data="noi_advance")]]
            ),
        )
        
    elif query.data == "noi_fun":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗙𝗨𝗡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──**"
            f"\n❍ /runs: reply a random string from an array of replies."
            f"\n❍ /slap: slap a user, or get slapped if not a reply."
            f"\n❍ /shrug: get shrug XD."
            f"\n❍ /table: get flip/unflip :v."
            f"\n❍ /decide: Randomly answers yes/no/maybe."
            f"\n❍ /toss: Tosses A coin."
            f"\n❍ /bluetext: check urself :V."
            f"\n❍ /roll: Roll a dice."
            f"\n❍ /rlg: Join ears,nose,mouth and create an emo."
            f"\n❍ /shout <keyword>: write anything you want to give loud shout."
            f"\n❍ /weebify <text>: returns a weebified text."
            f"\n❍ /sanitize: always use this before /pat or any contact."
            f"\n❍ /pat: pats a user, or get patted."
            f"\n❍ /8ball: predicts using 8ball method."
            f"\n❍ /animequotes: for anime quotes randomly as photos. \n❍ /quote: send quotes randomly as text \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="↪ Back", callback_data="noi_advance")]]
            ),
        )

    elif query.data == "noi_info":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗜𝗡𝗙𝗢 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──**"
            f"\n❍ /id: get the current group id. If used by replying to a message, gets that user's id.."
            f"\n❍ /gifid: reply to a gif to me to tell you its file ID."
            f"\n❍ /setme <text>: will set your info."
            f"\n❍ /me: will get your or another user's info."
            f"\n❍ /bio: will get your or another user's bio. This cannot be set by yourself.."
            f"\n❍ /setbio <text>: while replying, will save another user's bio."
            f"\n❍ /info: get information about a user."
            f"\n❍ /json: Get Detailed info about any message. \n❍ /quote: send quotes randomly as text \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="↪ Back", callback_data="noi_advance")]]
            ),
        )
        
        
    elif query.data == "noi_text":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗦𝗧𝗬𝗟𝗘 𝗧𝗘𝗫𝗧 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──**"
            f"\n❍ /weebify <text>: weebify your text"
            f"\n❍ /bubble <text>: bubble your text."
            f"\n❍ /fbubble <text>: bubble-filled your text."
            f"\n❍ /square <text>: square your text."
            f"\n❍ /fsquare <text>: square-filled your text."
            f"\n❍ /blue <text>: bluify your text!."
            f"\n❍ /latin <text>: latinify your text."
            f"\n❍ /lined <text>: lined your text. \n❍ /quote: send quotes randomly as text \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="↪ Back", callback_data="noi_advance")]]
            ),
        )
        
    elif query.data == "noi_weather":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗪𝗘𝗔𝗧𝗛𝗘𝗥 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──**"
            f"\n❍ /time <country code>: Gives information about a timezone"
            f"\n❍ /weather <city>: Get weather info in a particular place."
            f"\n❍ /wttr <city>: Advanced weather module."
            f"\n❍ /wttr moon: Get the current status of moon. \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="↪ Back", callback_data="noi_advance")]]
            ),
        )
        
            elif query.data == "noi_promote":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗧𝗘𝗟𝗘𝗚𝗥𝗔𝗣𝗛 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──**"
            f"\n\n❍ /fullpromote : to convert any image to telegraph link."
            f"\n\n❍ /halfpromote : any text change to telegraph link. \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="↪ Back", callback_data="noi_advance")]]
            ),
        )

## //////////////////////////////////////////////// F U N S C O M M A N D S  / /////////////////////////////////////////////////////////////

    elif query.data == "noi_funs":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗕𝗔𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ Hey this feature has many commands, & this feature is knnown as Extra command.\n❍ this feature is also help you to manage your group \n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                    InlineKeyboardButton("T & D", callback_data="noi_td"),
                    InlineKeyboardButton("Backup", callback_data="noi_backup"),
                    InlineKeyboardButton("Night", callback_data="noi_night"),
                    ],
                    [
                    InlineKeyboardButton("Chatbot", callback_data="noi_chatbot"),
                    InlineKeyboardButton("↪ Back", callback_data="noi_"),
                    InlineKeyboardButton("Sticker", callback_data="noi_sticker"),
                    ],
                ]
            ),
        )
        
    elif query.data == "noi_td":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗪𝗘𝗔𝗧𝗛𝗘𝗥 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──**"
            f"\n❍ /truth : this commands for fun."
            f"\n❍ /dare : this commands for fun. \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="↪ Back", callback_data="noi_advance")]]
            ),
        )
        
    elif query.data == "noi_backup":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗪𝗘𝗔𝗧𝗛𝗘𝗥 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──**"
            f"\n❍ /import: Reply to the backup file for the butler / NOINOI group to import as much as possible, making transfers very easy!  Note that files / photos cannot be imported due to telegram restrictions."
            f"\n❍ /export: Export group data, which will be exported are: rules, notes (documents, images, music, video, audio, voice, text, text buttons). \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="↪ Back", callback_data="noi_advance")]]
            ),
        )
        
    elif query.data == "noi_night":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗪𝗘𝗔𝗧𝗛𝗘𝗥 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──**"
            f"\n❍ /night [ on / off ] : for night mod on. \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="↪ Back", callback_data="noi_advance")]]
            ),
        )
        
    elif query.data == "noi_chatbot":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗪𝗘𝗔𝗧𝗛𝗘𝗥 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──**"
            f"\n❍ /chatbot [ on / off ] : for chatbot on. \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="↪ Back", callback_data="noi_advance")]]
            ),
        )
        

    elif query.data == "noi_text":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗦𝗧𝗬𝗟𝗘 𝗧𝗘𝗫𝗧 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──**"
            f"\n❍ /stickerid: reply to a sticker to me to tell you its file ID."
            f"\n❍ /getsticker: reply to a sticker to me to upload its raw PNG file."
            f"\n❍ /kang: reply to a sticker to add it to your pack."
            f"\n❍ /stickers: Find stickers for given term on combot sticker catalogue."
            f"\n❍ /addblsticker <sticker link>: Add the sticker trigger to the black list. Can be added via reply sticker."
            f"\n❍ /unblsticker <sticker link>: Remove triggers from blacklist. The same newline logic applies here, so you can delete multiple triggers at once!."
            f"\n❍ /rmblsticker <sticker link>: Same as above."
            f"\n❍ /blstickermode <delete/ban/tban/mute/tmute>: sets up a default action on what to do if users use blacklisted stickers."
            f"\n❍ /sticker link> can be https://t.me/addstickers/<sticker> or just <sticker> or reply to the sticker message. \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="↪ Back", callback_data="noi_advance")]]
            ),
        )
        
        
## //////////////////////////////////////////////////////// owner conmands ////////////////////////////////////////////////////////////////////



    elif query.data == "noi_setup":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗕𝗔𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──**"
            f"\n\n❍ First, add me to your group."
            f"\n\n❍ Then, promote me as administrator and give all permissions except Anonymous Admin."
            f"\n\n❍ After promoting me, type /reload in group to refresh the admin data."
            f"\n\n❍ Add **ASSISTANT** to your group or type /userbotjoin to invite her."
            f"\n\n❍ Turn on the video chat first before start to play music."
            f"\n\n❍ Sometimes, reloading the bot by using /reload command can help you to fix some problem.."
            f"\n\n❍ If the userbot not joined to video chat, make sure if the video chat already turned on, or type /userbotleave then type /join again."
            f"\n\n❍ for any querry join our @bazigarxd."
            f"\n\n❍ Hey this feature has many commands, & this feature is knnown as setup of noinoi.\n❍ this feature is also help you to manage your group \n\n 🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                    InlineKeyboardButton("Updates", url="https://t.me/bazigarxd"),
                    InlineKeyboardButton("Support", url="https://t.me/cfc_bot_support"),
                    ],
                    [
                    InlineKeyboardButton("↪ Back", callback_data="noi_"),
                    ],
                ]
            ),
        )

    elif query.data == "noi_setting":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗩𝗜𝗗𝗘𝗢 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──**"
            f"\n\n❍ /help - ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪꜱ ꜰᴏʀ ᴘʟᴀʏɪɴɢ ᴀ ᴠɪᴅᴇᴏ ɪɴ ᴜʀ ɢʀᴏᴜᴘꜱ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ. ᴜꜱᴇ ɪᴛ ʟɪᴋᴇ ᴀ ᴘʟᴀʏ ᴄᴏᴍᴍᴀɴᴅ."
            f"\n❍ /settings - ꜰᴏʀ ᴇɴᴅ ꜱᴛʀᴇᴀᴍɪɴɢ \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Back", callback_data="noi_")]]
            ),
        )



        
    elif query.data == "noi_admin":
        query.message.edit_text(
            text=f"**──𝗡𝗢𝗜𝗡𝗢𝗜 𝗩𝗜𝗗𝗘𝗢 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──**"
            f"\n\n» /vplay - ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪꜱ ꜰᴏʀ ᴘʟᴀʏɪɴɢ ᴀ ᴠɪᴅᴇᴏ ɪɴ ᴜʀ ɢʀᴏᴜᴘꜱ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ. ᴜꜱᴇ ɪᴛ ʟɪᴋᴇ ᴀ ᴘʟᴀʏ ᴄᴏᴍᴍᴀɴᴅ."
            f"\n» /vpause - ꜰᴏʀ ᴘᴀᴜꜱɪɴɢ ꜱᴛʀᴇᴀᴍɪɴɢ."
            f"\n» /vresume - ꜰᴏʀ ʀᴇꜱᴜᴍᴇ ꜱᴛʀᴇᴀᴍɪɴɢ."
            f"\n» /vskip - ꜰᴏʀ ꜱᴋɪᴘᴘɪɴɢ ᴄᴜʀʀᴇɴᴛ ꜱᴏɴɢ ᴀɴᴅ ᴘʟᴀʏɪɴɢ ɴᴇxᴛ ꜱᴏɴɢ."
            f"\n» /vmute - ꜰᴏʀ ᴍᴜᴛᴜɪɴɢ ᴀꜱꜱɪꜱᴛᴀɴᴛ ɪɴ ᴠᴄ."
            f"\n» /vunmute - ꜰᴏʀ ᴜɴᴍᴜᴛᴇ ᴀꜱꜱɪꜱᴛᴀɴᴛ ɪɴ ᴠᴄ."
            f"\n/» /vend - ꜰᴏʀ ᴇɴᴅ ꜱᴛʀᴇᴀᴍɪɴɢ \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Back", callback_data="noi_")]]
            ),
        )

    elif query.data == "noi_notes":
        query.message.edit_text(
            text=f"──𝗡𝗢𝗜𝗡𝗢𝗜 𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📘──\n\n"
            f"» /pause - ᴘᴀᴜꜱᴇ ᴛʜᴇ ꜱᴛʀᴇᴀᴍ"
            f"» /resume - ʀᴇꜱᴜᴍᴇ ᴛʜᴇ ꜱᴛʀᴇᴀᴍ"
            f"\n» /skip - ꜱᴡɪᴛᴄʜ ᴛᴏ ɴᴇxᴛ ꜱᴛʀᴇᴀᴍ"
            f"\n» /stop - ꜱᴛᴏᴘ ᴛʜᴇ ꜱᴛʀᴇᴀᴍɪɴɢ"
            f"\n» /vmute - ᴍᴜᴛᴇ ᴛʜᴇ ᴜꜱᴇʀʙᴏᴛ ᴏɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ"
            f"\n» /vunmute - ᴜɴᴍᴜᴛᴇ ᴛʜᴇ ᴜꜱᴇʀʙᴏᴛ ᴏɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ"
            f"\n» /reload - ʀᴇʟᴏᴀᴅ ʙᴏᴛ ᴀɴᴅ ʀᴇꜰʀᴇꜱʜ ᴛʜᴇ ᴀᴅᴍɪɴ ᴅᴀᴛᴀ"
            f"\n» /userbotjoin - ɪɴᴠɪᴛᴇ ᴛʜᴇ ᴜꜱᴇʀʙᴏᴛ ᴛᴏ ᴊᴏɪɴ ɢʀᴏᴜᴘ"
            f"\n» /userbotleave - ᴏʀᴅᴇʀ ᴜꜱᴇʀʙᴏᴛ ᴛᴏ ʟᴇᴀᴠᴇ ꜰʀᴏᴍ ɢʀᴏᴜᴘ\n\n\     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Back", callback_data="noi_")]]
            ),
        )
    elif query.data == "noi_support":
        query.message.edit_text(
            text=f"──𝗡𝗢𝗜𝗡𝗢𝗜 𝗦𝗨𝗗𝗢 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📌──\n"
                 f"\n/player - sʜᴏᴡ ᴛʜᴇ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ sᴛᴀᴛs"
                 f"\n/join - ɪɴᴠɪᴛᴇ ᴜsᴇʀʙᴏᴛ ᴛᴏ ᴊᴏɪɴ ɢʀᴏᴜᴘs"
                 f"\n/leave - ᴏʀᴅᴇʀ ᴛᴏ ᴜsᴇʀʙᴏᴛ ᴛᴏ ʟᴇᴀᴠᴇ ɢʀᴏᴜᴘ"
                 f"\n/auth - ᴀᴜᴛʜᴜʀɪᴢᴇ ᴜsᴇʀ ғᴏʀ ᴜsᴇ ᴍᴜsɪᴄ ʙᴏᴛ"
                 f"\n/unauth - ᴜɴ-ᴀᴜᴛʜᴜʀɪᴢᴇ ᴜsᴇʀ ғᴏʀ ᴜsᴇ ᴍᴜsɪᴄ ʙᴏᴛ"
                 f"\n/control - open the player settings panel"
                 f"\n/delcmd (on | off) - ᴏᴘᴇɴ ᴘʟᴀʏᴇʀ sᴇᴛᴛɪɴɢs"
                 f"\n/clean - remove all files from databace"
                 f"\n/maintenance - enable desable maintenus mod"
                 f"\n/sptest - enable and desable s p tets"
                 f"\n/music (on / off) - ᴇɴᴀʙʟᴇ | ᴅɪsᴀʙʟᴇ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="Back", callback_data="noi_"),
                 
                 ]
                ]
            ),
        )
    elif query.data == "noi_source":
        query.message.edit_text(
            text=f" 🧩 Hear the noinoi page.\n\n"
            f"\n\n❍ Hey welcome hear to noinoi's private page we are saying big thanks to you for using our bot."
            f"\n\n❍ Our bot is superfast with smooth music player with advance new featurs"
            f"\n\n❍ We remove no need space up plugins & noinoi is now is stable and easily deploy in 2 min."
            f"\n\n❍ Today i am sharing the source code of this bot with"
            f"\n\n 💡 Powerd by @BAZIGARXD",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [
                [
                     InlineKeyboardButton(text="Noinoi's repo 📂", url="https://github.com/hyko-xd/noinoirobot"),
                 ],
                 [
                    InlineKeyboardButton(text="Back", callback_data="noi_back"),
                 
                 ]
                ]
            ),
        )

    elif query.data == "noi_aselole":
        query.message.edit_text(
            text=f"𝗡𝗢𝗜𝗡𝗢𝗜 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦 ⚙️\n"
                 f"\n/filters - ғᴏʀ ᴄʜᴇᴀᴋ ғɪʟᴛᴇʀs ɪɴ ɢʀᴏᴜᴘ.\n"
                 f"\n/start - ғᴏʀ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ\n"
                 f"\n/help ғᴏʀ ᴏᴘᴇɴ ᴍᴀɴᴀɢᴇʀ sᴇᴛᴛɪɴɢ ᴏғ ʙᴏᴛ\n",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="Back", callback_data="noi_"),
                 
                 ]
                ]
            ),
        )

    elif query.data == "noi_asu":
        query.message.edit_text(
            text=f"──𝗡𝗢𝗜𝗡𝗢𝗜 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 🗂──\n"
                     f"\n» /song - ꜰᴏʀ ᴅᴏᴡɴʟᴏᴀᴅ ᴍᴜꜱɪᴄ ꜰʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ ꜱᴇʀᴠᴇʀ ɪɴ ᴍᴘ3 ꜰᴏʀᴍᴀᴛ"
                     f"\n» /video - ꜰᴏʀ ᴅᴏᴡɴʟᴏᴀᴅ ᴍᴜꜱɪᴄ ꜰʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ ꜱᴇʀᴠᴇʀ ɪɴ ᴠɪᴅᴇᴏ ꜰᴏʀᴍᴀᴛ \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Back", callback_data="noi_")]]
            ),
        )

    elif query.data == "noi_asi":
        query.message.edit_text(
            text=f"──𝗡𝗢𝗜𝗡𝗢𝗜 𝗦𝗧𝗔𝗧𝗨𝗦 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📒──\n"
                     f"\n» /alive - ꜰᴏʀ ᴄʜᴇᴄᴋɪɴɢ ᴀʟʟ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ʙᴏᴛ ꜱʏꜱᴛᴇᴍ."
                     f"\n» /ping - ꜰᴏʀ ᴘɪɴɢ.\n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Back", callback_data="noi_")]]
            ),
        )

    elif query.data == "noi_puqi":
        query.message.edit_text(
            text=f"──𝗡𝗢𝗜𝗡𝗢𝗜 𝗢𝗪𝗡𝗘𝗥 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 📚──\n"
                 f"\n» /gban - ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪꜱ ᴏɴʟʏ ꜰᴏʀ ᴏᴡɴᴇʀ ᴍᴀꜱᴛᴇʀ ᴄʀᴇᴀᴛᴏʀ ᴘᴀᴠᴀɴ ꜰᴏʀ ᴄʜᴇᴄᴋɪɴɢ ʙᴏᴛ ᴘʀᴏᴄᴇꜱꜱᴏʀ."
                 f"\n» /broadcast - ғᴏʀ ʙʀᴏᴀᴅᴄᴀsᴛ ᴍᴇssᴀɢᴇ ɪɴ ɢʀᴏᴜᴘs ᴀs ᴡᴇʟʟ ᴀs ᴜsᴇʀs."
                 f"\n» /addsudo - add sudo direct \n\n     🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                  [
                     InlineKeyboardButton(text="Back", callback_data="noi_"),
                  ]
                ]
            ),
        )

    elif query.data == "noi_angjay":
        query.message.edit_text(
            text=f"──𝗡𝗢𝗜𝗡𝗢𝗜 𝗕𝗔𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 📁──\n"
                 f"\n» /play [ꜱᴏɴɢ ɴᴀᴍᴇ/ʟɪɴᴋ] - ᴘʟᴀʏ ᴍᴜꜱɪᴄ ᴏɴ ᴠɪᴅᴇᴏ ᴄʜᴀᴛ" 
                 f"\n» /vplay    [ᴠɪᴅᴇᴏ ɴᴀᴍᴇ/ʟɪɴᴋ] - ᴘʟᴀʏ ᴠɪᴅᴇᴏ ᴏɴ ᴠɪᴅᴇᴏ ᴄʜᴀᴛ"
                 f"\n» /vstream - ᴘʟᴀʏ ʟɪᴠᴇ ᴠɪᴅᴇᴏ ꜰʀᴏᴍ ʏᴛ ʟɪᴠᴇ/ᴍ3ᴜ8"
                 f"\n» /playlist - ꜱʜᴏᴡ ʏᴏᴜ ᴛʜᴇ ᴘʟᴀʏʟɪꜱᴛ"
                 f"\n» /video [Qᴜᴇʀʏ] - ᴅᴏᴡɴʟᴏᴀᴅ ᴠɪᴅᴇᴏ ꜰʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ"
                 f"\n» /song [Qᴜᴇʀʏ] - ᴅᴏᴡɴʟᴏᴀᴅ ꜱᴏɴɢ ꜰʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ"
                 f"\n» /lyrics [Qᴜᴇʀʏ] - ꜱᴄʀᴀᴘ ᴛʜᴇ ꜱᴏɴɢ ʟʏʀɪᴄ"
                 f"\n» /search [Qᴜᴇʀʏ] - ꜱᴇᴀʀᴄʜ ᴀ ʏᴏᴜᴛᴜʙᴇ ᴠɪᴅᴇᴏ ʟɪɴᴋ"
                 f"\n» /ping - ꜱʜᴏᴡ ᴛʜᴇ ʙᴏᴛ ᴘɪɴɢ ꜱᴛᴀᴛᴜꜱ"
                 f"\n» /alive - ꜱʜᴏᴡ ᴛʜᴇ ʙᴏᴛ ᴀʟɪᴠᴇ ɪɴꜰᴏ [ɪɴ ɢʀᴏᴜᴘ] \n\n      🌸 𝗣𝗢𝗪𝗘𝗗 𝗕𝗬 𝗡𝗢𝗜𝗡𝗢𝗜 𝗠𝗨𝗦𝗜𝗖 𝗣𝗟𝗔𝗬𝗘𝗥",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                  [
                     InlineKeyboardButton(text="Back", callback_data="noi_"),
                  ]
                ]
            ),
        )   

@run_async
def Source_about_callback(update, context):
    query = update.callback_query
    if query.data == "source_":
        query.message.edit_text(
            text=""" Hi.. ɪ'ᴀᴍ noinoi*
                 \nHere is the [sᴏᴜʀᴄᴇ📂](https://github.com/hyko-xd/noinoirobot) .""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="Updates ✨", url="https://t.me/bazigarxd")
                 ]
                ]
            ),
        )
    elif query.data == "source_back":
        query.message.edit_text(
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=False,
        )

@run_async
def Source_about_callback(update, context):
    query = update.callback_query
    if query.data == "source_":
        query.message.edit_text(
            text=""" Hi.. ɪ'ᴀᴍ noinoi*
                 \nHere is the [sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ](https://github.com/hyko-xd/noinoirobot) .""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                 [
                    InlineKeyboardButton(text="Updates 📍", url="https://t.me/bazigarxd")
                 ]
                ]
            ),
        )
    elif query.data == "source_back":
        query.message.edit_text(
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
                disable_web_page_preview=False,
        )
              

@run_async
def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"Contact me in PM to get help of {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Help",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_text(
            "💡 Hear all noinoi commands menu is opend you can cheak the following menu bar click on buttons.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                     InlineKeyboardButton(text=" Menu ⚙", callback_data="noi_"),
                 ],
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Here is the available help for the *{}* module:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="ʙᴀᴄᴋ", callback_data="help_back")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Sepertinya tidak ada pengaturan khusus pengguna yang tersedia :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )


@run_async
def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Back",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


@run_async
def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Settings",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "Click here to check your settings."

    else:
        send_settings(chat.id, user.id, True)


@run_async
def donate(update: Update, context: CallbackContext):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            DONATE_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
        )

        if OWNER_ID != 1963422158 and DONATION_LINK:
            update.effective_message.reply_text(
                "You can also donate to the person currently running me "
                "[here]({})".format(DONATION_LINK),
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        try:
            bot.send_message(
                user.id,
                DONATE_STRING,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

            update.effective_message.reply_text(
                "I've PM'ed you about donating to my creator!"
            )
        except Unauthorized:
            update.effective_message.reply_text(
                "Contact me in PM first to get donation information."
            )


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop


def main():

    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.sendMessage(f"@{SUPPORT_CHAT}", "I Aᴍ Aʟɪᴠᴇ 🔥")
        except Unauthorized:
            LOGGER.warning(
                "Bot isnt able to send message to support_chat, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)

    test_handler = CommandHandler("test", test)
    start_handler = CommandHandler("start", start)

    help_handler = CommandHandler("help", get_help)
    help_callback_handler = CallbackQueryHandler(help_button, pattern=r"help_.*")

    settings_handler = CommandHandler("settings", get_settings)
    settings_callback_handler = CallbackQueryHandler(settings_button, pattern=r"stngs_")

    about_callback_handler = CallbackQueryHandler(noi_about_callback, pattern=r"noi_")
    source_callback_handler = CallbackQueryHandler(Source_about_callback, pattern=r"source_")

    donate_handler = CommandHandler("donate", donate)
    migrate_handler = MessageHandler(Filters.status_update.migrate, migrate_chats)

    # dispatcher.add_handler(test_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(about_callback_handler)
    dispatcher.add_handler(source_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(donate_handler)

    dispatcher.add_error_handler(error_callback)

    if WEBHOOK:
        LOGGER.info("Using webhooks.")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)

        if CERT_PATH:
            updater.bot.set_webhook(url=URL + TOKEN, certificate=open(CERT_PATH, "rb"))
        else:
            updater.bot.set_webhook(url=URL + TOKEN)

    else:
        LOGGER.info("Using long polling.")
        updater.start_polling(timeout=15, read_latency=4, clean=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == "__main__":
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    pbot.start()
    main()