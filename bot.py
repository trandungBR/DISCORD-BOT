import discord
import asyncio
import os
import random
from keep_alive import keep_alive

# Bật Intents
intents = discord.Intents.default()
intents.voice_states = True

FFMPEG_OPTIONS = {'options': '-vn'}

class BodyguardBot(discord.Client):
    # Thay đổi cốt lõi: Nhận vào một dictionary (vip_config) thay vì 2 biến rời rạc
    # Ví dụ: { 123456: "nhac1.mp3", 789101: ["nhac1.mp3", "nhac2.mp3"] }
    def __init__(self, vip_config):
        super().__init__(intents=intents)
        self.vip_config = vip_config
        self.bot_loop = None 

    async def on_ready(self):
        self.bot_loop = asyncio.get_running_loop()
        print(f"[ONLINE] Vệ sĩ {self.user} đã lên sóng sẵn sàng phục vụ các VIP!")

    async def on_voice_state_update(self, member, before, after):
        if member == self.user:
            return

        # Log check nhảy phòng
        if after.channel is not None and before.channel != after.channel:
            print(f"[DEBUG] {member.name} vừa nhảy vào phòng: {after.channel.name}")

        # Chỉ hoạt động khi vào phòng LOBBY
        if after.channel is not None and after.channel.name.upper() == "LOBBY":
            if before.channel is None or before.channel.name.upper() != "LOBBY":
                
                # Kiểm tra xem ID của người vào có nằm trong danh sách VIP của bot này không
                if member.id not in self.vip_config:
                    print(f"[BỎ QUA] {member.name} vào LOBBY nhưng không phải VIP của bot {self.user}")
                    return 
                
                # Lấy cấu hình nhạc của riêng người này ra
                user_music_setting = self.vip_config[member.id]
                
                # Nếu cấu hình là một danh sách (list) nhiều bài, thì random 1 bài
                if isinstance(user_music_setting, list):
                    selected_music = random.choice(user_music_setting)
                # Nếu chỉ là 1 bài (chuỗi string), thì lấy luôn
                else:
                    selected_music = user_music_setting

                print(f"[VIP IN] Chủ tướng {member.name} giá lâm! {self.user} bốc trúng bài '{selected_music}'...")

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
                    raw_source = discord.FFmpegPCMAudio(selected_music, executable="ffmpeg", **FFMPEG_OPTIONS)
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
                        print(f"[PLAYING] Đang xập xình bài {selected_music} cho sếp {member.name}")

                except Exception as e:
                    print(f"[LỖI NHẠC] Không thể phát nhạc: {e}")
                    if voice_client:
                        await voice_client.disconnect()

async def safe_start(bot, token, name):
    if not token:
        print(f"[CẢNH BÁO] Biến môi trường {name} đang trống! Bỏ qua bot này.")
        return
    try:
        await bot.start(token)
    except Exception as e:
        print(f"[CRASH TỪNG PHẦN] Bot {name} chết ngỏm vì lỗi: {e}")

async def main():
    # --- CẤU HÌNH BOT DUY ANH SIÊU CẤP ---
    # Phục vụ 2 sếp với rule khác nhau
    config_duyanh = {
        469547032688984075: "da.mp3",                           # Duy Anh: Fix cứng 1 bài
        1231976395605807146: ["da.mp3", "da(1).mp3"]            # Kiến Phát 2: Random 1 trong 2 bài
    }
    bot_duyanh = BodyguardBot(vip_config=config_duyanh)

    # --- CẤU HÌNH CÁC BOT CÒN LẠI ---
    bot_kienphat = BodyguardBot(vip_config={1047924907805253692: "anhkiemphat.mp3"})
    bot_huyly = BodyguardBot(vip_config={916156563931168808: "emhuyly.mp3"})
    bot_giabao = BodyguardBot(vip_config={508480474381942794: "anhgiabao.mp3"})
    
    # Hà có 2 acc, dùng chung 1 bài
    bot_ha = BodyguardBot(vip_config={
        1482033286027935796: "ha.mp3", 
        952619435095629896: "ha.mp3"
    })
    
    bot_dung = BodyguardBot(vip_config={843320963298623568: "anhtrandung.mp3"})
    
    await asyncio.gather(
        safe_start(bot_duyanh, os.environ.get("BOT_DUYANH", ""), "BOT_DUYANH"),
        safe_start(bot_kienphat, os.environ.get("BOT_KIENPHAT", ""), "BOT_KIENPHAT"),
        safe_start(bot_huyly, os.environ.get("BOT_HUY", ""), "BOT_HUYLY"),
        safe_start(bot_giabao, os.environ.get("BOT_GIABAO", ""), "BOT_GIABAO"),
        safe_start(bot_ha, os.environ.get("BOT_HA", ""), "BOT_HA"),
        safe_start(bot_dung, os.environ.get("BOT_DUNG", ""), "BOT_DUNG")
    )

keep_alive()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Đã tắt toàn bộ hệ thống Bot.")
