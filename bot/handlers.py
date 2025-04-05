import requests
import utils

from aiogram import Router, F, html
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

# commands:
    # add_expense
    # get_expenses
    # remove_expense
    # edit_expense

memo = MemoryStorage()

API_URL= "http://api:80"
HELP_MSG = "This is help message"

# ============= ROUTER =================
router = Router()

MAIN_KEYBOARD = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Додати статтю витрат", callback_data="add_expense")],
    [InlineKeyboardButton(text="Отримати звіт за період", callback_data="get_expenses")],
    [InlineKeyboardButton(text="Видалити статтю витрат", callback_data="remove_expense")],
    [InlineKeyboardButton(text="Редагувати статтю витрат", callback_data="edit_expense")]
], resize_keyboard=True)


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Що бажаєте зробити?", reply_markup=MAIN_KEYBOARD)


@router.message(Command("help"))
async def get_help(message: Message) -> None:
    await message.answer("\help")


# =================== FSM for post expense into API ====================    
class Postexpense(StatesGroup):
    description = State()
    uah_amount = State()
    expense_date = State()


@router.message(Command("add_expense"))
@router.callback_query(F.data == "add_expense")
async def post_expense_state_entrance(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")
    await callback.message.answer("Як буде називатись стаття витрат?")
    await state.set_state(Postexpense.description)
    

@router.message(Postexpense.description)
async def post_expense_state_descr(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(f"Введіть суму в гривнях.")
    await state.set_state(Postexpense.uah_amount)
    

@router.message(Postexpense.uah_amount)
async def post_expense_state_uah(message: Message, state: FSMContext):
    await state.update_data(uah_amount=message.text)
    await message.answer(f"Введіть будь ласка дату.")
    await state.set_state(Postexpense.expense_date)
    
    
@router.message(Postexpense.expense_date)
async def post_expense_state_date(message: Message, state: FSMContext):
    await state.update_data(expense_date=message.text)
    expense_data = await state.get_data()
    msg = f"Додано витрату\n<code>{expense_data["description"]}\t|\t{expense_data["uah_amount"]}\t|\t{expense_data["expense_date"]}</code>"
       
    db_item = {
        "description": expense_data["description"],
        "uah_amount": float(expense_data["uah_amount"]),
        "date": utils.to_db_date(expense_data["expense_date"])
    }
    requests.post(f"{API_URL}/expense/", json=db_item)
    await state.clear()
    await message.answer(msg, parse_mode="HTML")
    await message.answer(f"Що бажаєте зробити?", reply_markup=MAIN_KEYBOARD)
    
    
# =========================== Show Expenses in Date Range ===========================
class ExpensesByDate(StatesGroup):
    start_date = State()
    end_date = State()


@router.message(Command("get_expenses"))
@router.callback_query(F.data == "get_expenses")
async def get_expenses_by_date_range(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")
    await callback.message.answer("З якої дати бажаєте отримати звіт?")
    await state.set_state(ExpensesByDate.start_date)
    

@router.message(ExpensesByDate.start_date)
async def post_expense_state_descr(message: Message, state: FSMContext):
    await state.update_data(start_date=message.text)
    await message.answer(f"По яку дату влючно вивести звіт?")
    await state.set_state(ExpensesByDate.end_date)


@router.message(ExpensesByDate.end_date)
async def post_expense_state_descr(message: Message, state: FSMContext):
    await state.update_data(end_date=message.text)
    
    dates = await state.get_data()
    
    expenses_by_date_range = requests.get(f"{API_URL}/expenses/daterange/", params={"start_date": utils.to_db_date(dates["start_date"]), "end_date":utils.to_db_date(dates["end_date"])}).json()
    table = utils.make_table(expenses_by_date_range)
    answ = f"Ваш звіт\n<code>{table}</code>"
    
    await message.answer(answ, parse_mode="HTML")
    await state.clear()
    await message.answer(f"Що бажаєте зробити?", reply_markup=MAIN_KEYBOARD)
    

