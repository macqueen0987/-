import interactions

import var
from interact import reply_to, send_to, delete_to, add_reaction_to, clear_reaction_of, give_role_to, remove_role_of
import re
from random import randint, shuffle

# allowed_mentions = interactions.AllowedMentions(replied_user=False)
days = ["일", "월", "화", "수", "목", "금", "토"]
# var.parties[message.id] = {'join_party': [author_id], 'wait_party_primary':[], 'author':author_id, 'party_time':party_time, 'send_message':send_message, 'max_player':max_player, 'game':game}
async def party(message, emoji, member, remove_only=False):
    except_member=[]
    message_id = int(message.id)
    parties = var.parties
    message = await var.bot.get_channel(int(parties[message_id]['message'].channel_id)).fetch_message(int(parties[message_id]['message'].id))
    user_id = int(member.id)
    edit = False
    # ===============================Join Memeber===============================
    if emoji in var.party_emoji: 
        if user_id == int(parties[message_id]['author']):
            if remove_only:
                await reply_to(message, "파티장은 나갈수 없습니다.", delete_after=10)
            return

        for i in parties[message_id]['wait_party_primary']+parties[message_id]['wait_party_secondary']:
            if user_id == int(i):
                if not remove_only:
                    await reply_to(message, f"<@{user_id}> 이미 대기멤버입니다. 먼저 대기멤버에서 탈퇴해주세요", delete_after=10)
                return

        found = False
        edit = True
        for i in range(len(parties[message_id]['join_party'])):
            if user_id == parties[message_id]['join_party'][i]:
                found = True
                if remove_only:
                    parties[message_id]['join_party'].pop(i)
                    if len(parties[message_id]['wait_party_primary']) > 0:
                        parties[message_id]['join_party'].append(parties[message_id]['wait_party_primary'][0])
                        usr = await interactions.get(var.client, interactions.Member, object_id=int(parties[message_id]['wait_party_primary'][0]), parent_id=int(parties[message_id]['message'].guild_id))
                        await usr.send(f"{message.author.name}님의 {parties[message_id]['game']}파티멤버가 되었습니다!")
                        parties[message_id]['wait_party_primary'].pop(0)
                    break

        if not found and not remove_only:
            if parties[message_id]['max_player'] is None:
                parties[message_id]['join_party'].append(user_id)
            else:
                if len(parties[message_id]['join_party']) >= parties[message_id]['max_player']:
                    parties[message_id]['wait_party_primary'].append(user_id)
                else:
                    parties[message_id]['join_party'].append(user_id)


    # ===============================Wait Member===============================
    elif emoji in var.wait_emoji:
        if user_id == int(parties[message_id]['author']):
            if not remove_only:
                await reply_to(message, "파티장은 대기멤버가 될 수 없습니다.", delete_after=10)
            return

        for i in range(len(parties[message_id]['join_party'])):
            if user_id == parties[message_id]['join_party'][i]:
                if not remove_only:
                    await reply_to(message, f"<@{user_id}> 이미 파티멤버입니다. 먼저 파티멤버에서 탈퇴해주세요", delete_after=10)
                return

        found = False
        edit = True
        for i in range(len(parties[message_id]['wait_party_secondary'])):
            if user_id == parties[message_id]['wait_party_secondary'][i]:
                found = True
                if remove_only:
                    parties[message_id]['wait_party_secondary'].pop(i)
                    break

        if not found and not remove_only:
            parties[message_id]['wait_party_secondary'].append(user_id)

    # ===============================Delete Party===============================
    elif emoji in var.delete_emoji:
        if user_id == int(parties[message_id]['author']):
            await message.delete()
            author = await interactions.get(var.client, interactions.Member, object_id=int(user_id), parent_id=int(parties[message_id]['message'].guild_id))
            author = author.name
            game = parties[message_id]['game']

            if not remove_only:
                party_member = parties[message_id]['join_party']
                for i in except_member:
                    if i in party_member:
                        party_member.remove(i)
                await message_party(party_member, parties[message_id]['message'].guild_id, f"{author}님의 {game}파티가 취소되었습니다!")
            parties.pop(message_id)

    # ===============================Start Party===============================
    elif emoji in var.start_emoji:
        if user_id == int(parties[message_id]['author']):
            author = await interactions.get(var.client, interactions.Member, object_id=int(user_id), parent_id=int(parties[message_id]['message'].guild_id))
            author = author.name
            game = parties[message_id]['game']

            if not remove_only:
                party_member = parties[message_id]['join_party']
                for i in except_member:
                    if i in party_member:
                        party_member.remove(i)
                await message_party(party_member, parties[message_id]['message'].guild_id, f"{author}님의 {game}파티가 시작되었습니다!")
                await clear_reaction_of(parties[message_id]['message'], var.start_emoji)

    # ===============================End Party===============================
    elif emoji in var.complete_emoji:
        if user_id == int(parties[message_id]['author']):
            if parties[message_id]['civil']:
                status = await clear_reaction_of(parties[message_id]['message'])
                if status[0] != 4: return
                game = var.games[parties[message_id]['game']]
                content = var.number_emojis[0] + ': ' + game['position'][0]
                for i in range(1,len(game['position'])):
                    content += ', ' + var.number_emojis[i] + ': ' + game['position'][i]
                content += '\n실력 상 중 하: ' + var.gosu_emoji[0] + ' ' + var.gamer_emoji[0] + ' ' + var.noob_emoji[0]+'\n파티장: '+var.shuffle_emoji[0] + ' 팀 배정'
                await parties[message_id]['message'].edit(content=content)
                if game['position'] is not None:
                    status = await add_reaction_to(parties[message_id]['message'], var.number_emojis[:len(game['position'])])
                    if status[0] != 4: return
                await add_reaction_to(parties[message_id]['message'], var.gosu_emoji+var.gamer_emoji+var.noob_emoji+var.shuffle_emoji)
                var.civil_party[message_id] = parties[message_id]
                var.civil_party[message_id]['position'] = {}
                for i in range(len(game['position'])):
                    var.civil_party[message_id]['position'][i] = []
                var.civil_party[message_id]['level'] = {2: [], 1: [], 0: []}
            else:
                await clear_reaction_of(message)
                try:
                    embed = message.embeds[0]
                    embed.set_footer(text = "이 파티는 종료되었습니다.")
                    await message.edit(content="", embed=embed)
                except Exception as e:
                    print("ERROR during changing completed party footer", e)
                # await message.delete()
            parties.pop(message_id)

    # ===============================Edit Embed===============================
    var.parties = parties

    if edit:
        await edit_embed(message)


async def edit_embed(message):
    message_id = int(message.id)
    party = var.parties[message_id]
    embed = message.embeds[0]
    time_idx, ID_idx, party_member_idx, wait_member_idx = None, None, None, None
    embed_field = embed.fields
    for i in range(len(embed_field)):
        if "시간" in embed_field[i].name:
            time_idx = i
        if "ID" in embed_field[i].name:
            ID_idx = i
        if "참가자" in embed_field[i].name:
            party_member_idx = i
        if "대기자" in embed_field[i].name:
            wait_member_idx = i


    if not party['quick_party']:
        if time_idx is None:
            embed.insert_field_at(0, name="시간", value=f"{party['party_time'].strftime('%Y-%m-%d %H:%M:%S')} {days[int(party['party_time'].strftime('%w'))]}요일 KST", inline=False)
            await message.edit(content = message.content, embeds=embed)
            return await edit_embed(message)


        embed.set_field_at(0, name="시간", value=f"{party['party_time'].strftime('%Y-%m-%d %H:%M:%S')} {days[int(party['party_time'].strftime('%w'))]}요일 KST", inline=True)
        if ID_idx is None:
            embed.insert_field_at(1, name="파티 ID", value=str(message_id), inline=True)
            await message.edit(content = message.content, embeds=embed)
            return await edit_embed(message)


    if party_member_idx is not None:
        if party['max_player'] is not None:
            name = f"참가자: {len(party['join_party'])}/{party['max_player']}"
        else:
            name = f"참가자: {len(party['join_party'])}"
        value = "```\n"
        for i in party['join_party']:
            usr = await interactions.get(var.client, interactions.Member, object_id=int(i), parent_id=int(party['message'].guild_id))
            usr = usr.name
            value += usr + ", "
        value = value[:-2]
        value += "```"
        embed.set_field_at(party_member_idx, name=name, value=value, inline=False)


    if len(party['wait_party_primary'] + party['wait_party_secondary']) > 0:
        wait_name = "대기자"
        wait_value = "```\n"
        for i in party['wait_party_primary'] + party['wait_party_secondary']:
            usr = await interactions.get(var.client, interactions.Member, object_id=int(i), parent_id=(party['message'].guild_id))
            usr = usr.name
            wait_value += usr + ", "
        wait_value = wait_value[:-2]
        wait_value += "```"

        if wait_member_idx is not None:
            embed.set_field_at(wait_member_idx, name=wait_name, value=wait_value, inline=False)

        else:
            embed.add_field(name=wait_name, value=wait_value, inline=False)

    else:
        if wait_member_idx is not None:
            embed.remove_field(wait_member_idx)

    if party['voice_channel_id'] is not None:
        embed.url = f"https://discord.com/channels/{party['message'].guild_id}/{party['voice_channel_id']}"

    author_name = await interactions.get(var.client, interactions.Member, object_id=int(party['author']), parent_id=int(party['message'].guild_id))
    author_name = author_name.name
    embed.title = f"{author_name}님의 {party['game']}파티"
    if type(message) == interactions.Message:
        await message.edit(content=message.content, embeds=embed)
    else:
        try:
            await message.edit(content=message.content, embed=embed)
        except Exception as e:
            print("ERROR at edit_embed:",e)


async def message_party(members, guild_id, message):
    for member in members:
        try:
            usr = await interactions.get(var.client, interactions.Member, object_id=int(member), parent_id=int(guild_id))
            await usr.send(f"<@{member}>님, {message}")
        except Exception as e:
            print(e)


async def add_role_emoji(message, emoji):
    temp_role_message = var.temp_role_message
    message_id = message.id

    if emoji == var.repeat_emoji[0]:
        status = await clear_reaction_of(message)
        if status[0] != 4: return
        content = "미지급 역할: "
        for i in temp_role_message[message_id]['roles_backup']:
            content += " "+i
        content += f'\n앞의 역할부터 할당할 이모티콘으로 차례로 본인의 메시지에 반응하세요! \n{var.repeat_emoji[0]}를 누르시면 처음부터 다시시작합니다.\n{var.delete_emoji[0]}를 누르시면 해당과정을 중단합니다.'
        await temp_role_message[message_id]["description_message"].edit(content=content)
        await add_reaction_to(message, var.repeat_emoji+var.delete_emoji)
        temp_role_message[message_id]['roles'] = temp_role_message[message_id]['roles_backup']


    elif emoji == var.delete_emoji[0]:
        status = await delete_to(message)
        temp_role_message.pop(message_id)
        

    else:
        status = await add_reaction_to(message, [emoji])
        if status[0] != 4: return
        role = temp_role_message[message_id]['roles'][0]
        role = int(re.sub('\D', '', role))
        temp_role_message[message_id]['roles'].pop(0)
        temp_role_message[message_id][emoji] = role


        if len(temp_role_message[message_id]['roles']) > 0:
            content = "미지급 역할: "
            for i in temp_role_message[message_id]['roles']:
                content += " "+i
            content += f'\n앞의 역할부터 할당할 이모티콘으로 차례로 본인의 메시지에 반응하세요! {var.repeat_emoji[0]}를 누르시면 처음부터 다시시작합니다.'
            await temp_role_message[message_id]["description_message"].edit(content=content)

        else:
            await temp_role_message[message_id]["description_message"].edit(content="설정이 완료되었습니다. 위의 메시지를 수정하여도 메시지가 삭제되지만 않는다면 역할지급은 계속 동작합니다. 명령어 부분을 빼는등 입맛대로 수정해보세요!\n이 메시지는 30초 후 삭제됩니다.", delete_after=30)
            status = await clear_reaction_of(message, var.repeat_emoji+var.delete_emoji)
            if status[0] != 4: return   
            temp_role_message[message_id].pop('roles')
            temp_role_message[message_id].pop('roles_backup')
            temp_role_message[message_id].pop('description_message')
            var.role_message[str(message_id)] = temp_role_message[message_id]
            temp_role_message.pop(message_id)
            var.write_role_messages()

    var.temp_role_message = temp_role_message


async def give_role(message, emoji, member, remove_only=False):
    message_id = str(message.id)
    roles = var.role_message[message_id]

    for role in roles:
        if role == emoji:
            role_id = int(roles[role])
            break

    role = message.guild.get_role(role_id)
    if role is None:
        await send_to(message, "지정되었던 역할을 찾을 수 없습니다!")
        return

    if not remove_only:
        await give_role_to(message, member, role)
    else:
        await remove_role_of(message, member, role)


async def civil_party(message, emoji, member, remove_only=False):
    message_id = message.id
    author = await interactions.get(var.client, interactions.Member, object_id=int(var.civil_party[message_id]['author']), parent_id=int(var.civil_party[message_id]['message'].guild_id))

    if member.id not in var.civil_party[message_id]['join_party']:
        return

    civil_party_postion_pre = []
    for i in var.civil_party[message_id]['position']:
        for j in var.civil_party[message_id]['position'][i]:
            if j not in civil_party_postion_pre:
                civil_party_postion_pre.append(j)

    civil_party_level_pre = []
    for i in var.civil_party[message_id]['level']:
        for j in var.civil_party[message_id]['level'][i]:
            if j not in civil_party_level_pre:
                civil_party_level_pre.append(j)

    if emoji in var.number_emojis:
        index = var.number_emojis.index(emoji)
        if remove_only:
            try:
                var.civil_party[message_id]['position'][index].remove(member.id)
            except:
                pass
        else:
            var.civil_party[message_id]['position'][index].append(member.id)

    if emoji in var.gosu_emoji + var.gamer_emoji + var.noob_emoji:
        for i in range(3):
            try:
                var.civil_party[message_id]['level'][i].remove(member.id)
            except:
                pass

    if emoji in var.gosu_emoji and not remove_only:
        var.civil_party[message_id]['level'][2].append(member.id)

    if emoji in var.gamer_emoji and not remove_only:
        var.civil_party[message_id]['level'][1].append(member.id)

    if emoji in var.noob_emoji and not remove_only:
        var.civil_party[message_id]['level'][0].append(member.id)

    civil_party_postion = []
    for i in var.civil_party[message_id]['position']:
        for j in var.civil_party[message_id]['position'][i]:
            if j not in civil_party_postion:
                civil_party_postion.append(j)

    civil_party_level = []
    for i in var.civil_party[message_id]['level']:
        for j in var.civil_party[message_id]['level'][i]:
            if j not in civil_party_level:
                civil_party_level.append(j)

    if len(civil_party_postion_pre) != len(civil_party_postion) or len(civil_party_level_pre) != len(civil_party_level):
        embed = interactions.Embed(title=f"{author.nick}님의 {var.civil_party[message_id]['game']}내전", description="내전 포지션 배정중!")
        value = ''
        for i in var.civil_party[message_id]['join_party']:
            if i not in civil_party_postion:
                user = await interactions.get(var.client, interactions.Member, object_id=int(i), parent_id=int(var.civil_party[message_id]['message'].guild_id))
                value += ', ' + user.nick
        value = value[2:]
        if len(civil_party_postion) == var.civil_party[message_id]['max_player']:
            value = "없음"
        embed.add_field(name=f"포지션 {var.civil_party[message_id]['max_player']}명중 {len(civil_party_postion)}명 고름", value=f"선택 안한 멤버:\n```\n{value}```", inline=False)
        value = ''
        for i in var.civil_party[message_id]['join_party']:
            if i not in civil_party_level:
                user = await interactions.get(var.client, interactions.Member, object_id=int(i), parent_id=int(var.civil_party[message_id]['message'].guild_id))
                value += ', ' + user.nick
        value = value[2:]
        if len(civil_party_level) == var.civil_party[message_id]['max_player']:
            value = "없음"
        embed.add_field(name=f"실력 {var.civil_party[message_id]['max_player']}명중 {len(civil_party_level)}명 고름", value=f"선택 안한 멤버:\n```\n{value}```", inline=False)

        await var.civil_party[message_id]['message'].edit(content=var.civil_party[message_id]['message'].content, embeds=embed)

    if member.id == var.civil_party[message_id]['author'] and emoji in var.shuffle_emoji and not remove_only:
        message = await var.bot.get_channel(int(var.civil_party[message_id]['message'].channel_id)).fetch_message(int(var.civil_party[message_id]['message'].id))
        if len(civil_party_level) < var.civil_party[message_id]['max_player']:
            await send_to(message, "모든 멤버가 실력을 선택하지 않았습니다!", delete_after=10)
            return

        if len(civil_party_postion) < var.civil_party[message_id]['max_player']:
            await send_to(message, "포지션을 선택하지 않은 멤버가 있습니다!", delete_after=10)
            return

        # def _rl():
        #     _list = [1,2,3,4,5,6,7,8,9,10]
        #     shuffle(_list)
        #     return _list[:randint(0,9)]

        # rand_pos = {0:_rl(), 4:_rl(), 3:_rl(),2:_rl(),1:_rl()}
        # _list = [1,2,3,4,5,6,7,8,9]
        # shuffle(_list)
        # rand_level = sorted([_list[0], _list[1]])
        # _list = [1,2,3,4,5,6,7,8,9,10]
        # shuffle(_list)

        # var.civil_party[message_id]['position'] = rand_pos
        # var.civil_party[message_id]['level'] = {2:_list[:rand_level[0]], 1:_list[rand_level[0]:rand_level[1]], 0:_list[rand_level[1]:]}
        game_name = var.civil_party[message_id]['game']
        game = var.games[game_name]
        position_mismatch = []
        position_dic = {}
        for i in var.civil_party[message_id]['position']:
            if len(var.civil_party[message_id]['position'][i]) < 2:
                position_mismatch.append(i)

            for j in var.civil_party[message_id]['position'][i]:
                if j not in position_dic.keys():
                    position_dic[j] = [i]
                else:
                    position_dic[j].append(i)

        position_dic = dict(sorted(position_dic.items(), key=lambda x: x))
        for i in position_dic:
            shuffle(position_dic[i])

        if len(position_mismatch) > 0:
            msg = "하나 이상의 포지션이 불균형합니다." + game['position'][position_mismatch[0]]
            for i in range(1,len(position_mismatch)):
                msg += ', ' + game['position'][position_mismatch[0]]
            await send_to(message, "하나 이상의 포지션이 불균형합니다.", delete_after=10)
            return

        try:
            loop = 0
            while True:
                loop += 1
                if loop > 20:
                    await send_to(message, "20번 넘게 시도했지만 팀을 배정할 수 없었어요... 포지션이나 실력을 바꿔보세요.", delete_after=10)
                    return
                team = [{'position':{}, 'players':[]}, {'position':{}, 'players':[]}]
                for i in var.civil_party[message_id]['level']:
                    shuffle(var.civil_party[message_id]['level'][i])

                cnt = 0
                for i in var.civil_party[message_id]['level'][2]:
                    team[cnt%2]['players'].append(i)
                    for j in position_dic[i]:
                        if j not in team[cnt%2]['position'].keys():
                            team[cnt%2]['position'][j] = [i]
                        else:
                            team[cnt%2]['position'][j].append(i)
                    cnt += 1

                cnt += 1
                if len(var.civil_party[message_id]['level'][1]) > 0:
                    team[cnt%2]['players'].append(var.civil_party[message_id]['level'][1][0])
                    for j in position_dic[var.civil_party[message_id]['level'][1][0]]:
                        if j not in team[cnt%2]['position'].keys():
                            team[cnt%2]['position'][j] = [var.civil_party[message_id]['level'][1][0]]
                        else:
                            team[cnt%2]['position'][j].append(var.civil_party[message_id]['level'][1][0])

                for i in range(1,len(var.civil_party[message_id]['level'][1])):
                    team[cnt%2]['players'].append(var.civil_party[message_id]['level'][1][i])
                    for j in position_dic[var.civil_party[message_id]['level'][1][i]]:
                        if j not in team[cnt%2]['position'].keys():
                            team[cnt%2]['position'][j] = [var.civil_party[message_id]['level'][1][i]]
                        else:
                            team[cnt%2]['position'][j].append(var.civil_party[message_id]['level'][1][i])
                    cnt += 1

                cnt += 1
                for i in var.civil_party[message_id]['level'][0]:
                    if len(team[cnt%2]['players']) >= var.civil_party[message_id]['max_player']/2:
                        cnt += 1

                    team[cnt%2]['players'].append(i)
                    for j in position_dic[i]:
                        if j not in team[cnt%2]['position'].keys():
                            team[cnt%2]['position'][j] = [i]
                        else:
                            team[cnt%2]['position'][j].append(i)

                run = True
                for i in team:
                    if len(i['position']) < len(game['position']):
                        run = False

                _list = [{}, {}]
                cnt = 0
                for i in team:
                    i['position'] = dict(sorted(i['position'].items(), key=lambda x: x[0]))

                    for j in i['position']:
                        shuffle(i['position'][j])

                    for j in i['position']:
                        try:
                            temp = i['position'][j][0]
                            _list[cnt][j] = temp
                            for k in i['position']:
                                try:
                                    i['position'][k].remove(temp)
                                except:
                                    pass
                        except:
                            run = False
                            break
                    cnt += 1

                if run:
                    break
        except:
            await send_to(message, "에러가 발생했습니다. "+var.shuffle_emoji[0]+"를 눌러 다시 시도해주세요!")
            return


        embed = interactions.Embed(title=f"{author.name}님의 {var.civil_party[message_id]['game']}내전", description="팀 배정됨!")

        cnt = 0
        for team in _list:
            cnt += 1
            msg = ''
            for position in team:
                player = team[position]
                try:
                    player = await interactions.get(var.client, interactions.Member, object_id=int(player), parent_id=int(var.civil_party[message_id]['message'].guild_id))
                    player.name
                except:
                    pass
                msg += game['position'][position] + ': \n' + str(player) + '\n\n'

            embed.add_field(name=f'팀 {cnt}', value=msg)

        await var.civil_party[message_id]['message'].edit(content = '', embeds=embed)
        await clear_reaction_of(var.civil_party[message_id]['message'])
        var.civil_party.pop(message_id)
