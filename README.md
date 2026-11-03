# FoodDelivery v2.0

Учебный MVP приложения доставки еды.  
Финальная стадия проекта курса «Основы проектного менеджмента в области аналитики и эксплуатации ИС».

**Репозиторий:** https://github.com/Nikolaj-Python/food-delivery-v2-Nikolaj  
**Release:** v2.0.0

---

## Возможности

- Просмотр меню по категориям
- Корзина и оформление заказа
- Промокоды (SAVE10, WELCOME)
- История заказов
- Программа лояльности (10% бонусов)
- Сохранение данных между запусками

---

## Быстрый старт

```bash
# Клонирование
git clone https://github.com/Nikolaj-Python/food-delivery-v2-Nikolaj.git
cd food-delivery-v2-Nikolaj

# Установка
pip install streamlit

# Запуск
streamlit run app.py
```

Приложение откроется в браузере: http://localhost:8501

---

## Структура проекта

```
food-delivery-v2-Nikolaj/
├── app.py                 # Основное приложение (Streamlit)
├── orders.json            # История заказов
├── bonus.json             # Баланс бонусов
├── USER_GUIDE.md          # Руководство пользователя
├── RETROSPECTIVE.md       # Ретроспектива Спринта 2
├── CHANGELOG.md           # История изменений
├── README.md
├── .gitignore
├── docs/
│   └── screenshots/       # Скриншоты интерфейса
└── presentation/
    └── demo.md            # Презентация для заказчика
```

---

## Документация

- [Руководство пользователя](USER_GUIDE.md)
- [Презентация для заказчика](presentation/demo.md)
- [Ретроспектива](RETROSPECTIVE.md)
- [Changelog](CHANGELOG.md)

---

## Технологии

- Python 3
- Streamlit
- JSON для хранения данных

---

## Автор

Nikolaj-Python  
Учебный проект, 2026
