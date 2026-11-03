"""
FoodDelivery v2.0 — простой MVP приложения доставки еды
Запуск: streamlit run app.py
"""

import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path

# === Пути к файлам данных ===
DATA_DIR = Path(__file__).parent
ORDERS_FILE = DATA_DIR / "orders.json"
BONUS_FILE = DATA_DIR / "bonus.json"

# === Меню ===
MENU = {
    "Пицца Маргарита": {"price": 450, "category": "Пицца", "emoji": "🍕"},
    "Пицца Пепперони": {"price": 520, "category": "Пицца", "emoji": "🍕"},
    "Пицца Четыре сыра": {"price": 580, "category": "Пицца", "emoji": "🍕"},
    "Бургер Классический": {"price": 320, "category": "Бургеры", "emoji": "🍔"},
    "Картофель фри": {"price": 180, "category": "Гарниры", "emoji": "🍟"},
    "Кола 0.5л": {"price": 120, "category": "Напитки", "emoji": "🥤"},
    "Сок апельсиновый": {"price": 150, "category": "Напитки", "emoji": "🧃"},
    "Салат Цезарь": {"price": 290, "category": "Салаты", "emoji": "🥗"},
}

PROMO_CODES = {
    "SAVE10": 0.10,   # 10% скидка
    "WELCOME": 0.15,  # 15% скидка
}


def load_json(path: Path, default):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def save_json(path: Path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def init_session():
    if "cart" not in st.session_state:
        st.session_state.cart = {}
    if "promo" not in st.session_state:
        st.session_state.promo = None
    if "page" not in st.session_state:
        st.session_state.page = "menu"


def get_bonus_balance() -> int:
    data = load_json(BONUS_FILE, {"balance": 0})
    return int(data.get("balance", 0))


def set_bonus_balance(value: int):
    save_json(BONUS_FILE, {"balance": max(0, value)})


def add_to_cart(item: str):
    cart = st.session_state.cart
    cart[item] = cart.get(item, 0) + 1
    st.session_state.cart = cart


def remove_from_cart(item: str):
    cart = st.session_state.cart
    if item in cart:
        cart[item] -= 1
        if cart[item] <= 0:
            del cart[item]
    st.session_state.cart = cart


def cart_total() -> tuple[int, int, int]:
    """Возвращает (сумма_до_скидки, скидка, итого)"""
    subtotal = sum(MENU[item]["price"] * qty for item, qty in st.session_state.cart.items())
    discount = 0
    if st.session_state.promo and st.session_state.promo in PROMO_CODES:
        discount = int(subtotal * PROMO_CODES[st.session_state.promo])
    return subtotal, discount, subtotal - discount


def place_order(email: str, address: str, use_bonuses: int):
    subtotal, discount, total = cart_total()
    total = max(0, total - use_bonuses)

    # Начисляем 10% бонусов от итоговой суммы (после скидки, до списания бонусов)
    earned = int((subtotal - discount) * 0.10)

    order = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "email": email,
        "address": address,
        "items": dict(st.session_state.cart),
        "subtotal": subtotal,
        "discount": discount,
        "bonuses_used": use_bonuses,
        "total": total,
        "bonuses_earned": earned,
        "promo": st.session_state.promo,
    }

    orders = load_json(ORDERS_FILE, [])
    orders.insert(0, order)
    save_json(ORDERS_FILE, orders)

    # Обновляем баланс бонусов
    balance = get_bonus_balance()
    balance = balance - use_bonuses + earned
    set_bonus_balance(balance)

    # Очищаем корзину
    st.session_state.cart = {}
    st.session_state.promo = None
    return order


# === UI ===
st.set_page_config(
    page_title="FoodDelivery v2.0",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()

# --- Sidebar ---
with st.sidebar:
    st.title("🍔 FoodDelivery")
    st.caption("v2.0 — Учебный MVP")

    st.markdown("---")
    if st.button("📋 Меню", use_container_width=True):
        st.session_state.page = "menu"
    if st.button("🛒 Корзина", use_container_width=True):
        st.session_state.page = "cart"
    if st.button("📜 История заказов", use_container_width=True):
        st.session_state.page = "history"
    if st.button("⭐ Программа лояльности", use_container_width=True):
        st.session_state.page = "loyalty"

    st.markdown("---")
    balance = get_bonus_balance()
    st.metric("Ваши бонусы", f"{balance} ⭐")

# --- Main content ---
page = st.session_state.page

if page == "menu":
    st.header("📋 Меню")
    st.write("Выберите блюда и добавьте их в корзину")

    categories = sorted(set(item["category"] for item in MENU.values()))
    for cat in categories:
        st.subheader(cat)
        cols = st.columns(3)
        items = [(name, data) for name, data in MENU.items() if data["category"] == cat]
        for idx, (name, data) in enumerate(items):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"### {data['emoji']} {name}")
                    st.write(f"**{data['price']} ₽**")
                    if st.button("В корзину", key=f"add_{name}", use_container_width=True):
                        add_to_cart(name)
                        st.toast(f"Добавлено: {name}", icon="✅")

elif page == "cart":
    st.header("🛒 Корзина")

    if not st.session_state.cart:
        st.info("Корзина пуста. Перейдите в меню и добавьте блюда.")
    else:
        for item, qty in list(st.session_state.cart.items()):
            col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
            col1.write(f"{MENU[item]['emoji']} **{item}**")
            col2.write(f"{qty} шт.")
            col3.write(f"{MENU[item]['price'] * qty} ₽")
            if col4.button("➖", key=f"rm_{item}"):
                remove_from_cart(item)
                st.rerun()

        st.markdown("---")
        subtotal, discount, total = cart_total()

        # Промокод
        promo_col1, promo_col2 = st.columns([3, 1])
        with promo_col1:
            promo_input = st.text_input("Промокод", placeholder="Например: SAVE10")
        with promo_col2:
            if st.button("Применить"):
                code = promo_input.strip().upper()
                if code in PROMO_CODES:
                    st.session_state.promo = code
                    st.success(f"Промокод {code} применён!")
                    st.rerun()
                else:
                    st.error("Промокод не найден")

        if st.session_state.promo:
            st.write(f"Применён промокод: **{st.session_state.promo}** (−{int(PROMO_CODES[st.session_state.promo]*100)}%)")

        st.write(f"Сумма: **{subtotal} ₽**")
        if discount:
            st.write(f"Скидка: **−{discount} ₽**")
        st.write(f"### Итого: {total} ₽")

        st.markdown("---")
        st.subheader("Оформление заказа")

        email = st.text_input("Email", placeholder="user@example.com")
        address = st.text_input("Адрес доставки", placeholder="ул. Примерная, д. 1, кв. 10")

        max_bonus = min(get_bonus_balance(), total)
        use_bonuses = st.slider("Списать бонусы", 0, max_bonus, 0, step=10) if max_bonus > 0 else 0

        final_total = max(0, total - use_bonuses)
        st.write(f"**К оплате: {final_total} ₽**")

        if st.button("✅ Оформить заказ", type="primary", use_container_width=True):
            if not email or not address:
                st.error("Заполните email и адрес")
            elif not st.session_state.cart:
                st.error("Корзина пуста")
            else:
                order = place_order(email, address, use_bonuses)
                st.success(f"Заказ #{order['id']} успешно создан! Начислено {order['bonuses_earned']} бонусов.")
                st.balloons()
                st.session_state.page = "history"
                st.rerun()

elif page == "history":
    st.header("📜 История заказов")
    orders = load_json(ORDERS_FILE, [])

    if not orders:
        st.info("Заказов пока нет.")
    else:
        for order in orders:
            with st.expander(f"Заказ #{order['id']} — {order['date']} — {order['total']} ₽"):
                st.write(f"**Email:** {order['email']}")
                st.write(f"**Адрес:** {order['address']}")
                st.write("**Состав:**")
                for item, qty in order["items"].items():
                    st.write(f"- {item} × {qty}")
                st.write(f"Сумма: {order['subtotal']} ₽")
                if order.get("discount"):
                    st.write(f"Скидка: −{order['discount']} ₽")
                if order.get("bonuses_used"):
                    st.write(f"Списано бонусов: {order['bonuses_used']}")
                st.write(f"**Итого: {order['total']} ₽**")
                st.write(f"Начислено бонусов: +{order.get('bonuses_earned', 0)} ⭐")

elif page == "loyalty":
    st.header("⭐ Программа лояльности")
    balance = get_bonus_balance()
    st.metric("Текущий баланс бонусов", f"{balance} ⭐")

    st.markdown("""
    ### Как это работает?

    - За каждый заказ вы получаете **10%** от суммы заказа (после скидки) в виде бонусов.
    - 1 бонус = 1 ₽.
    - Бонусы можно списать при следующем заказе.
    - Пример: заказ на 1000 ₽ → начисляется 100 бонусов.

    ### Активные промокоды
    | Промокод | Скидка |
    |----------|--------|
    | SAVE10   | 10%    |
    | WELCOME  | 15%    |
    """)

st.markdown("---")
st.caption("FoodDelivery v2.0 · Учебный проект · Спринт 2")
