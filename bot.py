import json
import os
import uuid
import qrcode

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MAX_QUANTITY = 10


def load_json(filename):
    with open(os.path.join(BASE_DIR, filename), "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filename, data):
    with open(
        os.path.join(BASE_DIR, filename),
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


config = load_json("config.json")
products = load_json("products.json")

STOCK_FILE = os.path.join(BASE_DIR, "stock.json")

if not os.path.exists(STOCK_FILE):
    save_json("stock.json", {})

stock = load_json("stock.json")

BOT_TOKEN = config["BOT_TOKEN"]
ADMIN_ID = int(config["ADMIN_ID"])
UPI_ID = config["UPI_ID"]
STORE_NAME = config["STORE_NAME"]

pending_orders = {}


def get_product(product_id):
    for product in products:
        if product["id"] == product_id:
            return product
    return None


FILE_STOCK_EXTENSIONS = {".zip"}

def get_file_stock(product_id):
    folder = os.path.join(BASE_DIR, "stock", product_id)
    if not os.path.isdir(folder):
        return []

    return sorted(
        os.path.join(folder, name)
        for name in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, name))
        and os.path.splitext(name)[1].lower() in FILE_STOCK_EXTENSIONS
    )

def get_stock_count(product_id):
    file_stock = get_file_stock(product_id)
    if file_stock:
        return len(file_stock)
    return len(stock.get(product_id, []))


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton(
                "🛍️ Products",
                callback_data="products"
            )
        ],
        [
            InlineKeyboardButton(
                "📜 Terms & Conditions",
                callback_data="terms"
            )
        ],
        [
            InlineKeyboardButton(
                "📞 Support",
                callback_data="support"
            )
        ]
    ]

    await update.message.reply_text(
        f"👋 Welcome to {STORE_NAME}!\n\n"
        "🛒 Buy your products easily and securely.\n\n"
        "📌 Please read our Terms & Conditions "
        "before placing an order.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# TERMS
# =========================

async def terms(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "🔙 Back",
                callback_data="home"
            )
        ]
    ]

    await query.edit_message_text(
        "📜 TERMS & CONDITIONS\n\n"
        "1️⃣ Check the product details and price "
        "before ordering.\n\n"
        "2️⃣ Pay only to the UPI ID shown by the bot.\n\n"
        "3️⃣ Upload a clear and genuine payment "
        "screenshot after payment.\n\n"
        "4️⃣ Orders are processed after payment "
        "verification by the admin.\n\n"
        "5️⃣ Digital products may not be refundable "
        "after successful delivery.\n\n"
        "6️⃣ Fake or duplicate payment claims are "
        "not allowed.\n\n"
        "7️⃣ Contact support if you have an order issue.\n\n"
        "By placing an order, you confirm that you "
        "have read and agreed to these terms.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# HOME
# =========================

async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "🛍️ Products",
                callback_data="products"
            )
        ],
        [
            InlineKeyboardButton(
                "📜 Terms & Conditions",
                callback_data="terms"
            )
        ],
        [
            InlineKeyboardButton(
                "📞 Support",
                callback_data="support"
            )
        ]
    ]

    await query.edit_message_text(
        f"👋 Welcome to {STORE_NAME}!\n\n"
        "Choose an option below:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# PRODUCTS
# =========================

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = []

    for product in products:

        product_id = product["id"]
        available = get_stock_count(product_id)

        if available > 0:
            text = (
                f"{product['name']} - ₹{product['price']} "
                f"(Stock: {available})"
            )
        else:
            text = f"{product['name']} - OUT OF STOCK"

        keyboard.append(
            [
                InlineKeyboardButton(
                    text,
                    callback_data=(
                        f"buy:{product_id}"
                        if available > 0
                        else "outofstock"
                    )
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                "🔙 Back",
                callback_data="home"
            )
        ]
    )

    await query.edit_message_text(
        "🛍️ SELECT A PRODUCT\n\n"
        "Choose the product you want to buy:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# OUT OF STOCK
# =========================

async def out_of_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer(
        "❌ This product is out of stock.",
        show_alert=True
    )


# =========================
# SELECT PRODUCT
# =========================

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    product_id = query.data.split(":")[1]
    product = get_product(product_id)

    if not product:
        await query.edit_message_text(
            "❌ Product not found."
        )
        return

    available = get_stock_count(product_id)

    if available <= 0:
        await query.edit_message_text(
            "❌ This product is out of stock."
        )
        return

    context.user_data["selected_product"] = product_id
    context.user_data["quantity"] = 1

    await show_quantity(
        query,
        product,
        1
    )


# =========================
# QUANTITY
# =========================

async def show_quantity(query, product, quantity):

    available = get_stock_count(product["id"])

    max_allowed = min(
        MAX_QUANTITY,
        available
    )

    if quantity > max_allowed:
        quantity = max_allowed

    total = product["price"] * quantity

    keyboard = [
        [
            InlineKeyboardButton(
                "➖",
                callback_data="qty:minus"
            ),
            InlineKeyboardButton(
                f"Qty: {quantity}",
                callback_data="qty:none"
            ),
            InlineKeyboardButton(
                "➕",
                callback_data="qty:plus"
            )
        ],
        [
            InlineKeyboardButton(
                "✅ Confirm Quantity",
                callback_data="qty:confirm"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Back",
                callback_data="products"
            )
        ]
    ]

    await query.edit_message_text(
        f"🛒 {product['name']}\n\n"
        f"💰 Price: ₹{product['price']} each\n"
        f"📦 Available: {available}\n"
        f"🔢 Quantity: {quantity}\n"
        f"💵 Total: ₹{total}\n\n"
        f"Select quantity (1–{max_allowed}):",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def quantity_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    product_id = context.user_data.get(
        "selected_product"
    )

    if not product_id:
        await query.edit_message_text(
            "❌ Session expired. Please use /start."
        )
        return

    product = get_product(product_id)

    if not product:
        await query.edit_message_text(
            "❌ Product not found."
        )
        return

    available = get_stock_count(product_id)

    max_allowed = min(
        MAX_QUANTITY,
        available
    )

    if max_allowed <= 0:
        await query.edit_message_text(
            "❌ Product is now out of stock."
        )
        return

    quantity = context.user_data.get(
        "quantity",
        1
    )

    action = query.data.split(":")[1]

    if action == "minus":
        quantity = max(
            1,
            quantity - 1
        )

    elif action == "plus":
        quantity = min(
            max_allowed,
            quantity + 1
        )

    elif action == "none":
        return

    elif action == "confirm":

        if quantity > available:
            await query.answer(
                "Not enough stock.",
                show_alert=True
            )
            return

        await create_order(
            query,
            context,
            product,
            quantity
        )
        return

    context.user_data["quantity"] = quantity

    await show_quantity(
        query,
        product,
        quantity
    )


# =========================
# CREATE ORDER
# =========================

async def create_order(
    query,
    context,
    product,
    quantity
):
    available = get_stock_count(product["id"])

    if quantity > available:
        await query.answer(
            "Not enough stock available.",
            show_alert=True
        )
        return

    order_id = "BLX-" + uuid.uuid4().hex[:8].upper()
    total = product["price"] * quantity

    pending_orders[order_id] = {
        "user_id": query.from_user.id,
        "product_id": product["id"],
        "product_name": product["name"],
        "price": product["price"],
        "quantity": quantity,
        "amount": total,
        "status": "waiting_payment"
    }

    # Exact-amount UPI payment URI.
    # The amount is calculated from price x quantity.
    upi_link = (
        "upi://pay?"
        f"pa={UPI_ID}"
        f"&pn={STORE_NAME}"
        f"&am={total}"
        "&cu=INR"
        f"&tn={order_id}"
    )

    # Generate a temporary QR image for this exact order amount.
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )
    qr.add_data(upi_link)
    qr.make(fit=True)

    qr_image = qr.make_image()
    qr_path = os.path.join(BASE_DIR, f"qr_{order_id}.png")
    qr_image.save(qr_path)

    keyboard = [
        [
            InlineKeyboardButton(
                "💳 I Have Paid",
                callback_data=f"paid:{order_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "🛍️ Products",
                callback_data="products"
            )
        ]
    ]

    caption = (
        "🧾 ORDER CREATED\n\n"
        f"🆔 Order ID: {order_id}\n"
        f"📦 Product: {product['name']}\n"
        f"💰 Price: ₹{product['price']} each\n"
        f"🔢 Quantity: {quantity}\n"
        f"💵 TOTAL: ₹{total}\n\n"
        f"💳 UPI ID:\n{UPI_ID}\n\n"
        "📲 Scan the QR code to pay the exact amount.\n"
        "After payment, press \"I Have Paid\"."
    )

    try:
        with open(qr_path, "rb") as qr_file:
            await context.bot.send_photo(
                chat_id=query.from_user.id,
                photo=qr_file,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    finally:
        try:
            os.remove(qr_path)
        except OSError:
            pass


# =========================
# PAID
# =========================

async def paid(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    order_id = query.data.split(":")[1]

    if order_id not in pending_orders:
        # The QR message is a photo, so never try to edit it as text.
        await query.answer(
            "❌ Order expired. Please create a new order.",
            show_alert=True
        )
        return

    pending_orders[order_id]["status"] = (
        "waiting_screenshot"
    )

    # The order message is a photo (QR), so it has a caption,
    # not editable text. Send the screenshot instruction as a new message.
    await query.message.reply_text(
        f"📸 ORDER `{order_id}`\n\n"
        "Please send your payment screenshot here.",
        parse_mode="Markdown"
    )

    # Remove the payment buttons from the QR message.
    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass


# =========================
# SCREENSHOT
# =========================

async def receive_screenshot(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message or not update.message.photo:
        return

    user_id = update.effective_user.id

    order_id = None

    for oid, order in pending_orders.items():

        if (
            order["user_id"] == user_id
            and
            order["status"] == "waiting_screenshot"
        ):
            order_id = oid
            break

    if not order_id:
        await update.message.reply_text(
            "❌ No active order found.\n"
            "Please create a new order using /start."
        )
        return

    order = pending_orders[order_id]

    order["status"] = "waiting_admin"

    photo = update.message.photo[-1]

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ APPROVE",
                callback_data=f"approve:{order_id}"
            ),
            InlineKeyboardButton(
                "❌ REJECT",
                callback_data=f"reject:{order_id}"
            )
        ]
    ]

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo.file_id,
        caption=(
            "🔔 NEW PAYMENT\n\n"
            f"🆔 Order ID: {order_id}\n"
            f"👤 User ID: {user_id}\n"
            f"👤 Username: "
            f"@{update.effective_user.username or 'No username'}\n\n"
            f"📦 Product: {order['product_name']}\n"
            f"💰 Price: ₹{order['price']}\n"
            f"🔢 Quantity: {order['quantity']}\n"
            f"💵 Total: ₹{order['amount']}\n\n"
            "Verify payment and choose an action."
        ),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await update.message.reply_text(
        f"✅ Payment screenshot received.\n\n"
        f"Order ID: `{order_id}`\n"
        "Your payment is being checked.",
        parse_mode="Markdown"
    )


# =========================
# APPROVE + DELIVER CODES
# =========================

async def approve(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    order_id = query.data.split(":")[1]

    if order_id not in pending_orders:
        await query.answer("Order not found.", show_alert=True)
        return

    order = pending_orders[order_id]

    if order["status"] != "waiting_admin":
        await query.answer(
            "This order has already been processed.",
            show_alert=True
        )
        return

    product_id = order["product_id"]
    quantity = order["quantity"]

    # ZIP file stock takes priority when stock/<product_id>/ contains ZIPs.
    file_stock = get_file_stock(product_id)

    if file_stock:
        if len(file_stock) < quantity:
            await query.answer(
                "Not enough file stock to deliver this order.",
                show_alert=True
            )
            return

        selected_files = file_stock[:quantity]

        try:
            for path in selected_files:
                with open(path, "rb") as f:
                    await context.bot.send_document(
                        chat_id=order["user_id"],
                        document=f,
                        caption=(
                            "🎉 PAYMENT APPROVED ✅\n\n"
                            f"🆔 Order ID: {order_id}\n"
                            f"📦 Product: {order['product_name']}\n"
                            f"🔢 Quantity: {quantity}\n\n"
                            "📦 Your file is attached below."
                        )
                    )
        except Exception as exc:
            print("File delivery error:", exc)
            await query.answer(
                "Delivery failed. Stock was not changed.",
                show_alert=True
            )
            return

        # Remove files only after all requested files were sent.
        for path in selected_files:
            try:
                os.remove(path)
            except OSError as exc:
                print("Could not remove delivered file:", exc)

        order["status"] = "approved"
        order["delivered_files"] = [
            os.path.basename(path) for path in selected_files
        ]

        await query.edit_message_caption(
            caption=(
                "🎉 PAYMENT APPROVED & DELIVERED ✅\n\n"
                f"🆔 Order ID: {order_id}\n"
                f"📦 Product: {order['product_name']}\n"
                f"🔢 Quantity: {quantity}\n"
                f"📦 Files delivered: {quantity}"
            )
        )
        return

    # Existing code-stock fallback.
    available_codes = stock.get(product_id, [])

    if len(available_codes) < quantity:
        await query.answer(
            "Not enough stock to deliver this order.",
            show_alert=True
        )
        return

    delivered_codes = available_codes[:quantity]
    stock[product_id] = available_codes[quantity:]
    save_json("stock.json", stock)

    order["status"] = "approved"
    order["delivered_codes"] = delivered_codes

    codes_text = "\n".join(
        f"{i + 1}. `{code}`"
        for i, code in enumerate(delivered_codes)
    )

    await context.bot.send_message(
        chat_id=order["user_id"],
        text=(
            "🎉 PAYMENT APPROVED ✅\n\n"
            f"🆔 Order ID: {order_id}\n"
            f"📦 Product: {order['product_name']}\n"
            f"🔢 Quantity: {quantity}\n"
            f"💵 Total: ₹{order['amount']}\n\n"
            "🎁 YOUR CODES\n\n"
            f"{codes_text}\n\n"
            "Please keep these codes safe."
        ),
        parse_mode="Markdown"
    )

    await query.edit_message_caption(
        caption=(
            "🎉 PAYMENT APPROVED & DELIVERED ✅\n\n"
            f"🆔 Order ID: {order_id}\n"
            f"📦 Product: {order['product_name']}\n"
            f"🔢 Quantity: {quantity}\n"
            f"💵 Total: ₹{order['amount']}\n"
            f"📦 Codes delivered: {quantity}"
        )
    )


# =========================
# REJECT
# =========================

async def reject(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    order_id = query.data.split(":")[1]

    if order_id not in pending_orders:
        await query.answer(
            "Order not found.",
            show_alert=True
        )
        return

    order = pending_orders[order_id]

    if order["status"] != "waiting_admin":
        await query.answer(
            "This order has already been processed.",
            show_alert=True
        )
        return

    order["status"] = "rejected"

    await context.bot.send_message(
        chat_id=order["user_id"],
        text=(
            "❌ PAYMENT REJECTED\n\n"
            f"🆔 Order ID: {order_id}\n\n"
            "The payment could not be verified.\n\n"
            "If you believe this is an error, "
            "please contact support."
        )
    )

    await query.edit_message_caption(
        caption=(
            "❌ PAYMENT REJECTED\n\n"
            f"🆔 Order ID: {order_id}\n"
            f"📦 Product: {order['product_name']}\n"
            f"🔢 Quantity: {order['quantity']}\n"
            f"💵 Total: ₹{order['amount']}"
        )
    )


# =========================
# SUPPORT
# =========================

async def support(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "🔙 Back",
                callback_data="home"
            )
        ]
    ]

    await query.edit_message_text(
        "📞 SUPPORT\n\n"
        "If you have a problem with your order "
        "or payment, please contact the store admin.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# MAIN
# =========================

def main():

    application = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CallbackQueryHandler(
            show_products,
            pattern="^products$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            buy,
            pattern="^buy:"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            quantity_handler,
            pattern="^qty:"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            paid,
            pattern="^paid:"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            approve,
            pattern="^approve:"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            reject,
            pattern="^reject:"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            terms,
            pattern="^terms$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            home,
            pattern="^home$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            support,
            pattern="^support$"
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            out_of_stock,
            pattern="^outofstock$"
        )
    )

    application.add_handler(
        MessageHandler(
            filters.PHOTO,
            receive_screenshot
        )
    )

    print(
        "Babluxselling Bot is running..."
    )

    application.run_polling()


if __name__ == "__main__":
    main()