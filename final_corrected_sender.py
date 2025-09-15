#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный скрипт для отправки правильного уведомления о грунтовых кортах
"""

import sys
import os
from datetime import datetime, timedelta

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from corrected_monitor import CorrectedTennisMonitor
from telegram_notifier import TelegramNotifier, get_telegram_config

def send_corrected_notification():
    """
    Отправляет правильное уведомление о свободных грунтовых кортах завтра в 22:00
    """
    
    print("🎾 ОТПРАВКА ПРАВИЛЬНОГО УВЕДОМЛЕНИЯ")
    print("=" * 50)
    print("Используем исправленный монитор для точных данных")
    print("=" * 50)
    
    # Получаем конфигурацию Telegram
    config = get_telegram_config()
    if not config:
        print("❌ Конфигурация Telegram не найдена!")
        return False
    
    # Инициализируем мониторы
    monitor = CorrectedTennisMonitor()
    notifier = TelegramNotifier(config['bot_token'], config['chat_id'])
    
    # Проверяем соединение с Telegram
    print("🔗 Проверка соединения с Telegram...")
    if not notifier.test_connection():
        print("❌ Ошибка соединения с Telegram!")
        return False
    
    print("✅ Соединение с Telegram установлено")
    
    # Получаем завтрашние свободные корты
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')
    
    print(f"📅 Проверяем свободные слоты на завтра: {tomorrow_str}")
    
    try:
        # Получаем свободные грунтовые корты в 22:00
        free_courts = monitor.get_ground_courts_22h_with_verification(tomorrow_str)
        
        if not free_courts:
            print("❌ Свободных грунтовых кортов в 22:00 не найдено")
            
            # Отправляем уведомление об отсутствии слотов
            message = f"❌ Свободных грунтовых кортов в 22:00-23:00 на {tomorrow_str} не найдено\n\n"
            message += "🔗 Проверить: https://x19.spb.ru/bronirovanie/"
            
            success = notifier.send_message(message)
            if success:
                print("✅ Уведомление об отсутствии слотов отправлено")
                return True
            else:
                print("❌ Ошибка отправки уведомления")
                return False
        
        print(f"✅ Найдено {len(free_courts)} свободных грунтовых кортов в 22:00")
        
        # Отправляем уведомление
        print("\n📤 Отправка уведомления в Telegram...")
        
        # Формируем сообщение
        message = f"🎾 <b>Свободные теннисные корты</b>\n"
        message += f"📅 Дата: {tomorrow_str}\n"
        message += f"🏟️ Тип корта: Грунт\n"
        message += f"⏰ Время: 22:00-23:00\n"
        message += f"✅ Найдено: {len(free_courts)} свободных слотов\n\n"
        
        message += f"⏰ <b>22-23</b>\n"
        for court in free_courts:
            message += f"  🏟️ {court['court_type']} (Корт №{court['court_number']})\n"
        
        message += "\n🔗 <a href='https://x19.spb.ru/bronirovanie/'>Забронировать</a>"
        
        success = notifier.send_message(message)
        
        if success:
            print("✅ Уведомление успешно отправлено в Telegram!")
            print(f"📊 Отправлена информация о {len(free_courts)} свободных грунтовых кортах")
            print("\n📋 Детали отправленных слотов:")
            for court in free_courts:
                print(f"  • Корт №{court['court_number']} - {court['court_type']}")
            return True
        else:
            print("❌ Ошибка отправки уведомления")
            return False
            
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        return False

def main():
    """Основная функция"""
    
    print("🎾 Финальная отправка правильного уведомления")
    print("=" * 50)
    
    while True:
        print("\nВыберите действие:")
        print("1. Отправить правильное уведомление о грунтовых кортах завтра в 22:00")
        print("2. Проверить данные без отправки")
        print("3. Тест соединения с Telegram")
        print("4. Выход")
        
        choice = input("\nВведите номер (1-4): ").strip()
        
        if choice == "1":
            send_corrected_notification()
            
        elif choice == "2":
            # Проверка данных без отправки
            monitor = CorrectedTennisMonitor()
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
            print(f"\n🔍 Проверка данных на завтра: {tomorrow}")
            
            free_courts = monitor.get_ground_courts_22h_with_verification(tomorrow)
            
            if free_courts:
                print(f"\n✅ Найдено {len(free_courts)} свободных грунтовых кортов в 22:00")
                print("📋 Свободные корты:")
                for court in free_courts:
                    print(f"  • Корт №{court['court_number']} - {court['court_type']}")
            else:
                print("❌ Свободных грунтовых кортов в 22:00 не найдено")
                
        elif choice == "3":
            config = get_telegram_config()
            if config:
                notifier = TelegramNotifier(config['bot_token'], config['chat_id'])
                if notifier.test_connection():
                    print("✅ Соединение с Telegram работает")
                else:
                    print("❌ Ошибка соединения с Telegram")
            else:
                print("❌ Конфигурация Telegram не найдена")
                
        elif choice == "4":
            print("👋 До свидания!")
            break
            
        else:
            print("❌ Неверный выбор! Попробуйте еще раз.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Программа остановлена пользователем")
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
