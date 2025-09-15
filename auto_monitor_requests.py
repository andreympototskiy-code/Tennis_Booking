#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматический мониторинг отложенных запросов на бронирование
"""

import sys
import os
import time
from datetime import datetime, timedelta

# Добавляем текущую директорию в путь
sys.path.insert(0, '/root/tennis-monitor')

from smart_booking_system import SmartBookingSystem

def auto_monitor_requests():
    """Автоматический мониторинг запросов"""
    print("🤖 АВТОМАТИЧЕСКИЙ МОНИТОРИНГ ЗАПРОСОВ")
    print("=" * 50)
    
    system = SmartBookingSystem()
    
    # Проверяем каждые 2 часа
    check_interval = 2 * 60 * 60  # 2 часа в секундах
    
    print(f"🔄 Проверка каждые 2 часа")
    print(f"📅 Начало мониторинга: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("=" * 50)
    
    while True:
        try:
            current_time = datetime.now()
            print(f"\n🕐 {current_time.strftime('%d.%m.%Y %H:%M:%S')} - Проверка запросов...")
            
            # Загружаем запросы
            requests = system.load_booking_requests()
            pending_requests = [r for r in requests if r['status'] in ['pending', 'waiting']]
            
            if pending_requests:
                print(f"📋 Найдено {len(pending_requests)} активных запросов")
                system.check_and_process_requests()
            else:
                print("📋 Активных запросов нет")
            
            # Показываем статистику
            completed = len([r for r in requests if r['status'] == 'completed'])
            failed = len([r for r in requests if r['status'] == 'failed'])
            waiting = len([r for r in requests if r['status'] in ['pending', 'waiting']])
            
            print(f"📊 Статистика: ✅ {completed} | ❌ {failed} | ⏳ {waiting}")
            
            # Следующая проверка
            next_check = current_time + timedelta(seconds=check_interval)
            print(f"⏰ Следующая проверка: {next_check.strftime('%d.%m.%Y %H:%M:%S')}")
            
            # Ждем до следующей проверки
            time.sleep(check_interval)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Мониторинг остановлен пользователем")
            break
        except Exception as e:
            print(f"\n❌ Ошибка в мониторинге: {e}")
            print("🔄 Повтор через 30 минут...")
            time.sleep(30 * 60)  # 30 минут

if __name__ == "__main__":
    auto_monitor_requests()
