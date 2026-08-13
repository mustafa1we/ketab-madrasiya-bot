import os
import time
import re
import logging
import requests
from collections import defaultdict, deque
from openai import OpenAI


# =========================================================
# الإعدادات
# =========================================================

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]

# إذا كان موديلك الحالي يعمل اتركه كما هو من Render Environment.
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")

TG = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


# =========================================================
# Logging
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# =========================================================
# DeepSeek
# =========================================================

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)


# =========================================================
# قائمة المنتجات
#
# مهم:
# الصق هنا قائمة المنتجات والأسعار التي عندك.
# كل سطر:
# اسم المنتج = السعر
#
# تگدر تخلي أكثر من سعر لنفس الاسم.
# =========================================================

PRODUCTS_TEXT = r"""
طين اسطناعي|1000
طباشير|1000
اسامي مواد|2000
رحله|5000
قلم تأشير باكيت|500
دفتر سجل|2500
سجل شفاف|2500
دفتر سجل كبير|2500
دفتر سجل كبير|2500
دفتر سجل كبير|2000
دفتر سجل كبير ملون|2500
دفتر عادي كبير|2000
سجل 100 سيم شفاف|2000
سجل 200 سيم شفاف|3000
سجل 100 سيم خشبي|2000
سجل 200 سيم خشبي|3000
دفتر ملاحضات A4|5000
سجل بدون سيم ازرق ابو 100|2000
سجل بدون سيم ازرق ابو 200|3000
سجل 400 ورقة|7000
صبورة صغيرة|7000
صبورة وسط|8000
صبورة كبيرة|12000
ميدالية مفاتيح|1500
الوان جاف|2500
الوان جاف|2500
الوان جاف|5000
الوان جاف|2000
الوان جاف|2500
قلم صبوره باكيت|500
نبولة قلم صبورة|250
مساحة صبورة|500
صجم كسرية|2000
دفتر بياني|1000
دفتر تلوين كبير|500
دفتر تلوين صغير|250
اطار صورة|3000
فايل كارتوني|10000
فريمات 40*60|4500
فريمات 50*70|6500
فريمات 40*30|3000
فريمات 30*30|2500
فريمات 20*30|2000
فريمات 40*40|3500
دفتر ملاحضات سيم صغير A7|250
دفتر ملاحضات سيم ازرق وسط A6|500
دفتر ملاحضات سيم ازرق 8*5|750
دفتر ملاحضات سيم ازرق 9*7|1000
دفتر ملاحظات ازرق سيم|1500
ورق ملاحضات لاسق الوان اشكال|1000
ورق ملاحضات لاسق|2000
ورق ملاحضات بدون لاسق|3000
دفتر احضار دروس|5000
قران صغير|5000
قران كبير|10000
بطاقه مدرسية|1000
مغناطيس|2000
دفتر رسم ابو 20|500
دفتر رسم ابو 40|1000
دقتر كانسل A3|5000
دفتر كانسل A4|4000
دفتر رسم ابو 60|2000
ظرف صغير|2000
ظرف A3|8000
ظرف A4|7000
قائمة حساب كبير|2000
قائمة حساب صغير|1000
كلبس كابسة باكيت|2500
كلبس كابسه باكيت|5000
فواصل|5000
قرص|13000
ثاقبة|3000
طاولي|10000
قاطعة لاسق كبيره|3000
فايل طباكه مربعات|2500
فايل شفاف|2000
فايل طباكه|2000
قاصه|1000
صمغ ورق ابو 1000 ناشف|1000
صمغ سائل ابو 1000|1000
صمغ ابو 2000|2000
لاستيك فلوس|1000
دفتر ملاحظات مدرسي وسط|2000
دفتر ملاحضات مدرسي صغير|1000
دفتر ملاحظات مدرسي وسط|2000
دفتر ملاحظات مدرسي كبير|3000
صمع ابو خمسمية|500
ورق تقارير طبكتين|5000
ورق تقرير|1000
دنبوس حايط|1000
دنبوس حلزوني|0
نبالات ام 250|250
نبالات ام 1000|1000
راوتر زين كبير|110000
راوتر زين وسط|70000
راوتر زين صغير|60000
نبالات جداحه|500
قلم نبالات ابو 1000|1000
سكوشي|1000
مداليات اشكال|1000
باكيت اقلام رصاص الوان|250
اقلام رصاص ابو الف|125
حبر ابيض فرجة|1000
الوان خشبية ام 1000|1000
الوان مائية صغيرة|1000
الوان مائية وسط|2000
الوان مائية كبير|3000
مسدس سليكون|5000
بوكس فايل كبير|3000
ورق ملاحظات شريط كبير|1000
حاسبة ام 12000|12000
حاسبه ام 10000|10000
حاسبة محل ام 8000|8000
حاسبة ام 5000|5000
حاسبة ام 3000|3000
حاسبة ام 2000|2000
مقطاطة هندر|3000
قالعة صغيرة|1000
عصارات اكرلك|3000
لاسق ابو 500|500
ورق لعب|5000
دومنة|5000
طوبه مال عضلات|1000
هندسة|1000
الوان ماجك ابو 1000|1000
الوان ماجك ابو 4000|4000
الوان ماجك ابو 3000|3000
الوان ماجك ابو 2000|2000
سطنبة|1000
ورق ملاحظات شريط صغير|500
الوان باستيل كبير|2000
الوان باستيل صغير|1000
اونو|2000
الوان نتراجة كبير|2000
لعبة اطفال|3000
حبر ابيض قلم|1000
لاسق وجهية|2000
بورد خشب|2000
قلم نبالات ابو 3000|3000
كابسة ام 8000|8000
الوان خشبية ام 500|500
دنابيس|1000
حبر اسطنبة|1000
كابسة ام 3000|3000
قلم ذهبي|1000
كابسة ام 2500|2500
كابسة ام 10000|9000
"""


# =========================================================
# بناء قاعدة المنتجات
# =========================================================

PRODUCTS = []

for line in PRODUCTS_TEXT.splitlines():

    line = line.strip()

    if not line or "|" not in line:
        continue

    name, price = line.rsplit("|", 1)

    try:
        price = int(price.strip())
    except ValueError:
        continue

    PRODUCTS.append({
        "name": name.strip(),
        "price": price
    })


# =========================================================
# Normalize
# =========================================================

def normalize(text):

    if not text:
        return ""

    text = str(text).lower().strip()

    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ى": "ي",
        "ة": "ه",
        "ؤ": "و",
        "ئ": "ي",
    }

    for a, b in replacements.items():
        text = text.replace(a, b)

    text = re.sub(r"[\u064B-\u065F\u0670]", "", text)

    text = text.replace("ـ", "")

    text = re.sub(r"[^\w\s*]", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =========================================================
# كلمات غير مهمة
# =========================================================

STOP_WORDS = {
    "اريد",
    "أريد",
    "اريدلي",
    "ريد",
    "اريدكم",
    "عندكم",
    "عدكم",
    "اكو",
    "اكوو",
    "موجود",
    "موجوده",
    "موجودين",
    "شنو",
    "شكو",
    "شكد",
    "كم",
    "سعر",
    "سعره",
    "سعرة",
    "سعرها",
    "اسعار",
    "اسعارها",
    "الي",
    "اللي",
    "من",
    "عند",
    "ممكن",
    "اريد اعرف",
}


# =========================================================
# Aliases
# =========================================================

ALIASES = {
    "طبشوره": "طباشير",
    "طباشوره": "طباشير",
    "اقلام رصاص": "اقلام رصاص ابو الف",
    "قلم رصاص": "اقلام رصاص ابو الف",
    "اقلام الرصاص": "اقلام رصاص ابو الف",
    "قلم الرصاص": "اقلام رصاص ابو الف",
    "صبوره": "صبورة",
    "سبوره": "صبورة",
    "سبورات": "صبورة",
    "دفاتر سجل": "دفتر سجل",
    "دفاتر السجل": "دفتر سجل",
    "سجل شفاف": "سجل شفاف",
    "سجلات شفافة": "سجل شفاف",
}


# =========================================================
# ذاكرة المحادثة
#
# نخزن آخر 12 رسالة لكل محادثة.
# =========================================================

CHAT_HISTORY = defaultdict(lambda: deque(maxlen=12))

# حتى لا يعيد البوت رسالة الترحيب كل مرة
INTRO_SENT = set()

# منع معالجة update مرتين
PROCESSED_UPDATES = deque(maxlen=500)


# =========================================================
# استخراج الأرقام
# =========================================================

def has_number(text, number):
    return str(number) in normalize(text)


# =========================================================
# إيجاد المنتجات المذكورة في الرسالة
#
# يدعم:
# "اريد دفاتر وسجلات وشكد سعر الطباشير"
# ويطلع أكثر من منتج بنفس الرسالة.
# =========================================================

def find_products(text):

    normalized = normalize(text)

    found = []

    # الأطول أولاً
    sorted_products = sorted(
        PRODUCTS,
        key=lambda p: len(normalize(p["name"])),
        reverse=True
    )

    for product in sorted_products:

        product_name = normalize(product["name"])

        if not product_name:
            continue

        if product_name in normalized:

            # لا نكرر نفس المنتج إذا كان مكرر بالقائمة
            if not any(
                x["name"] == product["name"]
                for x in found
            ):
                found.append(product)

    # aliases
    for alias, real_name in ALIASES.items():

        if normalize(alias) in normalized:

            for product in PRODUCTS:

                if normalize(product["name"]) == normalize(real_name):

                    if not any(
                        x["name"] == product["name"]
                        for x in found
                    ):
                        found.append(product)

    return found


# =========================================================
# بحث ذكي عن المنتج من كلمات متفرقة
#
# مثال:
# "100 شفاف"
# بعد ما يكون السياق السابق "سجل"
# =========================================================

def contextual_product_search(text, history):

    normalized = normalize(text)

    candidates = find_products(text)

    if candidates:
        return candidates

    # إذا قال "شفاف" والسياق السابق كان سجل
    context_text = " ".join(
        item["content"]
        for item in history
        if item["role"] == "user"
    )

    context = normalize(context_text)

    if "سجل" in context or "سجلات" in context:

        if "شفاف" in normalized:

            if "100" in normalized:
                return [
                    p for p in PRODUCTS
                    if normalize(p["name"]) == normalize("سجل 100 سيم شفاف")
                ]

            if "200" in normalized:
                return [
                    p for p in PRODUCTS
                    if normalize(p["name"]) == normalize("سجل 200 سيم شفاف")
                ]

            return [
                p for p in PRODUCTS
                if normalize(p["name"]) == normalize("سجل شفاف")
            ]

        if "خشبي" in normalized:

            if "100" in normalized:
                return [
                    p for p in PRODUCTS
                    if normalize(p["name"]) == normalize("سجل 100 سيم خشبي")
                ]

            if "200" in normalized:
                return [
                    p for p in PRODUCTS
                    if normalize(p["name"]) == normalize("سجل 200 سيم خشبي")
                ]

    return []


# =========================================================
# تنسيق السعر
# =========================================================

def money(price):

    return f"{price:,}".replace(",", "،")


# =========================================================
# رد مباشر على الأسعار
#
# إذا الرسالة تحتوي أكثر من منتج:
# يجاوبهم كلهم برسالة واحدة.
# =========================================================

def product_answer(products):

    if not products:
        return None

    lines = []

    for product in products:

        name = product["name"]
        price = product["price"]

        if price == 0:
            lines.append(
                f"• {name}: السعر يحتاج تأكيد من المكتبة 🌷"
            )
        else:
            lines.append(
                f"• {name}: {money(price)} دينار"
            )

    return "أكيد 🌷\n" + "\n".join(lines)


# =========================================================
# أسئلة عامة عن فئة المنتجات
# =========================================================

def category_answer(text):

    t = normalize(text)

    # سجلات
    if (
        "سجلات" in t
        or "دفاتر سجل" in t
        or "دفتر سجل" in t
    ):

        items = []

        for p in PRODUCTS:

            n = normalize(p["name"])

            if "سجل" in n and p["name"] not in [
                x["name"] for x in items
            ]:
                items.append(p)

        if items:

            lines = []

            for p in items:
                if p["price"] == 0:
                    lines.append(
                        f"• {p['name']}: يحتاج تأكيد"
                    )
                else:
                    lines.append(
                        f"• {p['name']}: {money(p['price'])} دينار"
                    )

            return (
                "إي عدنا عدة أنواع من السجلات 🌷\n"
                + "\n".join(lines)
            )

    # دفاتر
    if "دفاتر" in t or "دفتر" in t:

        items = []

        for p in PRODUCTS:

            n = normalize(p["name"])

            if (
                "دفتر" in n
                and p["name"] not in [x["name"] for x in items]
            ):
                items.append(p)

        if items:

            # لا نرمي القائمة كلها بوجه الزبون
            # نخليه يحدد النوع بطريقة طبيعية.

            return (
                "إي عدنا دفاتر هواي 🌷\n"
                "عدنا سجل، ملاحظات، رسم، تلوين ودفاتر مدرسية.\n"
                "إذا تريد، گلي مثلاً: سجل، ملاحظات، رسم... وأطلعلك الأسعار."
            )

    # صبورات
    if (
        "صبوره" in t
        or "سبوره" in t
        or "صبورات" in t
        or "سبورات" in t
    ):

        return (
            "إي عدنا صبورات 🌷\n"
            "الصغيرة 7،000 دينار، الوسط 8،000، والكبيرة 12،000."
        )

    # أقلام رصاص
    if (
        "قلم رصاص" in t
        or "اقلام رصاص" in t
        or "اقلام الرصاص" in t
    ):

        return (
            "إي موجودة 🌷\n"
            "قلم الرصاص أبو الألف بـ125 دينار، "
            "وباكت أقلام رصاص ألوان بـ250 دينار."
        )

    return None


# =========================================================
# الرد على التحيات والنهايات
# =========================================================

def simple_reply(text):

    t = normalize(text)

    if t in {
        "هلو",
        "هلا",
        "هاي",
        "مرحبا",
        "السلام عليكم",
        "سلام عليكم",
        "اهلا",
        "اهلين",
    }:

        return (
            "هلا بيك 🌷\n"
            "آني بوت مكتبة أم القرى، مو صاحب المكتبة، "
            "وأكدر أساعدك بالمنتجات والأسعار الموجودة عندي."
        )

    if t in {
        "شكرا",
        "شكرا جزيلا",
        "تمام",
        "فهمت",
        "اوكي",
        "اوكي تمام",
        "ماريد",
        "ما اريد",
        "لا شكرا",
        "خلص",
        "خلاص",
    }:

        return "تمام 🌷 بالخدمة بأي وقت."

    return None


# =========================================================
# هل السؤال عن ملازم؟
# =========================================================

def asks_about_malazim(text):

    t = normalize(text)

    return (
        "ملازم" in t
        or "ملزمه" in t
        or "ملزمة" in t
        or "ملازمه" in t
    )


# =========================================================
# تعليمات AI
# =========================================================

SYSTEM_PROMPT = """
أنت بوت محادثة رسمي لمكتبة أم القرى.

مهمتك الأساسية:
تتحدث مع الزبون مثل موظف خدمة زبائن محترم، طبيعي، ومرتب.

أنت BOT ولست صاحب المكتبة.
لا تدّعي أنك صاحب المكتبة.
لا تقل إنك إنسان.
إذا احتاج الأمر، وضح باختصار أنك بوت.

أسلوب الكلام:
- عراقي طبيعي.
- مختصر لكن مفيد.
- لا تتفلسف.
- لا تكرر نفس الكلام.
- لا تبدأ كل رد بـ "هلا".
- لا تستخدم كلمة "حبيبي".
- لا تستخدم "حبيبتي".
- لا تستخدم "عزيزي".
- لا تستخدم "عزيزتي".
- لا تستخدم "يابه".
- لا تستخدم كلاماً مستفزاً.
- لا تقل "وضحلي شنو تحتاج" إذا السؤال مفهوم.
- لا تسأل سؤالاً جديداً إذا الزبون أنهى المحادثة.

أهم قاعدة:
افهم المحادثة ككل، وليس الرسالة الأخيرة وحدها.

مثال:
الزبون:
"عدكم سجلات؟"

البوت:
"إي عدنا 🌷 عدنا شفاف وخشبي وبدون سيم وبأحجام مختلفة."

الزبون:
"شفاف"

يجب أن تفهم أنه يقصد السجل الشفاف.

الزبون:
"100"

يجب أن تفهم أنه يقصد سجل 100 سيم شفاف إذا كان هذا هو السياق.

إذا قال:
"أريد دفاتر وسجلات وشكد سعر الطباشير؟"

افهم أنها 3 طلبات:
1. يريد دفاتر
2. يريد سجلات
3. يريد سعر الطباشير

ولا تجاوب على واحدة فقط.

إذا سأل عن منتج موجود في معلومات القائمة:
استخدم السعر الموجود فقط.

ممنوع اختراع سعر.

إذا المنتج له أكثر من سعر أو أكثر من نوع:
اذكر الأنواع والأسعار الموجودة.

إذا سأل عن منتج غير موجود بالقائمة:
قل:
"هذا السعر يحتاج تأكيد من المكتبة 🌷"

إذا سأل عن توفر شيء ولا توجد معلومة مؤكدة عن توفره:
قل:
"التوفر يحتاج تأكيد من المكتبة 🌷"

الملازم:
إذا سأل عن ملازم، قل إنك بوت وإن سعر/توفر الملازم يحتاج تأكيد من المكتبة.
لا تخترع سعر ملازم.

لا تعيد تعريف نفسك في كل رسالة.
التعريف يكون أول مرة فقط أو إذا سأل الزبون من أنت.

لا ترسل أكثر من جواب لنفس الرسالة.

لا ترسل قائمتك كاملة إلا إذا طلب الزبون قائمة المنتجات أو كل الأسعار.

إذا كان السؤال عاماً:
مثل "شنو متوفر بالمكتبة؟"
جاوب بشكل مفيد ومرتب:
اذكر الفئات الموجودة، ثم اسأل إذا يريد الأسعار أو نوع معين.

إذا قال "شكراً" أو "تمام":
"تمام 🌷 بالخدمة بأي وقت."

إذا قال كلام غير واضح:
اسأل سؤالاً واحداً بسيطاً يساعد على فهمه، وليس "وضحلي شنو تحتاج".

إذا كان الكلام مسيئاً:
لا تسب ولا تعصب.
رد بهدوء واحترام.

لا تذكر API أو البرمجة أو DeepSeek.
"""


# =========================================================
# بناء معلومات المنتجات للـ AI
# =========================================================

def build_product_context(products):

    if not products:
        return ""

    lines = []

    for p in products:

        if p["price"] == 0:
            price = "يحتاج تأكيد من المكتبة"
        else:
            price = f"{money(p['price'])} دينار"

        lines.append(
            f"- {p['name']}: {price}"
        )

    return "\n".join(lines)


# =========================================================
# AI
# =========================================================

def ask_ai(chat_id, user_text, products):

    history = list(CHAT_HISTORY[chat_id])

    product_context = build_product_context(products)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    # آخر المحادثة
    for item in history[-10:]:

        messages.append({
            "role": item["role"],
            "content": item["content"]
        })

    current_message = user_text

    if product_context:

        current_message += (
            "\n\nمعلومات مؤكدة من قائمة المكتبة "
            "للاستخدام في هذا الرد فقط:\n"
            + product_context
        )

    messages.append({
        "role": "user",
        "content": current_message
    })

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=500
    )

    if not response.choices:
        return "ما لحگت أفهم الطلب 🌷"

    answer = response.choices[0].message.content

    if not answer:
        return "ما لحگت أفهم الطلب 🌷"

    # منع الكلمات غير المرغوبة
    forbidden = [
        "حبيبي",
        "حبيبتي",
        "عزيزي",
        "عزيزتي"
    ]

    for word in forbidden:
        answer = answer.replace(word, "")

    # تنظيف
    answer = re.sub(r"\n{3,}", "\n\n", answer)
    answer = re.sub(r"[ \t]{2,}", " ", answer)

    return answer.strip()


# =========================================================
# إرسال Telegram
# =========================================================

def send_message(
    chat_id,
    text,
    business_connection_id=None
):

    if not text:
        return

    data = {
        "chat_id": chat_id,
        "text": str(text)
    }

    if business_connection_id:
        data["business_connection_id"] = business_connection_id

    response = requests.post(
        TG + "/sendMessage",
        json=data,
        timeout=30
    )

    if not response.ok:

        logging.error(
            "TELEGRAM ERROR | STATUS=%s | RESPONSE=%s | CHAT=%s | BUSINESS=%s",
            response.status_code,
            response.text,
            chat_id,
            business_connection_id
        )

    response.raise_for_status()


# =========================================================
# حذف Webhook
# =========================================================

def remove_webhook():

    try:

        response = requests.post(
            TG + "/deleteWebhook",
            json={
                "drop_pending_updates": False
            },
            timeout=30
        )

        if response.ok:
            logging.info("Webhook removed successfully")
        else:
            logging.error(
                "Webhook removal failed: %s",
                response.text
            )

    except Exception:
        logging.exception("Webhook removal error")


# =========================================================
# معالجة الرسالة
# =========================================================

def process_message(msg):

    if not msg:
        return

    chat = msg.get("chat")

    if not chat:
        return

    chat_id = chat.get("id")

    if not chat_id:
        return

    business_connection_id = msg.get(
        "business_connection_id"
    )

    text = msg.get("text", "").strip()

    if not text:
        return

    logging.info(
        "MESSAGE | chat=%s | business=%s | text=%s",
        chat_id,
        bool(business_connection_id),
        text
    )

    # =====================================================
    # /start
    # =====================================================

    if text.startswith("/start"):

        send_message(
            chat_id,
            (
                "هلا بيك 🌷\n"
                "آني بوت مكتبة أم القرى، مو صاحب المكتبة.\n"
                "أكدر أساعدك بالمنتجات والأسعار الموجودة عندي.\n"
                "اكتبلي شنو تحتاج."
            ),
            business_connection_id
        )

        INTRO_SENT.add(chat_id)

        return

    # =====================================================
    # الترحيب الأول
    # =====================================================

    if chat_id not in INTRO_SENT:

        send_message(
            chat_id,
            (
                "هلا بيك 🌷\n"
                "آني بوت مكتبة أم القرى، مو صاحب المكتبة.\n"
                "أكدر أساعدك بالمنتجات والأسعار الموجودة عندي."
            ),
            business_connection_id
        )

        INTRO_SENT.add(chat_id)

        # لا نخلي التعريف وحده يمنع الرد على سؤال الزبون
        # نكمل ونرد على نفس الرسالة.

    # =====================================================
    # لا تحفظ الأوامر كنصوص عادية
    # =====================================================

    previous_history = list(CHAT_HISTORY[chat_id])

    # =====================================================
    # ردود بسيطة
    # =====================================================

    simple = simple_reply(text)

    if simple:

        send_message(
            chat_id,
            simple,
            business_connection_id
        )

        CHAT_HISTORY[chat_id].append({
            "role": "user",
            "content": text
        })

        CHAT_HISTORY[chat_id].append({
            "role": "assistant",
            "content": simple
        })

        return

    # =====================================================
    # ملازم
    # =====================================================

    if asks_about_malazim(text):

        answer = (
            "بالنسبة للملازم 🌷\n"
            "آني بوت وما عندي تأكيد مباشر على أسعار أو توفر الملازم، "
            "فالأفضل أتأكد من المكتبة."
        )

        send_message(
            chat_id,
            answer,
            business_connection_id
        )

        CHAT_HISTORY[chat_id].append({
            "role": "user",
            "content": text
        })

        CHAT_HISTORY[chat_id].append({
            "role": "assistant",
            "content": answer
        })

        return

    # =====================================================
    # منتجات مذكورة بشكل مباشر أو حسب السياق
    # =====================================================

    products = contextual_product_search(
        text,
        previous_history
    )

    # =====================================================
    # إذا السؤال عن فئة كاملة
    # =====================================================

    if not products:

        category = category_answer(text)

        if category:

            send_message(
                chat_id,
                category,
                business_connection_id
            )

            CHAT_HISTORY[chat_id].append({
                "role": "user",
                "content": text
            })

            CHAT_HISTORY[chat_id].append({
                "role": "assistant",
                "content": category
            })

            return

    # =====================================================
    # إذا وجد منتجات واضحة:
    # نجاوب على كل المنتجات برسالة واحدة.
    # =====================================================

    if products:

        # إذا كانت الرسالة سؤال سعر مباشر
        answer = product_answer(products)

        if answer:

            # إذا المنتج مجرد ذكر داخل جملة طويلة
            # نخلي AI يكمل الحوار بشكل طبيعي،
            # لكن الأسعار تبقى مؤكدة.

            try:

                ai_answer = ask_ai(
                    chat_id,
                    text,
                    products
                )

                # إذا AI رجع جواب مفيد، استخدمه.
                # لكن إذا لعب بالأسعار، نستخدم الرد المؤكد.
                if ai_answer:

                    answer = ai_answer

            except Exception:

                logging.exception(
                    "AI ERROR while answering product"
                )

        send_message(
            chat_id,
            answer,
            business_connection_id
        )

        CHAT_HISTORY[chat_id].append({
            "role": "user",
            "content": text
        })

        CHAT_HISTORY[chat_id].append({
            "role": "assistant",
            "content": answer
        })

        return

    # =====================================================
    # AI مع ذاكرة المحادثة
    # =====================================================

    try:

        answer = ask_ai(
            chat_id,
            text,
            []
        )

        send_message(
            chat_id,
            answer,
            business_connection_id
        )

        CHAT_HISTORY[chat_id].append({
            "role": "user",
            "content": text
        })

        CHAT_HISTORY[chat_id].append({
            "role": "assistant",
            "content": answer
        })

    except Exception as error:

        logging.exception("AI ERROR")

        error_text = str(error).lower()

        if (
            "429" in error_text
            or "rate limit" in error_text
            or "quota" in error_text
        ):

            answer = (
                "الخدمة مشغولة حالياً 🌷 "
                "حاول بعد شوي."
            )

        elif (
            "401" in error_text
            or "api key" in error_text
            or "authentication" in error_text
        ):

            answer = "صار خلل بإعدادات الخدمة 🌷"

        else:

            answer = (
                "صار تأخير بسيط بالخدمة 🌷 "
                "حاول بعد شوي."
            )

        send_message(
            chat_id,
            answer,
            business_connection_id
        )


# =========================================================
# Main
# =========================================================

def main():

    logging.info("Bot starting...")
    logging.info("Using model: %s", MODEL)
    logging.info("Products loaded: %s", len(PRODUCTS))

    remove_webhook()

    offset = None

    while True:

        try:

            params = {
                "timeout": 50,
                "allowed_updates": [
                    "message",
                    "business_message"
                ]
            }

            if offset is not None:
                params["offset"] = offset

            response = requests.get(
                TG + "/getUpdates",
                params=params,
                timeout=65
            )

            # =================================================
            # 409
            # =================================================

            if response.status_code == 409:

                logging.error(
                    "409 CONFLICT: another bot instance is using this token."
                )

                time.sleep(10)

                continue

            response.raise_for_status()

            data = response.json()

            if not data.get("ok"):

                logging.error(
                    "Telegram API ERROR: %s",
                    data
                )

                time.sleep(5)

                continue

            updates = data.get("result", [])

            for update in updates:

                update_id = update.get("update_id")

                if update_id is not None:

                    # حماية من التكرار
                    if update_id in PROCESSED_UPDATES:
                        continue

                    PROCESSED_UPDATES.append(update_id)

                    offset = update_id + 1

                # رسالة عادية
                msg = update.get("message")

                # Business
                if msg is None:
                    msg = update.get("business_message")

                if not msg:
                    continue

                try:

                    process_message(msg)

                except Exception:

                    logging.exception(
                        "Message processing error"
                    )

        except requests.exceptions.ReadTimeout:

            # طبيعي بسبب long polling
            continue

        except requests.exceptions.RequestException:

            logging.exception(
                "Telegram polling error"
            )

            time.sleep(5)

        except Exception:

            logging.exception(
                "Unexpected main loop error"
            )

            time.sleep(5)


# =========================================================
# تشغيل
# =========================================================

if __name__ == "__main__":
    main()
