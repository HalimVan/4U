# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
# Port to UserBot by @MoveAngel

from datetime import datetime
from covid import Covid
from userbot import CMD_HELP
from userbot.events import register

@register(outgoing=True, pattern="^.covid (.*)")
async def corona(event):
    await event.edit("`Processing...`")
    country = event.pattern_match.group(1)
    covid = Covid()
    country_data = covid.get_status_by_country_name(country)
    if country_data:
        output_text =  f"`Dikonfirmasi : {country_data['confirmed']}`\n"
        output_text += f"`Aktif        : {country_data['active']}`\n"
        output_text += f"`Meninggal    : {country_data['deaths']}`\n"
        output_text += f"`Pulih.       : {country_data['recovered']}`\n"
        output_text += (
            "`Last update : "
            f"{datetime.utcfromtimestamp(country_data['last_update'] // 1000).strftime('%Y-%m-%d %H:%M:%S')}`\n"
        )
        output_text += f"Data yang disediakan oleh YusrilSyahruddin](https://www.instagram.com/yuskychan/?hl=id)"
    else:
        output_text = "Tulis nama negara dengan benar BANGSAT!"
    await event.edit(f"Corona Virus Info in {country}:\n\n{output_text}")


CMD_HELP.update({
        "covid": 
        ".covid <negara>"
        "\nPenggunaan: mendapatkan informasi tentang data covid-19 di negara Anday.\n"
    })
