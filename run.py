# Импорт необходимых библиотек
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Конфигурация бота
DB_PATH = "BD.db"  # Путь к базе данных
BOT_TOKEN = "7577124754:AAG5XDNRijKgxdVjDj_qpwim--W-VoefnIQ"  # Токен бота

def fetch_games_by_column(column_name: str, value: int) -> list:
    """Получение игр по указанному столбцу и значению."""
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Формируем SQL-запрос для поиска игр
        query = f"""
            SELECT Name_game 
            FROM Games 
            WHERE {column_name} = ?
        """
        cursor.execute(query, (value,))
        games = cursor.fetchall()
        conn.close()
        return [game[0] for game in games]  # Возвращаем список названий игр
    except sqlite3.Error as e:
        print(f"Ошибка работы с БД: {e}")
        return []

def get_random_game() -> str:
    """Получение случайной игры из базы данных."""
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Выбираем случайную игру
        cursor.execute("SELECT Name_game FROM Games ORDER BY RANDOM() LIMIT 1")
        game = cursor.fetchone()
        conn.close()
        return game[0] if game else "Не удалось найти игру"
    except sqlite3.Error as e:
        print(f"Ошибка работы с БД: {e}")
        return "Ошибка при получении игры"

def count_games() -> int:
    """Подсчет общего количества игр в базе."""
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Считаем количество игр
        cursor.execute("SELECT COUNT(*) FROM Games")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except sqlite3.Error as e:
        print(f"Ошибка работы с БД: {e}")
        return 0

async def add_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды добавления игры."""
    # Проверяем наличие аргументов
    if not context.args:
        await update.message.reply_text(
            "Пожалуйста, укажите данные игры в формате:\n"
            "/add Название игры; Жанр; Разработчик; Издатель; Самый популярный тег; Локализация\n\n"
            "Пример:\n"
            "/add The Witcher 3; RPG; CD Projekt; CD Projekt RED; Открытый мир; Полная"
        )
        return
    
    try:
        # Разбиваем ввод пользователя на компоненты
        data = ' '.join(context.args).split(';')
        if len(data) != 4:
            raise ValueError("Неверный формат данных")
            
        name, genre, developer, publisher, localization = [x.strip() for x in data]
        
        # Подключаемся к базе данных
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Проверяем, существует ли игра
        cursor.execute("SELECT id FROM Games WHERE Name_game = ?", (name,))
        if cursor.fetchone():
            await update.message.reply_text("Эта игра уже есть в базе данных!")
            conn.close()
            return
            
        # Получаем или добавляем жанр
        cursor.execute("SELECT id FROM Genres WHERE Name = ?", (genre,))
        genre_id = cursor.fetchone()
        if not genre_id:
            cursor.execute("INSERT INTO Genres (Name) VALUES (?)", (genre,))
            genre_id = cursor.lastrowid
        else:
            genre_id = genre_id[0]
            
        # Получаем или добавляем разработчика
        cursor.execute("SELECT id FROM Developers WHERE Name = ?", (developer,))
        developer_id = cursor.fetchone()
        if not developer_id:
            cursor.execute("INSERT INTO Developers (Name) VALUES (?)", (developer,))
            developer_id = cursor.lastrowid
        else:
            developer_id = developer_id[0]
            
        # Получаем или добавляем издателя
        cursor.execute("SELECT id FROM Publishers WHERE Name = ?", (publisher,))
        publisher_id = cursor.fetchone()
        if not publisher_id:
            cursor.execute("INSERT INTO Publishers (Name) VALUES (?)", (publisher,))
            publisher_id = cursor.lastrowid
        else:
            publisher_id = publisher_id[0]

        # Получаем или добавляем тег
        cursor.execute("SELECT id FROM Tags WHERE Name = ?", (tags,))
        tags_id = cursor.fetchone()
        if not tags_id:
            cursor.execute("INSERT INTO Tags (Name) VALUES (?)", (tags,))
            tags_id = cursor.lastrowid
        else:
            tags_id = tags_id[0]

        # Получаем или добавляем локализацию
        cursor.execute("SELECT id FROM Localization WHERE Name = ?", (localization,))
        localization_id = cursor.fetchone()
        if not localization_id:
            cursor.execute("INSERT INTO Localization (Name) VALUES (?)", (localization,))
            localization_id = cursor.lastrowid
        else:
            localization_id = localization_id[0]
            
        # Добавляем игру в базу данных
        cursor.execute(
            "INSERT INTO Games (Name_game, id_Genre, id_Developer, id_Publisher, id_Tags, id_Localization) VALUES (?, ?, ?, ?)",
            (name, genre_id, developer_id, publisher_id, tags_id, localization_id)
        )
        
        conn.commit()
        conn.close()
        await update.message.reply_text(f"Игра '{name}' успешно добавлена в базу данных!")
        
    except Exception as e:
        await update.message.reply_text(f"Ошибка при добавлении игры: {str(e)}")
        print(f"Ошибка добавления игры: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    # Создаем клавиатуру с кнопками
    keyboard = [
        [InlineKeyboardButton("По жанру", callback_data='genre'),
         InlineKeyboardButton("По разработчику", callback_data='developer')],
        [InlineKeyboardButton("По самому популярному тегу", callback_data='tags'),
         InlineKeyboardButton("По локализации", callback_data='localization')],
        [InlineKeyboardButton("По издателю", callback_data='publisher'),
         InlineKeyboardButton("Случайная игра", callback_data='random_game')],
        [InlineKeyboardButton("Количество игр", callback_data='count_games'),
         InlineKeyboardButton("Добавить игру", callback_data='add_game')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора категории."""
    query = update.callback_query
    await query.answer()

    # Обрабатываем различные типы запросов
    if query.data == 'genre':
        await query.edit_message_text("Введите ID жанра для поиска игр:")
        context.user_data['filter'] = 'id_Genre'
    elif query.data == 'developer':
        await query.edit_message_text("Введите ID разработчика для поиска игр:")
        context.user_data['filter'] = 'id_Developer'
    elif query.data == 'publisher':
        await query.edit_message_text("Введите ID издателя для поиска игр:")
        context.user_data['filter'] = 'id_Publisher'
    elif query.data == 'tags':
        await query.edit_message_text("Введите ID популярного тега для поиска игр:")
        context.user_data['filter'] = 'id_Tags'    
    elif query.data == 'localization':
        await query.edit_message_text("Введите ID локализации для поиска игр:")
        context.user_data['filter'] = 'id_Localization'
    elif query.data == 'random_game':
        game = get_random_game()
        await query.edit_message_text(f"Случайная игра: {game}")
    elif query.data == 'count_games':
        count = count_games()
        await query.edit_message_text(f"Всего игр в базе: {count}")
    elif query.data == 'add_game':
        await query.edit_message_text(
            "Пожалуйста, укажите данные игры в формате:\n"
            "/add Название игры; Жанр; Разработчик; Издатель; Самый популярный тег; Локализация\n\n"
            "Пример:\n"
            "/add The Witcher 3; RPG; CD Projekt; CD Projekt RED; Открытый мир; Полная"
        )

async def filter_games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстового ввода для фильтрации."""
    # Получаем тип фильтра из контекста
    column_name = context.user_data.get('filter')
    
    if not column_name:
        await update.message.reply_text("Пожалуйста, выберите категорию с помощью команды /start.")
        return

    try:
        # Преобразуем ввод в число и ищем игры
        value = int(update.message.text)
        games = fetch_games_by_column(column_name, value)
        
        if games:
            result = "\n".join(games)
            await update.message.reply_text(f"Найденные игры:\n{result}")
        else:
            await update.message.reply_text("Игры по вашему запросу не найдены.")
            
    except ValueError:
        await update.message.reply_text("Введите корректный ID (число).")
    except Exception as e:
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")
        print(f"Ошибка обработки запроса: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help."""
    help_text = """
    Доступные команды:
    /start - начать работу с ботом
    /help - показать это сообщение
    /random - получить случайную игру
    /count - узнать количество игр в базе
    """
    await update.message.reply_text(help_text)

async def random_game_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /random."""
    game = get_random_game()
    await update.message.reply_text(f"Случайная игра: {game}")

async def count_games_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /count."""
    count = count_games()
    await update.message.reply_text(f"Всего игр в базе: {count}")

def main():
    """Основная функция запуска бота."""
    # Создаем приложение бота
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("random", random_game_command))
    application.add_handler(CommandHandler("count", count_games_command))
    application.add_handler(CallbackQueryHandler(handle_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_games))
    
    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
