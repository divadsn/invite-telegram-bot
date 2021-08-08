from datetime import datetime, timedelta
from urllib.parse import quote_plus

from invitebot import logger, database as db, OWNER_ID, MAX_INVITES_PER_USER, EXPIRY_HOURS
from invitebot.database import query_invites_for_user
from invitebot.utils import extract_status_change, get_sender_name

from telegram import Update, User, Bot, Chat, ChatInviteLink, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackContext, CommandHandler, ChatMemberHandler, Filters
from telegram.error import TelegramError
from telegram.utils import helpers


class InviteBot:

    updater: Updater
    me: User

    def __init__(self, bot_token: str):
        # Create the Updater and pass it your bot's token.
        self.updater = Updater(bot_token)

        # Get the dispatcher to register handlers
        dispatcher = self.updater.dispatcher

        # Register commands
        dispatcher.add_handler(CommandHandler("help", self.help_command, filters=~Filters.update.edited_message))
        dispatcher.add_handler(CommandHandler("start", self.start_command, filters=~Filters.update.edited_message))
        dispatcher.add_handler(CommandHandler("invite", self.invite_command, filters=~Filters.update.edited_message))
        dispatcher.add_handler(CommandHandler("my_invites", self.my_invites_command, filters=~Filters.update.edited_message))
        dispatcher.add_handler(CommandHandler("check_invite", self.check_invite_command, filters=~Filters.update.edited_message))

        # Handle members joining/leaving chats.
        dispatcher.add_handler(ChatMemberHandler(self.new_chat_member, ChatMemberHandler.CHAT_MEMBER))

        # Create all tables in the database
        db.create_tables()

    def start(self):
        # Start the Bot
        # We pass 'allowed_updates' handle *all* updates including `chat_member` updates
        # To reset this, simply pass `allowed_updates=[]`
        self.updater.start_polling(allowed_updates=Update.ALL_TYPES)

        # Notify that the bot is running.
        self.me = self.updater.bot.get_me()
        logger.info("Bot started!")

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()

    def new_chat_member(self, update: Update, context: CallbackContext) -> None:
        print("Kek")

    def help_command(self, update: Update, context: CallbackContext) -> None:
        pass

    def start_command(self, update: Update, context: CallbackContext) -> None:
        # send welcome message if no args provided from deep linking
        if not context.args or update.effective_chat.type != Chat.PRIVATE:
            update.effective_message.reply_text(
                text=(
                    f"Hey, I'm *{self.me.full_name}*, yet another Telegram bot for managing group invite links.\n\n"
                    f"To get started, use /invite in a group chat."
                ),
                parse_mode=ParseMode.MARKDOWN
            )
            return

        bot: Bot = self.updater.bot  # fix missing typing

        try:
            chat_id = int(context.args[0])
        except ValueError:
            update.effective_message.reply_text("What am I supposed to do with this?!")
            return

        # check if the limit has been exceeded for this chat
        if query_invites_for_user(chat_id, update.effective_user.id).count() >= MAX_INVITES_PER_USER and update.effective_user.id != OWNER_ID:
            update.effective_message.reply_text(
                text=(
                    f"You've used your limit of *{MAX_INVITES_PER_USER} invite links*, "
                    f"use up the previous ones before you create another one!"
                ),
                parse_mode=ParseMode.MARKDOWN
            )
            return

        create_date = datetime.utcnow().replace(microsecond=0)
        expire_date = create_date + timedelta(hours=EXPIRY_HOURS)

        try:
            chat_invite: ChatInviteLink = bot.create_chat_invite_link(
                chat_id=chat_id,
                expire_date=expire_date,
                member_limit=1
            )
        except TelegramError as e:
            update.effective_message.reply_text(text=f"*{e.message}!*", parse_mode=ParseMode.MARKDOWN)
            return

        # add new entry to database
        invite = db.Invite(
            chat_id=chat_id,
            link=chat_invite.invite_link,
            from_id=update.effective_user.id,
            from_name=update.effective_user.full_name,
            create_date=create_date,
            expire_date=chat_invite.expire_date
        )

        db.session.add(invite)
        db.session.commit()

        logger.info(f"User {get_sender_name(update.effective_user)} ({update.effective_user.id}) created a new invite link for chat ID {chat_id}")

        update.effective_message.reply_text(
            text=(
                f"A new invite link has been created!\n\n"
                f"{helpers.escape_markdown(chat_invite.invite_link)}\n\n"
                f"This link is valid for *{EXPIRY_HOURS} hours* until *{invite.expire_date:%Y-%m-%d %H:%M:%S} UTC* and limited to single use. "
                f"Remember, you can only have *{MAX_INVITES_PER_USER} unused* invite links at a time!"
            ),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup.from_button(
                InlineKeyboardButton(
                    text="Share invite link",
                    url=f"https://t.me/share/url?url={quote_plus(chat_invite.invite_link)}"
                )
            )
        )

    def invite_command(self, update: Update, context: CallbackContext) -> None:
        # check if message was sent in PM
        if update.effective_chat.type == Chat.PRIVATE:
            update.effective_message.reply_text(
                text=(
                    f"You cannot use this command here!\n\n"
                    f"To get started, use /invite in a group chat."
                ),
                parse_mode=ParseMode.MARKDOWN
            )
            return

        update.effective_message.reply_text(
            text="Click the button below to get started:",
            reply_markup=InlineKeyboardMarkup.from_button(
                InlineKeyboardButton(
                    text="Create a new invite link!",
                    url=helpers.create_deep_linked_url(self.me.username, str(update.effective_message.chat_id))
                )
            )
        )

    def my_invites_command(self, update: Update, context: CallbackContext) -> None:
        pass

    def check_invite_command(self, update: Update, context: CallbackContext) -> None:
        pass
