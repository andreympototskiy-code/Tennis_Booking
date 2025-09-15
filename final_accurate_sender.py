#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный точный отправитель уведомлений о теннисных кортах
"""

import sys
import os
from datetime import datetime, timedelta

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from corrected_monitor import CorrectedTennisMonitor
from telegram_notifier import TelegramNotifier, get_telegram_config

def send_accurate_notification():
    """
    Отправляет точное уведомление о свободных грунтовых кортах завтра в 22:00
    """
    
    print("🎾 ОТПРАВКА ТОЧНОГО УВЕДОМЛЕНИЯ")
    print("=" * 50)
    print("Используем правильную терминологию: ЛИНИИ кортов")
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
    
    # Получаем свободные корты на сегодня для тестирования
    today = datetime.now()
    today_str = today.strftime('%Y-%m-%d')
    
    print(f"📅 Проверяем свободные слоты на сегодня (тестирование): {today_str}")
    
    try:
        # Получаем свободные грунтовые корты в 22:00
        free_courts = monitor.get_ground_courts_22h_with_verification(today_str)
        
        if not free_courts:
            print("❌ Свободных грунтовых кортов в 22:00 не найдено")
            
            # Отправляем уведомление об отсутствии слотов
            message = f"❌ Свободных грунтовых кортов в 22:00-00:00 на {today_str} не найдено\n\n"
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
        
        # Формируем сообщение с правильной терминологией
        message = f"🎾 <b>Свободные теннисные корты</b>\n"
        message += f"📅 Дата: {today_str}\n"
        message += f"🏟️ Тип корта: Грунт\n"
        message += f"✅ Найдено: {len(free_courts)} свободных слотов (2 часа)\n\n"
        
        # Группируем по физическим кортам
        court_groups = {}
        for court in free_courts:
            court_number = court['court_number']
            if court_number in [4, 5, 6]:
                physical_court = "Дутик № 2"
            elif court_number in [7, 8, 9]:
                physical_court = "Дутик № 3"
            elif court_number in [10, 11, 12, 13]:
                physical_court = "Дутик № 4"
            else:
                physical_court = f"Корт № {court_number}"
            
            if physical_court not in court_groups:
                court_groups[physical_court] = []
            
            # Добавляем время для каждого корта
            time_display = court.get('time_display', f"22:00-23:00")
            court_groups[physical_court].append({
                'number': court_number,
                'time': time_display
            })
        
        for physical_court, courts_info in court_groups.items():
            message += f"🏟️ <b>{physical_court}</b>\n"
            for court_info in courts_info:
                message += f"  • Корт №{court_info['number']} - {court_info['time']}\n"
        
        message += "\n🔗 <a href='https://x19.spb.ru/bronirovanie/'>Забронировать</a>"
        
        success = notifier.send_message(message)
        
        if success:
            print("✅ Уведомление успешно отправлено в Telegram!")
            print(f"📊 Отправлена информация о {len(free_courts)} свободных грунтовых кортах")
            print("\n📋 Детали отправленных слотов:")
            for court in free_courts:
                print(f"  • Линия {court['court_number']} - {court['court_type']}")
            return True
        else:
            print("❌ Ошибка отправки уведомления")
            return False
            
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        return False

def main():
    """Основная функция"""
    
    print("🎾 Финальная отправка точного уведомления")
    print("=" * 50)
    
    while True:
        print("\nВыберите действие:")
        print("1. Отправить точное уведомление о грунтовых кортах завтра в 22:00")
        print("2. Проверить данные без отправки")
        print("3. Тест соединения с Telegram")
        print("4. Выход")
        
        choice = input("\nВведите номер (1-4): ").strip()
        
        if choice == "1":
            send_accurate_notification()
            
        elif choice == "2":
            # Проверка данных без отправки
            monitor = CorrectedTennisMonitor()
            today = datetime.now().strftime('%Y-%m-%d')
            
            print(f"\n🔍 Проверка данных на сегодня (тестирование): {today}")
            
            free_courts = monitor.get_ground_courts_22h_with_verification(today)
            
            if free_courts:
                print(f"\n✅ Найдено {len(free_courts)} свободных грунтовых кортов в 22:00")
                print("📋 Свободные корты:")
                
                # Группируем по физическим кортам
                court_groups = {}
                for court in free_courts:
                    court_number = court['court_number']
                    if court_number in [4, 5, 6]:
                        physical_court = "Дутик № 2"
                    elif court_number in [7, 8, 9]:
                        physical_court = "Дутик № 3"
                    elif court_number in [10, 11, 12, 13]:
                        physical_court = "Дутик № 4"
                    else:
                        physical_court = f"Корт № {court_number}"
                    
                    if physical_court not in court_groups:
                        court_groups[physical_court] = []
                    
                    # Добавляем время для каждого корта
                    time_display = court.get('time_display', f"22:00-23:00")
                    court_groups[physical_court].append({
                        'number': court_number,
                        'time': time_display
                    })
                
                for physical_court, courts_info in court_groups.items():
                    print(f"  • {physical_court}:")
                    for court_info in courts_info:
                        print(f"    - Корт №{court_info['number']} - {court_info['time']}")
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
