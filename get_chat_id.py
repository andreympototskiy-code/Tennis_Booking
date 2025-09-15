#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для получения Chat ID через Telegram Bot API
"""

import requests
import json
import time

def get_chat_id():
    """
    Получает последние сообщения от бота и извлекает Chat ID
    """
    
    bot_token = "8381840391:AAHuxT53GUYKeT_RitxfhAaD-r-YX3zy1v4"
    api_url = f"https://api.telegram.org/bot{bot_token}"
    
    print("🤖 Получение Chat ID для вашего Telegram бота")
    print("=" * 50)
    print("📋 Инструкции:")
    print("1. Найдите вашего бота в Telegram")
    print("2. Отправьте боту любое сообщение (например: /start)")
    print("3. Нажмите Enter здесь для проверки сообщений")
    print("=" * 50)
    
    input("Нажмите Enter после отправки сообщения боту...")
    
    try:
        # Получаем обновления (последние сообщения)
        url = f"{api_url}/getUpdates"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('ok') and data.get('result'):
            updates = data['result']
            
            if not updates:
                print("❌ Сообщения не найдены")
                print("💡 Убедитесь, что вы отправили сообщение боту")
                return None
            
            # Берем последнее сообщение
            last_update = updates[-1]
            message = last_update.get('message', {})
            chat = message.get('chat', {})
            
            chat_id = chat.get('id')
            chat_type = chat.get('type')
            first_name = chat.get('first_name', '')
            username = chat.get('username', '')
            
            print(f"✅ Chat ID найден!")
            print(f"🆔 Chat ID: {chat_id}")
            print(f"👤 Имя: {first_name}")
            if username:
                print(f"📱 Username: @{username}")
            print(f"💬 Тип чата: {chat_type}")
            
            # Обновляем конфигурацию
            config = {
                "bot_token": bot_token,
                "chat_id": str(chat_id)
            }
            
            with open('telegram_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ Конфигурация сохранена в telegram_config.json")
            print(f"🚀 Теперь можно отправлять уведомления!")
            
            return chat_id
            
        else:
            print(f"❌ Ошибка API: {data}")
            return None
            
    except requests.RequestException as e:
        print(f"❌ Ошибка соединения: {e}")
        return None
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        return None

def test_bot_connection():
    """
    Тестирует соединение с ботом
    """
    
    bot_token = "8381840391:AAHuxT53GUYKeT_RitxfhAaD-r-YX3zy1v4"
    api_url = f"https://api.telegram.org/bot{bot_token}"
    
    try:
        url = f"{api_url}/getMe"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('ok'):
            bot_info = data['result']
            print("✅ Бот подключен успешно!")
            print(f"🤖 Имя бота: {bot_info.get('first_name', 'Unknown')}")
            print(f"📱 Username: @{bot_info.get('username', 'unknown')}")
            print(f"🆔 ID бота: {bot_info.get('id', 'unknown')}")
            return True
        else:
            print(f"❌ Ошибка API: {data}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")
        return False

if __name__ == "__main__":
    print("🎾 Настройка Telegram бота для теннисного монитора")
    print("=" * 60)
    
    # Тестируем соединение с ботом
    print("\n1️⃣ Проверка соединения с ботом...")
    if test_bot_connection():
        print("\n2️⃣ Получение Chat ID...")
        get_chat_id()
    else:
        print("❌ Не удалось подключиться к боту")
        print("💡 Проверьте правильность токена")
