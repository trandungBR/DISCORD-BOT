import discord
import asyncio
import os
import random
from keep_alive import keep_alive

# Bật Intents
intents = discord.Intents.default()
intents.voice_states = True

FFMPEG_OPTIONS = {'options': '-vn'}

# ==========================================
# KHỞI TẠO CLASS "VỆ SĨ BOT"
# ==========================================
class BodyguardBot(discord.Client):
    def __init__(self, vip_ids, music_file):
        super().__init__(intents=intents)
        self.vip_ids = [vip_ids] if isinstance(vip_ids, int) else vip_ids
        self.music_file = music_file if isinstance(music_file, list) else [music_file]
        self.bot_loop = None

    async def on_ready(self):
        self.bot_loop = asyncio.get_running_loop()
        print(f"[ONLINE] Vệ sĩ {self.user} đã sẵn sàng phục vụ VIP IDs: {self.vip_ids}")

    async def on_voice_state_update(self, member, before, after):
        if member == self.user:
            return

        if after.channel is not None and after.channel.name == "LOBBY":
            if before.channel is None or before.channel.name != "LOBBY":
                
                if member.id not in self.vip_ids:
                    return 
                
                current_music = random.choice(self.music_file)
                print(f"[VIP IN] Chủ nhân {member.name} đã tới. {self.user} đang bật nhạc '{current_music}'...")

                voice_client = discord.utils.get(self.voice_clients, guild=after.channel.guild)

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
                    raw_source = discord.FFmpegPCMAudio(current_music, executable="ffmpeg", **FFMPEG_OPTIONS)
                    vol_source = discord.PCMVolumeTransformer(raw_source, volume=0.74)

                    def after_playing(error):
                        if error:
                            print(f"Lỗi FFmpeg: {error}")
                        if self.bot_loop and voice_client:
                            coro = voice_client.disconnect()
                            asyncio.run_coroutine_threadsafe(coro, self.bot_loop)

                    if not voice_client.is_playing():
                        voice_client.play(vol_source, after=after_playing)
                        print(f"[PLAYING] {self.user} đang phát nhạc cho {member.name}")

                except Exception as e:
                    print(f"Lỗi hệ thống phát nhạc: {e}")
                    if voice_client:
                        await voice_client.disconnect()

# ==========================================
# HÀM BẮT BOT XẾP HÀNG ĐỂ NÉ LỖI CLOUDFLARE
# ==========================================
async def delayed_start(bot, token, name, delay_seconds):
    if not token:
        print(f"[BỎ QUA] {name} thiếu token đăng nhập.")
        return
    
    if delay_seconds > 0:
        print(f"[XẾP HÀNG] {name} đang chờ {delay_seconds} giây tới lượt...")
        await asyncio.sleep(delay_seconds)
    
    print(f"[ĐANG VÀO] {name} bắt đầu xuất kích!")
    try:
        await bot.start(token)
    except Exception as e:
        print(f"[CRASH TỪNG PHẦN] Á đù, {name} bị văng mạng rồi! Lỗi: {e}")

async def main():
    bot_duyanh = BodyguardBot(vip_ids=469547032688984075, music_file="da.mp3")
    bot_kienphat = BodyguardBot(vip_ids=1047924907805253692, music_file="anhkiemphat.mp3")
    bot_huyly = BodyguardBot(vip_ids=916156563931168808, music_file="emhuyly.mp3")
    bot_giabao = BodyguardBot(vip_ids=508480474381942794, music_file="anhgiabao.mp3")
    bot_dung = BodyguardBot(vip_ids=843320963298623568, music_file="anhtrandung.mp3")
    
    bot_kienphat2 = BodyguardBot(vip_ids=1231976395605807146, music_file=["da.mp3", "da(1).mp3"])
    bot_ha = BodyguardBot(vip_ids=(1482033286027935796, 952619435095629896), music_file="ha.mp3")
    
    # Kèm thêm tên gọi để dễ bắt bệnh
    await asyncio.gather(
        delayed_start(bot_duyanh, os.environ.get("BOT_DUYANH", ""), "BOT_DUYANH", 0),
        delayed_start(bot_kienphat, os.environ.get("BOT_KIENPHAT", ""), "BOT_KIENPHAT", 60),
        delayed_start(bot_huyly, os.environ.get("BOT_HUY", ""), "BOT_HUYLY", 120),
        delayed_start(bot_giabao, os.environ.get("BOT_GIABAO", ""), "BOT_GIABAO", 180),
        delayed_start(bot_kienphat2, os.environ.get("BOT_KIENPHAT2", ""), "BOT_KIENPHAT2", 240), 
        delayed_start(bot_ha, os.environ.get("BOT_HA", ""), "BOT_HA", 300),
        delayed_start(bot_dung, os.environ.get("BOT_DUNG", ""), "BOT_DUNG", 360)
    )

# Khởi động Web Server ảo
keep_alive()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Đã tắt toàn bộ hệ thống Bot.")
