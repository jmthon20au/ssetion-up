# bot_string_session_optional.py
# -*- coding: utf-8 -*-

from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PhoneNumberInvalidError

# API ID و HASH الافتراضي
default_api_id = 24484469
default_api_hash = "f864ff1bb135fe7faa895d260ce57ba9"

# التوكن مال البوت
bot_token = "8377625839:AAGfk82qlExU8ggHe82L_1jr3Lldqd_ZpQY"

# نشغل البوت
bot = TelegramClient("bot_session", default_api_id, default_api_hash).start(bot_token=bot_token)

# مكان نخزن الجلسات
bot.session_cache = {}

# حقوق
CREDITS = "\n\n👨‍💻 بواسطة: @altaee_z | جميع الحقوق محفوظة ✅"


@bot.on(events.NewMessage(pattern="/start"))
async def start_handler(event):
    await event.respond(
        "👋 أهلاً بيك\n"
        "استخدم /session لاستخراج كود الجلسة."
        f"{CREDITS}",
        buttons=[Button.url("📢 تابعنا", url="https://t.me/my00002")]
    )


@bot.on(events.NewMessage(pattern="/session"))
async def session_handler(event):
    user_id = event.sender_id

    async with bot.conversation(user_id, timeout=180) as conv:
        await conv.send_message(
            "🔑 تريد تدخل API ID و API HASH مالتك؟\n"
            "➡️ إذا تريد دخلهم (سطرين).\n"
            "➡️ إذا لا اكتب (تخطي)."
            f"{CREDITS}"
        )

        msg1 = await conv.get_response()

        if msg1.raw_text.strip().lower() == "تخطي":
            api_id = default_api_id
            api_hash = default_api_hash
        else:
            try:
                api_id = int(msg1.raw_text.strip())
                await conv.send_message("أرسل الآن API HASH:")
                msg2 = await conv.get_response()
                api_hash = msg2.raw_text.strip()
            except:
                await conv.send_message("❌ خطأ بالمدخلات. أعد المحاولة." + CREDITS)
                return

        # تسجيل الدخول بالحساب
        client = TelegramClient(StringSession(), api_id, api_hash)
        await client.connect()

        if not await client.is_user_authorized():
            await conv.send_message("📱 أرسل رقم موبايلك (مثال: +96477XXXXXXX):")
            phone = (await conv.get_response()).raw_text.strip()

            try:
                await client.send_code_request(phone)
            except PhoneNumberInvalidError:
                await conv.send_message("❌ رقم الموبايل غير صحيح." + CREDITS)
                await client.disconnect()
                return

            await conv.send_message("✉️ دخل الكود اللي وصلك:\n💡 تقدر تدزه مجزأ مثل: 1 2 3 4 5")
            code = (await conv.get_response()).raw_text.strip()
            code = code.replace(" ", "")  # تنظيف الكود إذا كان بي مسافات

            try:
                await client.sign_in(phone, code)
            except PhoneCodeInvalidError:
                await conv.send_message("❌ الكود غلط أو منتهي." + CREDITS)
                await client.disconnect()
                return
            except SessionPasswordNeededError:
                await conv.send_message("🔒 عندك كلمة سر 2FA، دخلها:")
                pw = (await conv.get_response()).raw_text.strip()
                await client.sign_in(password=pw)

        # إذا وصلنا هنا → تسجيل الدخول ناجح
        session_str = client.session.save()
        me = await client.get_me()

        # إرسال الكود داخل البوت مباشرة
        await conv.send_message(
            f"✅ تم استخراج كود الجلسة:\n\n`{session_str}`\n\n"
            f"👤 الحساب: {me.first_name} {me.last_name or ''}\n"
            f"📱 الرقم: {me.phone}\n"
            f"🆔 ID: `{me.id}`\n\n"
            "اختر إذا تريد أرسله للمحفوظات:"
            f"{CREDITS}",
            buttons=[Button.inline("📩 إرسال للمحفوظات", data=b"tosaved")]
        )

        # نخزن الجلسة مؤقتاً حتى نستعملها بالزر
        bot.session_cache[user_id] = (client, session_str)


@bot.on(events.CallbackQuery(data=b"tosaved"))
async def save_session_handler(event):
    user_id = event.sender_id
    if user_id not in bot.session_cache:
        await event.answer("❌ ماكو جلسة محفوظة.", alert=True)
        return

    client, session_str = bot.session_cache[user_id]

    try:
        await client.send_message("me", f"✅ هذا كود الجلسة:\n\n`{session_str}`" + CREDITS)
        await event.edit("✅ تم إرسال كود الجلسة للمحفوظات." + CREDITS)
    except Exception as e:
        await event.edit(f"⚠️ صار خطأ: {e}" + CREDITS)

    await client.disconnect()
    bot.session_cache.pop(user_id, None)


print("🚀 البوت يشتغل... استعمل /start")
bot.run_until_disconnected()
