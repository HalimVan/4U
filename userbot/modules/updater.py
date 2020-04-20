# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
# credits to @AvinashReddy3108
#
"""
This module updates the userbot based on upstream revision
"""

from os import remove, execle, path, environ
import asyncio
import sys

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from userbot import (CMD_HELP, HEROKU_API_KEY,
                     HEROKU_APP_NAME, UPSTREAM_REPO_URL, UPSTREAM_REPO_BRANCH)
from userbot.events import register

requirements_path = path.join(
    path.dirname(path.dirname(path.dirname(__file__))), 'requirements.txt')


async def gen_chlog(repo, diff):
    ch_log = ''
    d_form = "%d/%m/%y"
    for c in repo.iter_commits(diff):
        ch_log += f'•[{c.committed_datetime.strftime(d_form)}]: {c.summary} <{c.author}>\n'
    return ch_log


async def update_requirements():
    reqs = str(requirements_path)
    try:
        process = await asyncio.create_subprocess_shell(
            ' '.join([sys.executable, "-m", "pip", "install", "-r", reqs]),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        await process.communicate()
        return process.returncode
    except Exception as e:
        return repr(e)


async def deploy(event, repo, ups_rem, ac_br, txt):
    if HEROKU_API_KEY is not None:
        import heroku3
        heroku = heroku3.from_key(HEROKU_API_KEY)
        heroku_app = None
        heroku_applications = heroku.apps()
        if HEROKU_APP_NAME is None:
            await event.edit(
                '`[HEROKU]: Silakan mengatur` **HEROKU_APP_NAME** `variabel'
                'untuk dapat menyebarkan perubahan terbaru dari userbot.`'
            )
            repo.__del__()
            return
        for app in heroku_applications:
            if app.name == HEROKU_APP_NAME:
                heroku_app = app
                break
        if heroku_app is None:
            await event.edit(
                f'{txt}\n`Kredensial Heroku tidak valid untuk menyebarkan userbot dyno.`'
            )
            return repo.__del__()
        await event.edit('`[HEROKU]:'
                         '\nDyno Userbot sedang berlangsung, silakan tunggu...`'
                         )
        ups_rem.fetch(ac_br)
        repo.git.reset("--hard", "FETCH_HEAD")
        heroku_git_url = heroku_app.git_url.replace(
            "https://", "https://api:" + HEROKU_API_KEY + "@")
        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(heroku_git_url)
        else:
            remote = repo.create_remote("heroku", heroku_git_url)
        try:
            remote.push(refspec="HEAD:refs/heads/master", force=True)
        except GitCommandError as error:
            await event.edit(f'{txt}\n`berikut adalah error log:\n{error}`')
            return repo.__del__()
        await event.edit('`Berhasil Diperbarui!\n'
                         'Memulai ulang, mohon tunggu...`')
    else:
        await event.edit('`[HEROKU]:'
                         '\nTolong persiapkan.` **HEROKU_API_KEY** `variabel.`'
                         )
    return


async def update(event, repo, ups_rem, ac_br):
    try:
        ups_rem.pull(ac_br)
    except GitCommandError:
        repo.git.reset("--hard", "FETCH_HEAD")
    await update_requirements()
    await event.edit('`Berhasil Diperbarui!\n'
                     'Bot sedang memulai ulang... Tunggu sebentar !`')
    # Spin a new instance of bot
    args = [sys.executable, "-m", "userbot"]
    execle(sys.executable, *args, environ)
    return


@register(outgoing=True, pattern=r"^.up(?: |$)(n/?deploy)?")
async def upstream(event):
    "For .up command, check if the bot is up to date, update if specified"
    await event.edit("`Memeriksa pembaruan, silakan tunggu....`")
    conf = event.pattern_match.group(1)
    off_repo = UPSTREAM_REPO_URL
    force_update = False
    try:
        txt = "'UPS.. Pembaruan tidak dapat dilanjutkan karena "
        txt += "beberapa masalah terjadi`\n\n**LOGTRACE:**\n"
        repo = Repo()
    except NoSuchPathError as error:
        await event.edit(f'{txt}\n`direktori {error} tidak ditemukan`')
        return repo.__del__()
    except GitCommandError as error:
        await event.edit(f'{txt}\n`Kegagalan awal! {error}`')
        return repo.__del__()
    except InvalidGitRepositoryError as error:
        if conf is None:
            return await event.edit(
                f"`Sayangnya, direktori {error} sepertinya bukan repositori git."
                "\nTapi kita bisa memperbaikinya dengan paksa memperbarui userbot menggunakan .upn.`"
            )
        repo = Repo.init()
        origin = repo.create_remote('upstream', off_repo)
        origin.fetch()
        force_update = True
        repo.create_head('master', origin.refs.master)
        repo.heads.master.set_tracking_branch(origin.refs.master)
        repo.heads.master.checkout(True)

    ac_br = repo.active_branch.name
    if ac_br != UPSTREAM_REPO_BRANCH:
        await event.edit(
            '**[PEMBARUAN]:**\n'
            f'`Sepertinya Anda menggunakan cabang Anda sendiri Suai ({ac_br}). '
            'dalam hal ini, Pembaruan tidak dapat mengidentifikasi '
            'cabang mana yang akan digabung. '
            'silakan periksa untuk setiap cabang resmi`')
        return repo.__del__()
    try:
        repo.create_remote('upstream', off_repo)
    except BaseException:
        pass

    ups_rem = repo.remote('upstream')
    ups_rem.fetch(ac_br)

    changelog = await gen_chlog(repo, f'HEAD..upstream/{ac_br}')

    if changelog == '' and force_update is False:
        await event.edit(
            f'\n`USERBOT Anda`  ** ter-update **  `dengan`  **{UPSTREAM_REPO_BRANCH}**\n')
        return repo.__del__()

    if conf is None and force_update is False:
        changelog_str = f'**Pembaruan baru tersedia untuk [{ac_br}]:\n\nCHANGELOG:**\n`{changelog}`'
        if len(changelog_str) > 4096:
            await event.edit("`Changelog terlalu besar, lihat berkas untuk melihatnya.`")
            file = open("output.txt", "w+")
            file.write(changelog_str)
            file.close()
            await event.client.send_file(
                event.chat_id,
                "output.txt",
                reply_to=event.id,
            )
            remove("output.txt")
        else:
            await event.edit(changelog_str)
        return await event.respond('`ketik perintah ".upn/deploy" untuk memperbarui`')

    if force_update:
        await event.edit(
            '`Paksa sinkronisasi untuk kode userbot terakhir stabil, Mohon tunggu...`')
    else:
        await event.edit('`Memperbarui userbot, Mohon tunggu....`')
    if conf == "now":
        await update(event, repo, ups_rem, ac_br)
    elif conf == "deploy":
        await deploy(event, repo, ups_rem, ac_br, txt)
    return


CMD_HELP.update({
    'update':
    ">`.up`"
    "\nPenggunaan: memeriksa apakah repositori userbot utama memiliki pemutakhiran dan menunjukkan changelog bila demikian ."
    "\n\n>`.upn`"
    "\nid: Penggunaan: Perbarui userbot Anda, bila ada pembaruan di repositori userbot Anda."
    "\n\n>`.update deploy`"
    "\nPenggunaan: sebarkan userbot Anda, bila ada pembaruan di repositori userbot Anda."
})
