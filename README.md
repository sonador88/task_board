# task_board
# Запуск проекта:
- Создать виртуальное окружение и активировать его:
```sh
> python3 -m env env
> source venv/bin/activate
> pip install -r requirements.txt
```
- Заполнить файл .env по примеру .env.example
- Если запуск происходит в Linux - в корне проекта создать папку .pgadmin_data под данные pgadmin и выдать нужные права к ней:
```sh
> mkdir -p .pgadmin_data
> sudo chown -R 5050:5050 .pgadmin_data/
```
- Запустить сборку контейнеров из корня проекта:
```sh
> docker compose up
```

После данных действий будет активировано виртуальное окружение, необходимое для запуска приложения, а так же поднята БД Postgres и графический интерфейс для управления ею PGAdmin
