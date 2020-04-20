# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
""" Userbot module which contains afk-related commands """

from datetime import datetime
import time
from random import choice, randint
from asyncio import sleep

from telethon.events import StopPropagation

from userbot import (AFKREASON, COUNT_MSG, CMD_HELP, ISAFK, BOTLOG,
                     BOTLOG_CHATID, USERS, PM_AUTO_BAN)
from userbot.events import register

# ========================= CONSTANTS ============================
AFKSTR = [
    "Aku sedang sibuk sekarang. Silahkan bicara dalam tas dan ketika aku kembali Anda hanya bisa memberi saya tas!",
    "Aku pergi sekarang. Jika kau butuh sesuatu, tinggalkan pesan setelah bunyi bep:\n`beeeeeeepppp!`",
    "Kau merindukanku, lain kali bidik lebih baik.",
    "Aku akan kembali dalam beberapa menit dan jika tidak...,\n... tunggu lagi.",
    "Aku tidak di sini sekarang, jadi aku mungkin di tempat lain.",
    "Mawar berwarna merah, pentungan yang biru, tinggalkan pesan, dan aku akan menghubungimu kembali.",
    "Kadang-kadang hal-hal terbaik dalam hidup adalah layak menunggu...,\naku akan segera kembali .",
    "Aku akan segera kembali, jika aku tidak benar kembali, aku akan kembali nanti.",
    "Jika kau belum mengetahuinya,\naku tidak di sini.",
    "Halo, selamat datang di pesan saya, bagaimana mungkin saya mengabaikan Anda hari ini ?",
    "Aku pergi lebih dari 7 laut dan 7 negara,\n 7 perairan dan 7 benua,\n 7 gunung dan 7 bukit,\n 7 dataran dan 7 gundukan,\n 7 kolam renang dan 7 danau,\n 7 mata air dan 7 padang rumput,\n 7 kota dan 7 lingkungan,\n 7 blok dan 7 rumah...\n\nDimana bahkan pesan Anda tidak dapat menghubungi saya!",
    "Aku sedang jauh dari keyboard sekarang, tetapi jika Anda akan berteriak cukup keras di layar Anda, aku mungkin hanya mendengar Anda.",
    "Aku pergi ke arah sana\n---->",
    "Aku pergi lewat sini\n<----",
    "Silahkan tinggalkan pesan dan membuat saya merasa bahkan lebih penting.",
    "Saya tidak di sini jadi berhenti menulis kepada saya,\natau Anda akan menemukan diri Anda dengan layar penuh pesan Anda sendiri.",
    "Jika aku ada di sini,\nAku akan memberitahumu di mana aku berada.\n\nTapi aku tidak,\njadi tanyakan padaku ketika aku kembali...",
    "Aku pergi!\nAku tidak tahu kapan aku akan kembali!\nMudah-mudahan beberapa menit dari sekarang!",
    "Aku tidak ada sekarang jadi silakan tinggalkan nama, nomor, alamat dan aku akan tangkai anda nanti.",
    "Maaf, aku tidak di sini sekarang.\nJangan ragu untuk berbicara dengan userbot saya selama Anda suka.\nAku akan kembali kepada anda nanti.",
    "Saya yakin Anda mengharapkan balasan pesan dari saya:v",
    "Hidup ini begitu singkat, ada begitu banyak hal yang harus dilakukan...\nAku pergi melakukan salah satu dari mereka..",
    "Aku tidak di sini sekarang...\ntapi jika aku kembali...\n\napa yang anda anda perlukan?",
]

global USER_AFK  # pylint:disable=E0602
global afk_time  # pylint:disable=E0602
global afk_start
global afk_end
USER_AFK = {}
afk_time = None
afk_start = {}

# =================================================================
@register(outgoing=True, pattern="^.afk(?: |$)(.*)", disable_errors=True)
async def set_afk(afk_e):
    """ For .afk command, allows you to inform people that you are afk when they message you """
    message = afk_e.text
    string = afk_e.pattern_match.group(1)
    global ISAFK
    global AFKREASON
    global USER_AFK  # pylint:disable=E0602
    global afk_time  # pylint:disable=E0602
    global afk_start
    global afk_end
    global reason
    USER_AFK = {}
    afk_time = None
    afk_end = {}
    start_1 = datetime.now()
    afk_start = start_1.replace(microsecond=0)
    if string:
        AFKREASON = string
        await afk_e.edit(f"Pergi AFK!\
        \nKarena: `{string}`")
    else:
        await afk_e.edit("Pergi AFK!")
    if BOTLOG:
        await afk_e.client.send_message(BOTLOG_CHATID, "#AFK\nAnda pergi AFK!")
    ISAFK = True
    afk_time = datetime.now()  # pylint:disable=E0602
    raise StopPropagation


@register(outgoing=True)
async def type_afk_is_not_true(notafk):
    """ This sets your status as not afk automatically when you write something while being afk """
    global ISAFK
    global COUNT_MSG
    global USERS
    global AFKREASON
    global USER_AFK  # pylint:disable=E0602
    global afk_time  # pylint:disable=E0602
    global afk_start
    global afk_end
    back_alive = datetime.now()
    afk_end = back_alive.replace(microsecond=0)
    if ISAFK:
        ISAFK = False
        msg = await notafk.respond("Aku tidak lagi AFK.")
        time.sleep(3)
        await msg.delete()
        if BOTLOG:
            await notafk.client.send_message(
                BOTLOG_CHATID,
                "You've recieved " + str(COUNT_MSG) + " messages from " +
                str(len(USERS)) + " chats while you were away",
            )
            for i in USERS:
                name = await notafk.client.get_entity(i)
                name0 = str(name.first_name)
                await notafk.client.send_message(
                    BOTLOG_CHATID,
                    "[" + name0 + "](tg://user?id=" + str(i) + ")" +
                    " sent you " + "`" + str(USERS[i]) + " messages`",
                )
        COUNT_MSG = 0
        USERS = {}
        AFKREASON = None


@register(incoming=True, disable_edited=True)
async def mention_afk(mention):
    """ This function takes care of notifying the people who mention you that you are AFK."""
    global COUNT_MSG
    global USERS
    global ISAFK
    global USER_AFK  # pylint:disable=E0602
    global afk_time  # pylint:disable=E0602
    global afk_start
    global afk_end
    back_alivee = datetime.now()
    afk_end = back_alivee.replace(microsecond=0)
    afk_since = "a while ago"
    if mention.message.mentioned and not (await mention.get_sender()).bot:
        if ISAFK:
            now = datetime.now()
            datime_since_afk = now - afk_time  # pylint:disable=E0602
            time = float(datime_since_afk.seconds)
            days = time // (24 * 3600)
            time = time % (24 * 3600)
            hours = time // 3600
            time %= 3600
            minutes = time // 60
            time %= 60
            seconds = time
            if days == 1:
                afk_since = "Yesterday"
            elif days > 1:
                if days > 6:
                    date = now + \
                        datetime.timedelta(
                            days=-days, hours=-hours, minutes=-minutes)
                    afk_since = date.strftime("%A, %Y %B %m, %H:%I")
                else:
                    wday = now + datetime.timedelta(days=-days)
                    afk_since = wday.strftime('%A')
            elif hours > 1:
                afk_since = f"`{int(hours)} jam {int(minutes)} menit` yang lalu"
            elif minutes > 0:
                afk_since = f"`{int(minutes)} menit {int(seconds)} detik` yang lalu"
            else:
                afk_since = f"`{int(seconds)} detik` yang lalu"
            if mention.sender_id not in USERS:
                if AFKREASON:
                    await mention.reply(f"Aku pergi AFK sejak {afk_since}.\
                        \nKarena: `{AFKREASON}`")
                else:
                    await mention.reply(str(choice(AFKSTR)))
                USERS.update({mention.sender_id: 1})
                COUNT_MSG = COUNT_MSG + 1
            elif mention.sender_id in USERS:
                if USERS[mention.sender_id] % randint(2, 4) == 0:
                    if AFKREASON:
                        await mention.reply(f"Aku masih AFK sejak {afk_since}.\
                            \nKarena: `{AFKREASON}`")
                    else:
                        await mention.reply(str(choice(AFKSTR)))
                    USERS[mention.sender_id] = USERS[mention.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1
                else:
                    USERS[mention.sender_id] = USERS[mention.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1


@register(incoming=True, disable_errors=True)
async def afk_on_pm(sender):
    """ Function which informs people that you are AFK in PM """
    global ISAFK
    global USERS
    global COUNT_MSG
    global COUNT_MSG
    global USERS
    global ISAFK
    global USER_AFK  # pylint:disable=E0602
    global afk_time  # pylint:disable=E0602
    global afk_start
    global afk_end
    back_alivee = datetime.now()
    afk_end = back_alivee.replace(microsecond=0)
    afk_since = "a while ago"
    if sender.is_private and sender.sender_id != 777000 and not (
            await sender.get_sender()).bot:
        if PM_AUTO_BAN:
            try:
                from userbot.modules.sql_helper.pm_permit_sql import is_approved
                apprv = is_approved(sender.sender_id)
            except AttributeError:
                apprv = True
        else:
            apprv = True
        if apprv and ISAFK:
            now = datetime.now()
            datime_since_afk = now - afk_time  # pylint:disable=E0602
            time = float(datime_since_afk.seconds)
            days = time // (24 * 3600)
            time = time % (24 * 3600)
            hours = time // 3600
            time %= 3600
            minutes = time // 60
            time %= 60
            seconds = time
            if days == 1:
                afk_since = "Yesterday"
            elif days > 1:
                if days > 6:
                    date = now + \
                        datetime.timedelta(
                            days=-days, hours=-hours, minutes=-minutes)
                    afk_since = date.strftime("%A, %Y %B %m, %H:%I")
                else:
                    wday = now + datetime.timedelta(days=-days)
                    afk_since = wday.strftime('%A')
            elif hours > 1:
                afk_since = f"`{int(hours)} jam {int(minutes)} menit` yang lalu"
            elif minutes > 0:
                afk_since = f"`{int(minutes)} menit {int(seconds)} detik` yang lalu"
            else:
                afk_since = f"`{int(seconds)} detik` yang lalu"
            if sender.sender_id not in USERS:
                if AFKREASON:
                    await sender.reply(f"Aku pergi AFK
                                       f"\nKarena: `{AFKREASON}`"
                                       f"\nAFK SEJAK: `{afk_since}`")
                else:
                    await sender.reply(str(choice(AFKSTR)))
                USERS.update({sender.sender_id: 1})
                COUNT_MSG = COUNT_MSG + 1
            elif apprv and sender.sender_id in USERS:
                if USERS[sender.sender_id] % randint(2, 4) == 0:
                    if AFKREASON:
                        await sender.reply(f"Aku masih AFK sejak {afk_since}.\
                            \nKarena: `{AFKREASON}`"
                    else:
                        await sender.reply(str(choice(AFKSTR)))
                    USERS[sender.sender_id] = USERS[sender.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1
                else:
                    USERS[sender.sender_id] = USERS[sender.sender_id] + 1
                    COUNT_MSG = COUNT_MSG + 1


CMD_HELP.update({
    "afk":
    ".afk [Optional Reason]\
\nUsage: Membuat anda seperti afk.\nBalasan bagi siapa saja yang menandai anda / PM \
Anda mengatakan kepada mereka bahwa Anda AFK(karena).\n\nMatikan AFK ketika Anda mengetik apa pun, di mana saja.\
"
})
