#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка статуса процесса бронирования
"""

import os
import subprocess
import time
from datetime import datetime

def check_booking_status():
    """Проверка статуса процесса бронирования"""
    print("🔍 ПРОВЕРКА СТАТУСА БРОНИРОВАНИЯ")
    print("=" * 50)
    
    # Проверяем процесс
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'book_sept24_20h.py' in result.stdout:
            print("✅ Процесс бронирования запущен")
            
            # Извлекаем PID
            lines = result.stdout.split('\n')
            for line in lines:
                if 'book_sept24_20h.py' in line and 'grep' not in line:
                    parts = line.split()
                    if len(parts) > 1:
                        pid = parts[1]
                        print(f"📊 PID: {pid}")
                        break
        else:
            print("❌ Процесс бронирования не найден")
    except Exception as e:
        print(f"❌ Ошибка проверки процесса: {e}")
    
    # Проверяем лог
    if os.path.exists('booking_log.txt'):
        print("\n📝 ЛОГ ПРОЦЕССА:")
        print("-" * 30)
        try:
            with open('booking_log.txt', 'r') as f:
                content = f.read()
                if content.strip():
                    print(content)
                else:
                    print("Лог пустой (процесс еще не начал работу)")
        except Exception as e:
            print(f"❌ Ошибка чтения лога: {e}")
    else:
        print("❌ Лог файл не найден")
    
    # Текущее время
    now = datetime.now()
    print(f"\n🕐 Текущее время: {now.strftime('%H:%M:%S %d.%m.%Y')}")
    
    if now.hour >= 23:
        print("✅ Уже 23:00 или позже - процесс должен работать")
    else:
        hours_left = 23 - now.hour
        minutes_left = 60 - now.minute
        print(f"⏳ До 23:00 осталось: {hours_left-1}ч {minutes_left}мин")

if __name__ == "__main__":
    check_booking_status()
