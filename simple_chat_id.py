#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой способ получить Chat ID
"""

import requests
import json

def get_chat_id_simple():
    """
    Получает Chat ID простым способом
    """
    
    bot_token = "8381840391:AAHuxT53GUYKeT_RitxfhAaD-r-YX3zy1v4"
    
    print("🎾 Получение Chat ID для теннисного монитора")
    print("=" * 50)
    print("📋 Инструкции:")
    print("1. Откройте Telegram")
    print("2. Найдите бота: @TennisPotBooking_bot")
    print("3. Отправьте боту сообщение: /start")
    print("4. Подождите 5 секунд")
    print("5. Нажмите Enter")
    print("=" * 50)
    
    input("Нажмите Enter после отправки сообщения боту...")
    
    # Ждем немного
    import time
    print("⏳ Ожидание сообщений...")
    time.sleep(3)
    
    try:
        # Получаем обновления
        api_url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(api_url, timeout=10)
        data = response.json()
        
        if data.get('ok') and data.get('result'):
            updates = data['result']
            
            if updates:
                # Берем последнее сообщение
                last_update = updates[-1]
                message = last_update.get('message', {})
                chat = message.get('chat', {})
                
                chat_id = chat.get('id')
                first_name = chat.get('first_name', '')
                username = chat.get('username', '')
                
                print(f"✅ Chat ID найден!")
                print(f"🆔 Chat ID: {chat_id}")
                print(f"👤 Имя: {first_name}")
                if username:
                    print(f"📱 Username: @{username}")
                
                # Сохраняем конфигурацию
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
                print("❌ Сообщения не найдены")
                print("💡 Убедитесь, что вы отправили сообщение боту")
                return None
        else:
            print(f"❌ Ошибка API: {data}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    get_chat_id_simple()
