import re
import requests
import utils
from datetime import date

from aiogram import Router, F, html
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# commands:
    # add_expense
    # get_expenses
    # remove_expense
    # edit_expense

API_URL= "http://api:80"
HELP_MSG = "This is help message"
ERR_MSG = "Якісь проблеми з сервером.\nCпробуйте пізніше."

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
    if re.findall(r'[a-zA-Zа-яА-Я]|\-', message.text): # check if found any letters
        await message.answer(f"Cуму будь ласка тільки числами, або з дробною частиною") # if found any letter -> redo process
    else:
        await state.update_data(uah_amount=message.text)
        await message.answer(f"Введіть будь ласка дату у форматі дд.мм.РРРР")
        await state.set_state(Postexpense.expense_date)
    
    
@router.message(Postexpense.expense_date)
async def post_expense_state_date(message: Message, state: FSMContext):
    if re.findall(r'^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0,1,2])\.(19|20)\d{2}$', message.text): # check if there proper date `dd.mm.YYYY` format
        await state.update_data(expense_date=message.text)
        expense_data = await state.get_data()
    
        db_item = {
            "description": expense_data["description"],
            "uah_amount": float(expense_data["uah_amount"]),
            "date": utils.to_db_date(expense_data["expense_date"])
        }
        try:
            res = requests.post(f"{API_URL}/expense/", json=db_item)
            res.raise_for_status()
            msg = f"Додано витрату\n<code>{expense_data["description"]}\t|\t{expense_data["uah_amount"]}\t|\t{expense_data["expense_date"]}</code>"
            await state.clear()
            await message.answer(msg, parse_mode="HTML")
            await message.answer(f"Що бажаєте зробити?", reply_markup=MAIN_KEYBOARD)
        except:
            await state.clear()
            await message.answer(ERR_MSG)
            await message.answer(f"Що бажаєте зробити?", reply_markup=MAIN_KEYBOARD)
    else: # if non-proper format -> redo
        await message.answer(f"Щось не так з датою")
        
    
# =========================== Show Expenses in Date Range ===========================
class ExpensesByDate(StatesGroup):
    start_date = State()
    end_date = State()


@router.message(Command("get_expenses"))
@router.callback_query(F.data == "get_expenses")
async def get_expenses_by_date_range(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")
    await callback.message.answer("Введіть дату у форматі дд.мм.РРРР з якої бажаєте отримати звіт?")
    await state.set_state(ExpensesByDate.start_date)
    

@router.message(ExpensesByDate.start_date)
async def expense_by_range_start_state(message: Message, state: FSMContext):
    if re.findall(r'^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0,1,2])\.(19|20)\d{2}$', message.text): # check if there proper date `dd.mm.YYYY` format
        await state.update_data(start_date=message.text)
        await message.answer(f"Введіть дату у форматі дд.мм.РРРР по яку влючно вивести звіт?")
        await state.set_state(ExpensesByDate.end_date)
    else:
        await message.answer(f"Щось не так з датою")


@router.message(ExpensesByDate.end_date)
async def expense_by_range_end_state(message: Message, state: FSMContext):
    if re.findall(r'^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0,1,2])\.(19|20)\d{2}$', message.text): # check if there proper date `dd.mm.YYYY` format
        await state.update_data(end_date=message.text)
        dates = await state.get_data()
        
        try:
            expenses_by_date_range = requests.get(f"{API_URL}/expenses/daterange/", params={"start_date": utils.to_db_date(dates["start_date"]), "end_date":utils.to_db_date(dates["end_date"])}).json()
            if expenses_by_date_range[0] is None:
                raise Exception("Cant get expenses list")
            
            utils.make_xlsx_file(expenses_by_date_range)
            file = FSInputFile("./Expenses.xlsx", filename=f"Expenses {dates["start_date"]} - {dates['end_date']}.xlsx")

            await message.answer_document(file,caption=f"Ваш звіт за {dates["start_date"]} - {dates['end_date']}:")
            await state.clear()
            await message.answer(f"Що бажаєте зробити?", reply_markup=MAIN_KEYBOARD)
        except:
            await state.clear()
            await message.answer("Не зміг знайти витрати за цей період")
            await message.answer(f"Що бажаєте зробити?", reply_markup=MAIN_KEYBOARD)
    else:
        await message.answer(f"Щось не так з датою")
    

# ============================== Remove expense ==============================
class RemoveExpenses(StatesGroup):
    expense_id = State()


@router.message(Command("remove_expense"))
@router.callback_query(F.data == "remove_expense")
async def get_all_expenses(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")
    try:
        expenses = requests.get(f"{API_URL}/expenses/").json()
        if expenses[0] is None:
            raise Exception("Somethings with expenses")
        
        utils.make_xlsx_file(expenses)
        
        file = FSInputFile("./Expenses.xlsx", filename=f"Expenses-{date.today()}.xlsx")
        answ = f"Звіт по всім витратам"

        await callback.message.answer_document(file, caption=answ)
        await callback.message.answer(f"Напишіть ід витрати котру ви хочете видалити")
        await state.set_state(RemoveExpenses.expense_id)
    except:
        await state.clear()
        await callback.message.answer(ERR_MSG)
        await callback.message.answer(f"Що бажаєте зробити?", reply_markup=MAIN_KEYBOARD)
    

@router.message(RemoveExpenses.expense_id)
async def remove_expense(message: Message, state: FSMContext):
    if re.findall(r'\D', message.text):
        await message.answer(f"Щось не так з ІД")
    else:
        expense_id = message.text
        try:    
            removed_expense = requests.delete(f"{API_URL}/expense/", params={"expense_id": int(expense_id)}).json()
            if removed_expense["date"] is None:
                raise Exception("Something wrong with API")
            
            text = f"<code>{removed_expense["date"]}\t|\t{removed_expense["id"]}\t|\t{removed_expense["description"]}\t|\t{removed_expense["uah_amount"]}</code>"
            answ = f"Витрату видалено\n{text}"
            await message.answer(answ, parse_mode="HTML")
            await state.clear()
            await message.answer(f"Що бажаєте зробити?", reply_markup=MAIN_KEYBOARD)
        except:
            await state.clear()
            await message.answer(ERR_MSG)
            await message.answer(f"Що бажаєте зробити?", reply_markup=MAIN_KEYBOARD)
    
# ============================== Expense by date ==============================
class PutExpense(StatesGroup):
    to_edit_expense_id = State()
    description = State()
    uah_amount = State()
    expense_date = State()


@router.message(Command("edit_expense"))
@router.callback_query(F.data == "edit_expense")
async def get_all_expenses(callback: CallbackQuery, state: FSMContext):
    await callback.answer("")
    try:
        expenses = requests.get(f"{API_URL}/expenses/").json()
        if expenses[0] is None:
            raise Exception("Cant GET all expenses from API")
      
        utils.make_xlsx_file(expenses)
        
        file = FSInputFile("./Expenses.xlsx", filename=f"Expenses-{date.today()}.xlsx")
        answ = f"Звіт по всім витратам"

        await callback.message.answer_document(file, caption=answ)
        await callback.message.answer(f"Напишіть ід витрати котру ви хочете редагувати")
        await state.set_state(PutExpense.to_edit_expense_id)
    except:
        await state.clear()
        await callback.message.answer("Не зміг отримати данні за весь час")
        await callback.message.answer(f"Що бажаєте зробити?", reply_markup=MAIN_KEYBOARD)


@router.message(PutExpense.to_edit_expense_id)
async def remove_expense(message: Message, state: FSMContext):
    if re.findall(r'\D', message.text): # if found any non digit characher
        await message.answer(f"Щось не так з ІД")
    else:
        await state.update_data(to_edit_expense_id = message.text)
        await message.answer(f"Як буде називатись стаття витрат?")
        await state.set_state(PutExpense.description)


@router.message(PutExpense.description)
async def post_expense_state_descr(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(f"Введіть суму в гривнях.")
    await state.set_state(PutExpense.uah_amount)
    

@router.message(PutExpense.uah_amount)
async def post_expense_state_uah(message: Message, state: FSMContext):
    if re.findall(r'[a-zA-Zа-яА-Я]|\-', message.text): # check if found any letters
        await message.answer(f"Cуму будь ласка тільки числами, або з дробною частиною") # if found any letter -> redo process
    else:
        await state.update_data(uah_amount=message.text)
        await message.answer(f"Введіть будь ласка дату.")
        await state.set_state(PutExpense.expense_date)
    
    
@router.message(PutExpense.expense_date)
async def post_expense_state_date(message: Message, state: FSMContext):
    if re.findall(r'^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0,1,2])\.(19|20)\d{2}$', message.text): # check if there proper date `dd.mm.YYYY` format
        await state.update_data(expense_date=message.text)
        expense_data = await state.get_data()
        
        db_item = {
            "description": expense_data["description"],
            "uah_amount": float(expense_data["uah_amount"]),
            "date": utils.to_db_date(expense_data["expense_date"])
        }
        try:
            res = requests.put(f"{API_URL}/expense/", params={"expense_id": expense_data["to_edit_expense_id"]},json=db_item).json()
            if res["date"] is None:
                raise Exception("cant PUT expense")
            
            msg = f"Нові данні:\n<code>{res["description"]}\t|\t{res["uah_amount"]}\t|\t{res["date"]}</code>"
            
            await state.clear()
            await message.answer(msg, parse_mode="HTML")
            await message.answer(f"Що бажаєте зробити?", reply_markup=MAIN_KEYBOARD)
        except:
            await state.clear()
            await message.answer(ERR_MSG)
            await message.answer(f"Що бажаєте зробити?", reply_markup=MAIN_KEYBOARD)
    else:
        await message.answer(f"Щось не так з датою")