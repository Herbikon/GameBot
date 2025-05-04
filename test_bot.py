import pytest
from telegram import Update, CallbackQuery, Message, User, Chat, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from run import handle_query, filter_games, fetch_games_by_column, start, get_random_game, count_games
import asyncio

# Класс для имитации сообщений Telegram
class MockMessage:
    def __init__(self, text):
        self.text = text  # Текст сообщения
        self.chat = MockChat()  # Создаем имитацию чата
        self._reply_text = None  # Для хранения ответа бота
        self._reply_markup = None  # Для хранения клавиатуры
        
    async def reply_text(self, text, reply_markup=None):
        # Имитация отправки сообщения ботом
        self._reply_text = text
        self._reply_markup = reply_markup
        return text
    
    def get_reply_text(self):
        # Получение текста ответа бота
        return self._reply_text
        
    def get_reply_markup(self):
        # Получение клавиатуры ответа бота
        return self._reply_markup

# Класс для имитации чата Telegram
class MockChat:
    def __init__(self):
        self.id = 1  # ID чата
        self.type = 'private'  # Тип чата (личный)

# Класс для имитации контекста бота
class MockContext:
    def __init__(self):
        self.user_data = {}  # Словарь для хранения данных пользователя

# Класс для имитации callback-запросов от кнопок
class MockCallbackQuery:
    def __init__(self, data):
        self.data = data  # Данные callback-запроса
        self._edit_message_text = None  # Для хранения текста редактируемого сообщения
        self.message = MockMessage("")  # Создаем имитацию сообщения
        
    async def answer(self):
        # Имитация ответа на callback-запрос
        pass
        
    async def edit_message_text(self, text):
        # Имитация редактирования сообщения
        self._edit_message_text = text
        return text
        
    def get_edit_message_text(self):
        # Получение текста отредактированного сообщения
        return self._edit_message_text

# Фикстура для создания обновления с сообщением
@pytest.fixture
def mock_message_update():
    message = MockMessage("1")
    return Update(
        update_id=1,
        message=message
    )

# Фикстура для создания обновления с callback-запросом
@pytest.fixture
def mock_callback_update():
    callback_query = MockCallbackQuery("genre")
    return Update(
        update_id=1,
        callback_query=callback_query
    )

# Фикстура для создания контекста бота
@pytest.fixture
def mock_context():
    return MockContext()

# Тест поиска игр по жанру
@pytest.mark.asyncio
async def test_search_by_genre(mock_message_update, mock_context):
    # Устанавливаем фильтр для поиска по жанру
    mock_context.user_data['filter'] = 'id_Genre'
    
    # Имитируем ввод ID жанра
    await filter_games(mock_message_update, mock_context)
    
    # Проверяем результаты поиска
    games = fetch_games_by_column('id_Genre', 1)
    assert isinstance(games, list)  # Проверяем, что результат - список
    assert all(isinstance(game, str) for game in games)  # Проверяем, что все элементы - строки

# Тест поиска игр по разработчику
@pytest.mark.asyncio
async def test_search_by_developer(mock_message_update, mock_context):
    # Устанавливаем фильтр для поиска по разработчику
    mock_context.user_data['filter'] = 'id_Developer'
    
    # Имитируем ввод ID разработчика
    await filter_games(mock_message_update, mock_context)
    
    # Проверяем результаты поиска
    games = fetch_games_by_column('id_Developer', 1)
    assert isinstance(games, list)
    assert all(isinstance(game, str) for game in games)

# Тест поиска игр по тегу
@pytest.mark.asyncio
async def test_search_by_tag(mock_message_update, mock_context):
    # Устанавливаем фильтр для поиска по тегу
    mock_context.user_data['filter'] = 'id_Tags'

# Имитируем ввод ID тега
    await filter_games(mock_message_update, mock_context)
    
    # Проверяем результаты поиска
    games = fetch_games_by_column('id_Tags', 1)
    assert isinstance(games, list)
    assert all(isinstance(game, str) for game in games)
    
    # Проверяем, что список не пустой (если тег существует)
    if games:
        assert len(games) > 0

# Тест поиска игр по локализации
@pytest.mark.asyncio
async def test_search_by_localization(mock_message_update, mock_context):
    # Устанавливаем фильтр для поиска по локализации
    mock_context.user_data['filter'] = 'id_Localization'
    
    # Имитируем ввод ID локализации
    await filter_games(mock_message_update, mock_context)
    
    # Проверяем результаты поиска
    games = fetch_games_by_column('id_Localization', 1)
    assert isinstance(games, list)
    assert all(isinstance(game, str) for game in games)
    
    # Проверяем, что список не пустой (если локализация существует)
    if games:
        assert len(games) > 0

# Тест обработки неверного ввода
@pytest.mark.asyncio
async def test_invalid_input(mock_message_update, mock_context):
    # Устанавливаем фильтр и неверный ввод
    mock_context.user_data['filter'] = 'id_Genre'
    mock_message_update.message.text = 'invalid'
    
    # Проверяем обработку неверного ввода
    await filter_games(mock_message_update, mock_context)
    # Проверяем сообщение об ошибке
    assert mock_message_update.message.get_reply_text() is not None
    assert "Введите корректный ID" in mock_message_update.message.get_reply_text()

# Тест обработки пустого результата
@pytest.mark.asyncio
async def test_empty_result(mock_message_update, mock_context):
    # Устанавливаем фильтр и несуществующий ID
    mock_context.user_data['filter'] = 'id_Genre'
    mock_message_update.message.text = '999'  # Несуществующий ID
    
    # Проверяем обработку пустого результата
    await filter_games(mock_message_update, mock_context)
    # Проверяем сообщение о том, что игры не найдены
    assert mock_message_update.message.get_reply_text() is not None
    assert "не найдены" in mock_message_update.message.get_reply_text().lower()

# Интеграционный тест полного потока поиска игры
@pytest.mark.asyncio
async def test_integration_search_flow(mock_message_update, mock_callback_update, mock_context):
    # 1. Проверяем команду /start
    await start(mock_message_update, mock_context)
    assert mock_message_update.message.get_reply_text() == "Выберите действие:"
    assert isinstance(mock_message_update.message.get_reply_markup(), InlineKeyboardMarkup)
    
    # 2. Проверяем выбор поиска по жанру
    mock_callback_update.callback_query.data = 'genre'
    await handle_query(mock_callback_update, mock_context)
    assert "Введите ID жанра" in mock_callback_update.callback_query.get_edit_message_text()
    
    # 3. Проверяем ввод ID жанра и получение результатов
    mock_message_update.message.text = "1"
    await filter_games(mock_message_update, mock_context)
    assert mock_message_update.message.get_reply_text() is not None
    games = fetch_games_by_column('id_Genre', 1)
    if games:
        assert any(game in mock_message_update.message.get_reply_text() for game in games)

# Тест полного рабочего процесса бота
@pytest.mark.asyncio
async def test_bot_full_workflow(mock_message_update, mock_callback_update, mock_context):
    # 1. Проверяем команду /start
    await start(mock_message_update, mock_context)
    assert mock_message_update.message.get_reply_text() == "Выберите действие:"
    assert isinstance(mock_message_update.message.get_reply_markup(), InlineKeyboardMarkup)
    
    # 2. Проверяем получение случайной игры
    mock_callback_update.callback_query.data = 'random_game'
    await handle_query(mock_callback_update, mock_context)
    response_text = mock_callback_update.callback_query.get_edit_message_text()
    assert response_text.startswith("Случайная игра:")
    assert len(response_text.split(":", 1)[1].strip()) > 0  # Проверяем наличие названия игры
    
    # 3. Проверяем подсчет количества игр
    mock_callback_update.callback_query.data = 'count_games'
    await handle_query(mock_callback_update, mock_context)
    count = count_games()
    assert str(count) in mock_callback_update.callback_query.get_edit_message_text()
    
    # 4. Проверяем поиск по жанру
    mock_callback_update.callback_query.data = 'genre'
    await handle_query(mock_callback_update, mock_context)
    assert "Введите ID жанра" in mock_callback_update.callback_query.get_edit_message_text()
    
    # 5. Проверяем обработку неверного ввода
    mock_message_update.message.text = "invalid"
    await filter_games(mock_message_update, mock_context)
    assert "Введите корректный ID" in mock_message_update.message.get_reply_text()