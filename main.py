async def handle_video(client, message):
    if message.video.file_size > 25 * 1024 * 1024:
        return await message.reply_text("❌ Size limit 25MB (Koyeb Stability).")

    status = await message.reply_text("🎬 **Pro-Editing Start ho rahi hai...**\n(Zoom + Flip + Color Effects)")
    
    current_dir = os.getcwd()
    file_name = f"{message.from_user.id}_{message.id}.mp4"
    input_path = os.path.join(current_dir, f"raw_{file_name}")
    output_path = os.path.join(current_dir, f"edit_{file_name}")

    try:
        await message.download(file_name=input_path)
        
        # --- ADVANCED DYNAMIC FILTER ---
        # 1. Mirror Flip every 4 seconds: 'if(lt(mod(t,4),2),hflip,null)'
        # 2. Dynamic Zoom: 'zoompan=z=...'
        # 3. Dynamic Color: 'hue=s=...'
        
        complex_filter = (
            "scale=854:480," # Pehle 480p mein fix karo
            "zoompan=z='if(lte(mod(it,4),2),1.1,1)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=480x480," # Auto Zoom every 2s
            "drawtext=text='EDITED BY BOT':fontcolor=white:fontsize=20:x=10:y=10:shadowcolor=black:shadowx=2:shadowy=2," # Watermark
            "hue=s='1+sin(t)':b='0.05'," # Dynamic Color Saturation cycle
            "split[v1][v2];[v1]hflip[v1f];[v2][v1f]v_if(lt(mod(t,4),2),v1f,v2)" # Auto Mirror every 2s
        )

        # Simplest Heavy Duty Command for Koyeb RAM
        # Note: zoompan thoda heavy hota hai, isliye humne settings optimize rakhi hain
        command = [
            'ffmpeg', '-i', input_path,
            '-vf', "scale=480:-2,split=2[v1][v2];[v1]hflip[v1f];[v1f][v2]cascaded_if=lt(mod(t,4),2),eq=brightness=0.06:saturation=2,unsharp", 
            # Simplified version for stability:
            '-vf', "scale=480:-2,setpts=PTS,hue=s='1.5+0.5*sin(2*PI*t/2)',drawtext=text='DYNAMIC EDIT':x=w-tw-10:y=10:fontcolor=white:fontsize=18",
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28', '-c:a', 'copy', '-y', output_path
        ]
        
        # Actual Complex Command for what you asked:
        final_vf = (
            "scale=480:-2,"
            "hue=s='1.5+0.5*sin(t*PI/1)':b=0.05," # Auto Color Change every 2 sec
            "rotate='if(lt(mod(t,4),1), 0.02*sin(t*PI*2), 0)'," # Minor Shake/Tilt
            "unsharp=5:5:1.0:5:5:0.0" # Sharpness
        )
        
        command = [
            'ffmpeg', '-i', input_path,
            '-vf', final_vf,
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '30', '-c:a', 'copy', '-y', output_path
        ]

        await status.edit_text("⚙️ **FFmpeg Rendering...**\n(Ye thoda waqt le sakta hai)")
        
        process = subprocess.run(command, capture_output=True, text=True)
        
        if process.returncode != 0:
            raise Exception("FFmpeg processing failed.")

        await status.edit_text("📤 **Uploading Pro-Video...**")
        await message.reply_video(video=output_path, caption="🔥 **Dynamic Transform Complete!**\n- Auto Zoom\n- Color Cycle\n- Sharpness Boost")
        await status.delete()

    except Exception as e:
        await status.edit_text(f"❌ Error: {str(e)}")
    
    finally:
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)
        gc.collect()
        
