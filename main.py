import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from config import TELEGRAM_TOKEN, MESSAGES
from generator import generate_logo

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Хранилище выбранных стилей пользователей
user_styles = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    await update.message.reply_text(
        MESSAGES["start"],
        parse_mode="Markdown"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    await update.message.reply_text(
        MESSAGES["help"],
        parse_mode="Markdown"
    )


async def style_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /style - показывает меню стилей"""
    await update.message.reply_text(
        MESSAGES["style_menu"],
        parse_mode="Markdown"
    )


async def set_style(update: Update, context: ContextTypes.DEFAULT_TYPE, style: str, style_name: str) -> None:
    """Устанавливает выбранный стиль для пользователя"""
    user_id = update.effective_user.id
    user_styles[user_id] = style
    await update.message.reply_text(
        MESSAGES["style_selected"].format(style=style_name),
        parse_mode="Markdown"
    )


async def minimal_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_style(update, context, "minimal", "Минималистичный")

async def vintage_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_style(update, context, "vintage", "Винтажный")

async def modern_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_style(update, context, "modern", "Современный")

async def geometric_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_style(update, context, "geometric", "Геометрический")

async def hand_drawn_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_style(update, context, "hand_drawn", "Рисованный")


async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений - генерация логотипа"""
    user_id = update.effective_user.id
    user_prompt = update.message.text
    
    # Получаем выбранный стиль пользователя (если есть)
    style = user_styles.get(user_id)
    
    # Отправляем сообщение о начале генерации
    status_message = await update.message.reply_text(MESSAGES["generating"])
    
    try:
        # Генерируем логотип
        logger.info(f"Generating logo for user {user_id}: {user_prompt[:50]}...")
        image_bytes = generate_logo(user_prompt, style)
        
        if image_bytes:
            # Отправляем изображение (байты)
            await update.message.reply_photo(
                photo=image_bytes,
                caption=f"🎨 Логотип по запросу: _{user_prompt}_",
                parse_mode="Markdown"
            )
            # Удаляем сообщение о генерации
            await status_message.delete()
            logger.info(f"Logo generated successfully for user {user_id}")
        else:
            # Ошибка генерации
            await status_message.edit_text(MESSAGES["error"])
            logger.error(f"Failed to generate logo for user {user_id}")
            
    except Exception as e:
        logger.error(f"Error generating logo: {e}")
        await status_message.edit_text(MESSAGES["error"])


def main() -> None:
    """Запуск бота"""
    # Создаём приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("style", style_menu))
    
    # Обработчики выбора стиля
    application.add_handler(CommandHandler("minimal", minimal_style))
    application.add_handler(CommandHandler("vintage", vintage_style))
    application.add_handler(CommandHandler("modern", modern_style))
    application.add_handler(CommandHandler("geometric", geometric_style))
    application.add_handler(CommandHandler("hand_drawn", hand_drawn_style))
    
    # Обработчик текстовых сообщений (генерация логотипа)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, generate))
    
    # Запускаем бота
    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
