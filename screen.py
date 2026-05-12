import discord
from discord.ext import commands
from playwright.async_api import async_playwright
from PIL import Image
import io
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

async def capture_and_split(url, part_height=1000):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        screenshot_bytes = await page.screenshot(full_page=True)
        await browser.close()
        img = Image.open(io.BytesIO(screenshot_bytes))
        width, height = img.size
        parts = []
        for i in range(0, height, part_height):
            box = (0, i, width, min(i + part_height, height))
            part_img = img.crop(box)
            img_byte_arr = io.BytesIO()
            part_img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            parts.append(img_byte_arr)
        return parts

@bot.command()
async def shot(ctx, url: str):
    await ctx.send("In progress...")

    try:
        image_parts = await capture_and_split(url)
        for i, part in enumerate(image_parts):
            file = discord.File(fp=part, filename=f"part_{i}.png")
            await ctx.send(content=f"Part {i+1}/{len(image_parts)}", file=file)

    except Exception as e:
        await ctx.send(f"Error: {e}")

bot.run('YOUR_BOT_TOKEN')
