import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta
from configs.config import TELEGRAM_BOT_TOKEN, SEARCH_PERIODS
from management.main import get_cheap_flights, get_popular_destinations_from_berlin, find_cheapest_flights_from_berlin
from management.calendar_factory import CalendarMarkup, CalendarCallbackFactory

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

calendar = CalendarMarkup()

user_data = {}

def create_main_keyboard():
    keyboard = [
        [KeyboardButton(text="🔍 Найдешевші рейси")],
        [KeyboardButton(text="🌍 Пошук по місту")],
        [KeyboardButton(text="📅 Пошук на конкретну дату")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def create_period_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="На тиждень", callback_data="period_week"),
            InlineKeyboardButton(text="На місяць", callback_data="period_month"),
            InlineKeyboardButton(text="На 3 місяці", callback_data="period_three_months")
        ]
    ])
    return keyboard

def create_cities_keyboard():
    """Creates a keyboard with cities"""
    destinations = get_popular_destinations_from_berlin()
    buttons = []
    row = []
    for dest in destinations:
        row.append(InlineKeyboardButton(
            text=dest["city"],
            callback_data=f"city_{dest['code']}"
        ))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    text = ("Вітаю! Я допоможу знайти дешеві рейси з Берліна.\n\n"
           "🔍 Найдешевші рейси - показати найдешевші рейси за всіма напрямками\n"
           "🌍 Пошук по місту - вибрати конкретне місто призначення\n"
           "📅 Пошук на конкретну дату - знайти найдешевші рейси до всіх міст на обрану дату")

    if message.from_user.username == "eds_l":
        text = "Добидень, бібізяна! 🐵\n\n" + text
        gif_url = 'https://media1.tenor.com/m/GInmBLIFgKMAAAAd/fat-fat-monkey.gif'
        try:
            await message.answer_animation(gif_url)
        except Exception as e:
            print(f"Error sending GIF: {e}")

    await message.answer(text, reply_markup=create_main_keyboard())

@dp.message(lambda message: message.text == "🔍 Найдешевші рейси")
async def show_cheapest_flights(message: types.Message):
    await message.answer("Виберіть період пошуку:",
                        reply_markup=create_period_keyboard())

@dp.message(lambda message: message.text == "🌍 Пошук по місту")
async def show_cities(message: types.Message):
    await message.answer("Виберіть місто призначення:",
                        reply_markup=create_cities_keyboard())

@dp.message(lambda message: message.text == "📅 Пошук на конкретну дату")
async def show_date_search(message: types.Message):
    await message.answer("Виберіть дату для пошуку найдешевших рейсів:",
                        reply_markup=calendar.create_calendar())

    # Save an empty city code to indicate we're searching for all cities
    user_data[message.from_user.id] = {"city": None, "search_type": "all_cities"}

@dp.callback_query(lambda c: c.data.startswith('period_'))
async def handle_period_selection(callback: types.CallbackQuery):
    period = callback.data.split('_')[1]
    days = SEARCH_PERIODS[period]

    await callback.answer()
    await callback.message.edit_text("🔄 Шукаю найдешевші рейси для кожного міста (це може зайняти до 2-3 хвилин)...")

    # Use days to form the correct date range
    today = datetime.now()
    end_date = today + timedelta(days=days)

    date_from = today.strftime("%Y-%m-%d")
    date_to = end_date.strftime("%Y-%m-%d")

    # Use the function with the correct date parameters
    flights = find_cheapest_flights_from_berlin(date_from, date_to)

    if not flights:
        await callback.message.answer("На жаль, рейсів не знайдено 😢")
        return

    # Create a nice message with the information
    period_text = ""
    if period == "week":
        period_text = f"найближчий тиждень"
    elif period == "month":
        period_text = f"найближчий місяць"
    elif period == "three_months":
        period_text = f"найближчі 3 місяці"

    response = f"🔥 Найдешевші рейси на {period_text} з Берліна:\n\n"

    # Pass all found flights (already sorted by price)
    for flight in flights:
        # Format the date for better display
        flight_date = datetime.strptime(flight['date'].split('T')[0], '%Y-%m-%d').strftime('%d.%m.%Y')
        flight_time = flight['date'].split('T')[1][:5] if 'T' in flight['date'] else ""
        time_info = f", {flight_time}" if flight_time else ""

        response += (f"🛫 {flight['city']}\n"
                    f"💰 Ціна: {flight['price']}€\n"
                    f"📅 Дата: {flight_date}{time_info}\n"
                    f"🔗 [Забронювати]({flight['link']})\n\n")

    await callback.message.answer(response,
                                parse_mode="Markdown",
                                disable_web_page_preview=True)

@dp.callback_query(lambda c: c.data.startswith('city_'))
async def handle_city_selection(callback: types.CallbackQuery):
    city_code = callback.data.split('_')[1]

    await callback.answer()
    await callback.message.edit_text(
        "Виберіть дату початку пошуку:",
        reply_markup=calendar.create_calendar()
    )

    # Save the selected city in memory
    user_data[callback.from_user.id] = {
        "city": city_code,
        "search_type": "specific_city"
    }

@dp.callback_query(CalendarCallbackFactory.filter())
async def process_calendar(callback: types.CallbackQuery, callback_data: CalendarCallbackFactory):
    act = callback_data.act
    year = callback_data.year
    month = callback_data.month
    day = callback_data.day

    if act == "IGNORE":
        await callback.answer(cache_time=60)
        return

    if act == "DAY":
        # Get the selected date
        selected_date = datetime(year=year, month=month, day=day)

        # Check that the date is not in the past
        if selected_date < datetime.now():
            await callback.answer("Не можна вибрати дату в минулому!", show_alert=True)
            return

        # Get the saved user data
        user_id = callback.from_user.id
        user_info = user_data.get(user_id, {})
        city_code = user_info.get("city")
        search_type = user_info.get("search_type", "specific_city")  # Default to specific city search

        await callback.message.edit_text("🔄 Шукаю рейси...")

        # Format the selected date
        date_str = selected_date.strftime("%Y-%m-%d")

        if search_type == "specific_city":
            # Search for flights to specific city on the selected date
            if not city_code:
                await callback.message.edit_text("Помилка: місто не вибрано. Почніть спочатку.")
                return

            flights = get_cheap_flights(
                "BER",
                city_code,
                date_str,
                ""  # Leave empty because API searches on the selected date +/- flexible days
            )

            if not flights:
                await callback.message.edit_text(
                    f"На {selected_date.strftime('%d.%m.%Y')} рейсів не знайдено 😢\n\n"
                    f"Спробуйте обрати іншу дату або інший напрямок."
                )
                return

            response = f"Знайдені рейси на {selected_date.strftime('%d.%m.%Y')}:\n\n"

            # Sort by price and take the 5 cheapest
            sorted_flights = sorted(flights, key=lambda x: x['price'])[:5]

            for flight in sorted_flights:
                flight_date = datetime.strptime(flight['date'].split('T')[0], '%Y-%m-%d').strftime('%d.%m.%Y')
                flight_time = flight['date'].split('T')[1][:5] if 'T' in flight['date'] else ""
                time_info = f", час: {flight_time}" if flight_time else ""

                response += (f"💰 Ціна: {flight['price']}€\n"
                           f"📅 Дата: {flight_date}{time_info}\n"
                           f"🔗 [Забронювати]({flight['link']})\n\n")
        else:
            # Search for cheapest flights to all cities on the selected date
            # We'll use a function to find flights for a specific date across all destinations
            destinations = get_popular_destinations_from_berlin()

            await callback.message.edit_text(f"🔄 Шукаю найдешевші рейси на {selected_date.strftime('%d.%m.%Y')} до всіх міст (це може зайняти до 2-3 хвилин)...")

            cheapest_per_city = {}

            for dest in destinations:
                flights = get_cheap_flights("BER", dest["code"], date_str, "")

                if flights:
                    # Add city name to each flight
                    for flight in flights:
                        flight["city"] = dest["city"]

                    # Find the cheapest flight for this city
                    cheapest_flight = min(flights, key=lambda x: x["price"])
                    cheapest_per_city[dest["city"]] = cheapest_flight

            if not cheapest_per_city:
                await callback.message.edit_text(
                    f"На {selected_date.strftime('%d.%m.%Y')} рейсів не знайдено 😢\n\n"
                    f"Спробуйте обрати іншу дату."
                )
                return

            # Convert dictionary to list and sort by price
            cheapest_flights = list(cheapest_per_city.values())
            sorted_flights = sorted(cheapest_flights, key=lambda x: x["price"])

            response = f"🔥 Найдешевші рейси на {selected_date.strftime('%d.%m.%Y')} з Берліна:\n\n"

            for flight in sorted_flights:
                flight_date = datetime.strptime(flight['date'].split('T')[0], '%Y-%m-%d').strftime('%d.%m.%Y')
                flight_time = flight['date'].split('T')[1][:5] if 'T' in flight['date'] else ""
                time_info = f", {flight_time}" if flight_time else ""

                response += (f"🛫 {flight['city']}\n"
                           f"💰 Ціна: {flight['price']}€\n"
                           f"📅 Дата: {flight_date}{time_info}\n"
                           f"🔗 [Забронювати]({flight['link']})\n\n")

        await callback.message.edit_text(
            response,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

    elif act in ["PREV-MONTH", "NEXT-MONTH"]:
        if act == "PREV-MONTH":
            if month == 1:
                month = 12
                year -= 1
            else:
                month -= 1
        else:
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1

        await callback.message.edit_reply_markup(
            reply_markup=calendar.create_calendar(year, month)
        )

    await callback.answer()
