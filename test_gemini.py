import google.generativeai as genai
import os

# Используйте ваш API ключ
api_key = os.getenv('GEMINI_API_KEY', 'YOUR_KEY_HERE')
genai.configure(api_key=api_key)

print("Доступные модели Gemini:")
print("=" * 50)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
        print(f"   Описание: {model.display_name}")
        print()

print("\nПопробуем разные варианты:")
print("=" * 50)

models_to_try = [
    'gemini-2.5-flash',
    'models/gemini-2.5-flash'
]

for model_name in models_to_try:
    try:
        model = genai.GenerativeModel(model_name)
        print(f"✅ {model_name} - РАБОТАЕТ")
    except Exception as e:
        print(f"❌ {model_name} - ОШИБКА: {str(e)[:80]}")
