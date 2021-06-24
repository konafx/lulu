import discord
from dispander import dispand, delete_dispand, regex_discord_message_url, regex_extra_url
import os
from typing import Optional
import re


def get_dispand_info(url: str) -> Optional[dict]:
    """
    メッセージリンクから情報を取得します。
    改変元：https://github.com/DiscordBotPortalJP/dispander/blob/f7a0f0592acd8a2912aa51fa10c09de4d8769490/dispander/module.py#L153-L165
    :param url:
    :return: Optional[dict]
    """
    dispand_url_match = re.match(regex_discord_message_url + regex_extra_url, url)
    if dispand_url_match is None:
        return None

    data = dispand_url_match.groupdict()
    return {
        'origin_author_id': int(data['base_author_id']),
        'operator_id': int(data['author_id']),
        'extra_messages': [int(_id) for _id in data['extra_messages'].split(',')] if data['extra_messages'] else []
    }


async def internal_delete_dispand(bot: discord.Client, message: discord.Message, operator_id: int):
    """
    改変元：https://github.com/DiscordBotPortalJP/dispander/blob/f7a0f0592acd8a2912aa51fa10c09de4d8769490/dispander/module.py#L63-L79
    :param bot:
    :param message: 削除したいメッセージ
    :param operator_id: 削除指示したやつのID
    """
    if message.author.id != bot.user.id:
        return

    embed = message.embeds[0]

    if embed.author is None:
        # author が設定されていない埋め込みメッセージは discord が展開した embed と仮定して削除する
        print("embed.author is None, delete")
        await message.delete()
        return

    if getattr(embed.author, 'url', None) is None:
        # author.url が設定されたいない埋め込みメッセージは discord が展開した embed と仮定して削除する
        print("embed.author.url is None, delete")
        await message.delete()
        return

    params = get_dispand_info(embed.author.url)
    if params is None:
        # params が取得できない埋め込みメッセージは discord が展開した embed (twitterなど) と仮定して削除する
        print("dispand info is None, delete")
        await message.delete()
        return

    if operator_id not in params.values():
        print(f"operator is invalid. {params=} {operator_id=}")
        return

    print("operator is valid")
    await message.delete()
    for message_id in params['extra_messages']:
        extra_message = await message.channel.fetch_message(message_id)
        if extra_message is not None:
            await extra_message.delete()


def main():
    intents = discord.Intents.none()
    intents.guild_messages = True
    intents.reactions = True
    # message.guild 取得に必要
    intents.guilds = True

    client = discord.Client(intents=intents)

    token = os.environ['DISCORD_BOT_TOKEN']

    @client.event
    async def on_message(message):
        if message.author.bot:
            return
        if message.reference is not None:
            """
            delete dispand message
            """
            if not message.content.startswith('del'):
                return

            m = message.reference.cached_message
            if m is None:
                channel = message.guild.get_channel(message.reference.channel_id)
                m = await channel.fetch_message(message.reference.message_id)

            print(m)
            if m is None:
                return
            if m.author.id != client.user.id:
                return

            await internal_delete_dispand(client, m, message.author.id)
        else:
            """
            dispand message
            """
            await dispand(message)

    @client.event
    async def on_raw_reaction_add(payload):
        await delete_dispand(client, payload=payload)

    print("running...")
    client.run(token)


if __name__ == '__main__':
    main()

