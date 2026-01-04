import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from moviepy import VideoFileClip, concatenate_videoclips, vfx
import time

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Movie Clip bhejo, main 2-sec auto-cut aur zoom ke saath edit kar dunga!')

def process_video(update: Update, context: CallbackContext):
    message = update.message.reply_text("Video mil gayi! Edit ho rahi hai, thoda intezar karein...")
    
    video_file = context.bot.get_file(update.message.video.file_id)
    input_path = "input_video.mp4"
    output_path = "output_edited.mp4"
    video_file.download(input_path)

    try:
        clip = VideoFileClip(input_path)
        # 10 minute movie clip logic
        duration = int(clip.duration)
        segments = []

        for i in range(0, duration, 2):
            start_t = i
            end_t = min(i + 2, duration)
            sub = clip.subclip(start_t, end_t)

            # Har 2 second mein Auto-Zoom effect
            if (i // 2) % 2 == 0:
                # 20% Zoom-in aur center align
                sub = sub.resize(1.2).set_position(("center", "center"))
            
            segments.append(sub)

        # Saare tukdon ko jodna
        final_video = concatenate_videoclips(segments)
        
        # Reels/Shorts ke liye Auto-Resize (Vertical 9:16)
        final_video = final_video.resize(height=1280) # HD Height
        final_video = final_video.crop(x_center=final_video.w/2, width=720)

        # Rendering (Fast settings for Koyeb)
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", threads=4, preset="ultrafast")

        # Video wapas bhejna
        context.bot.send_video(chat_id=update.effective_chat.id, video=open(output_path, 'rb'), caption="Auto-Edited by your Bot")
        message.delete()

    except Exception as e:
        update.message.reply_text(f"Error: {str(e)}")
    
    # Files clean up
    if os.path.exists(input_path): os.remove(input_path)
    if os.path.exists(output_path): os.remove(output_path)

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.video, process_video))
    
    # Koyeb health check ke liye web server (Optional but recommended)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
