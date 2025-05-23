import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta
from configs.config import TELEGRAM_BOT_TOKEN, SEARCH_PERIODS
from management.main import (
    get_cheap_flights,
    get_popular_destinations_from_berlin,
    find_cheapest_flights_from_berlin,
    find_cheapest_flights_from_berlin_async,
    search_all_cities_for_date_async
)
from management.calendar_factory import CalendarMarkup, CalendarCallbackFactory
import logging

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
    # Extract period correctly: if there are multiple parts, join them after the first underscore
    parts = callback.data.split('_')
    period = '_'.join(parts[1:]) if len(parts) > 2 else parts[1]

    days = SEARCH_PERIODS[period]

    await callback.answer()
    progress_message = await callback.message.edit_text("🔄 Шукаю найдешевші рейси для кожного міста (це може зайняти до 2-3 хвилин)...")

    # Use days to form the correct date range
    today = datetime.now()
    end_date = today + timedelta(days=days)

    date_from = today.strftime("%Y-%m-%d")
    date_to = end_date.strftime("%Y-%m-%d")

    # Use the async function to find flights in parallel
    try:
        start_time = datetime.now()
        flights = await find_cheapest_flights_from_berlin_async(date_from, date_to)
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        print(f"Flight search completed in {execution_time:.2f} seconds")
    except Exception as e:
        await callback.message.answer(f"Сталася помилка при пошуку: {e}")
        return

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

    await progress_message.edit_text(
        response,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

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

        # Send a progress message that can be updated
        progress_message = await callback.message.edit_text("🔄 Шукаю рейси...")

        # Format the selected date
        date_str = selected_date.strftime("%Y-%m-%d")

        try:
            start_time = datetime.now()

            if search_type == "specific_city":
                # Search for flights to specific city on the selected date
                if not city_code:
                    await progress_message.edit_text("Помилка: місто не вибрано. Почніть спочатку.")
                    return

                flights = get_cheap_flights(
                    "BER",
                    city_code,
                    date_str,
                    ""  # Leave empty because API searches on the selected date +/- flexible days
                )

                if not flights:
                    await progress_message.edit_text(
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
                await progress_message.edit_text(f"🔄 Шукаю найдешевші рейси на {selected_date.strftime('%d.%m.%Y')} до всіх міст...")

                # Use the async function for parallel requests
                sorted_flights = await search_all_cities_for_date_async(date_str)

                if not sorted_flights:
                    await progress_message.edit_text(
                        f"На {selected_date.strftime('%d.%m.%Y')} рейсів не знайдено 😢\n\n"
                        f"Спробуйте обрати іншу дату."
                    )
                    return

                response = f"🔥 Найдешевші рейси на {selected_date.strftime('%d.%m.%Y')} з Берліна:\n\n"

                for flight in sorted_flights:
                    flight_date = datetime.strptime(flight['date'].split('T')[0], '%Y-%m-%d').strftime('%d.%m.%Y')
                    flight_time = flight['date'].split('T')[1][:5] if 'T' in flight['date'] else ""
                    time_info = f", {flight_time}" if flight_time else ""

                    response += (f"🛫 {flight['city']}\n"
                               f"💰 Ціна: {flight['price']}€\n"
                               f"📅 Дата: {flight_date}{time_info}\n"
                               f"🔗 [Забронювати]({flight['link']})\n\n")

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            print(f"Flight search completed in {execution_time:.2f} seconds")

            await progress_message.edit_text(
                response,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        except Exception as e:
            await progress_message.edit_text(f"Сталася помилка при пошуку: {e}")
            return

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

async def handle_period_selection(message: types.Message):
    """Handle selection of search period"""
    user_id = message.from_user.id
    period = message.text.lower()

    # Save the selected period in user state
    user_data[user_id]["period"] = period

    # Calculate date range based on selected period
    today = datetime.now()

    if period == "тиждень":
        date_to = today + timedelta(days=SEARCH_PERIODS["week"])
    elif period == "місяць":
        date_to = today + timedelta(days=SEARCH_PERIODS["month"])
    elif period == "три місяці":
        date_to = today + timedelta(days=SEARCH_PERIODS["three_months"])
    else:
        # Default to one month
        date_to = today + timedelta(days=SEARCH_PERIODS["month"])

    # Format dates
    date_from = today.strftime("%Y-%m-%d")
    date_to = date_to.strftime("%Y-%m-%d")

    # Store dates in user data
    user_data[user_id]["date_from"] = date_from
    user_data[user_id]["date_to"] = date_to

    # Log period and date range
    logging.info(f"User {user_id} selected period: {period}, searching from {date_from} to {date_to}")

    # Send a message to inform the user that search is in progress
    search_message = await message.answer("🔍 Шукаю найдешевші квитки з Берліна... Це може зайняти деякий час.")

    # Store the search message ID for later updates
    user_data[user_id]["search_message_id"] = search_message.message_id

    try:
        # Use the period to determine how to search
        if period == "тиждень":
            # For shorter periods, use simpler search
            results = await find_cheapest_flights_from_berlin_async(date_from, date_to)
        elif period == "місяць":
            # For month, use the specific dates
            results = await find_cheapest_flights_from_berlin_async(date_from, date_to)
        elif period == "три місяці":
            # For three months, use the specific dates
            results = await find_cheapest_flights_from_berlin_async(date_from, date_to)
        else:
            # Default to one month
            results = await find_cheapest_flights_from_berlin_async(date_from, date_to)

        # Sort results by price
        results = sorted(results, key=lambda x: x["price"])

        # Get the top 5 cheapest flights
        top_5_flights = results[:5]

        # Format a message with the results
        if top_5_flights:
            # Create a nice message with flight details
            message_text = f"🔥 Найдешевші квитки з Берліна за {period}:\n\n"

            for i, flight in enumerate(top_5_flights, 1):
                # Extract the date without time
                date_str = flight["date"].split("T")[0]
                message_text += f"{i}. {flight['city']}: {flight['price']}€ ({date_str})\n"
                message_text += f"   🔗 [Забронювати]({flight['link']})\n\n"

            # Update the previous search message with the results
            await bot.edit_message_text(
                message_text,
                chat_id=message.chat.id,
                message_id=user_data[user_id]["search_message_id"],
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        else:
            await bot.edit_message_text(
                "😔 Не знайдено жодних квитків для вибраного періоду.",
                chat_id=message.chat.id,
                message_id=user_data[user_id]["search_message_id"]
            )
    except Exception as e:
        logging.error(f"Error during flight search: {e}")
        await bot.edit_message_text(
            "😢 Сталася помилка під час пошуку квитків. Спробуйте пізніше.",
            chat_id=message.chat.id,
            message_id=user_data[user_id]["search_message_id"]
        )
