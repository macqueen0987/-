import discord
import traceback
import interactions
import asyncio
import var

mention_author = False
# allowed_mentions = interactions.AllowedMentions(replied_user=False)
async def reply_to(message, msg, embed=None, delete_after=None, status=None):
    if embed is None:
        try:
            message = await message.reply(msg, mention_author=mention_author, delete_after=delete_after)
            if status is None: status = 0
            return [status, message]
        except:
            pass 
    else:
        try:
            message = await message.reply(content=msg, embed=embed, mention_author=mention_author, delete_after=delete_after)
            return [0, message]
        except:
            msg = "봇이 해당채널에서 임베드 메시지를 보낼 수 없습니다!"
            return await reply_to(message, msg, status=3, delete_after=20)


async def send_to(msg, channel, embed=None, delete_after=None, status=None):
    if embed is None:
        try:
            message = await channel.send(msg)
            await asyncio.sleep(delete_after)
            await msg.delete()
            if status is None: status = 0
            return [status, message]
        except:
            try:
                user = await var.client.fetch_user(message.author.id)
                await user.send("봇이 해당채널에서 메시지를 보낼수 없습니다!\n"+msg)
                if status is None: status = 1
                return [status]
            except:
                if status is None: status = 2
                return [status]
    else:
        try:
            if message is None:
                message = await channel.send(content='', embed=embed, mention_author=mention_author, delete_after=delete_after)
            else:
                message = await channel.send(content=msg.format(message), embed=embed, mention_author=mention_author, delete_after=delete_after)
            return [0, message]
        except:
            traceback.print_exc()
            msg = "봇이 해당채널에서 임베드 메시지를 보낼 수 없습니다!"
            return await send_to(message, msg, delete_after=20, status=3)


async def delete_to(message):
    try:
        await message.delete()
        return [5]
    except:
        await send_to(message, "봇이 해당채널에서 메시지를 삭제할 수 없습니다! 메시지 관리하기 권한이 없나요?", delete_after=10)
        # pass


async def add_reaction_to(message, emoji):
    if type(message) == discord.Message:
        message = await interactions.get(var.client, interactions.Message, object_id=int(message.id), parent_id=int(message.channel.id))
    try:
        for i in emoji:
            await message.create_reaction(i)
        return [4]
    except:
        delete_after = 20
        await reply_to(message, "이모티콘을 추가할 수 없습니다! 메시지 읽기 권한과 반응 추가하기 권한이 빠졌나요..?", delete_after=delete_after)


async def clear_reaction_of(message, emoji=None):
    if type(message) == interactions.Message:
        message = await var.bot.get_channel(int(message.channel_id)).fetch_message(int(message.id))
    try:
        if emoji is None:
            await message.clear_reactions()
            return [4]
        else:
            for i in emoji:
                await message.clear_reaction(i)
            return [4]
    except:
        delete_after = 20
        await reply_to(message, "이모티콘을 삭제할 수 없습니다! 메시지 관리하기 권한이 빠졌나요..?", delete_after=delete_after)


async def give_role_to(message, member, role):
    member = await message.guild.fetch_member(member.id)
    try:
        await member.add_roles(role)
        return [6]
    except:
        await send_to(message, "역할을 지급할 수 없습니다! 권한 관리하기 권이 있나요?", delete_after=10)


async def remove_role_of(message, member, role):
    member = await message.guild.fetch_member(member.id)
    try:
        await member.remove_roles(role)
        return [6]
    except Exception as e:
        print(e)
        await send_to(message, "역할을 뺄 수 없습니다! 권한 관리하기 권이 있나요?", delete_after=10)