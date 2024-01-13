from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

from CV import make_CV

from data.database import *

import time
import os

async def on_startup(_):
    print('Бот запустился')


API_TOKEN = "your_api_token"

bot = Bot(API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class MakeCVGroup(StatesGroup):
    personal_data = State()
    purpose = State()
    exp = State()
    education = State()
    personal_qualities = State()

class UpdateCVGroup(StatesGroup):
    key = State()
    data = State()


kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(
    types.KeyboardButton('На прошлый шаг'),
    types.KeyboardButton('Отменить создание резюме')
)
cancel_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
cancel_kb.add(
    types.KeyboardButton('Отменить создание резюме')
)


@dp.message_handler(commands=['start'])
async def on_start_handler(msg: types.Message):
    await msg.answer('Здравствуйте!\nЯ - бот по созданию резюме. Я помогу вам создать резюме в word файл, а также вы можете отредактировать ваше резюме')
    time.sleep(1)
    await msg.answer('Чтобы начать создавать резюме, напишите команду /make_cv и введите данные, которые я буду запрашивать')


@dp.message_handler(commands=['make_cv'])
async def start_making_cv(msg: types.Message):
    await msg.answer('<b>Шаг 1</b>\nВаши личные данные(ФИО, номер телефона или почта)', reply_markup=cancel_kb, parse_mode='HTML')
    await MakeCVGroup.personal_data.set()


@dp.message_handler(state=MakeCVGroup.personal_data)
async def get_purpose(msg: types.Message, state: FSMContext):
    if msg.text == 'Отменить создание резюме':
        await msg.answer('Отменено создание резюме', reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        return
    
    await state.update_data({'personal_data': msg.text})
    await msg.answer('<b>Шаг 2</b>\nЦель этого резюме: чего вы хотите достичь и какую позицию желаете', parse_mode='HTML', reply_markup=kb)
    await MakeCVGroup.next()


@dp.message_handler(state=MakeCVGroup.purpose)
async def get_personal_data(msg: types.Message, state: FSMContext):
    if msg.text == 'Отменить создание резюме':
        await msg.answer('Отменено создание резюме', reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        return
    if msg.text == 'На прошлый шаг':
        await msg.answer('<b>Шаг 1</b>\nВаш личные данные(ФИО, номер телефона или почта)', reply_markup=cancel_kb, parse_mode='HTML')
        await MakeCVGroup.previous()
        return

    await state.update_data({'purpose': msg.text})
    await msg.answer('<b>Шаг 3</b>\nПрофессиональный опыт: перечень мест работы, компаний в которых вы работали, период работы', parse_mode='HTML', reply_markup=kb)
    await MakeCVGroup.next()


@dp.message_handler(state=MakeCVGroup.exp)
async def get_personal_data(msg: types.Message, state: FSMContext):
    if msg.text == 'Отменить создание резюме':
        await msg.answer('Отменено создание резюме', reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        return
    if msg.text == 'На прошлый шаг':
        await msg.answer('<b>Шаг 2</b>\nЦель этого резюме: чего вы хотите достичь и какую позицию желаете', parse_mode='HTML', reply_markup=kb)
        await MakeCVGroup.previous()
        return

    await state.update_data({'exp': msg.text})
    await msg.answer('<b>Шаг 4</b>\nОбразование: учебные заведения, в которых вы обучались, полученные квалификации или специальности', parse_mode='HTML', reply_markup=kb)
    await MakeCVGroup.next()


@dp.message_handler(state=MakeCVGroup.education)
async def get_personal_data(msg: types.Message, state: FSMContext):
    if msg.text == 'Отменить создание резюме':
        await msg.answer('Отменено создание резюме', reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        return
    if msg.text == 'На прошлый шаг':
        await msg.answer('<b>Шаг 3</b>\nПрофессиональный опыт: перечень мест работы, компаний в которых вы работали, период работы', parse_mode='HTML', reply_markup=kb)
        await MakeCVGroup.previous()
        return

    await state.update_data({'education': msg.text})
    await msg.answer('<b>Шаг 5</b>\nЛичные качества: кратко опишите свои личные качества, которые могут пригодиться в работе', parse_mode='HTML', reply_markup=kb)
    await MakeCVGroup.next()


@dp.message_handler(state=MakeCVGroup.personal_qualities)
async def get_personal_data(msg: types.Message, state: FSMContext):
    if msg.text == 'Отменить создание резюме':
        await msg.answer('Отменено создание резюме', reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        return
    if msg.text == 'На прошлый шаг':
        await msg.answer('<b>Шаг 4</b>\nОбразование: учебные заведения, в которых вы обучались, полученные квалификации или специальности', parse_mode='HTML', reply_markup=kb)
        await MakeCVGroup.previous()
        return

    await state.update_data({'personal_qualities': msg.text})
    await msg.answer('Подготавливаю ваше резюме...')
    async with state.proxy() as data:
        personal_data = data['personal_data']
        purpose = data['purpose']
        exp = data['exp']
        education = data['education']
        personal_qualities = data['personal_qualities']

        if get_user(msg.from_id):
            update_user_column(msg.from_id,
                               {'personal_data': personal_data, 'purpose': purpose,
                                'exp': exp, 'education': education, 'personal_qualities': personal_qualities})
        else:
            add_user(msg.from_id, personal_data, purpose, exp, education, personal_qualities)

        CV_file_path = make_CV(personal_data, purpose, exp, education, personal_qualities, msg.from_user.id)
        CV_file = types.InputFile(CV_file_path)

        await bot.send_document(msg.chat.id, CV_file)
        await msg.answer('Введите /change_cv чтобы изменить параметры резюме')

        os.remove(CV_file_path)

    await state.finish()


@dp.message_handler(commands=['change_cv'])
async def change_cv_kb(msg: types.Message):
    if not get_user(msg.from_id):
        await msg.answer('У вас еще нету резюме чтобы вы могли его изменить')
        return
    menu_cv_kb = types.InlineKeyboardMarkup(1)
    menu_cv_kb.add(
        types.InlineKeyboardButton('Личная информация', callback_data='personal_data'),
        types.InlineKeyboardButton('Цель резюме', callback_data='purpose'),
        types.InlineKeyboardButton('Профессиональный опыт', callback_data='exp'),
        types.InlineKeyboardButton('Образование', callback_data='education'),
        types.InlineKeyboardButton('Личные качества', callback_data='personal_qualities')
    )

    await msg.answer('Что вы хотите изменить в вашем резюме?', reply_markup=menu_cv_kb)

@dp.message_handler(state=UpdateCVGroup.data)
async def update_data(msg: types.Message, state: FSMContext):
    text = msg.text
    await state.update_data({'data': text})
    await state.get_data()
    async with state.proxy() as data:
        update_user_column(msg.from_id, {data['key']: data['data']})

    await msg.answer('Данные обновлены. Высылаю вам отредактированный файл...', reply_markup=types.ReplyKeyboardRemove())

    get_user_params = get_user(msg.from_id)
    new_file_path = make_CV(get_user_params[1], get_user_params[2], get_user_params[3], get_user_params[4], get_user_params[5], msg.from_id)
    file = types.InputFile(new_file_path)

    await bot.send_document(msg.chat.id, file)

    os.remove(new_file_path)


@dp.callback_query_handler(state='*')
async def btn_hanlder(cback: types.CallbackQuery, state: FSMContext):
    key_code = cback.data
    await UpdateCVGroup.data.set()
    await state.update_data({'key': key_code})
    await cback.message.answer('Введите новые данные для выбранной опции', reply_markup=cancel_kb)



if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
