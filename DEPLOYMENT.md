# Руководство по деплою на Ubuntu 22.04

## Вариант 1: Локальный сервер / VPS

### Предварительные требования

- Ubuntu 22.04 LTS
- Доступ по SSH (для VPS)
- Права sudo
- Минимум 512 MB RAM
- 1 GB свободного места

### Шаг 1: Подключение к серверу

```bash
# Для VPS
ssh user@your-server-ip

# Для локального сервера - пропустите этот шаг
```

### Шаг 2: Обновление системы

```bash
sudo apt update && sudo apt upgrade -y
```

### Шаг 3: Установка Git (если нужно)

```bash
sudo apt install git -y
```

### Шаг 4: Клонирование проекта

```bash
# Если у вас есть Git репозиторий
git clone https://github.com/your-username/callbot.git
cd callbot

# Или создайте директорию и скопируйте файлы
mkdir callbot
cd callbot
# Загрузите файлы через scp или другим способом
```

### Шаг 5: Запуск автоматической установки

```bash
chmod +x install.sh
./install.sh
```

Скрипт запросит:
1. **Telegram Bot Token** - получите у @BotFather
2. **Gemini API Key** - получите на https://makersuite.google.com/app/apikey
3. **Admin IDs** (опционально) - ваш Telegram ID

### Шаг 6: Проверка работы

```bash
# Проверка статуса
docker compose ps

# Просмотр логов
docker compose logs -f

# Если все ОК, вы увидите:
# "Бот запущен"
```

### Шаг 7: Тестирование

1. Откройте Telegram
2. Найдите вашего бота по username
3. Отправьте `/start`
4. Отправьте любое фото
5. Выберите тип анализа

## Вариант 2: Ручная установка

### Установка Docker

```bash
# Скачивание скрипта установки
curl -fsSL https://get.docker.com -o get-docker.sh

# Установка Docker
sudo sh get-docker.sh

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Применение изменений (или перезайдите)
newgrp docker

# Проверка
docker --version
```

### Установка Docker Compose

```bash
sudo apt install docker-compose-plugin -y

# Проверка
docker compose version
```

### Настройка проекта

```bash
# Создание .env файла
cp .env.example .env

# Редактирование
nano .env
```

Заполните:
```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
GEMINI_API_KEY=AIzaSyABC123def456GHI789jkl
ADMIN_IDS=123456789
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

### Запуск бота

```bash
# Сборка образа
docker compose build

# Запуск в фоновом режиме
docker compose up -d

# Просмотр логов
docker compose logs -f
```

## Вариант 3: Деплой через SCP

### На локальной машине

```bash
# Создание архива проекта
tar -czf callbot.tar.gz callbot/

# Копирование на сервер
scp callbot.tar.gz user@server-ip:/home/user/
```

### На сервере

```bash
# Распаковка
tar -xzf callbot.tar.gz
cd callbot

# Запуск установки
chmod +x install.sh
./install.sh
```

## Настройка автозапуска

Бот уже настроен на автозапуск через Docker (`restart: unless-stopped`).

### Проверка автозапуска

```bash
# Перезагрузка сервера
sudo reboot

# После перезагрузки (через SSH)
docker compose ps

# Бот должен быть в статусе "Up"
```

### Отключение автозапуска

```bash
# Изменить в docker-compose.yml
restart: "no"

# Или остановить контейнер
docker compose down
```

## Управление ботом

### Основные команды

```bash
# Запуск
docker compose up -d

# Остановка
docker compose down

# Перезапуск
docker compose restart

# Статус
docker compose ps

# Логи (последние)
docker compose logs --tail=100

# Логи (в реальном времени)
docker compose logs -f

# Использование ресурсов
docker stats nutritionist_bot
```

### Обновление бота

```bash
# Остановка
docker compose down

# Обновление кода
git pull  # или замените файлы вручную

# Пересборка и запуск
docker compose up -d --build

# Проверка
docker compose logs -f
```

### Очистка логов

```bash
# Очистка файла логов
rm logs/bot.log

# Перезапуск для создания нового файла
docker compose restart
```

### Полная очистка

```bash
# Остановка и удаление контейнера
docker compose down

# Удаление образа
docker rmi callbot-nutritionist-bot

# Удаление неиспользуемых образов
docker system prune -a
```

## Мониторинг

### Просмотр логов

```bash
# Все логи
docker compose logs

# Последние 50 строк
docker compose logs --tail=50

# С временными метками
docker compose logs -t

# Файл логов
tail -f logs/bot.log
```

### Проверка здоровья

```bash
# Статус контейнера
docker compose ps

# Детальная информация
docker inspect nutritionist_bot

# Использование ресурсов
docker stats nutritionist_bot --no-stream
```

### Настройка алертов (опционально)

```bash
# Создание скрипта проверки
cat > check_bot.sh << 'EOF'
#!/bin/bash
if ! docker compose ps | grep -q "Up"; then
    echo "Бот не работает!" | mail -s "Bot Alert" your@email.com
    docker compose restart
fi
EOF

chmod +x check_bot.sh

# Добавление в cron (проверка каждые 5 минут)
crontab -e
# Добавьте строку:
# */5 * * * * cd /path/to/callbot && ./check_bot.sh
```

## Безопасность

### Настройка файрвола (UFW)

```bash
# Установка UFW
sudo apt install ufw -y

# Разрешить SSH
sudo ufw allow ssh

# Включить файрвол
sudo ufw enable

# Проверка статуса
sudo ufw status
```

### Защита .env файла

```bash
# Установка прав доступа
chmod 600 .env

# Проверка
ls -la .env
# Должно быть: -rw------- (только владелец может читать/писать)
```

### Регулярные обновления

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Обновление Docker образов
docker compose pull
docker compose up -d --build
```

## Резервное копирование

### Создание бэкапа

```bash
# Бэкап .env
cp .env .env.backup.$(date +%Y%m%d)

# Бэкап логов
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/

# Полный бэкап проекта
cd ..
tar -czf callbot_backup_$(date +%Y%m%d).tar.gz callbot/
```

### Автоматический бэкап

```bash
# Создание скрипта
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/user/backups"
DATE=$(date +%Y%m%d)
mkdir -p $BACKUP_DIR
cd /home/user/callbot
tar -czf $BACKUP_DIR/callbot_$DATE.tar.gz .
# Удаление старых бэкапов (старше 7 дней)
find $BACKUP_DIR -name "callbot_*.tar.gz" -mtime +7 -delete
EOF

chmod +x backup.sh

# Добавление в cron (ежедневно в 3:00)
crontab -e
# Добавьте:
# 0 3 * * * /home/user/callbot/backup.sh
```

### Восстановление из бэкапа

```bash
# Остановка бота
docker compose down

# Восстановление
cd /home/user
tar -xzf callbot_backup_20260505.tar.gz

# Запуск
cd callbot
docker compose up -d
```

## Решение проблем

### Бот не запускается

```bash
# Проверка логов
docker compose logs

# Проверка .env файла
cat .env

# Проверка прав
ls -la .env

# Пересоздание контейнера
docker compose down
docker compose up -d --force-recreate
```

### Ошибки Docker

```bash
# Проверка статуса Docker
sudo systemctl status docker

# Перезапуск Docker
sudo systemctl restart docker

# Проверка места на диске
df -h

# Очистка неиспользуемых ресурсов
docker system prune -a
```

### Проблемы с сетью

```bash
# Проверка подключения к интернету
ping -c 3 google.com

# Проверка DNS
nslookup api.telegram.org

# Перезапуск сети
sudo systemctl restart networking
```

## Производительность

### Оптимизация для слабых серверов

В `docker-compose.yml` добавьте ограничения:

```yaml
services:
  nutritionist-bot:
    # ... существующие настройки
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          memory: 128M
```

### Мониторинг ресурсов

```bash
# Использование памяти
free -h

# Использование CPU
top

# Использование диска
df -h

# Docker статистика
docker stats nutritionist_bot
```

## Масштабирование

### Запуск нескольких ботов

```bash
# Копирование проекта
cp -r callbot callbot2

# Изменение имени контейнера в docker-compose.yml
cd callbot2
nano docker-compose.yml
# Измените: container_name: nutritionist_bot_2

# Создание отдельного .env с другим токеном
nano .env

# Запуск
docker compose up -d
```

### Использование Docker Swarm (для продакшена)

```bash
# Инициализация Swarm
docker swarm init

# Деплой стека
docker stack deploy -c docker-compose.yml nutritionist

# Масштабирование
docker service scale nutritionist_nutritionist-bot=3
```

## Полезные ссылки

- Docker документация: https://docs.docker.com/
- Telegram Bot API: https://core.telegram.org/bots/api
- Google Gemini API: https://ai.google.dev/docs
- Ubuntu Server Guide: https://ubuntu.com/server/docs

---

**Готово!** Ваш бот-нутрициолог запущен и работает 24/7.

Для поддержки создайте Issue в репозитории проекта.
