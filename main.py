from config_data.config import load_config
from aiogram import Bot, Dispatcher


config = load_config()

bot = Bot(token=config.tg_bot.token)
dp = Dispatcher()

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
await dp.start_polling(bot)