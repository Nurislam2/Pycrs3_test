from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import database


survey_router = Router()

gender=['Мужчина', 'Женщина']

kb = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text="Мужской")
        ],
        [
            types.KeyboardButton(text="Женский")
        ]
    ],
    resize_keyboard=True
)


class Survey(StatesGroup):
    name = State()
    age = State()
    gender = State()
    occupation = State()


@survey_router.message(Command("start"))
async def start_survey(message: types.Message, state: FSMContext):
    await state.set_state(Survey.name)
    await message.answer("Ваше имя?")


@survey_router.message(Survey.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Survey.age)
    await message.answer("Сколько вам лет?")


@survey_router.message(Survey.age)
async def process_age(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        if 17 < int(message.text):
            await state.update_data(age=message.text)
            await state.set_state(Survey.gender)
            await message.answer("Какого Вы пола?", reply_markup=kb)

        else:
            await message.answer("Вам не 17 лет опрос окончен")
            await state.clear()

    else:
        await message.answer("Пожалуйста, введите в цифрах.")


@survey_router.message(Survey.gender)
async def process_gender(message: types.Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await state.set_state(Survey.occupation)
    await message.answer("Какие род занятий у вас?")


@survey_router.message(Survey.occupation)
async def process_occupation(message: types.Message, state: FSMContext):
    await state.update_data(occupation=message.text)
    await state.set_state(Survey.age)
    await message.answer("Вы прошли опрос")
    data = await state.get_data()
    database.execute(
        query="INSERT INTO survey (name, age, gender, occupation) VALUES (?, ?, ?, ?)",
        params=(
            data.get('name'),
            data.get('age'),
            data.get('gender'),
            data.get('occupation')
        )
    )
    await state.clear()

@survey_router.message(Command("stop"))
@survey_router.message(F.text.lower() == "стоп")
async def stop(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Спасибо за прохождение опроса!")
