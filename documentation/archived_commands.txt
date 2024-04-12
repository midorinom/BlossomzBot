# Insert all member ids into the members table
@slash_command(name="insert_all_member_ids", description="Inserts the id of everyone in the discord server into the members table", scopes=SCOPES)
async def insert_all_member_ids(ctx: SlashContext):
    if not ctx.member.has_role(config_values["leader_role"]) and not ctx.member.has_role(config_values["officer_role"]):
        await ctx.send("You do not have permission to use this command.", ephemeral=True)
    else:
        blossomz_bot_channel = ctx.guild.get_channel(config_values["blossomz_bot_channel_id"])
        await ctx.send("Loading...", ephemeral=True)
        await ctx.delete()

        member_id_array = []
        for member in ctx.guild.members:
            if not member.bot:
                member_id_array.append(member.id)

        for member_id in member_id_array:
            result = query_database(sql_check_if_member_exists(member_id), DATABASE_CREDENTIALS)
            if not result:
                query_database(sql_insert_member(member_id), DATABASE_CREDENTIALS, True)

        await blossomz_bot_channel.send(f"All member ids have been inserted.")