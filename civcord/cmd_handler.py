import asyncio
import discord
import random
import sys
from collections import namedtuple
from importlib import reload

import emojis
import world
from utils import Autodict


ttk2_strings = [l.strip().replace(r'\n', '\n') for l in open(
    'ttk2_reddit_civcraft_1k.phrases').read().split('\n') if l.strip()]


Command = namedtuple('Command', 'func name args desc hidden')

commands = {}


def register_cmd(name, args=None, desc=None, hidden=False):
    def decorate(func):
        commands[name] = Command(func, name, args, desc, hidden)
        return func
    return decorate


def restrict_cmd_to_roles(*allowed_roles):
    def decorate(func):
        async def wrapper(state, message, *args, **kwargs):
            for role in message.author.roles:
                if role.name in allowed_roles:
                    return await func(state, message, *args, **kwargs)
            else:
                await respond_on_react(
                    state, message, emojis.no_entry_sign,
                    'Not authenticated. You need one of these roles: '
                    + ', '.join(allowed_roles))
        return wrapper
    return decorate


def fmt_cmd_usage(state, name):
    desc = commands[name].desc
    desc_str = ''
    if desc:
        desc_str = ' ' + desc
    args = commands[name].args
    args_str = ''
    if args:
        args_str = ' ' + args
    return '`{state.prefix}{name}{args_str}`{desc_str}'.format(**locals())


@register_cmd('help', args='[command]', desc='Show help for command, or for all commands')
async def cmd_help(state, message, cmd_name=None, *args):
    if not cmd_name:
        responses = []
        for cmd in commands.values():
            if cmd.hidden:
                continue
            responses.append(fmt_cmd_usage(state, cmd.name))
        await message.channel.send('\n'.join(responses))
        return

    if cmd_name in commands:
        await message.channel.send('Usage: ' + fmt_cmd_usage(state, cmd_name))
    else:
        await message.channel.send('No such command: {cmd_name}\nTry {state.prefix}help'.format(**locals()))


@register_cmd('reload', desc='reload commands', hidden=True)
@restrict_cmd_to_roles('Voice of ttk2')
async def cmd_reload(state, message, *args):
    try:
        reload(sys.modules[__name__])
        sys.modules[__name__].init_state(state.client, state)
        await respond_on_react(
            state, message, emojis.checkmark,
            'Successfully reloaded the commands module')
    except Exception as e:
        await respond_on_react(
            state, message, emojis.no_entry_sign,
            'Error while reloading: {}'.format(e))


@register_cmd('delete', args='<userid> [count]', desc='delete all (or last `count`) messages by that user in this channel')
@restrict_cmd_to_roles('Voice of ttk2')
async def cmd_delete(state, message, userid_str, delete_count=None, *args):
    if len(userid_str) != 21:
        await respond_on_react(
            state, message, emojis.no_entry_sign,
            'Invalid userid {}, use a player mention: <@{}>'
            .format(userid_str, state.client.user.id))
        return
    userid = int(userid_str[2:-1])  # <@123456789012345678>
    with message.channel.typing():
        n_deleted = 0
        async for msg in message.channel.history(limit=None):
            if msg.author.id == userid:
                await msg.delete()
                n_deleted += 1
                if delete_count and n_deleted >= int(delete_count):
                    break
        await message.channel.send('Deleted {} messages by <@{}>'.format(n_deleted, userid))


@register_cmd('react', args='<emoji> [emoji...]', desc='react with all these emoji')
async def cmd_react(state, message, *emojis):
    for emoji in emojis:
        await message.add_reaction(emoji)


@register_cmd('say', desc='ttk2 Reddit quote')
async def cmd_say(state, message, *args):
    await message.channel.send(random.choice(ttk2_strings))


@register_cmd('sleep', desc='sleep 5s')
async def cmd_sleep(state, message, *args):
    with message.channel.typing():
        await asyncio.sleep(5.0)
        await message.channel.send('Done sleeping.')


@register_cmd('reworld', desc='recreate world from scratch')
@restrict_cmd_to_roles('Voice of ttk2')
async def cmd_reworld(state, message, *args):
    await message.add_reaction(emojis.hourglass_flowing_sand)
    state.world = world.create_new()
    await message.add_reaction(emojis.checkmark)
    await message.remove_reaction(emojis.hourglass_flowing_sand, state.client.user)
    await respond_on_react(
        state, message, emojis.checkmark,
        'Successfully recreated the world')


@register_cmd('hi', desc='join game')
async def cmd_hi(state, message, *args):
    player = state.world.get_or_create_player(message.author.id)
    await message.channel.send(message.author.display_name + ' joined the game world')


@register_cmd('inventory', desc='show carried items')
async def cmd_inventory(state, message, *args):
    player = state.world.get_or_create_player(message.author.id)
    items = player.inventory
    if not items:
        await message.channel.send(message.author.display_name + ' has no items')
    else:
        msg = message.author.display_name + ' has these items:'
        for i, item in enumerate(items):
            msg += '\n`{}`: {}'.format(i, item)
        await message.channel.send(msg)


@register_cmd('craft', args='<item> [item...]', desc='combine items')
async def cmd_craft(state, message, *args):
    player = state.world.get_or_create_player(message.author.id)
    await message.channel.send('TODO: implement crafting')
    await message.add_reaction(emojis.construction_site)


@register_cmd('travel', args='<destination>', desc='travel to destination channel')
async def cmd_travel(state, message, destination=None, *args):
    if not destination:
        await message.channel.send('Usage: ' + fmt_cmd_usage(state, 'travel'))
    else:
        destination = destination.lstrip('#')

        guild = message.guild
        author = message.author

        dest_channel = discord.utils.get(guild.channels, name=destination)

        if dest_channel == message.channel:
            await message.channel.send('You are already in <#{}>'.format(dest_channel.id))
            await message.add_reaction(emojis.no_entry_sign)
            return

        player = state.world.get_or_create_player(author.id)
        # XXX for testing, create region if not exists

        # for testing, create channel if not exists
        if not dest_channel:
            category = discord.utils.get(guild.categories, name='map')
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                # guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            dest_channel = await guild.create_text_channel(
                destination,
                overwrites=overwrites, category=category, reason='cmd_travel')

        # XXX add player to destination region
        # XXX remove player from current region

        await dest_channel.set_permissions(author, read_messages=True, send_messages=True)
        await message.channel.set_permissions(author, overwrite=None)

        await message.channel.send('{} travelled to <#{}>'.format(author.display_name, dest_channel.id))
        await dest_channel.send('{} arrived'.format(author.display_name))


def init_state(client, state):
    if not state:
        state = Autodict()
    if not state.prefix:
        state.prefix = ','
    if not state.client:
        state.client = client
    if not state.world:
        state.world = world.create_new()
    return state


async def handle_message(state, message):
    if not message.content.startswith(state.prefix):
        return
    cmd_name, *args = message.content[len(state.prefix):].split(' ')
    if not cmd_name:
        return

    if cmd_name in commands:
        print('Running command', message.author, message.content)
        try:
            await commands[cmd_name].func(state, message, *args)
        except Exception as e:
            print('Handler for', cmd_name, 'failed on', message.content)
            await message.add_reaction(emojis.no_entry_sign)
            raise e
    else:
        await respond_on_react(
            state, message, emojis.question_mark,
            'No such command `{state.prefix}{cmd_name}`, try `{state.prefix}help`'.format(**locals()))


async def handle_reaction_change(state, reaction, user):
    pass


async def handle_member_join(state, member):
    pass


async def respond_on_react(state, message, emoji, response, restrict_to_user=False):
    await message.add_reaction(emoji)

    def check(reaction, user):
        return (not restrict_to_user or user == message.author) \
            and str(reaction.emoji) == emoji

    try:
        reaction, user = await state.client.wait_for(
            'reaction_add', check=check, timeout=60)
    except asyncio.TimeoutError:
        pass
    else:
        await message.channel.send(response)

    await message.remove_reaction(emoji, state.client.user)
