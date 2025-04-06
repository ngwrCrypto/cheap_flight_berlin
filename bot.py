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
    """Creates the main keyboard for navigation"""
    keyboard = [
        [KeyboardButton(text="🔍 Cheapest flights")],
        [KeyboardButton(text="🌍 Search by city")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def create_period_keyboard():
    """Creates a keyboard for selecting search period"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="For a week", callback_data="period_week"),
            InlineKeyboardButton(text="For a month", callback_data="period_month")
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
    text = ("Welcome! I'll help you find cheap flights from Berlin.\n\n"
           "🔍 Cheapest flights - show the cheapest flights for all destinations\n"
           "🌍 Search by city - select a specific destination city")

    if message.from_user.username == "eds_l":
        text = "Good day, monkey! 🐵\n\n" + text
        gif_url = 'https://media1.tenor.com/m/GInmBLIFgKMAAAAd/fat-fat-monkey.gif'
        try:
            await message.answer_animation(gif_url)
        except Exception as e:
            print(f"Error sending GIF: {e}")

    await message.answer(text, reply_markup=create_main_keyboard())

@dp.message(lambda message: message.text == "🔍 Cheapest flights")
async def show_cheapest_flights(message: types.Message):
    await message.answer("Select search period:",
                        reply_markup=create_period_keyboard())

@dp.message(lambda message: message.text == "🌍 Search by city")
async def show_cities(message: types.Message):
    await message.answer("Select destination city:",
                        reply_markup=create_cities_keyboard())

@dp.callback_query(lambda c: c.data.startswith('period_'))
async def handle_period_selection(callback: types.CallbackQuery):
    period = callback.data.split('_')[1]
    days = SEARCH_PERIODS[period]

    await callback.answer()
    await callback.message.edit_text("🔄 Searching for the cheapest flights...")

    flights = find_cheapest_flights_from_berlin()
    if not flights:
        await callback.message.answer("Sorry, no flights found 😢")
        return

    response = "Found the cheapest flights:\n\n"
    for flight in flights[:5]:
        response += (f"🛫 {flight['city']}\n"
                    f"💰 Price: {flight['price']}€\n"
                    f"📅 Date: {flight['date'].split('T')[0]}\n"
                    f"🔗 [Book Now]({flight['link']})\n\n")

    await callback.message.answer(response,
                                parse_mode="Markdown",
                                disable_web_page_preview=True)

@dp.callback_query(lambda c: c.data.startswith('city_'))
async def handle_city_selection(callback: types.CallbackQuery):
    city_code = callback.data.split('_')[1]

    await callback.answer()
    await callback.message.edit_text(
        "Select search start date:",
        reply_markup=calendar.create_calendar()
    )

    # Save the selected city in memory (you can use Redis or another storage)
    # Here we use a dictionary as an example
    user_data[callback.from_user.id] = {"city": city_code}

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
            await callback.answer("Cannot select a date in the past!", show_alert=True)
            return

        # Get the saved city
        user_id = callback.from_user.id
        city_code = user_data.get(user_id, {}).get("city")

        if not city_code:
            await callback.message.edit_text("Error: city not selected. Please start over.")
            return

        # Search for flights on the selected date
        end_date = selected_date + timedelta(days=1)
        flights = get_cheap_flights(
            "BER",
            city_code,
            selected_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )

        if not flights:
            await callback.message.edit_text(
                f"No flights found for {selected_date.strftime('%d.%m.%Y')} 😢"
            )
            return

        response = f"Found flights for {selected_date.strftime('%d.%m.%Y')}:\n\n"
        for flight in sorted(flights, key=lambda x: x['price'])[:5]:
            response += (f"💰 Price: {flight['price']}€\n"
                        f"📅 Date: {flight['date'].split('T')[0]}\n"
                        f"🔗 [Book Now]({flight['link']})\n\n")

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
