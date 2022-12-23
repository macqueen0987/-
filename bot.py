import discord
import interactions
from interactions.ext.tasks import IntervalTrigger, create_task
from interactions.ext.persistence import PersistentCustomID
from koreanbots.integrations.discord import DiscordpyKoreanbots

import time
from random import randint
import importlib
import os
import asyncio
from pprint import pprint
import requests
from json import loads
import json
from datetime import datetime, timedelta, timezone
import re
import base64

import var
from var import db_conn, db_disconn, db_query, dumps
import convert_time
import reaction_proc
from interact import send_to, delete_to, add_reaction_to, clear_reaction_of


cnt = 15
var.init()
party_emojis = var.party_emoji+var.wait_emoji+var.delete_emoji+var.start_emoji+var.complete_emoji
var.init()
days = ["일", "월", "화", "수", "목", "금", "토"]
start = 0
# mention_author = False
# allowed_mentions = discord.AllowedMentions.none()

client = interactions.Client(token=var.token)
client.load("interactions.ext.files")
client.load("interactions.ext.persistence", cipher_key=var.cipher_key)
var.client = client

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
var.bot = bot


def main():
    var.init()
    def convert(time):
        day = time // (24 * 3600)
        time = time % (24 * 3600)
        hour = time // 3600
        time %= 3600
        minutes = time // 60
        time %= 60
        seconds = time
        temp = ''
        if day != 0: temp += "%d일 " % day
        if hour != 0: temp += "%d시간 " % hour
        if minutes != 0: temp += "%d분 " % minutes
        if seconds != 0: temp += "%d초" % seconds
        return temp

    async def stringToBase64(s):
        return str(base64.b64encode(s.encode('EUC-KR')))[1:]

    async def base64ToString(b):
        return base64.b64decode(b).decode('EUC-KR')

    async def find_voice(guild_id, author_id):
        voice_channels = bot.get_guild(guild_id).voice_channels
        for voice_channel in voice_channels:
            for member in voice_channel.members:
                if member.id == author_id:
                    return voice_channel

        return None

    async def update_db():
        conn = db_conn()
        query = "SELECT message_id FROM party"
        results = db_query(conn, query)

        in_db = []
        pop = []

        for result in results:
            in_db.append(int(result['message_id']))

        for i in in_db:
            if i not in var.parties.keys():
                query = "DELETE FROM party WHERE message_id = " + str(i)
                db_query(conn, query)
                pop.append(i)

        for i in pop:
            in_db.remove(i)

        for i in var.parties:
            message_id = i
            channel_id = int(var.parties[i]['message'].channel_id)
            guild_id = int(var.parties[i]['message'].guild_id)
            join_party = dumps(var.parties[i]['join_party'])
            wait_party_primary = dumps(var.parties[i]['wait_party_primary'])
            wait_party_secondary = dumps(var.parties[i]['wait_party_secondary'])
            author = var.parties[i]['author']
            send_message = var.parties[i]['send_message']
            remove_reaction = var.parties[i]['remove_reaction']
            game = var.parties[i]['game']
            quick_party = var.parties[i]['quick_party']
            civil = var.parties[i]['civil']

            if i in in_db:
                query = f"UPDATE party SET join_party = '{join_party}', wait_party_primary = '{wait_party_primary}', wait_party_secondary = '{wait_party_secondary}', author = {author}, send_message = {send_message}, remove_reaction = {remove_reaction} WHERE message_id = {message_id};"

            else:
                query = f"INSERT INTO party(message_id, channel_id, guild_id, join_party, wait_party_primary, wait_party_secondary, author, send_message, remove_reaction, game, quick_party, civil) VALUES({message_id}, {channel_id}, {guild_id}, '{join_party}', '{wait_party_primary}', '{wait_party_secondary}', {author}, {send_message}, {remove_reaction}, '{game}', {quick_party}, {civil});"

            db_query(conn, query)

        db_disconn(conn)


    @client.command(
        name="sync_", description="sync", scope=698108955192197160,
    )
    async def _sync(ctx: interactions.CommandContext):
        if int(ctx.author.id) == var.me:
            await update_db()
            await ctx.send("synced")

    @client.command(
        name="reload", description="reload", scope=698108955192197160,
    )
    async def _reload(ctx:interactions.CommandContext):
        if int(ctx.author.id) == var.me:
            var.init()
            await ctx.send("reloaded")

    @client.command(
        name="hi", description="hello",
        name_localizations={interactions.Locale.KOREAN: "안녕"},
        description_localizations={interactions.Locale.KOREAN: "인사해줘요"},
    )
    async def hello(ctx: interactions.CommandContext):
        await ctx.send("해위", ephemeral=True)


    @client.command(
        name="commands", description="shows available commands",
        name_localizations={interactions.Locale.KOREAN: "명령어"},
        description_localizations={interactions.Locale.KOREAN: "파티봇의 명령어를 보여줍니다"},
    )
    async def _commands(ctx: interactions.CommandContext):
        color = randint(0, 0xFFFFFF)
        embed=interactions.Embed(title="파티봇 명령어", description="[ ] ←이 안에 있는 것은 대괄호 없이 해당 파라미터를 입력하는 것입니다!\n처음 초대시 권한이 모두 있어야 오류없이 작동합니다!", color=color)
        for i in var.commands:
            embed.add_field(name=i['title'], value=i['value'].replace("+prefix+",var.prefix), inline=False)
        embed.set_footer(text="기능건의는 언제나 환영입니다!\n1인 개발 봇입니다... 앞으로 더 고쳐나가겠습니다!")
        
        await ctx.send(embeds=embed, ephemeral=True)


    @client.command(
        name="uptime", description="shows uptime",
        name_localizations={interactions.Locale.KOREAN: "업타임"},
        description_localizations={interactions.Locale.KOREAN: "파티봇의 업타임을 보여줍니다"},
    )
    async def bot_uptime(ctx: interactions.CommandContext):
        msg = '봇 업타임: ' + convert(time.time() - start)
        await ctx.send(msg, ephemeral=True)


    @client.command(
        name="invite_link", description="shows bot's invite link",
        name_localizations={interactions.Locale.KOREAN: "초대링크"},
        description_localizations={interactions.Locale.KOREAN: "파티봇의 초대링크를 보여줍니다"},
    )
    async def inv_link(ctx: interactions.CommandContext):
        msg = '초대링크입니다: ' + var.invite_link
        await ctx.send(msg, ephemeral=True)


    @client.command(
        name="tips", description="shows some information about the bot that can be useful",
        name_localizations={interactions.Locale.KOREAN: "도움말"},
        description_localizations={interactions.Locale.KOREAN: "알아두면 유용할 파티봇의 여러가지 도움말을 보여줍니다."},
    )
    async def _help(ctx: interactions.CommandContext):
        color = randint(0, 0xFFFFFF)
        embed=interactions.Embed(title="파티봇 도움말", description="몇가지 유익한 정보들이에요~", color=color)
        for i in var.help_msg:
            embed.add_field(name=i['title'], value=i['value'].replace("+prefix+",var.prefix), inline=False)
        embed.set_footer(text="기능건의는 언제나 환영입니다!\n1인 개발 봇입니다... 앞으로 더 고쳐나가겠습니다!")

        await ctx.send(embeds=embed, ephemeral=True)


    @client.command(
        name="supported_games", description="shows games that bot supprots",
        name_localizations={interactions.Locale.KOREAN: "지원게임"},
        description_localizations={interactions.Locale.KOREAN: "파티봇이 지원하는 게임목록을 보여줘요~"},
    )
    async def support_game(ctx: interactions.CommandContext):
        msg = "아래 링크에서 확인 가능합니다. 곧 더 보기 좋게 바꿀 예정입니다.\nhttps://raw.githubusercontent.com/macqueen0987/Party-Bot/main/games.json"
        await ctx.send(msg, ephemeral=True)


    @client.command(
        name="party", description="creates a party",
        name_localizations={interactions.Locale.KOREAN: "파티"},
        options=[
            interactions.Option(
                name="create", description="creates a party",
                name_localizations={interactions.Locale.KOREAN: "생성"},
                description_localizations={interactions.Locale.KOREAN: "파티를 생성해요"},
                type=interactions.OptionType.SUB_COMMAND,
                options=[
                    interactions.Option(
                        name="activity_name", description="activity the party will do.",
                        name_localizations={interactions.Locale.KOREAN: "활동_이름"},
                        description_localizations={interactions.Locale.KOREAN: "파티에서 어떤 활동을 할건가요?"},
                        type=interactions.OptionType.STRING,
                        required=True,
                    ),
                    interactions.Option(
                        name="start_member", description="Who will be the initial member?",
                        name_localizations={interactions.Locale.KOREAN: "시작_멤버"},
                        description_localizations={interactions.Locale.KOREAN: "어떤 멤버를 포함시킬건가요? 멘션해주세요"},
                        type=interactions.OptionType.STRING,
                        required=False,
                    ),
                    interactions.Option(
                        name="mention_role", description="which role will you mention?",
                        name_localizations={interactions.Locale.KOREAN: "역할_멘션"},
                        description_localizations={interactions.Locale.KOREAN: "어떤 역할을 멘션하실건가요? 공란일시 @everyone을 멘션합니다."},
                        type=interactions.OptionType.ROLE,
                        required=False,
                    ),
                ],
            ),
            interactions.Option(
                name="change_time", description="change time of party",
                name_localizations={interactions.Locale.KOREAN: "시간변경"},
                description_localizations={interactions.Locale.KOREAN: "파티 시간을 미루거나 앞당깁니다."},
                type=interactions.OptionType.SUB_COMMAND,
                options=[
                    interactions.Option(
                        name="party_id", description="the id of party",
                        name_localizations={interactions.Locale.KOREAN: "파티_id"},
                        description_localizations={interactions.Locale.KOREAN: "파티 ID를 입력하세요"},
                        type=interactions.OptionType.STRING,
                        required=True,
                    ),
                    interactions.Option(
                        name="activity_name", description="postpone or prepone",
                        name_localizations={interactions.Locale.KOREAN: "키워드"},
                        description_localizations={interactions.Locale.KOREAN: "단축 또는 연기"},
                        type=interactions.OptionType.STRING,
                        required=True,
                        autocomplete=True,
                    ),
                    interactions.Option(
                        name="keywords", description="some keywords with supported time format",
                        name_localizations={interactions.Locale.KOREAN: "시간"},
                        description_localizations={interactions.Locale.KOREAN: "지원되는 형식의 시간 키워드들"},
                        type=interactions.OptionType.STRING,
                        required=True,
                    ),
                ],
            ),
            interactions.Option(
                name="change_leader", description="change leader of party",
                name_localizations={interactions.Locale.KOREAN: "파티장변경"},
                description_localizations={interactions.Locale.KOREAN: "파티장을 바꿉니다"},
                type=interactions.OptionType.SUB_COMMAND,
                options=[
                    interactions.Option(
                        name="party_id", description="the id of party",
                        name_localizations={interactions.Locale.KOREAN: "파티_id"},
                        description_localizations={interactions.Locale.KOREAN: "파티 ID를 입력하세요"},
                        type=interactions.OptionType.STRING,
                        required=True,
                    ),
                    interactions.Option(
                        name="mention_member", description="mention new leader",
                        name_localizations={interactions.Locale.KOREAN: "파티장"},
                        description_localizations={interactions.Locale.KOREAN: "새로운 파티장을 멘션하세요"},
                        type=interactions.OptionType.USER,
                        required=True,
                    ),
                ],
            ),
            interactions.Option(
                name="change_description", description="change the description of the party",
                name_localizations={interactions.Locale.KOREAN: "설명변경"},
                description_localizations={interactions.Locale.KOREAN: "파티의 설명을 바꿉니다"},
                type=interactions.OptionType.SUB_COMMAND,
                options=[
                    interactions.Option(
                        name="party_id", description="the id of party",
                        name_localizations={interactions.Locale.KOREAN: "파티_id"},
                        description_localizations={interactions.Locale.KOREAN: "파티 ID를 입력하세요"},
                        type=interactions.OptionType.STRING,
                        required=True,
                    ),
                ],
            ),
        ],
    )
    async def party(ctx: interactions.CommandContext, sub_command: str, activity_name: str = "", party_id:str = "", keywords:str = "", start_member:str = "", mention_member: interactions.Member = None, mention_role:interactions.Role = None):
        if party_id.replace(" ","") != "":
            try:
                party_id = int(party_id)
            except:
                await ctx.send("파티 ID 변수가 잘못되었습니다.", ephemeral=True)
        if sub_command == 'create':
            description_input = interactions.TextInput(style=interactions.TextStyleType.PARAGRAPH,
                                                       label="파티에 대한 설명을 적어주세요!",
                                                       custom_id="activity_description")
            if mention_role is None:
                custom_id = PersistentCustomID(client, "create_party_modal", [await stringToBase64(activity_name), start_member])
            else:
                custom_id = PersistentCustomID(client, "create_party_modal", [await stringToBase64(activity_name), start_member, int(mention_role.id)])
            modal = interactions.Modal(title="파티 설명", custom_id=str(custom_id),components=[description_input])
            await ctx.popup(modal)

        if sub_command == 'change_time':
            try:
                party = var.parties[party_id]
                author = party['author']
            except:
                await ctx.send("해당 ID의 파티가 존재하지 않습니다!", ephemeral=True)
                return

            if int(author) != int(ctx.author.id):
                await ctx.send("파티장만 리더를 변경할 수 있어요~", ephemeral=True)
                return

            response = convert_time.change_time(var.parties[int(party_id)]['party_time'], keywords)
            if activity_name in ["postpone", "연기"]:
                activity_name = 1
            elif activity_name in ['prepone', "단축"]:
                activity_name = -1
            else:
                await ctx.send("잘못된 시간 키워드를 감지했어요.", ephemeral=True)
            if response[0] != 1:
                for i in range(len(response)):
                    response[i] = response[i]*activity_name
                party['party_time'] = party['party_time'] + timedelta(days=response[1], hours=response[2], minutes=response[3])
                var.parties[party_id] = party
                await reaction_proc.edit_embed(party['message'])
                await ctx.send("성공적으로 변경했습니다.", ephemeral=True)
            else:
                await ctx.send("잘못된 시간입력을 감지했어요!\n지원되는 시간입력은 □일 □시간 □분 또는 [일]:[시간]:[분]/[시간]:[분] 이에요.", ephemeral=True)

        if sub_command == "change_leader":
            if mention_member.user.bot:
                await ctx.send("봇은 파티리더가 될 수 없습니다!", ephemeral=True)
                return

            try:
                party = var.parties[party_id]
                author = party['author']
            except:
                await ctx.send("해당 ID의 파티가 존재하지 않습니다!", ephemeral=True)
                return

            if int(author) == int(ctx.author.id):
                if int(mention_member.id) not in party['join_party']:
                    party['join_party'].append(int(mention_member.id))
                party['join_party'].remove(author)
                party['author'] = int(mention_member.id)
                var.parties[party_id] = party
                await reaction_proc.edit_embed(party['message'])
                await ctx.send("성공적으로 변경되었습니다.", ephemeral=True)

            else:
                await ctx.send("파티장만 파티장을 변결할 수 있습니다.", ephemeral=True)

        if sub_command == "change_description":
            try:
                party = var.parties[party_id]
                author = party['author']
            except:
                await ctx.send("해당 ID의 파티가 존재하지 않습니다!", ephemeral=True)
                return

            if author != int(ctx.author.id):
                await ctx.send("파티장만 설명을 변경할 수 있습니다", ephemeral=True)
            else:
                description_input = interactions.TextInput(style=interactions.TextStyleType.PARAGRAPH,
                                                           label="파티에 대한 설명을 적어주세요!",
                                                           custom_id="activity_description")
                custom_id = PersistentCustomID(client, "change_party_description", party_id)
                modal = interactions.Modal(title="파티 설명", custom_id=str(custom_id),components=[description_input])
                await ctx.popup(modal)                


    @client.autocomplete("party", "activity_name")
    async def party_autocomplete(ctx: interactions.CommandContext, value: str = ""):
        items = ["postpone", "prepone", "단축", "연기"]
        choices = [
            interactions.Choice(name=item, value=item) for item in items if value in item
        ] 
        await ctx.populate(choices)

    @client.persistent_modal("create_party_modal")
    async def make_party(ctx: interactions.CommandContext, package, description):
        datetime_kst = datetime.now()
        activity_name = await base64ToString(package[0])
        start_member = package[1]
        mention_role = "@everyone"
        if len(package) > 2:
            mention_role = f"<@&{package[2]}>"

        author_id = int(ctx.author.id)
        author_name = ctx.author.name
        join_party = [author_id]
        join_party_name = str(author_name)

        r = re.compile('<@\d+>')
        m = r.findall(start_member)
        for i in m:
            member_id = int(i.replace("<@","").replace(">",""))
            join_party.append(member_id)
            join_party_name += ', ' + (await interactions.get(client, interactions.Member, object_id=member_id, parent_id=int(ctx.guild_id))).name


        url = None
        color = randint(0, 0xFFFFFF)
        status, party_time, matches = convert_time.get_time(datetime_kst, description)

        embed = interactions.Embed(title=f"{author_name}님의 {activity_name}파티", description=description, color=color)
        send_message = False
        quick_party = False

        if status == 1:
            await ctx.send("잘못된 시간입력을 감지했어요", ephemeral=True)
            return
        elif status == 0:
            embed.add_field(name="시간", value=f"{party_time.strftime('%Y-%m-%d %H:%M:%S')} {days[int(party_time.strftime('%w'))]}요일 KST", inline=False)
            send_message = True

        else:
            quick_party = True
            party_time = datetime_kst

        voice_channel_id = None
        if quick_party:
            voice_channel = None
            try:
                voice_channel = await find_voice(int(ctx.guild_id), author_id)
            except Exception as e:
                print(e)

            if voice_channel is not None:
                voice_channel_id = voice_channel.id
                for member in voice_channel.members:
                    if member.id not in join_party:
                        join_party.append(member.id)
                        join_party_name += f', {member.name}'
                url = f"https://discord.com/channels/{int(ctx.guild_id)}/{voice_channel_id}"
                embed = discord.Embed(title=f"{author_name}님의 {activity_name}파티", description=description, color=color, url=url)


        civil = False
        if "내전" in description:
            civil = True

        if activity_name in var.games.keys():
            activity = var.games[activity_name]
            max_player = activity['max_player']
            if civil:
                max_player = 2*max_player
            embed.add_field(name=f"참가자 {len(join_party)}/{max_player}", value = f"```\n{join_party_name}```", inline=False)
        else:
            if civil:
                await ctx.send("지원되지 않는 게임은 내전이 불가합니다...")
                return

            usr = await interactions.get(client, interactions.Member, object_id=int(var.me), parent_id=int(var.support_server))
            await usr.send("지원되지 않는 활동: " + activity_name)
            max_player = None
            embed.add_field(name="참가자", value = f"```\n{join_party_name}```", inline=False)
        if not quick_party:
            embed.set_footer(text="참가자: 🙋‍♂️ 참가, 불참, 파티 만원시 대기, 공석시 자동 참여 \n                🤔 대기하지만 자동으로 파티에 참여 안함\n파티장: 🚫삭제, ▶️시작, ✅완료")
        else:
            embed.set_footer(text="이 파티는 퀵 파티입니다!\n파티장이 음성채널에 들어가면 시작\n파티장이 음성채널에서 나오면 종료")
        message = await ctx.send(content=mention_role, embeds=embed)
        message.guild_id = ctx.guild_id
        if not quick_party:
            embed.set_field_at(0, name="시간", value=f"{party_time.strftime('%Y-%m-%d %H:%M:%S')} {days[int(party_time.strftime('%w'))]}요일 KST", inline=True)
            embed.insert_field_at(1, name = "파티 ID", value = str(message.id), inline = True)
        else:
            embed.insert_field_at(0, name = "파티 ID", value = str(message.id), inline = False)
        await message.edit(content=mention_role, embeds=embed)
        if quick_party:
            var.parties[int(message.id)] = {'join_party': join_party, 'wait_party_primary':[], 'wait_party_secondary':[], 'author':author_id, 'party_time':party_time, 'send_message':send_message, 'remove_reaction':True, 'max_player':max_player, 'game':activity_name, 'message':message, 'voice_channel_id':voice_channel_id, 'quick_party':quick_party, 'civil':civil}
        else:
            status = await add_reaction_to(message, party_emojis)
            if status[0] == 4:
                var.parties[int(message.id)] = {'join_party': join_party, 'wait_party_primary':[], 'wait_party_secondary':[], 'author':author_id, 'party_time':party_time, 'send_message':send_message, 'remove_reaction':True, 'max_player':max_player, 'game':activity_name, 'message':message, 'voice_channel_id':voice_channel_id, 'quick_party':quick_party, 'civil':civil}


    @client.persistent_modal("change_party_description")
    async def change_party_description(ctx: interactions.CommandContext, package, description):
        message = var.parties[int(package)]['message']
        embed = message.embeds[0]
        embed.description = description
        await message.edit(content=message.content, embeds=embed)
        await ctx.send("성공적으로 수정되었습니다.", ephemeral=True)

    '''
    @client.command(
        name="react_to_get_role", description="create a message that gives you certain role on reaction",
        name_localizations={interactions.Locale.KOREAN: "역할지급"},
        description_localizations={interactions.Locale.KOREAN: "메시지의 이모티콘으로 역할을 지급할 수 있도록 해요 "},
    )
    async def _roles(message, *, args):
        r = re.compile('<@&\d+>')
        m = r.findall(args)
        content = "미지급 역할: "
        for i in m:
            content += " "+i
        content += f'\n앞의 역할부터 할당할 이모티콘으로 차례로 본인의 메시지에 반응하세요! \n{var.repeat_emoji[0]}를 누르시면 처음부터 다시시작합니다.\n{var.delete_emoji[0]}를 누르시면 해당과정을 중단합니다.'
        status = await send_to(message, content)
        if status[0] != 0: return
        description_message = status[1]
        status = await add_reaction_to(message, var.repeat_emoji+var.delete_emoji)
        if status[0] != 4: return
        var.temp_role_message[message.message.id] = {"roles": m, "roles_backup":m, "channel_id":message.channel.id, "description_message":description_message}


    @client.command(aliases=var._stop)
    @commands.check(is_owner)
    async def _stop(message):
        await reply_to(message, "정지합니다.")
        await update_db()
        client.clear()
        await client.close()


    @client.command(aliases=var._restart)
    @commands.check(is_owner)
    async def _restart(message):
        var.restart = True
        await reply_to(message, "재시작합니다.")
        client.clear()
        await client.close()


    @client.command(aliases=var._send)
    @commands.check(is_owner)
    async def _send(message, channel_id, *, arg):
        channel = client.get_channel(int(channel_id))
        await send_to(message, arg, channel=channel)



    '''
# ==================================================================END OF COMMANDS====================================================

    @bot.event
    async def on_raw_reaction_add(reaction):
        message_id = int(reaction.message_id)
        channel_id = int(reaction.channel_id)
        emoji = reaction.emoji.name

        member = reaction.member
        message = await bot.get_channel(channel_id).fetch_message(message_id)

        civil_emoji = var.number_emojis+var.gosu_emoji+var.noob_emoji+var.gamer_emoji+var.shuffle_emoji

        if member.bot:
            return

        if emoji in party_emojis and message_id in var.parties.keys():
            await reaction_proc.party(message, emoji, member)

        if emoji in civil_emoji and message_id in var.civil_party.keys():
            await reaction_proc.civil_party(message, emoji, member)

        if message_id in var.temp_role_message.keys() and member.guild_permissions.administrator:
            if reaction.emoji.is_unicode_emoji():
                await reaction_proc.add_role_emoji(message, emoji)
            else:
                await send_to(message, "사용하신 이모티콘은 사용할 수 없는 이모티콘입니다!", delete_after=10)

        if message_id in list(map(int, var.role_message.keys())):
            await reaction_proc.give_role(message, emoji, member)


    @bot.event
    async def on_raw_reaction_remove(reaction):
        message_id = int(reaction.message_id)
        channel_id = int(reaction.channel_id)
        emoji = reaction.emoji.name

        member = await bot.fetch_user(int(reaction.user_id))
        message = await bot.get_channel(channel_id).fetch_message(message_id)

        if member.bot:
            return

        civil_emoji = var.number_emojis+var.gosu_emoji+var.noob_emoji+var.gamer_emoji+var.shuffle_emoji


        if emoji in party_emojis and message_id in var.parties.keys():
            await reaction_proc.party(message, emoji, member, remove_only=True)

        if message_id in list(map(int, var.role_message.keys())):
            await reaction_proc.give_role(message, emoji, member, remove_only=True)

        if emoji in civil_emoji and message_id in var.civil_party.keys():
            await reaction_proc.civil_party(message, emoji, member, remove_only=True)

# ==================================================================END OF COMPONENTS LISTENING====================================================

    # async def check_corrupt_messages():
    #     run = True
    #     while True:
    #         run = True
    #         for i in var.role_message:
    #             channel_id = var.role_message[i]['channel_id']
    #             try:
    #                 message = await interactions.get(client, interactions.Message, object_id=int(i), parent_id=int(channel_id))

    #             except:
    #                 var.role_message.pop(i)
    #                 run = False
    #                 break
    #         if run:
    #             break

    #     var.write_role_messages()
    #     var.get_role_messages()


    @create_task(IntervalTrigger(60))
    async def party_notify():
        global cnt
        datetime_kst = datetime.now()

        cnt += 1
        if cnt % 5 == 0:
            await update_db()

        # if cnt % 13 == 0:
            # await check_corrupt_messages()

        run = True
        while True:
            run = True
            for i in var.parties:
                time_diff = var.parties[i]['party_time'] - datetime_kst
                time_diff = time_diff.total_seconds()
                # print(i, var.parties[i]['party_time'], datetime_kst, time_diff)

                if time_diff < 300:
                    voice_channel = await find_voice(int(var.parties[i]['message'].guild_id), var.parties[i]['author'])
                    if voice_channel is not None:
                        var.parties[i]['voice_channel_id'] = voice_channel.id
                        await reaction_proc.edit_embed(var.parties[i]['message'])


                if var.parties[i]['send_message']:
                    if 4*60 <= time_diff <= 6*60:
                        var.parties[i]['send_message'] = False
                        author = await interactions.get(client, interactions.Member, object_id=int(var.parties[i]['author']), parent_id=int(var.parties[i]['message'].guild_id))
                        author = author.name
                        game = var.parties[i]['game']

                        await reaction_proc.message_party(var.parties[i]['join_party'], int(var.parties[i]['message'].guild_id), f"{author}님의 {game}파티가 약 5분 후에 시작되려합니다!")

                    if time_diff < 0:
                        var.parties[i]['send_message'] = False
                        voice_channel_id = None
                        found = False
                        voice_channels = bot.get_guild(var.parties[i]['message'].guild_id).voice_channels
                        for voice_channel in voice_channels:
                            for member in voice_channel.members:
                                if member.id == var.parties[i]['author']:
                                    voice_channel_id = voice_channel.id
                                    found = True

                                if found:
                                    break
                            if found:
                                break
                        var.parties[i]['voice_channel_id'] = voice_channel_id
                else:
                    if time_diff < 0 and var.parties[i]['remove_reaction'] and not var.parties[i]['quick_party']:
                        var.parties[i]['remove_reaction'] = False
                        try:
                            message = var.parties[i]['message']
                            embed = message.embeds[0]
                            embed.set_footer(text = "파티가 시작되었습니다!")
                            await message.edit(content="", embed=embed)
                        except Exception as e:
                            print(e)
                        await clear_reaction_of(var.parties[i]['message'], var.party_emoji+var.wait_emoji+var.start_emoji)

                    if (time_diff < -3600 and not var.parties[i]['quick_party']) or (time_diff < -(6*3600) and var.parties[i]['quick_party']):
                        message = var.parties[i]['message']
                        await clear_reaction_of(message)
                        try:
                            embed = message.embeds[0]
                            embed.set_footer(text = "이 파티는 종료되었습니다.")
                            embed.url = None
                            await message.edit(content="", embed=embed)
                        except Exception as e:
                            print("ERROR during changing completed party footer", e)
                        # await message.delete()
                        var.parties.pop(i)
                        run = False
                        break

            if run:
                break


# ==================================================================END OF TASKS====================================================
    
    @bot.event
    async def on_voice_state_update(member, before, after):
        before_id, after_id = None, None
        before_guild_id, after_guild_id = None, None
        after_dic = []
        before_dic = []
        if before.channel is not None:
            for before_member in before.channel.members:
                if before_member.id != member.id:
                    before_dic.append(before_member.id)
            before_id = before.channel.id
            before_guild_id = before.channel.guild.id
        if after.channel is not None:
            for after_member in after.channel.members:
                after_dic.append(after_member.id)
            after_id = after.channel.id
            after_guild_id = after.channel.guild.id

        if before_id != after_id:
            if after_id is not None:
                for i in var.parties:
                    if int(var.parties[i]['message'].guild_id) == after_guild_id and var.parties[i]['quick_party']:
                        if var.parties[i]['author'] == member.id:
                            var.parties[i]['voice_channel_id'] = after_id
                            var.parties[i]['join_party'] = after_dic
                            await reaction_proc.edit_embed(var.parties[i]['message'])
                            return

                        if var.parties[i]['voice_channel_id'] == after_id:
                            var.parties[i]['join_party'] = after_dic
                            try:
                                var.parties[i]['wait_party_primary'].remove(member.id)
                            except:
                                pass
                            try:
                                var.parties[i]['wait_party_secondary'].remove(member.id)
                            except:
                                pass
                            await reaction_proc.edit_embed(var.parties[i]['message'])
                            return

            else:
                for i in var.parties:
                    if int(var.parties[i]['message'].guild_id) == before_guild_id and var.parties[i]['quick_party'] and var.parties[i]['voice_channel_id'] == before_id:
                        if var.parties[i]['author'] == member.id:
                            await delete_to(var.parties[i]['message'])
                            var.parties.pop(i)
                            return
                        else:
                            var.parties[i]['join_party'] = before_dic
                            await reaction_proc.edit_embed(var.parties[i]['message'])
                            return


    @bot.event
    async def on_guild_join(guild):
        user = await bot.fetch_user(var.me)
        await user.send('%s 에 새롭게 초대됨' % guild.name)
        try:
            async for entry in guild.audit_logs(action=discord.AuditLogAction.bot_add, limit=1):
                await entry.user.send(var.welcomemessage.replace("+prefix+",var.prefix))
                break

        except Exception as e:
            print("ERROR while sending welcomemessage to user", e)
            if guild.system_channel is not None:
                try:
                    await guild.system_channel.send(var.welcomemessage.replace("+prefix+",var.prefix))
                except Exception as e:
                    print("ERROR while sending welcomemessage to guild.system_channel", e)
                    pass
            pass


    @bot.event
    async def on_guild_remove(guild):
        pass

    @bot.event
    async def on_ready():
        print("Starting up Dpy")
        # kb = DiscordpyKoreanbots(bot, 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijk3MTE5OTcwMjIxNTI5OTEzMiIsImlhdCI6MTY1MTkzOTUzMX0.HatPods44gUkaBF4fxdzmKf57nH6p4y8TWXgno5khqmYlT3TOXrfPWCqCFkHsQm7apB0ioyTfqa3-mtd-svaEJXE-J18I2r5IPtJMP0VkVG2guKV6G3C-IQEEq6fRCcU2Adv9jd-_upnJs-UjgEtTFAdfFLXCGr72LikmI2s3NY', run_task=True)


    @client.event
    async def on_start():
        global start
        print("Starting up interactions-client")

        await client.change_presence(interactions.ClientPresence(status=interactions.StatusType.ONLINE,activities=[interactions.PresenceActivity(name="/명령어", type=interactions.PresenceActivityType.GAME)]))

        conn = db_conn()
        query = "SELECT * FROM party;"
        results = db_query(conn, query)
        cnt = 0

        for result in results:
            message_id = int(result['message_id'])
            channel_id = int(result['channel_id'])
            guild_id = int(result['guild_id'])
            try:
                message = await interactions.get(client, interactions.Message, object_id=int(message_id), parent_id=int(channel_id))
                message.guild_id = guild_id
            except Exception as e:
                print(f"ERROR while fetching message {message_id} with Exception {e}")
                query = f"DELETE FROM party WHERE message_id = {message_id}"
                db_query(conn, query)
                try:
                    var.parties.pop(message_id)
                except Exception as e:
                    print(f"Unknown Party: {message_id}", e)

                try:
                    channel = await interactions.get(client, interactions.Channel, object_id=int(channel_id))
                    user = await interactions.get(client, interactions.Member, object_id=int(result['author']), parent_id=int(channel.guild_id))
                    await user.send(f"봇을 재시작하는 과정에서 <@{int(user.id)}>님의 파티에서 에러가 발생하였습니다. 다시 파티를 만들어주세요!")
                except:
                    print("error sending error message to party owner")
                continue

            cnt += 1
            join_party = json.loads(result['join_party'])
            wait_party_primary = json.loads(result['wait_party_primary'])
            wait_party_primary = list(map(int, wait_party_primary))
            wait_party_secondary = json.loads(result['wait_party_secondary'])
            wait_party_secondary = list(map(int, wait_party_secondary))
            author = int(result['author'])
            send_message = bool(result['send_message'])
            remove_reaction = bool(result['remove_reaction'])
            game = result['game']
            quick_party = bool(result['quick_party'])
            civil = bool(result['civil'])

            max_player = None
            if game in var.games.keys():
                max_player = var.games[game]['max_player']

            if quick_party:
                party_time = datetime.now()

            else:
                party_time = message.embeds[0].fields[0].value
                for i in party_time.split(" ")[2:]:
                    party_time = party_time.replace(" "+i, "")
                party_time = datetime.strptime(party_time, '%Y-%m-%d %H:%M:%S')

            var.parties[message_id] = {'join_party': join_party, 'wait_party_primary':wait_party_primary, 'wait_party_secondary':wait_party_secondary, 'author':author, 'party_time':party_time, 'send_message':send_message, 'remove_reaction':remove_reaction, 'max_player':max_player, 'game':game, 'message':message, 'voice_channel_id':None, 'quick_party':quick_party, 'civil':civil}
            # await reaction_proc.edit_embed(message)

        db_disconn(conn)

        # await check_corrupt_messages()
        await party_notify()
        print(f"Loaded {cnt} parties")
        print("ALL DONE, STARTING")

    start = time.time()
    cnt = 0

    try:
        party_notify.start()
    except Exception as e:
        print("ERROR while starting event: ", e)

    loop = asyncio.get_event_loop()

    task2 = loop.create_task(bot.start(var.token))
    task1 = loop.create_task(client.start())

    gathered = asyncio.gather(task1, task2, loop=loop)

    try:
        loop.run_until_complete(gathered)
    except Exception as e:
        print(e)
    finally:
        print("exiting")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
