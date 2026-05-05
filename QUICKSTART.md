# Быстрый старт для Ubuntu 22.04

## Автоматическая установка (рекомендуется)

```bash
# 1. Скачайте проект
git clone <your-repo-url>
cd callbot

# 2. Запустите скрипт установки
chmod +x install.sh
./install.sh
```

Скрипт автоматически:
- Установит Docker и Docker Compose
- Запросит ваши API ключи
- Создаст .env файл
- Соберет и запустит бота

## Ручная установка

### Шаг 1: Установка Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

### Шаг 2: Установка Docker Compose

```bash
sudo apt install docker-compose-plugin -y
```

### Шаг 3: Настройка бота

```bash
# Создайте .env файл
cp .env.example .env
nano .env
```

Заполните:
```env
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
GEMINI_API_KEY=ваш_ключ_от_Google
ADMIN_IDS=ваш_telegram_id
```

### Шаг 4: Запуск

```bash
docker compose up -d
```

## Проверка работы

```bash
# Статус
docker compose ps

# Логи
docker compose logs -f
```

## Получение API ключей

### Telegram Bot Token
1. Найдите @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен

### Gemini API Key
1. Откройте https://makersuite.google.com/app/apikey
2. Войдите с Google аккаунтом
3. Нажмите "Create API key"
4. Скопируйте ключ

## Готово!

Найдите вашего бота в Telegram и отправьте `/start`
