import requests
from config import HUGGINGFACE_API_TOKEN, STABLE_DIFFUSION_MODEL, STYLES

# API URL для Hugging Face Inference (новый endpoint)
API_URL = f"https://router.huggingface.co/hf-inference/models/{STABLE_DIFFUSION_MODEL}"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}


def generate_logo(prompt: str, style: str = None) -> bytes:
    """
    Генерирует логотип через Hugging Face Inference API.
    
    Args:
        prompt: Описание логотипа от пользователя
        style: Выбранный стиль (minimal, vintage, modern, geometric, hand_drawn)
    
    Returns:
        Байты изображения или None при ошибке
    """
    try:
        # Формируем промпт для генерации логотипа
        logo_prompt = build_logo_prompt(prompt, style)
        
        # Запускаем генерацию
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={"inputs": logo_prompt},
            timeout=120  # 2 минуты таймаут
        )
        
        # Проверяем ответ
        if response.status_code == 200:
            # Hugging Face возвращает байты изображения напрямую
            return response.content
        else:
            print(f"Hugging Face API error: {response.status_code} - {response.text}")
            return None
        
    except requests.exceptions.Timeout:
        print("Request timeout - model may be loading")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def build_logo_prompt(user_prompt: str, style: str = None) -> str:
    """
    Строит оптимизированный промпт для генерации логотипа.
    
    Args:
        user_prompt: Описание от пользователя
        style: Выбранный стиль
    
    Returns:
        Полный промпт для Stable Diffusion
    """
    # Базовые параметры для генерации логотипов
    base_params = "logo design, vector style, professional, high quality, centered composition, white background"
    
    # Добавляем стиль если выбран
    style_params = ""
    if style and style in STYLES:
        style_params = STYLES[style]
    
    # Собираем финальный промпт
    if style_params:
        full_prompt = f"{user_prompt}, {style_params}, {base_params}"
    else:
        full_prompt = f"{user_prompt}, {base_params}"
    
    return full_prompt


def get_available_styles() -> dict:
    """Возвращает словарь доступных стилей."""
    return STYLES
