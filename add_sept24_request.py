#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Добавление запроса на бронирование 24.09 в систему отложенного бронирования
"""

import sys
import os
from datetime import datetime

# Добавляем текущую директорию в путь
sys.path.insert(0, '/root/tennis-monitor')

from smart_booking_system import SmartBookingSystem

def add_sept24_request():
    """Добавление запроса на 24.09"""
    print("🎾 ДОБАВЛЕНИЕ ЗАПРОСА НА БРОНИРОВАНИЕ 24.09")
    print("=" * 50)
    
    system = SmartBookingSystem()
    
    # Параметры запроса
    date = "2025-09-24"
    time_from = 20  # 20:00
    duration_hours = 2  # 2 часа
    description = "Автоматический запрос на бронирование корта"
    
    print(f"📅 Дата: {date}")
    print(f"⏰ Время: {time_from}:00-{(time_from + duration_hours) % 24}:00")
    print(f"🏟️ Длительность: {duration_hours} часа")
    print(f"📝 Описание: {description}")
    
    # Проверяем доступность даты
    print(f"\n🔍 Проверяем доступность даты {date}...")
    
    if system.is_date_available(date):
        print(f"✅ Дата {date} доступна!")
        print("🤖 Выполняем немедленное бронирование...")
        
        # Создаем временный запрос для немедленного выполнения
        temp_request = {
            'id': 0,
            'date': date,
            'time_from': time_from,
            'duration_hours': duration_hours,
            'description': description,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'last_check': None,
            'attempts': 0
        }
        
        success, message = system.process_booking_request(temp_request)
        
        if success:
            print(f"🎉 Бронирование выполнено: {message}")
        else:
            print(f"❌ Ошибка бронирования: {message}")
    else:
        print(f"⏳ Дата {date} недоступна (больше 7 дней)")
        print("📝 Добавляем запрос в систему отложенного бронирования...")
        
        request_id = system.add_booking_request(date, time_from, duration_hours, description)
        
        print(f"\n✅ Запрос успешно добавлен!")
        print(f"🆔 ID запроса: #{request_id}")
        print(f"📋 Статус: Отложенное бронирование")
        print(f"🔄 Автоматическая обработка: Включена")
        
        print(f"\n📅 ПЛАН ОБРАБОТКИ:")
        print(f"  • Запрос будет проверяться автоматически")
        print(f"  • Когда {date} станет доступна (через 7 дней), система автоматически")
        print(f"    найдет свободный корт в {time_from}:00 и выполнит бронирование")
        print(f"  • Вы получите уведомление о результате")
    
    # Показываем все запросы
    print(f"\n📋 ВСЕ ЗАПРОСЫ НА БРОНИРОВАНИЕ:")
    print("-" * 50)
    system.show_requests_status()

if __name__ == "__main__":
    add_sept24_request()
