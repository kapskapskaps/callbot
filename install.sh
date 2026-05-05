#!/bin/bash

# Скрипт для быстрого развертывания бота на Ubuntu 22.04

set -e

echo "🚀 Установка бота-нутрициолога"
echo "================================"

# Проверка ОС
if [ ! -f /etc/os-release ]; then
    echo "❌ Не удалось определить ОС"
    exit 1
fi

source /etc/os-release
if [[ "$ID" != "ubuntu" ]]; then
    echo "⚠️  Этот скрипт предназначен для Ubuntu. Ваша ОС: $ID"
    read -p "Продолжить? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Обновление системы
echo "📦 Обновление системы..."
sudo apt update && sudo apt upgrade -y

# Установка Docker
if ! command -v docker &> /dev/null; then
    echo "🐋 Установка Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker установлен"
else
    echo "✅ Docker уже установлен"
fi

# Установка Docker Compose
if ! docker compose version &> /dev/null; then
    echo "🐋 Установка Docker Compose..."
    sudo apt install docker-compose-plugin -y
    echo "✅ Docker Compose установлен"
else
    echo "✅ Docker Compose уже установлен"
fi

# Создание .env файла
if [ ! -f .env ]; then
    echo ""
    echo "⚙️  Настройка переменных окружения"
    echo "================================"

    read -p "Введите Telegram Bot Token: " telegram_token
    read -p "Введите Gemini API Key: " gemini_key
    read -p "Введите Admin IDs через запятую (опционально): " admin_ids

    cat > .env << EOF
TELEGRAM_BOT_TOKEN=$telegram_token
GEMINI_API_KEY=$gemini_key
ADMIN_IDS=$admin_ids
EOF

    echo "✅ Файл .env создан"
else
    echo "✅ Файл .env уже существует"
fi

# Создание директории для логов
mkdir -p logs

# Сборка и запуск
echo ""
echo "🔨 Сборка Docker образа..."
docker compose build

echo ""
echo "🚀 Запуск бота..."
docker compose up -d

echo ""
echo "✅ Бот успешно запущен!"
echo ""
echo "Полезные команды:"
echo "  docker compose logs -f          # Просмотр логов"
echo "  docker compose restart          # Перезапуск бота"
echo "  docker compose down             # Остановка бота"
echo "  docker compose ps               # Статус контейнера"
echo ""
echo "Логи также доступны в: ./logs/bot.log"
echo ""
echo "⚠️  ВАЖНО: Если вы только что установили Docker, выполните:"
echo "  newgrp docker"
echo "  или перезайдите в систему для применения прав группы docker"
