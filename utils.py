import contextlib

from pyrogram import types, filters, Client, errors

convs = {}
info = {}


def conv_flt(conv_level: str):
    async def func(_, __, m: types.Message):
        return convs.get(m.from_user.id) == conv_level

    return filters.create(func, "ConvFilter")


async def download_media(c: Client, m: types.Message):
    chat_id = info.get(m.from_user.id, {}).get("chat_id")
    msg_id = info.get(m.from_user.id, {}).get("msg_id")
    x = await c.get_chat(chat_id)
    msg = await c.get_messages(x.id, msg_id)
    accepted_files = ["AUDIO", "VOICE", "VIDEO", "DOCUMENT", "PHOTO"]
    if msg.media.name not in accepted_files:
        return await m.reply("File ini tidak dapat di ambil")
    text = "Downloading..."
    x = await m.reply(text)
    media = await msg.download(progress=progress_for_pyrogram, progress_args=(x, text))
    text = "Download sukses\nMengupload..."
    upload_msg = await x.reply(text)
    if m.media.value != "video":
        send_media = getattr(m, f"reply_{msg.media.value}")
        return await send_media(
            media,
            progress=progress_for_pyrogram,
            progress_args=(upload_msg, text),
        )
    vid = msg.video
    vid_duration = vid.duration
    vid_width = vid.width
    vid_height = vid.height
    vid_thumb = vid.thumbs[0].file_id
    vid_caption = msg.caption
    return await m.reply_video(
        media,
        caption=vid_caption,
        duration=vid_duration,
        width=vid_width,
        height=vid_height,
        thumb=vid_thumb,
        progress=progress_for_pyrogram,
        progress_args=(upload_msg, text),
    )


async def progress_for_pyrogram(cur, tot, m: types.Message, text: str):
    with contextlib.suppress(errors.MessageNotModified):
        await m.edit(f"{text}\n{(cur * 100 / tot):.1f}%")
