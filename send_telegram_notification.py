#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для отправки уведомления в Telegram о свободных грунтовых кортах завтра в 22 часа
"""

import sys
import os
from datetime import datetime, timedelta

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from final_monitor import FinalTennisMonitor
from telegram_notifier import TelegramNotifier, get_telegram_config

def send_ground_courts_22h_notification():
    """
    Отправляет уведомление о свободных грунтовых кортах завтра в 22 часа
    """
    
    print("🎾 Отправка уведомления о свободных грунтовых кортах")
    print("=" * 60)
    
    # Получаем конфигурацию Telegram
    config = get_telegram_config()
    if not config:
        print("❌ Конфигурация Telegram не найдена!")
        print("📋 Создайте файл telegram_config.json с вашими данными")
        return False
    
    # Инициализируем монитор и уведомления
    monitor = FinalTennisMonitor()
    notifier = TelegramNotifier(config['bot_token'], config['chat_id'])
    
    # Проверяем соединение с Telegram
    print("🔗 Проверка соединения с Telegram...")
    if not notifier.test_connection():
        print("❌ Ошибка соединения с Telegram!")
        return False
    
    print("✅ Соединение с Telegram установлено")
    
    # Получаем завтрашние слоты
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')
    
    print(f"📅 Проверяем свободные слоты на завтра: {tomorrow_str}")
    
    try:
        slots = monitor.get_tomorrow_slots()
        
        if not slots:
            print("❌ Свободных слотов на завтра не найдено")
            return False
        
        print(f"✅ Найдено {len(slots)} свободных слотов на завтра")
        
        # Отправляем уведомление о грунтовых кортах в 22 часа
        print("📤 Отправка уведомления о грунтовых кортах в 22:00...")
        
        success = notifier.send_tennis_slots_notification(
            slots=slots,
            date=tomorrow_str,
            court_type="Грунт",
            time_filter="22"
        )
        
        if success:
            print("✅ Уведомление успешно отправлено в Telegram!")
            
            # Показываем краткую статистику
            ground_slots_22h = [slot for slot in slots 
                              if "Грунт" in slot.get('court_type', '') 
                              and slot.get('time_from') == '22']
            
            print(f"📊 Найдено {len(ground_slots_22h)} свободных грунтовых кортов в 22:00")
            
            if ground_slots_22h:
                print("🏟️ Доступные корты:")
                for slot in ground_slots_22h:
                    print(f"  • Грунт (Корт №{slot['court_number']}) - {slot['time_from']}-{slot['time_to']}")
            
            return True
        else:
            print("❌ Ошибка отправки уведомления")
            return False
            
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        return False


def send_custom_notification():
    """
    Интерактивная отправка уведомления с выбором параметров
    """
    
    print("🎾 Интерактивная отправка уведомления в Telegram")
    print("=" * 50)
    
    # Получаем конфигурацию Telegram
    config = get_telegram_config()
    if not config:
        print("❌ Конфигурация Telegram не найдена!")
        return False
    
    # Инициализируем монитор и уведомления
    monitor = FinalTennisMonitor()
    notifier = TelegramNotifier(config['bot_token'], config['chat_id'])
    
    # Проверяем соединение с Telegram
    if not notifier.test_connection():
        print("❌ Ошибка соединения с Telegram!")
        return False
    
    print("✅ Соединение с Telegram установлено")
    
    # Выбор даты
    print("\n📅 Выберите дату:")
    print("1. Завтра")
    print("2. Конкретная дата")
    
    date_choice = input("Введите номер (1-2): ").strip()
    
    if date_choice == "1":
        target_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        date_display = "завтра"
    elif date_choice == "2":
        target_date = input("Введите дату в формате YYYY-MM-DD: ").strip()
        date_display = target_date
    else:
        print("❌ Неверный выбор")
        return False
    
    # Выбор типа корта
    print("\n🏟️ Выберите тип корта:")
    print("1. Грунт")
    print("2. Хард")
    print("3. Трава")
    print("4. Все типы")
    
    court_choice = input("Введите номер (1-4): ").strip()
    
    court_types = {
        "1": "Грунт",
        "2": "Хард", 
        "3": "Трава",
        "4": None
    }
    
    court_type = court_types.get(court_choice)
    if court_type is None and court_choice != "4":
        print("❌ Неверный выбор")
        return False
    
    # Выбор времени
    print("\n⏰ Выберите время:")
    print("1. 22:00")
    print("2. Другое время")
    print("3. Все время")
    
    time_choice = input("Введите номер (1-3): ").strip()
    
    if time_choice == "1":
        time_filter = "22"
        time_display = "22:00"
    elif time_choice == "2":
        time_input = input("Введите час (0-23): ").strip()
        try:
            hour = int(time_input)
            if 0 <= hour <= 23:
                time_filter = f"{hour:02d}"
                time_display = f"{hour:02d}:00"
            else:
                print("❌ Неверный час")
                return False
        except ValueError:
            print("❌ Неверный формат времени")
            return False
    elif time_choice == "3":
        time_filter = None
        time_display = "все время"
    else:
        print("❌ Неверный выбор")
        return False
    
    # Получаем слоты
    print(f"\n🔍 Проверяем слоты на {date_display}...")
    
    try:
        if date_choice == "1":
            slots = monitor.get_tomorrow_slots()
        else:
            slots = monitor.get_slots_for_date(target_date)
        
        if not slots:
            print("❌ Свободных слотов не найдено")
            return False
        
        print(f"✅ Найдено {len(slots)} свободных слотов")
        
        # Отправляем уведомление
        print(f"\n📤 Отправка уведомления...")
        
        success = notifier.send_tennis_slots_notification(
            slots=slots,
            date=target_date,
            court_type=court_type,
            time_filter=time_filter
        )
        
        if success:
            print("✅ Уведомление успешно отправлено в Telegram!")
            return True
        else:
            print("❌ Ошибка отправки уведомления")
            return False
            
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        return False


def main():
    """Основная функция"""
    
    print("🎾 Telegram уведомления теннисного монитора")
    print("=" * 50)
    
    while True:
        print("\nВыберите действие:")
        print("1. Отправить уведомление о грунтовых кортах завтра в 22:00")
        print("2. Интерактивная отправка уведомления")
        print("3. Тест соединения с Telegram")
        print("4. Создать шаблон конфигурации")
        print("5. Выход")
        
        choice = input("\nВведите номер (1-5): ").strip()
        
        if choice == "1":
            send_ground_courts_22h_notification()
            
        elif choice == "2":
            send_custom_notification()
            
        elif choice == "3":
            config = get_telegram_config()
            if config:
                notifier = TelegramNotifier(config['bot_token'], config['chat_id'])
                if notifier.test_connection():
                    print("✅ Соединение с Telegram работает")
                    # Отправляем тестовое сообщение
                    test_message = "🎾 Тест уведомлений теннисного монитора\n✅ Соединение работает корректно"
                    if notifier.send_message(test_message):
                        print("✅ Тестовое сообщение отправлено")
                    else:
                        print("❌ Ошибка отправки тестового сообщения")
                else:
                    print("❌ Ошибка соединения с Telegram")
            else:
                print("❌ Конфигурация Telegram не найдена")
                
        elif choice == "4":
            from telegram_notifier import create_telegram_config_template
            create_telegram_config_template()
            
        elif choice == "5":
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
