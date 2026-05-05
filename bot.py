import logging
import os
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from analyzers import NutritionistAnalyzer
from config import TELEGRAM_BOT_TOKEN, GEMINI_API_KEY

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

analyzer = NutritionistAnalyzer(GEMINI_API_KEY)

ANALYSIS_TYPES = {
    'calories': 'Оценить калорийность',
    'composition': 'Анализ состава',
    'food': 'Оценить блюдо',
    'medical': 'Анализ медицинских данных',
    'stool': 'Анализ фекалий'
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = """👋 Привет! Я бот-нутрициолог.

Я помогу вам:
🍽 Оценить калорийность блюда по фото
📋 Проанализировать состав продукта
🥗 Дать рекомендации по питанию
🩺 Изучить медицинские анализы
💩 Проанализировать фекалии (копрограмма)

Просто отправьте мне фото, и я предложу варианты анализа!

Команды:
/start - Показать это сообщение
/help - Подробная справка
"""
    await update.message.reply_text(welcome_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """📖 Подробная справка

🍽 **Оценка калорийности**
Отправьте фото блюда, и я рассчитаю:
- Калории
- Белки, жиры, углеводы
- Примерный вес порции

📋 **Анализ состава продукта**
Сфотографируйте этикетку с составом, и я:
- Расшифрую ингредиенты
- Найду вредные добавки
- Оценю полезность продукта

🥗 **Оценка блюда**
Покажите фото еды, и я дам:
- Оценку сбалансированности
- Рекомендации по улучшению
- Советы, кому подходит

🩺 **Анализ медицинских данных**
Отправьте фото анализов крови, и я:
- Укажу отклонения от нормы
- Дам рекомендации по питанию
- Подскажу, что включить в рацион

💩 **Анализ фекалий (копрограмма)**
Отправьте фото стула, и я:
- Оценю по Бристольской шкале
- Определю возможные проблемы с пищеварением
- Дам рекомендации по питанию и режиму

⚠️ **Важно**: Мои рекомендации не заменяют консультацию врача!

Просто отправьте фото, и выберите тип анализа из меню."""
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик фотографий"""
    keyboard = [
        [
            InlineKeyboardButton("🍽 Калории", callback_data='calories'),
            InlineKeyboardButton("📋 Состав", callback_data='composition'),
        ],
        [
            InlineKeyboardButton("🥗 Оценить блюдо", callback_data='food'),
            InlineKeyboardButton("🩺 Анализы", callback_data='medical'),
        ],
        [
            InlineKeyboardButton("💩 Анализ стула", callback_data='stool'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    photo = update.message.photo[-1]
    context.user_data['photo_file_id'] = photo.file_id

    await update.message.reply_text(
        "Что вы хотите узнать об этом изображении?",
        reply_markup=reply_markup
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()

    analysis_type = query.data
    photo_file_id = context.user_data.get('photo_file_id')

    if not photo_file_id:
        await query.edit_message_text("Ошибка: фото не найдено. Отправьте фото заново.")
        return

    await query.edit_message_text(f"⏳ Анализирую изображение ({ANALYSIS_TYPES[analysis_type]})...\nЭто может занять несколько секунд.")

    try:
        file = await context.bot.get_file(photo_file_id)
        photo_bytes = await file.download_as_bytearray()

        if analysis_type == 'calories':
            result = await analyzer.analyze_calories(bytes(photo_bytes))
        elif analysis_type == 'composition':
            result = await analyzer.analyze_composition(bytes(photo_bytes))
        elif analysis_type == 'food':
            result = await analyzer.analyze_food(bytes(photo_bytes))
        elif analysis_type == 'medical':
            result = await analyzer.analyze_medical_tests(bytes(photo_bytes))
        elif analysis_type == 'stool':
            result = await analyzer.analyze_stool(bytes(photo_bytes))
        else:
            result = "Неизвестный тип анализа"

        if len(result) > 4096:
            for i in range(0, len(result), 4096):
                await query.message.reply_text(result[i:i+4096], parse_mode='HTML')
        else:
            await query.message.reply_text(result, parse_mode='HTML')

        logger.info(f"Пользователь {query.from_user.id} выполнил анализ: {analysis_type}")

    except Exception as e:
        logger.error(f"Ошибка при обработке фото: {e}")
        await query.message.reply_text(f"Произошла ошибка при анализе: {str(e)}")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    await update.message.reply_text(
        "Пожалуйста, отправьте мне фото для анализа.\n\n"
        "Используйте /help для получения подробной информации."
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Ошибка: {context.error}", exc_info=context.error)

    if update and update.effective_message:
        await update.effective_message.reply_text(
            "Произошла ошибка при обработке вашего запроса. Попробуйте позже."
        )


def main():
    """Запуск бота"""
    os.makedirs('logs', exist_ok=True)

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.add_error_handler(error_handler)

    logger.info("Бот запущен")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
