from config_data.config import load_config
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup  # default_state
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


LEXICON: dict[str, str] = {
    'create_task': 'Создать задачу',
    'task_list': 'Список задач',
    'people_list': 'Список людей',
    'add_comment': 'Добавить комментарий',
 }


HELP_TEXT = (
    'Если ты хочешь назначить новую задачу - нажми кнопку ',
    f'\'{LEXICON["create_task"]}\'',
    '\nЕсли ты хочешь просмотреть/отредактировать статистику по '
    f'выполнению задач - нажми кнопку \'{LEXICON["task_list"]}\''
    '\nЕсли ты хочешь посмотреть/отредактировать список '
    f'исполнителей/заказчиков - нажми кнопку \'{LEXICON["people_list"]}\''
    '\nЕсли ты хочешь написать сообщение по поводу исполнителя - '
    f'нажми кнопку \'{LEXICON["add_comment"]}\''
    '\nЯ - молодой бот, если есть вопросы/предложения/замечания - '
    'буду рад их прочитать, нажми для обратной связи /support'
)

# временная бд. ключи - клиенты, значения - список подчиненных исполнителей
temp_db = {

}

# в качестве ключей берем id пользователей, которые позже будем сохранять в бд
temp_executors = {
    "@bRhAdpqgfjqE": "Великородний Алексей",
    #"+7 995 262 8476": "Великородний Тимофей",
    '975508686': "Великородний Тимофей"
}


config = load_config()
# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage = MemoryStorage()
bot = Bot(token=config.tg_bot.token)
dp = Dispatcher(storage=storage)


# Создаем "базу данных" пользователей
user_dict: dict[int, dict[str, str | int | bool]] = {}


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSM(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодействия с пользователем
    create_task_text = State()  # Состояние ожидания ввода текста задания
    create_task_person = State()  # Состояние ожидания ввода ответственного

# some_var_1 = 1
# some_var_2 = 'Some text'

# ########## Подгрузка каких то данных в скрипты ###########
# подгружаем в хранилище workflow_data переменные. Они теперь будут доступны в
# любом месте по ключу (my_int_var, my_text_var)
# dp.workflow_data.update({'my_int_var': some_var_1, 'my_text_var': some_var_2})
# либо:
# dp['my_int_var'] = some_var_1
# dp['my_text_var'] = some_var_2
# либо используя передачу данных при старте поллинга:
# await dp.start_polling(bot, my_int_var=some_var_1, my_text_var=some_var_2)


# Функция для генерации клавиатуры исполнителей
def create_inline_executors(width: int = 1) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    for ex_nick, ex_name in temp_executors.items():
        buttons.append(InlineKeyboardButton(
                text=ex_name,
                callback_data=ex_nick))

    buttons.append(InlineKeyboardButton(
                text='Я',
                callback_data='i'))
    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


# Функция для генерации инлайн-клавиатур "на лету"
def create_inline_kb(width: int,
                     *args: str,
                     **kwargs: str) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    # Заполняем список кнопками из аргументов args и kwargs
    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=LEXICON[button] if button in LEXICON else button,
                callback_data=button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))

    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()


def get_keyboard_with_main_menu():
    return create_inline_kb(
        2, 'create_task', 'task_list', 'people_list', 'add_comment'
    )


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text='Привет!\nЯ буду помогать тебе в составлении заданий, а так же '
        'фиксации их завершения. '
        'Ты можешь добавлять исполнителей, а так же просить у других '
        'назначить задачи тебе '
        'Начнем? Нажми на кнопку "Назначить задачу" для создания своей задачи '
        'или "Добавить заказачика" для того, чтобы другой мог назначить '
        'задачу тебе!',
        reply_markup=get_keyboard_with_main_menu()
    )


# Этот хэндлер будет срабатывать на команду "/help"
@dp.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(HELP_TEXT, reply_markup=get_keyboard_with_main_menu())


@dp.message(Command(commands='cancel'))
async def process_clear_state(message: Message, state: FSMContext):
    # очищаем состояния
    await state.clear()
    await message.answer(
        text="Выбери, что хочешь сделать, либо нажми /help для помощи",
        reply_markup=get_keyboard_with_main_menu()
    )


# кнопка "Назначить задачу"
# @dp.message(Command(commands='create_task'))
@dp.callback_query(F.data == 'create_task')
async def process_create_task(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
            text='<b>Создание новой задачи</b>',
            parse_mode='HTML'
        )
    await callback.message.answer(
        text='Напишите текст задания, либо нажмите /cancel, '
        'если хотите отменить создание задачи'
    )
    # Устанавливаем состояние ожидания ввода имени
    await state.set_state(FSM.create_task_text)
    await callback.answer()


# функция для сохранения задачи
@dp.message(StateFilter(FSM.create_task_text), F.text)
async def process_save_task_text(message: Message, state: FSMContext):
    # Cохраняем введенное имя в хранилище по ключу "name"
    await state.update_data(task_text=message.text)
    await message.answer(
        text='Спасибо!\n\nА теперь укажите, кому поручить задание, '
        'либо нажмите /cancel, если хотите отменить создание задачи.',
        reply_markup=create_inline_executors()
    )
    await state.set_state(FSM.create_task_person)


# функция для назначения ответственного за задачу
@dp.callback_query(StateFilter(FSM.create_task_person))  # , F.data.as_('nick'))
async def process_save_task_person(callback: CallbackQuery, state: FSMContext, bot: Bot):
    # Cохраняем введенное имя в хранилище по ключу "name"
    task_person = callback.data
    await state.update_data(task_person=task_person)
    data = await state.get_data()
    # очищаем состояния
    await state.clear()

    if task_person == 'i':
        name_ex = 'Я'
    else:
        name_ex = temp_executors[data["task_person"]]
        # высылаем уведомление пользователю о задаче
        await bot.send_message(
            chat_id=task_person,
            text=f'<b>Вам назначена новая задача</b>:\n<i>{data["task_text"]}</i>',
            parse_mode='HTML'
        )

    await callback.message.edit_text(
            text=f'В качестве исполнителя выбран: {name_ex}',
        )
    #<a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a>
    await callback.message.answer(
        text=f'<b>Создана новая задача</b>: \n<i>{data["task_text"]}</i>\n\n'
        f'<b>Назначена</b>:\n<i><a href="tg://user?id={task_person}">{name_ex}</a></i>',
        parse_mode='HTML',
        reply_markup=get_keyboard_with_main_menu()
    )
    # await state.set_state(FSM.create_task_person)


# Этот хэндлер будет срабатывать на остальные любые сообщения
@dp.message()
async def process_other_answers(message: Message):
    await message.answer(
        text='Прости, я тебя не понял:('
        '\nВыбери, что хочешь сделать, либо нажми /help для помощи',
        reply_markup=get_keyboard_with_main_menu()
    )

if __name__ == '__main__':
    dp.run_polling(bot)
    # await dp.start_polling(bot)
