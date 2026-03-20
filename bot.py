import discord
import asyncio
import os
import random  # <-- Thêm thư viện này để bốc thăm
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
        # Ép kiểu thành list nếu chỉ truyền 1 ID vào, để dễ check
        self.vip_ids = [vip_ids] if isinstance(vip_ids, int) else vip_ids
        
        # <-- THÊM: Ép kiểu nhạc thành list để lỡ có nhiều bài thì lát random
        self.music_file = music_file if isinstance(music_file, list) else [music_file]
        
        self.bot_loop = None # Sẽ khởi tạo lúc bot ready

    async def on_ready(self):
        self.bot_loop = asyncio.get_running_loop()
        print(f"[ONLINE] Vệ sĩ {self.user} đã sẵn sàng phục vụ VIP IDs: {self.vip_ids}")

    async def on_voice_state_update(self, member, before, after):
        # Bỏ qua nếu là chính nó (bot)
        if member == self.user:
            return

        # Chỉ kích hoạt khi có người vào phòng LOBBY
        if after.channel is not None and after.channel.name == "LOBBY":
            if before.channel is None or before.channel.name != "LOBBY":
                
                # --- KIỂM TRA ĐÚNG CHỦ NHÂN MỚI CHẠY ---
                if member.id not in self.vip_ids:
                    return # Không phải chủ nhân -> Lơ đẹp!
                
                # <-- THÊM: Bốc random 1 bài hát trong danh sách nhạc của sếp này
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
                    # <-- SỬA: Chạy bài nhạc vừa bốc được
                    raw_source = discord.FFmpegPCMAudio(current_music, executable="ffmpeg", **FFMPEG_OPTIONS)
                    vol_source = discord.PCMVolumeTransformer(raw_source, volume=0.74)

                    def after_playing(error):
                        if error:
                            print(f"Lỗi FFmpeg: {error}")
                        # Dùng loop đã lưu để disconnect an toàn
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

async def main():
    # Sửa lại truyền tuple (id1, id2) cho bot_ha
    bot_duyanh = BodyguardBot(vip_ids=469547032688984075, music_file="da.mp3")
    bot_kienphat = BodyguardBot(vip_ids=1047924907805253692, music_file="anhkiemphat.mp3")
    bot_huyly = BodyguardBot(vip_ids=916156563931168808, music_file="emhuyly.mp3")
    bot_giabao = BodyguardBot(vip_ids=508480474381942794, music_file="anhgiabao.mp3")
    bot_dung = BodyguardBot(vip_ids=843320963298623568, music_file="anhtrandung.mp3")
    
    # <-- SỬA: Truyền hẳn 1 list 2 bài cho kienphat2 để nó random
    bot_kienphat2 = BodyguardBot(vip_ids=1231976395605807146, music_file=["da.mp3", "da(1).mp3"])
    
    # Gộp 2 ID vào 1 Tuple cho bot_ha
    bot_ha = BodyguardBot(vip_ids=(1482033286027935796, 952619435095629896), music_file="ha.mp3")
    
    # Khởi chạy đa luồng các bot
    await asyncio.gather(
        bot_duyanh.start(os.environ.get("BOT_DUYANH", "")),
        bot_kienphat.start(os.environ.get("BOT_KIENPHAT", "")),
        bot_huyly.start(os.environ.get("BOT_HUY", "")),
        bot_giabao.start(os.environ.get("BOT_GIABAO", "")),
        bot_kienphat2.start(os.environ.get("BOT_DUYANH", "")), 
        bot_ha.start(os.environ.get("BOT_HA", "")),
        bot_dung.start(os.environ.get("BOT_DUNG", ""))
    )

# Khởi động Web Server ảo
keep_alive()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Đã tắt toàn bộ hệ thống Bot.")
