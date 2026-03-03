import discord
import asyncio
import os
from keep_alive import keep_alive

# Bật Intents (Chỉ cần Voice States là đủ để bot vào phòng)
intents = discord.Intents.default()
intents.voice_states = True

FFMPEG_OPTIONS = {'options': '-vn'}

# ==========================================
# KHỞI TẠO CLASS "VỆ SĨ BOT"
# ==========================================
class BodyguardBot(discord.Client):
    def __init__(self, vip_id, music_file):
        super().__init__(intents=intents)
        self.vip_id = vip_id          # ID của người mà bot này phục vụ
        self.music_file = music_file  # Bài nhạc riêng của người đó

    async def on_ready(self):
        print(f"[ONLINE] Vệ sĩ {self.user} đã sẵn sàng phục vụ VIP ID: {self.vip_id}")

    async def on_voice_state_update(self, member, before, after):
        # Bỏ qua nếu là chính nó (bot)
        if member == self.user:
            return

        # Chỉ kích hoạt khi có người vào phòng LOBBY
        if after.channel is not None and after.channel.name == "LOBBY":
            if before.channel is None or before.channel.name != "LOBBY":
                
                # --- KIỂM TRA ĐÚNG CHỦ NHÂN MỚI CHẠY ---
                if member.id != self.vip_id:
                    return # Không phải chủ nhân -> Lơ đẹp!
                
                print(f"[VIP IN] Chủ nhân {member.name} đã tới. {self.user} đang bật nhạc '{self.music_file}'...")

                # Kiểm tra kết nối voice của con bot hiện tại
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
                    # Phát bài nhạc được giao cho con bot này
                    raw_source = discord.FFmpegPCMAudio(self.music_file, executable="ffmpeg", **FFMPEG_OPTIONS)
                    vol_source = discord.PCMVolumeTransformer(raw_source, volume=0.74)

                    def after_playing(error):
                        if error:
                            print(f"Lỗi FFmpeg: {error}")
                        coro = voice_client.disconnect()
                        fut = asyncio.run_coroutine_threadsafe(coro, self.loop)
                        try:
                            fut.result()
                        except:
                            pass

                    if not voice_client.is_playing():
                        voice_client.play(vol_source, after=after_playing)
                        print(f"[PLAYING] {self.user} đang phát nhạc cho {member.name}")

                except Exception as e:
                    print(f"Lỗi hệ thống phát nhạc: {e}")
                    if voice_client:
                        await voice_client.disconnect()

async def main():
    bot_duyanh = BodyguardBot(vip_id=469547032688984075, music_file="Anh DUy Anh.mp3")
    bot_kienphat = BodyguardBot(vip_id=1047924907805253692, music_file="anhkiemphat.mp3")
    bot_huyly = BodyguardBot(vip_id=916156563931168808, music_file="emhuylys.mp3")
    bot_giabao = BodyguardBot(vip_id=508480474381942794, music_file="anhgiabao.mp3")
    await asyncio.gather(
        bot_duyanh.start(os.environ.get("BOT_DUYANH", "")),
        bot_kienphat.start(os.environ.get("BOT_KIENPHAT", "")),
        bot_huyly.start(os.environ.get("BOT_HUY", ""))
        bot_gibao.start(os.environ.get("BOT_GIABAO", ""))
    )
    )

# Khởi động Web Server ảo
keep_alive()

# Kích hoạt Event Loop chính của Python
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Đã tắt toàn bộ hệ thống Bot.")
