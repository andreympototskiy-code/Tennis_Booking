#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматическое бронирование корта на 24.09 в 20:00
Запуск сегодня с 23:00
"""

import sys
import os
from datetime import datetime, timedelta
import time

# Добавляем текущую директорию в путь
sys.path.insert(0, '/root/tennis-monitor')

from integrated_monitor_booking import IntegratedMonitorBooking

def wait_until_23h():
    """Ожидание до 23:00"""
    while True:
        now = datetime.now()
        if now.hour >= 23:
            print(f"✅ Время пришло! Текущее время: {now.strftime('%H:%M:%S')}")
            break
        
        next_23h = now.replace(hour=23, minute=0, second=0, microsecond=0)
        if now.hour >= 23:
            next_23h += timedelta(days=1)
        
        wait_seconds = (next_23h - now).total_seconds()
        wait_hours = wait_seconds / 3600
        
        print(f"⏰ Ожидание до 23:00... Осталось: {wait_hours:.1f} часов")
        print(f"📅 Текущее время: {now.strftime('%H:%M:%S')}")
        
        # Ждем 5 минут
        time.sleep(300)

def book_sept24_20h():
    """Бронирование корта на 24.09 в 20:00"""
    print("🎾 АВТОМАТИЧЕСКОЕ БРОНИРОВАНИЕ КОРТА")
    print("=" * 50)
    print("📅 Дата: 24.09.2025")
    print("⏰ Время: 20:00-22:00 (2 часа)")
    print("🏟️ Тип: Грунт")
    print("👤 Пользователь: Потоцкий Андрей")
    print("💰 Оплата: В клубе")
    print("=" * 50)
    
    # Инициализируем систему
    system = IntegratedMonitorBooking()
    
    target_date = "2025-09-24"
    target_time = 20  # 20:00
    duration = 2      # 2 часа
    
    print(f"\n🔍 Поиск свободного корта на {target_date} в {target_time}:00...")
    
    # Поиск и бронирование
    success, message = system.monitor_and_book(
        date=target_date,
        time_from=target_time,
        duration_hours=duration,
        auto_book=True,  # Включаем автобронирование
        simulation=False  # Реальное бронирование!
    )
    
    if success:
        print(f"\n✅ УСПЕХ! {message}")
        print("📱 Проверьте Telegram для подтверждения")
    else:
        print(f"\n❌ ОШИБКА: {message}")
    
    return success, message

def main():
    """Главная функция"""
    print("🎾 TENNIS MONITOR - АВТОБРОНИРОВАНИЕ")
    print("=" * 60)
    print("📅 Цель: Корт на 24.09.2025 в 20:00-22:00")
    print("⏰ Запуск: Сегодня в 23:00")
    print("🤖 Режим: Автоматическое бронирование")
    print("=" * 60)
    
    # Проверяем текущее время
    now = datetime.now()
    print(f"🕐 Текущее время: {now.strftime('%H:%M:%S %d.%m.%Y')}")
    
    if now.hour >= 23:
        print("✅ Уже 23:00 или позже, запускаем сразу!")
        success, message = book_sept24_20h()
    else:
        print("⏳ Ожидание до 23:00...")
        wait_until_23h()
        success, message = book_sept24_20h()
    
    # Итоговый результат
    print("\n" + "=" * 60)
    if success:
        print("🎉 БРОНИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print("📱 Проверьте Telegram для деталей")
    else:
        print("❌ БРОНИРОВАНИЕ НЕ УДАЛОСЬ")
        print("📱 Проверьте Telegram для информации об ошибке")
    print("=" * 60)

if __name__ == "__main__":
    main()
