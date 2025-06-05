import discord
import json
import logging

def embed_loader(name: str, file: str) -> discord.Embed | None:
    # need to open the messages file to get all embeds in it
    with open(f"{file}", "r") as f:
        data = json.load(f)

    try:
        # ship to embed_builder to build and return the embed
        embed = embed_builder(data[name])
        return embed
    except KeyError:
        logging.error(f"Embed {name} not found")
        return None

def embed_builder(data: dict) -> discord.Embed:
    # i need to verify if the color is a valid color
    if data.get("color"):
        if isinstance(data["color"], int):
            color = data["color"]
        elif isinstance(data["color"], str):
            color = int(data["color"].replace("#", ""), 16)
        else:
            logging.error(f"Invalid color type: {type(data['color'])}")
            # default to yellow if a valid cant be extracted
            color = 16711680
    else:
        color = 16711680

    embed = discord.Embed(
        title=data.get("title", ""), # set a default title
        description=data.get("description", ""), #
        color=color
    )

    # need to grab all the fields since there could be multiple
    for field in data.get("fields", [])[:25]: # limit to 25 fields
        embed.add_field(
            name=field.get("name", "\u200b"), # zero width spacer so it can be hidden
            value=field.get("value", "\u200b"), # zero width spacer so it can be hidden
            inline=field.get("inline", False) # default to false
        )

    # footer setup
    if "footer" in data:
        embed.set_footer(text=data["footer"].get("text", ""), icon_url=data["footer"].get("icon", None))

    # thumbnail setup
    if "thumbnail" in data:
        embed.set_thumbnail(url=data["thumbnail"])

    # image setup
    if "image" in data:
        embed.set_image(url=data["image"])

    return embed


