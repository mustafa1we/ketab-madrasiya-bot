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
# كتالوج كامل للذكاء الاصطناعي
#
# نخلي كل المنتجات وأسعارها متاحة للـAI، مو بس الأقلام والدفاتر.
# =========================================================

CATALOG = []

for product in PRODUCTS:
    if not any(
        x["name"] == product["name"] and x["price"] == product["price"]
        for x in CATALOG
    ):
        CATALOG.append(product)


def build_full_catalog():
    lines = []
    for p in CATALOG:
        price = "يحتاج تأكيد من المكتبة" if p["price"] == 0 else f"{money(p["price"])} دينار"
        lines.append(f"- {p["name"]}: {price}")
    return "\n".join(lines)


FULL_CATALOG = None


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

    # تسميات شائعة من الزبائن
    "الوان تاشيره": "قلم تأشير باكيت",
    "الوان تأشيره": "قلم تأشير باكيت",
    "الوان تأشير": "قلم تأشير باكيت",
    "الوان تاشير": "قلم تأشير باكيت",
    "تاشيره": "قلم تأشير باكيت",
    "تاشيرة": "قلم تأشير باكيت",
    "تاشير": "قلم تأشير باكيت",
    "تأشير": "قلم تأشير باكيت",
    "تأشيره": "قلم تأشير باكيت",
    "تأشيرة": "قلم تأشير باكيت",
    "قلم تاشير": "قلم تأشير باكيت",
    "قلم تاشيره": "قلم تأشير باكيت",
    "قلم تاشيرة": "قلم تأشير باكيت",
    "قلم تأشير": "قلم تأشير باكيت",
    "اقلام تاشير": "قلم تأشير باكيت",
    "اقلام تاشيره": "قلم تأشير باكيت",
    "اقلام تاشيرة": "قلم تأشير باكيت",
    "اقلام تأشير": "قلم تأشير باكيت",
    "بورد": "بورد خشب",
    "بورد خشبي": "بورد خشب",
    "اصباخ خشبي": "الوان خشبية ام 1000",
    "اصباغ خشبي": "الوان خشبية ام 1000",
    "الوان خشبي": "الوان خشبية ام 1000",
    "الوان خشبيه": "الوان خشبية ام 1000",
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
    """
    مطابقة حتمية للمنتجات قبل الذكاء الاصطناعي.
    تمنع الردود العامة على أسماء المنتجات الواضحة.
    """
    normalized = normalize(text)
    found = []

    def add_product_by_name(real_name):
        real_norm = normalize(real_name)
        for product in PRODUCTS:
            if normalize(product["name"]) == real_norm:
                if not any(
                    x["name"] == product["name"] and x["price"] == product["price"]
                    for x in found
                ):
                    found.append(product)

    # الأسماء البديلة أولاً.
    for alias, real_name in sorted(
        ALIASES.items(),
        key=lambda item: len(normalize(item[0])),
        reverse=True
    ):
        alias_norm = normalize(alias)
        if alias_norm and alias_norm in normalized:
            add_product_by_name(real_name)

    # أسماء المنتجات الفعلية.
    for product in sorted(
        PRODUCTS,
        key=lambda p: len(normalize(p["name"])),
        reverse=True
    ):
        product_norm = normalize(product["name"])
        if product_norm and product_norm in normalized:
            if not any(
                x["name"] == product["name"] and x["price"] == product["price"]
                for x in found
            ):
                found.append(product)

    # صيغ الزبائن الشائعة للتأشير.
    marker_words = (
        "تاشيره", "تاشيرة", "تاشير",
        "تأشيره", "تأشيرة", "تأشير",
        "قلم تاشير", "قلم تاشيره", "قلم تاشيرة",
        "اقلام تاشير", "اقلام تاشيره", "اقلام تاشيرة",
        "الوان تاشير", "الوان تاشيره", "الوان تاشيرة",
    )
    if any(normalize(x) in normalized for x in marker_words):
        add_product_by_name("قلم تأشير باكيت")

    if re.search(r"(^|\s)بورد(\s|$)", normalized) or "بورد خشبي" in normalized:
        add_product_by_name("بورد خشب")

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

def category_answer(text, history=None):
    t = normalize(text)

    def unique_items(items):
        out = []
        seen = set()
        for p in items:
            key = (p["name"], p["price"])
            if key not in seen:
                seen.add(key)
                out.append(p)
        return out

    def lines_for(items):
        lines = []
        for p in items:
            if p["price"] == 0:
                lines.append(f"• {p['name']}: السعر يحتاج تأكيد من المكتبة")
            else:
                lines.append(f"• {p['name']}: {money(p['price'])} دينار")
        return lines

    parts = []

    # سجلات
    if (
        "سجلات" in t
        or "سجل" in t
        or "دفاتر سجل" in t
        or "دفتر سجل" in t
    ):
        items = []
        for p in PRODUCTS:
            n = normalize(p["name"])
            if "سجل" in n:
                items.append(p)
        items = unique_items(items)
        if items:
            parts.append(
                "إي، عدنا سجلات 🌷\n" + "\n".join(lines_for(items))
            )

    # دفاتر عامة
    # إذا كتب "دفاتر وسجلات" نجاوب على الاثنين، مو نعتبرهم سؤالاً واحداً.
    if "دفاتر" in t or "دفتر" in t:
        if not ("دفاتر سجل" in t or "دفتر سجل" in t):
            parts.append(
                "إي، عدنا دفاتر هواي 🌷\n"
                "عدنا دفاتر سجل، ملاحظات، رسم، تلوين ومدرسية. "
                "إذا تريد نوع معين گلي اسمه وأطلعلك أسعاره."
            )

    # صبورات
    if any(x in t for x in ("صبوره", "سبوره", "صبورات", "سبورات")):
        parts.append(
            "إي عدنا صبورات 🌷\n"
            "الصغيرة 7،000، الوسط 8،000، والكبيرة 12،000 دينار."
        )

    # أقلام رصاص
    if (
        "قلم رصاص" in t
        or "اقلام رصاص" in t
        or "اقلام الرصاص" in t
    ):
        parts.append(
            "إي موجودة 🌷\n"
            "قلم الرصاص أبو الألف بـ125 دينار، "
            "وباكت أقلام رصاص ألوان بـ250 دينار."
        )

    # ألوان مائية
    if "الوان مائيه" in t or "الوان مائيه" in t:
        items = [p for p in PRODUCTS if "الوان مائية" in p["name"]]
        if items:
            parts.append("إي عدنا ألوان مائية 🌷\n" + "\n".join(lines_for(unique_items(items))))

    # ألوان خشبية
    if "الوان خشبيه" in t or "الوان خشبيه" in t:
        items = [p for p in PRODUCTS if "الوان خشبية" in p["name"]]
        if items:
            parts.append("إي عدنا ألوان خشبية 🌷\n" + "\n".join(lines_for(unique_items(items))))

    # ماجك
    if "الوان ماجك" in t:
        items = [p for p in PRODUCTS if "الوان ماجك" in p["name"]]
        if items:
            parts.append("إي عدنا ألوان ماجك 🌷\n" + "\n".join(lines_for(unique_items(items))))

    # باستيل
    if "الوان باستيل" in t:
        items = [p for p in PRODUCTS if "الوان باستيل" in p["name"]]
        if items:
            parts.append("إي عدنا ألوان باستيل 🌷\n" + "\n".join(lines_for(unique_items(items))))

    # حاسبات
    if "حاسبات" in t or "حاسبه" in t or "حاسبه" in t:
        items = [p for p in PRODUCTS if "حاسب" in p["name"]]
        if items:
            parts.append("إي عدنا حاسبات 🌷\n" + "\n".join(lines_for(unique_items(items))))

    # فريمات
    if "فريمات" in t or "فريم" in t:
        items = [p for p in PRODUCTS if "فريمات" in p["name"]]
        if items:
            parts.append("إي عدنا فريمات 🌷\n" + "\n".join(lines_for(unique_items(items))))

    # فايلات
    if "فايلات" in t or "فايل" in t:
        items = [p for p in PRODUCTS if "فايل" in p["name"]]
        if items:
            parts.append("إي عدنا فايلات 🌷\n" + "\n".join(lines_for(unique_items(items))))

    # ظروف
    if "ظروف" in t or "ظرف" in t:
        items = [p for p in PRODUCTS if "ظرف" in p["name"]]
        if items:
            parts.append("إي عدنا ظروف 🌷\n" + "\n".join(lines_for(unique_items(items))))

    # ألعاب
    if "العاب" in t or "لعب" in t or "اونو" in t or "دومنه" in t:
        items = [p for p in PRODUCTS if p["name"] in {"ورق لعب", "دومنة", "اونو", "لعبة اطفال"}]
        if items:
            parts.append("إي عدنا ألعاب 🌷\n" + "\n".join(lines_for(unique_items(items))))

    # ملازم
    if asks_about_malazim(t):
        parts.append(
            "وبالنسبة للملازم، آني بوت وما عندي تأكيد مباشر على سعرها أو توفرها؛ "
            "هاي تحتاج تأكيد من المكتبة."
        )

    if parts:
        return "\n\n".join(parts)

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
أنت بوت خدمة زبائن لمكتبة أم القرى، ولست صاحب المكتبة ولا موظفاً بشرياً.

تتكلم باللهجة العراقية الطبيعية، بهدوء وباختصار مفيد، وكأنك موظف خدمة زبائن محترف لكن واضح أنك بوت.

أنت تعرف أن المكتبة ليست فقط أقلام ودفاتر. الكتالوج يحتوي أيضاً على صبورات، فريمات، فايلات، ظروف، صمغ ولاسق، كابسات وثاقبات، حاسبات، راوترات، ألعاب، ألوان، أدوات فنية، مستلزمات مدرسية وأشياء أخرى.

قواعد أساسية:
1) افهم المحادثة كلها، لا تتعامل مع آخر رسالة وكأنها منفصلة عن الكلام السابق.
2) إذا الزبون ذكر أكثر من طلب في رسالة واحدة، جاوب على كل طلب في نفس الرد وبترتيب واضح.
   مثال: "أريد دفاتر وسجلات وشكد سعر الطباشير؟" = دفاتر + سجلات + طباشير.
3) إذا كانت الرسالة متابعة لكلام سابق مثل "شفاف"، "100"، "وخشبي"، اربطها بالمنتج الذي كان الحديث عنه.
4) لا تعيد سؤال الزبون عن شيء سبق أن ذكره.
5) لا تستخدم "وضحلي شنو تحتاج" إذا كان بالإمكان فهم المقصود من السياق.
6) إذا كان الكلام غير واضح فعلاً، اسأل سؤالاً واحداً محدداً يساعدك على تحديد المنتج.
7) لا تكرر التحية أو تعريف نفسك في كل رسالة.
8) كلمة "حبيبي" و"حبيبتي" و"عزيزي" و"عزيزتي" و"يابه" ممنوعة.
9) لا تقل إنك صاحب المكتبة أو إنسان.
10) لا تذكر DeepSeek أو API أو البرمجة.
11) لا تخترع سعراً أو توفر منتج.
12) إذا أعطيتك معلومات مؤكدة من قائمة المنتجات، التزم بها حرفياً.
13) إذا كان للمنتج أكثر من نوع أو أكثر من سعر، اذكر الأنواع والأسعار ولا تختار من نفسك.
14) الملازم: قل إنك بوت وإن السعر والتوفر يحتاجان تأكيداً من المكتبة.
15) إذا الزبون قال شكراً/تمام/فهمت/ماريد، لا تفتح موضوعاً جديداً؛ رد باختصار.
16) إذا الزبون معصب أو مسيء، لا ترد بالإساءة. اعتذر باختصار وحاول مساعدته.

أسلوب البيع:
- إذا سأل عن منتج، أعطه المعلومة المطلوبة أولاً.
- إذا كان مناسباً، شجعه بلطف على اختيار النوع أو المقاس، بدون ضغط أو مبالغة.
- لا تغرق الزبون بقائمة كاملة إلا إذا طلبها.

مهم جداً:
المعلومات التي تأتيك تحت عنوان "حقائق مؤكدة من القائمة" هي المصدر الوحيد للأسعار.
لا تغيّر الأرقام ولا تستنتج سعراً غير موجود.
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
# AI — محادثة فعلية مع كتالوج المكتبة كامل
# =========================================================

def ask_ai(chat_id, user_text, products=None, extra_facts=""):
    global FULL_CATALOG

    if FULL_CATALOG is None:
        FULL_CATALOG = build_full_catalog()

    history = list(CHAT_HISTORY[chat_id])

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    for item in history[-12:]:
        messages.append({
            "role": item["role"],
            "content": item["content"]
        })

    # الكتالوج الكامل متاح دائماً حتى يعرف البوت أن المكتبة بيها
    # شغلات كثيرة غير الدفاتر والأقلام.
    current_message = (
        "رسالة الزبون الحالية:\n"
        + user_text
        + "\n\nكتالوج مكتبة أم القرى الكامل (المصدر الوحيد للأسعار والتوفر):\n"
        + FULL_CATALOG
    )

    if products:
        current_message += (
            "\n\nمنتجات طابقناها مباشرة مع رسالة الزبون. إذا كان السؤال عن سعرها، "
            "استخدم هذه الأسعار حرفياً:\n"
            + build_product_context(products)
        )

    if extra_facts:
        current_message += (
            "\n\nمعلومات إضافية مؤكدة:\n"
            + extra_facts
        )

    current_message += (
        "\n\nمطلوب منك الآن: جاوب الزبون على كلامه الحالي بشكل طبيعي. "
        "لا تلقي عليه قائمة طويلة إلا إذا طلب قائمة. "
        "إذا قال عندكم/موجود/شنو متوفر مع اسم منتج، اعتبرها سؤال توفر لذلك المنتج، "
        "وليس سؤال دوام. إذا ذكر أكثر من غرض، جاوب على كل غرض. "
        "إذا كانت الرسالة متابعة لرسالة سابقة، اربطها بالسياق. "
        "إذا سأل عن منتج موجود بالكتالوج، اذكر سعره فقط إذا كان السعر واضحاً. "
        "إذا كان المنتج أو الخدمة غير موجود بالكتالوج، لا تخترع وجوده أو سعره أو خدمة غير مذكورة؛ قل إن التوفر يحتاج تأكيداً من المكتبة. "
        "لا تذكر كتباً مدرسية أو طباعة أو استنساخ أو تجليد على أنها متوفرة إلا إذا كانت موجودة في الكتالوج. "
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

    answer = response.choices[0].message.content or ""
    if not answer.strip():
        return "ما لحگت أفهم الطلب 🌷"

    for word in ("حبيبي", "حبيبتي", "عزيزي", "عزيزتي", "يابه"):
        answer = answer.replace(word, "")

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

def save_history(chat_id, user_text, answer):
    CHAT_HISTORY[chat_id].append({
        "role": "user",
        "content": user_text
    })
    CHAT_HISTORY[chat_id].append({
        "role": "assistant",
        "content": answer
    })


def first_contact_prefix(chat_id):
    if chat_id in INTRO_SENT:
        return ""
    INTRO_SENT.add(chat_id)
    return "آني بوت مكتبة أم القرى، مو صاحب المكتبة. 🌷\n"


def build_general_availability():
    return (
        "إي، عدنا هواي شغلات بالمكتبة 🌷\n"
        "منها دفاتر وسجلات، ألوان، صبورات، أقلام، فايلات، ظروف، "
        "صمغ ولاسق، كابسات وثاقبات، فريمات، حاسبات وألعاب وغيرها.\n"
        "إذا تريد شي معين اكتب اسمه، وأگلك الأنواع والأسعار الموجودة بالقائمة."
    )


def is_general_availability_question(t):
    """سؤال التوفر العام فقط، وليس مجرد ذكر كلمة موجود."""
    t = normalize(t)
    if t in {
        "شنو متوفر", "شنو المتوفر", "شنو موجود", "شنو الموجود",
        "شنو متوفر بالمكتبه", "شنو المتوفر بالمكتبه",
        "شنو موجود بالمكتبه", "شنو الموجود بالمكتبه",
        "شنو متوفر بالمكتبه حاليا", "شنو المتوفر بالمكتبه حاليا",
        "شنو موجود بالمكتبه حاليا", "شنو الموجود بالمكتبه حاليا",
        "شنو عندكم بالمكتبه", "شنو عدكم بالمكتبه",
        "شنو عندكم من اغراض", "شنو عدكم من اغراض",
    }:
        return True
    return (
        "شنو" in t
        and any(x in t for x in ("متوفر", "المتوفر", "موجود", "الموجود"))
        and any(x in t for x in ("مكتبه", "اغراض", "منتجات"))
    )


def process_message(msg):
    if not msg:
        return

    chat = msg.get("chat")
    if not chat:
        return

    chat_id = chat.get("id")
    if not chat_id:
        return

    business_connection_id = msg.get("business_connection_id")
    text = msg.get("text", "").strip()

    if not text:
        return

    logging.info(
        "MESSAGE | chat=%s | business=%s | text=%s",
        chat_id,
        bool(business_connection_id),
        text
    )

    # الأوامر
    if text.startswith("/start"):
        answer = (
            "آني بوت مكتبة أم القرى، مو صاحب المكتبة. 🌷\n"
            "أكدر أساعدك بالمنتجات والأسعار الموجودة عندي.\n"
            "اكتبلي شنو تحتاج."
        )
        send_message(chat_id, answer, business_connection_id)
        INTRO_SENT.add(chat_id)
        save_history(chat_id, text, answer)
        return

    if text.startswith("/help"):
        answer = (
            "آني بوت مكتبة أم القرى 🌷\n"
            "اسألني عن أي منتج أو سعر، وحتى إذا عندك أكثر من طلب بنفس الرسالة "
            "أجاوبك عليهم كلهم."
        )
        send_message(chat_id, answer, business_connection_id)
        save_history(chat_id, text, answer)
        return

    previous_history = list(CHAT_HISTORY[chat_id])

    # لا ترسل رسالتين: نضيف التعريف إلى نفس الرد فقط إذا كانت أول مرة.
    intro = first_contact_prefix(chat_id)

    # إذا المستخدم فقط سلّم، التعريف يكون كافي ومناسب.
    simple = simple_reply(text)
    if simple:
        answer = intro + simple if intro else simple
        send_message(chat_id, answer, business_connection_id)
        save_history(chat_id, text, answer)
        return

    # بحث مباشر + بحث حسب السياق
    products = find_products(text)
    if not products:
        products = contextual_product_search(text, previous_history)

    # فئات/طلبات عامة في نفس الرسالة
    category = category_answer(text, previous_history)

    # إذا سأل "شنو متوفر حالياً" لا نرميه على سؤال توضيحي.
    t = normalize(text)
    availability_question = is_general_availability_question(t)

    # المنتج الواضح: رد حتمي من القائمة، لا نخليه للـAI حتى لا يجاوب جواباً عاماً.
    if products:
        answer = product_answer(products)
        if answer:
            answer = answer.replace("أكيد 🌷\n", "إي 🌷\n", 1)
        if intro:
            answer = intro + answer
        send_message(chat_id, answer.strip(), business_connection_id)
        save_history(chat_id, text, answer.strip())
        return

    # الفئات والأسئلة العامة: هنا فقط نخلي AI يصيغ الحوار.
    if category or availability_question:
        extra_facts = ""

        if category:
            extra_facts += (
                "هذه معلومات فئة استخرجناها من الكتالوج، استخدمها إذا كانت مرتبطة بالسؤال:\n"
                + category
            )

        if availability_question:
            extra_facts += (
                "\nالسؤال عام عن الموجود بالمكتبة. لا تقل إن المكتبة تبيع خدمات أو كتباً "
                "إذا لم تكن موجودة في الكتالوج. اذكر أمثلة من الكتالوج فقط وباختصار."
            )

        try:
            answer = ask_ai(
                chat_id,
                text,
                products,
                extra_facts
            )
        except Exception:
            logging.exception("AI ERROR while answering catalog question")
            # fallback مؤكد بدون اختراع
            if products:
                answer = product_answer(products) or "السعر يحتاج تأكيد من المكتبة 🌷"
            elif category:
                answer = category
            else:
                answer = build_general_availability()

        if intro:
            answer = intro + answer

        send_message(chat_id, answer.strip(), business_connection_id)
        save_history(chat_id, text, answer.strip())
        return

    # الملازم حتى لو ما كانت ضمن القائمة
    if asks_about_malazim(text):
        answer = (
            "بالنسبة للملازم 🌷 آني بوت، وما عندي تأكيد مباشر على سعرها أو توفرها؛ "
            "هاي تحتاج تأكيد من المكتبة."
        )
        answer = intro + answer
        send_message(chat_id, answer, business_connection_id)
        save_history(chat_id, text, answer)
        return

    # أي محادثة عامة أو متابعة غير موجودة حرفياً بالقائمة.
    try:
        answer = ask_ai(chat_id, text, [])
    except Exception as error:
        logging.exception("AI ERROR")
        error_text = str(error).lower()

        if "429" in error_text or "rate limit" in error_text or "quota" in error_text:
            answer = "الخدمة مشغولة حالياً 🌷 حاول بعد شوي."
        elif "401" in error_text or "api key" in error_text or "authentication" in error_text:
            answer = "صار خلل بإعدادات الخدمة 🌷"
        else:
            answer = "صار تأخير بسيط بالخدمة 🌷 حاول بعد شوي."

    # لا تكرر التعريف إلا أول رسالة، ولا تسمح بالكلمات الممنوعة.
    answer = intro + answer
    for word in ("حبيبي", "حبيبتي", "عزيزي", "عزيزتي", "يابه"):
        answer = answer.replace(word, "")

    send_message(chat_id, answer.strip(), business_connection_id)
    save_history(chat_id, text, answer.strip())

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
