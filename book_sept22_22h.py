#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматическое бронирование корта на 22.09 в 22:00
Запуск сегодня с 23:00
"""

import sys
import os
from datetime import datetime, timedelta
import time

# Добавляем текущую директорию в путь
sys.path.insert(0, '/root/tennis-monitor')

from corrected_30min_analyzer import Corrected30MinAnalyzer
from simple_auto_booking import SimpleAutoBooking

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

def book_sept22_22h():
    """Бронирование корта на 22.09 в 22:00"""
    print("🎾 АВТОМАТИЧЕСКОЕ БРОНИРОВАНИЕ КОРТА")
    print("=" * 50)
    print("📅 Дата: 22.09.2025")
    print("⏰ Время: 22:00-00:00 (2 часа)")
    print("🏟️ Тип: Грунт")
    print("👤 Пользователь: Потоцкий Андрей")
    print("💰 Оплата: В клубе")
    print("=" * 50)
    
    # Инициализируем компоненты
    analyzer = Corrected30MinAnalyzer()
    booking = SimpleAutoBooking()
    
    target_date = "2025-09-22"
    target_time = 22  # 22:00
    duration = 2      # 2 часа
    
    print(f"\n🔍 Поиск свободного корта на {target_date} в {target_time}:00...")
    
    # Анализируем доступные корты
    free_courts = analyzer.analyze_ground_courts_22h_corrected(target_date)
    
    if not free_courts:
        print("❌ Свободных кортов не найдено")
        return False, "Свободных кортов не найдено"
    
    print(f"✅ Найдено {len(free_courts)} кортов с доступными слотами")
    
    # Ищем корт с нужной длительностью
    target_duration = f"{target_time:02d}:00-{(target_time + duration) % 24:02d}:00"
    target_court = None
    
    print(f"\n🎯 Ищем корт с длительностью: {target_duration}")
    
    for court in free_courts:
        print(f"  • Корт №{court['court_number']}: {court['time_display']}")
        if court['time_display'] == target_duration:
            target_court = court
            print(f"    ✅ ПОДХОДИТ!")
            break
    
    if target_court:
        print(f"\n🎯 Найден подходящий корт №{target_court['court_number']}")
        
        # Выполняем бронирование
        print("\n🤖 Выполнение автобронирования...")
        success, message = booking.auto_book_court(
            date=target_date,
            time_from=target_time,
            duration_hours=duration,
            simulation=False  # Реальное бронирование!
        )
        
        if success:
            print("✅ Бронирование успешно!")
            print(f"📝 Результат: {message}")
            return True, message
        else:
            print("❌ Ошибка бронирования")
            print(f"📝 Ошибка: {message}")
            return False, message
    else:
        print(f"\n⚠️ Корт с длительностью {target_duration} не найден")
        print("📋 Доступные варианты:")
        for court in free_courts:
            duration_text = '2 часа' if court['time_display'] == '22:00-00:00' else '1.5 часа' if court['time_display'] == '22:30-00:00' else '1 час' if court['time_display'] == '23:00-00:00' else '30 мин'
            print(f"  • Корт №{court['court_number']}: {court['time_display']} ({duration_text})")
        
        return False, f"Корт с длительностью {target_duration} не найден"

def main():
    """Главная функция"""
    print("🎾 TENNIS MONITOR - АВТОБРОНИРОВАНИЕ")
    print("=" * 60)
    print("📅 Цель: Корт на 22.09.2025 в 22:00-00:00")
    print("⏰ Запуск: Сегодня в 23:00")
    print("🤖 Режим: Автоматическое бронирование")
    print("=" * 60)
    
    # Проверяем текущее время
    now = datetime.now()
    print(f"🕐 Текущее время: {now.strftime('%H:%M:%S %d.%m.%Y')}")
    
    if now.hour >= 23:
        print("✅ Уже 23:00 или позже, запускаем сразу!")
        success, message = book_sept22_22h()
    else:
        print("⏳ Ожидание до 23:00...")
        wait_until_23h()
        success, message = book_sept22_22h()
    
    # Итоговый результат
    print("\n" + "=" * 60)
    if success:
        print("🎉 БРОНИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print("📱 Проверьте Telegram для подтверждения")
    else:
        print("❌ БРОНИРОВАНИЕ НЕ УДАЛОСЬ")
        print("📱 Проверьте Telegram для информации об ошибке")
    print("=" * 60)

if __name__ == "__main__":
    main()
