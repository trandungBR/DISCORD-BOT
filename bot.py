import discord
import asyncio
import os
from keep_alive import keep_alive

# Bật Intents
intents = discord.Intents.default()
intents.voice_states = True

FFMPEG_OPTIONS = {'options': '-vn'}

class BodyguardBot(discord.Client):
    def __init__(self, vip_ids, music_file):
        super().__init__(intents=intents)
        self.vip_ids = [vip_ids] if isinstance(vip_ids, int) else vip_ids
        self.music_file = music_file
        self.bot_loop = None 

    async def on_ready(self):
        self.bot_loop = asyncio.get_running_loop()
        print(f"[ONLINE] Vệ sĩ {self.user} đã lên sóng! Nhạc: {self.music_file} | Phục vụ VIP: {self.vip_ids}")

    async def on_voice_state_update(self, member, before, after):
        if member == self.user:
            return

        # Bật log này lên để xem có ai ra/vào bất kỳ phòng nào không
        # Nếu dòng này không hiện, nghĩa là Bot chưa được cấp quyền đọc Voice Channel trong Developer Portal
        if after.channel is not None and before.channel != after.channel:
            print(f"[DEBUG] {member.name} vừa nhảy vào phòng: {after.channel.name}")

        # Tối ưu: Ép tên phòng về chữ in hoa để so sánh, tránh lỗi gõ nhầm
        if after.channel is not None and after.channel.name.upper() == "LOBBY":
            if before.channel is None or before.channel.name.upper() != "LOBBY":
                
                if member.id not in self.vip_ids:
                    print(f"[BỎ QUA] {member.name} vào LOBBY nhưng không phải VIP của bot {self.user}")
                    return 
                
                print(f"[VIP IN] Chủ tướng {member.name} giá lâm! {self.user} chuẩn bị lên nhạc '{self.music_file}'...")

                voice_client = discord.utils.get(self.voice_clients, guild=after.channel.guild)

                if voice_client and voice_client.is_connected():
                    if voice_client.is_playing():
                        return
                else:
                    try:
                        voice_client = await after.channel.connect()
                        print(f"[KẾT NỐI] {self.user} đã vào phòng voice thành công!")
                    except Exception as e:
                        print(f"[LỖI VOICE] {self.user} không vào được phòng: {e}")
                        return

                try:
                    raw_source = discord.FFmpegPCMAudio(self.music_file, executable="ffmpeg", **FFMPEG_OPTIONS)
                    vol_source = discord.PCMVolumeTransformer(raw_source, volume=0.74)

                    def after_playing(error):
                        if error:
                            print(f"Lỗi FFmpeg: {error}")
                        if self.bot_loop and voice_client:
                            coro = voice_client.disconnect()
                            asyncio.run_coroutine_threadsafe(coro, self.bot_loop)
                            print(f"[DISCONNECT] {self.user} đã phát xong và rời phòng.")

                    if not voice_client.is_playing():
                        voice_client.play(vol_source, after=after_playing)
                        print(f"[PLAYING] Đang xập xình bài {self.music_file} cho sếp {member.name}")

                except Exception as e:
                    print(f"[LỖI NHẠC] Không thể phát nhạc: {e}")
                    if voice_client:
                        await voice_client.disconnect()

# Hàm bọc an toàn: Con nào rớt mạng hoặc lỗi Token thì con khác vẫn sống
async def safe_start(bot, token, name):
    if not token:
        print(f"[CẢNH BÁO] Biến môi trường {name} đang trống! Bỏ qua bot này.")
        return
    try:
        await bot.start(token)
    except Exception as e:
        print(f"[CRASH TỪNG PHẦN] Bot {name} chết ngỏm vì lỗi: {e}")

async def main():
    bot_duyanh = BodyguardBot(vip_ids=469547032688984075, music_file="da.mp3")
    bot_kienphat = BodyguardBot(vip_ids=1047924907805253692, music_file="anhkiemphat.mp3")
    bot_huyly = BodyguardBot(vip_ids=916156563931168808, music_file="emhuyly.mp3")
    bot_giabao = BodyguardBot(vip_ids=508480474381942794, music_file="anhgiabao.mp3")
    bot_kienphat2 = BodyguardBot(vip_ids=1231976395605807146, music_file="da.mp3")
    bot_ha = BodyguardBot(vip_ids=(1482033286027935796, 952619435095629896), music_file="ha.mp3")
    bot_dung = BodyguardBot(vip_ids=843320963298623568, music_file="anhtrandung.mp3")
    
    await asyncio.gather(
        safe_start(bot_duyanh, os.environ.get("BOT_DUYANH", ""), "BOT_DUYANH"),
        safe_start(bot_kienphat, os.environ.get("BOT_KIENPHAT", ""), "BOT_KIENPHAT"),
        safe_start(bot_huyly, os.environ.get("BOT_HUY", ""), "BOT_HUYLY"),
        safe_start(bot_giabao, os.environ.get("BOT_GIABAO", ""), "BOT_GIABAO"),
        safe_start(bot_kienphat2, os.environ.get("BOT_KIENPHAT2", ""), "BOT_KIENPHAT2"),
        safe_start(bot_ha, os.environ.get("BOT_HA", ""), "BOT_HA"),
        safe_start(bot_dung, os.environ.get("BOT_DUNG", ""), "BOT_DUNG")
    )

keep_alive()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Đã tắt toàn bộ hệ thống Bot.")
