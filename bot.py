import discord
from discord.ext import commands
import asyncio
import os
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

TOKEN = os.environ.get("DISCORD_TOKEN")

FFMPEG_OPTIONS = {
    'options': '-vn',
}

USER_MUSIC = {
    1047924907805253692: "anhkiemphat.mp3",   
    916156563931168808: "emhuylys.mp3",  
    508480474381942794: "nhacgiabao.mp3",  
}

DEFAULT_MUSIC = "Anh DUy Anh (mp3cut.net).mp3"
# -----------------------------------

@bot.event
async def on_ready():
    print(f'--- DJ {bot.user} đã sẵn sàng phục vụ anh em! ---')

@bot.event
async def on_voice_state_update(member, before, after):
    if member == bot.user:
        return

    if after.channel is not None and after.channel.name == "LOBBY":
        if before.channel is None or before.channel.name != "LOBBY":
            
            # Log ra Terminal để bạn biết ID thật của người vừa vào
            print(f"[LOG] {member.name} (ID: {member.id}) vừa tham gia LOBBY.")

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
                selected_music = USER_MUSIC.get(member.id, DEFAULT_MUSIC)
                
                raw_source = discord.FFmpegPCMAudio(selected_music, executable="ffmpeg", **FFMPEG_OPTIONS)
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
                    print(f"[PLAYING] Đang phát file '{selected_music}' cho {member.name}")

            except Exception as e:
                print(f"Lỗi hệ thống phát nhạc: {e}")
                if voice_client:
                    await voice_client.disconnect()

keep_alive()

if TOKEN:
    bot.run(TOKEN)
else:
    print("LỖI: Chưa cấu hình DISCORD_TOKEN trên Render!")

