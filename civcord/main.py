import discord

import cmd_handler


class MyClient(discord.Client):
    def __init__(self):
        super().__init__()
        old_state = getattr(self, 'cmd_state', None)
        self.cmd_state = cmd_handler.init_state(self, old_state)

    async def on_ready(self):
        print('Logged in as', self.user.name, self.user.id)

    async def on_member_join(self, member):
        await cmd_handler.handle_member_join(self.cmd_state, member)

    async def on_message(self, message):
        if message.author == self.user:
            return
        await cmd_handler.handle_message(self.cmd_state, message)

    async def on_reaction_add(self, reaction, user):
        if user == self.user:
            return
        await cmd_handler.handle_reaction_change(self.cmd_state, reaction, user)

    async def on_reaction_remove(self, reaction, user):
        if user == self.user:
            return
        await cmd_handler.handle_reaction_change(self.cmd_state, reaction, user)


def main():
    import os
    import sys
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print('No token supplied, set DISCORD_TOKEN env.var.', file=sys.stderr)
        sys.exit(1)
    client = MyClient()
    client.run(token)


if __name__ == "__main__":
    main()
