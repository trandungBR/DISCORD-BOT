import discord
from discord.ext import commands
import asyncio
import os
from keep_alive import keep_alive 

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

MUSIC_PATH = "Anh DUy Anh (mp3cut.net).mp3"
TOKEN = os.environ.get("DISCORD_TOKEN")

FFMPEG_OPTIONS = {
    'options': '-vn',
}

@bot.event
async def on_ready():
    print(f'--- DJ {bot.user} đã sẵn sàng với âm lượng 74%! ---')

@bot.event
async def on_voice_state_update(member, before, after):
    if member == bot.user:
        return

    if after.channel is not None and after.channel.name == "LOBBY":
        if before.channel is None or before.channel.name != "LOBBY":
            
            voice_client = discord.utils.get(bot.voice_clients, guild=after.channel.guild)

            if voice_client and voice_client.is_connected():
                if voice_client.is_playing():
                    return
            else:
                try:
                    voice_client = await after.channel.connect()
                except Exception as e:
                    print(f"Lỗi kết nối Voice: {e}")
                    return

            try:
                raw_source = discord.FFmpegPCMAudio(MUSIC_PATH, executable="ffmpeg", **FFMPEG_OPTIONS)
                
                vol_source = discord.PCMVolumeTransformer(raw_source, volume=0.74)

                def after_playing(error):
                    if error:
                        print(f"Lỗi FFmpeg: {error}")
                    coro = voice_client.disconnect()
                    fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
                    try:
                        fut.result()
                    except:
                        pass

                if not voice_client.is_playing():
                    voice_client.play(vol_source, after=after_playing)
                    print(f"Đang phát nhạc chào mừng {member.name} với âm lượng 74%")

            except Exception as e:
                print(f"Lỗi hệ thống phát nhạc: {e}")
                if voice_client:
                    await voice_client.disconnect()

keep_alive()

if TOKEN:
    bot.run(TOKEN)
else:
    print("LỖI: Chưa cấu hình DISCORD_TOKEN trên Render!")