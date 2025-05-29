from config_data.config import load_config
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


HELP_TEXT = (
    'Если ты хочешь назначить новую задачу - нажми /create_task'
    '\nЕсли ты хочешь просмотреть/отредактировать статистику по '
    'выполнению задач - нажми /task_list'
    '\nЕсли ты хочешь посмотреть/отредактировать список '
    'исполнителей/заказчиков - нажми /people_list'
    '\nЕсли ты хочешь написать сообщение по поводу исполнителя - '
    'нажми /add_comment'
    '\nЯ - молодой бот, если есть вопросы/предложения/замечания - '
    'буду рад их прочитать, нажми для обратной связи /support'
)
LEXICON: dict[str, str] = {
    'create_task': 'Создать задачу',
    'task_list': 'Список задач',
    'people_list': 'Список людей',
    'add_comment': 'Добавить комментарий',
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
    create_task_text = State()        # Состояние ожидания ввода текста задания
    create_task_person = State()         # Состояние ожидания ввода ответственного за выполнения задачи


# some_var_1 = 1
# some_var_2 = 'Some text'

########### Подгрузка каких то данных в скрипты ###########
# подгружаем в хранилище workflow_data переменные. Они теперь будут доступны в любом месте по ключу (my_int_var, my_text_var)
# dp.workflow_data.update({'my_int_var': some_var_1, 'my_text_var': some_var_2})
# либо:
# dp['my_int_var'] = some_var_1
# dp['my_text_var'] = some_var_2
# либо используя передачу данных при старте поллинга:
# await dp.start_polling(bot, my_int_var=some_var_1, my_text_var=some_var_2)


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


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(CommandStart())
async def process_start_command(message: Message):
    keyboard = create_inline_kb(2, 'create_task', 'task_list', 'people_list', 'add_comment')
    await message.answer(
        text='Привет!\nЯ буду помогать тебе в составлении заданий, а так же фиксации их завершения. '
        'Ты можешь добавлять исполнителей, а так же просить у других назначить задачи тебе '
        'Начнем? Нажми на кнопку "Назначить задачу" для создания своей задачи '
        'или "Добавить заказачика" для того, чтобы другой мог назанчить задачу тебе!\n\n'
        'Чтобы узнать обо всех доступных командах и опциях - отправьте команду /help',
        reply_markup=keyboard
    )


# Этот хэндлер будет срабатывать на команду "/help"
@dp.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(HELP_TEXT)


# кнопка "Назначить задачу"
# @dp.message(Command(commands='create_task'))
@dp.callback_query(F.data == 'create_task')
async def process_create_task(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
            text='Напишите текст задания'
        )
    # Устанавливаем состояние ожидания ввода имени
    await state.set_state(FSM.create_task_text)
    await callback.answer()


# функция для сохранения задачи
@dp.message(StateFilter(FSM.create_task_text), F.text)
async def process_save_task_text(message: Message, state: FSMContext):
    # Cохраняем введенное имя в хранилище по ключу "name"
    await state.update_data(task_text=message.text)
    await message.answer(text='Спасибо!\n\nА теперь укажите, кому поручить задание')
    await state.set_state(FSM.create_task_person)


# функция для назначения ответственного за задачу
@dp.message(StateFilter(FSM.create_task_person), F.text)
async def process_save_task_person(message: Message, state: FSMContext):
    # Cохраняем введенное имя в хранилище по ключу "name"
    await state.update_data(task_person=message.text)
    data = await state.get_data()
    await message.answer(
        text=f'=== Задача: ===\n{data["task_text"]}\n\n==='
        f'Назначена: ===\n{data["task_person"]}'
    )
    # await state.set_state(FSM.create_task_person)




# Этот хэндлер будет срабатывать на остальные любые сообщения
@dp.message()
async def process_other_answers(message: Message):
    keyboard = create_inline_kb(2, 'create_task', 'task_list', 'people_list', 'add_comment')
    await message.answer(
        text='Прости, я тебя не понял:('
        '\n Нажми, что хочешь сделать:'
        f'\n {HELP_TEXT}',
        reply_markup=keyboard
    )

if __name__ == '__main__':
    dp.run_polling(bot)
    # await dp.start_polling(bot)
