import google.generativeai as genai
from typing import Optional
import logging
import io
from PIL import Image

logger = logging.getLogger(__name__)


class NutritionistAnalyzer:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # Актуальная модель Gemini 2.5 Flash с поддержкой изображений
        # Используем без префикса models/
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def compress_image(self, image_data: bytes, max_size: int = 800, quality: int = 75) -> bytes:
        """Сжимает изображение до указанного размера"""
        try:
            img = Image.open(io.BytesIO(image_data))

            # Конвертируем в RGB если нужно (для JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')

            # Вычисляем новые размеры
            width, height = img.size
            if width > height:
                if width > max_size:
                    new_width = max_size
                    new_height = int(height * (max_size / width))
                else:
                    new_width, new_height = width, height
            else:
                if height > max_size:
                    new_height = max_size
                    new_width = int(width * (max_size / height))
                else:
                    new_width, new_height = width, height

            # Изменяем размер
            if new_width != width or new_height != height:
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Сохраняем в байтовый поток
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            return output.getvalue()
        except Exception as e:
            logger.error(f"Ошибка сжатия изображения: {e}")
            return image_data

    async def analyze_photo_stateless(self, image_data: bytes) -> str:
        """Stateless анализ фото еды без контекста"""
        try:
            # Сжимаем изображение
            compressed_image = self.compress_image(image_data)

            prompt = """Ты дружелюбный нутрициолог с чувством юмора.

ВАЖНО: Начни ответ с дружеской шутки или прикола про это блюдо (1-2 предложения), как будто общаешься с другом.

Затем с новой строки напиши "<b>А если серьезно:</b>" и дай краткий анализ:
• Название блюда
• Примерные КБЖУ (калории, белки, жиры, углеводы)

ОГРАНИЧЕНИЕ: Весь ответ должен быть не более 400 символов. Будь краток и конкретен."""

            response = self.model.generate_content([prompt, {"mime_type": "image/jpeg", "data": compressed_image}])
            return response.text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                return "⏳ <b>Превышен дневной лимит запросов к AI</b>\n\nК сожалению, сегодня исчерпан лимит бесплатных запросов к нейросети. Попробуйте снова завтра или немного позже.\n\n💡 Это ограничение API, а не бота."
            logger.error(f"Ошибка анализа фото: {e}")
            return f"Ошибка при анализе изображения: {str(e)}"

    async def analyze_calories(self, image_data: bytes) -> str:
        """Анализ калорийности блюда по фото"""
        try:
            # Сжимаем изображение
            compressed_image = self.compress_image(image_data)

            prompt = """Ты дружелюбный нутрициолог с чувством юмора.

ВАЖНО: Начни ответ с дружеской шутки или прикола про это блюдо (1-2 предложения), как будто общаешься с другом. Используй разговорный стиль, можешь пошутить про калорийность, внешний вид или состав.

Затем с новой строки напиши "<b>А если серьезно, как нутрициолог:</b>" и дай профессиональный анализ:

<b>Название блюда/продукта</b>
• Примерный вес порции: X г
• Калорийность: X ккал
• Белки: X г
• Жиры: X г
• Углеводы: X г

<b>Рекомендации:</b>
Краткие рекомендации по питанию (2-3 предложения)

ОГРАНИЧЕНИЕ: Весь ответ должен быть не более 800 символов. Будь лаконичным и конкретным.

Если на фото нет еды, пошути об этом и вежливо попроси прислать фото еды."""

            response = self.model.generate_content([prompt, {"mime_type": "image/jpeg", "data": compressed_image}])
            return response.text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                return "⏳ <b>Превышен дневной лимит запросов к AI</b>\n\nК сожалению, сегодня исчерпан лимит бесплатных запросов к нейросети. Попробуйте снова завтра или немного позже.\n\n💡 Это ограничение API, а не бота."
            logger.error(f"Ошибка анализа калорий: {e}")
            return f"Ошибка при анализе изображения: {str(e)}"

    async def analyze_composition(self, image_data: bytes) -> str:
        """Анализ состава продукта по фото этикетки"""
        try:
            # Сжимаем изображение
            compressed_image = self.compress_image(image_data)

            prompt = """Ты дружелюбный нутрициолог с чувством юмора.

ВАЖНО: Начни ответ с дружеской шутки или прикола про этот продукт (1-2 предложения), как будто общаешься с другом. Можешь пошутить про состав, количество E-шек или маркетинговые уловки производителя.

Затем с новой строки напиши "<b>А если серьезно, как нутрициолог:</b>" и дай профессиональный анализ:

<b>Название продукта</b>

<b>Основные ингредиенты:</b>
Перечисли топ-5 ингредиентов

<b>Пищевая ценность на 100г:</b>
• Калории: X ккал
• Белки: X г | Жиры: X г | Углеводы: X г

<b>Вредные добавки:</b>
Перечисли основные E-добавки (если есть)

<b>Оценка:</b> X/10

<b>Рекомендации:</b>
Кратко: кому подходит, кому избегать (2-3 предложения)

ОГРАНИЧЕНИЕ: Весь ответ должен быть не более 1000 символов. Будь лаконичным.

Если на фото нет этикетки, пошути об этом и попроси прислать фото этикетки."""

            response = self.model.generate_content([prompt, {"mime_type": "image/jpeg", "data": compressed_image}])
            return response.text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                return "⏳ <b>Превышен дневной лимит запросов к AI</b>\n\nК сожалению, сегодня исчерпан лимит бесплатных запросов к нейросети. Попробуйте снова завтра или немного позже.\n\n💡 Это ограничение API, а не бота."
            logger.error(f"Ошибка анализа состава: {e}")
            return f"Ошибка при анализе состава: {str(e)}"

    async def analyze_food(self, image_data: bytes) -> str:
        """Общий анализ еды по фото"""
        try:
            # Сжимаем изображение
            compressed_image = self.compress_image(image_data)

            prompt = """Ты дружелюбный нутрициолог с чувством юмора.

ВАЖНО: Начни ответ с дружеской шутки или прикола про это блюдо (1-2 предложения), как будто общаешься с другом. Можешь пошутить про внешний вид, сочетание продуктов или размер порции.

Затем с новой строки напиши "<b>А если серьезно, как нутрициолог:</b>" и дай профессиональный анализ:

<b>Что на фото:</b>
Краткое описание блюда

<b>Оценка сбалансированности:</b>
Плюсы и минусы (по 2-3 пункта)

<b>Рекомендации:</b>
• Что добавить/убрать
• Для какого приёма пищи подходит
• Кому рекомендуется/избегать

ОГРАНИЧЕНИЕ: Весь ответ должен быть не более 900 символов. Будь конкретным и практичным."""

            response = self.model.generate_content([prompt, {"mime_type": "image/jpeg", "data": compressed_image}])
            return response.text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                return "⏳ <b>Превышен дневной лимит запросов к AI</b>\n\nК сожалению, сегодня исчерпан лимит бесплатных запросов к нейросети. Попробуйте снова завтра или немного позже.\n\n💡 Это ограничение API, а не бота."
            logger.error(f"Ошибка анализа еды: {e}")
            return f"Ошибка при анализе еды: {str(e)}"

    async def analyze_medical_tests(self, image_data: bytes) -> str:
        """Анализ медицинских анализов"""
        try:
            # Сжимаем изображение
            compressed_image = self.compress_image(image_data)

            prompt = """Ты дружелюбный нутрициолог с медицинским образованием и чувством юмора.

ВАЖНО: Начни ответ с дружеской шутки или поддерживающего комментария про анализы (1-2 предложения), как будто общаешься с другом. Можешь пошутить про цифры, медицинские термины или сам процесс сдачи анализов.

Затем с новой строки напиши "<b>А если серьезно, как нутрициолог:</b>" и дай профессиональный анализ:

<b>Тип анализа:</b>
Название анализа

<b>Ключевые показатели:</b>
• Показатель 1: значение (норма/выше/ниже)
• Показатель 2: значение (норма/выше/ниже)
• Показатель 3: значение (норма/выше/ниже)

<b>Что это значит:</b>
Краткое объяснение отклонений (2-3 предложения)

<b>Рекомендации по питанию:</b>
• Включить: список продуктов
• Ограничить: список продуктов
• Режим: краткие советы

⚠️ <b>Это не диагноз!</b> При серьёзных отклонениях обратитесь к врачу.

ОГРАНИЧЕНИЕ: Весь ответ должен быть не более 1100 символов."""

            response = self.model.generate_content([prompt, {"mime_type": "image/jpeg", "data": compressed_image}])
            return response.text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                return "⏳ <b>Превышен дневной лимит запросов к AI</b>\n\nК сожалению, сегодня исчерпан лимит бесплатных запросов к нейросети. Попробуйте снова завтра или немного позже.\n\n💡 Это ограничение API, а не бота."
            logger.error(f"Ошибка анализа медицинских данных: {e}")
            return f"Ошибка при анализе анализов: {str(e)}"

    async def analyze_stool(self, image_data: bytes) -> str:
        """Анализ фекалий (копрограмма)"""
        try:
            # Сжимаем изображение
            compressed_image = self.compress_image(image_data)

            prompt = """Ты дружелюбный гастроэнтеролог и нутрициолог с отличным чувством юмора.

ВАЖНО: Начни ответ с дружеской шутки про то, что ты видишь (1-2 предложения), как будто общаешься с другом. Можешь пошутить в стиле "вот это ты навалил конечно", "как вообще из тебя это вылезло" или про консистенцию/цвет. Будь смешным, но не переходи грань приличия.

Затем с новой строки напиши "<b>А если серьезно, как нутрициолог:</b>" и дай профессиональный анализ:

<b>Бристольская шкала:</b> Тип X/7

<b>Характеристики:</b>
• Цвет: описание
• Консистенция: описание
• Форма: описание

<b>Возможные причины:</b>
Краткое объяснение (2-3 предложения)

<b>Рекомендации по питанию:</b>
• Добавить: список продуктов
• Исключить: список продуктов
• Режим: питьевой режим и советы

⚠️ <b>Важно:</b>
• Это предварительная оценка, не заменяет лабораторную копрограмму
• При крови, черном цвете, сильной боли - срочно к врачу!

ОГРАНИЧЕНИЕ: Весь ответ должен быть не более 1000 символов.

Если на фото не фекалии, пошути об этом и вежливо попроси прислать правильное фото."""

            response = self.model.generate_content([prompt, {"mime_type": "image/jpeg", "data": compressed_image}])
            return response.text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                return "⏳ <b>Превышен дневной лимит запросов к AI</b>\n\nК сожалению, сегодня исчерпан лимит бесплатных запросов к нейросети. Попробуйте снова завтра или немного позже.\n\n💡 Это ограничение API, а не бота."
            logger.error(f"Ошибка анализа фекалий: {e}")
            return f"Ошибка при анализе: {str(e)}"

    async def ask_consultation(self, question: str, context_messages: list) -> str:
        """Профессиональная консультация с ограниченным контекстом (только последние 3 сообщения)"""
        try:
            # Берем только последние 3 сообщения из контекста
            limited_context = context_messages[-3:] if len(context_messages) > 3 else context_messages

            # Формируем историю для контекста
            history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in limited_context])

            prompt = f"""Ты - серьезный эксперт-нутрициолог. Отвечай сухо, профессионально, без юмора и лишних приветствий. Максимальный объем ответа - 500 символов.

Контекст последних сообщений:
{history_text}

Вопрос пользователя: {question}

Дай краткий профессиональный ответ."""

            response = self.model.generate_content(prompt)
            return response.text[:500]  # Жесткое ограничение на 500 символов
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                return "⏳ Превышен дневной лимит запросов к AI. Попробуйте позже."
            logger.error(f"Ошибка консультации: {e}")
            return f"Ошибка: {str(e)}"
