#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простое тестирование бронирования на 24.09 без Telegram
"""

import sys
import os
from datetime import datetime

# Добавляем текущую директорию в путь
sys.path.insert(0, '/root/tennis-monitor')

from corrected_30min_analyzer import Corrected30MinAnalyzer
from simple_auto_booking import SimpleAutoBooking

def simple_test_sept24():
    """Простое тестирование на 24.09"""
    print("🎾 ПРОСТОЕ ТЕСТИРОВАНИЕ БРОНИРОВАНИЯ НА 24.09")
    print("=" * 50)
    print("📅 Дата: 24.09.2025")
    print("⏰ Время: 20:00-22:00 (2 часа)")
    print("🏟️ Тип: Грунт")
    print("🤖 Режим: СИМУЛЯЦИЯ")
    print("=" * 50)
    
    # Инициализируем компоненты
    analyzer = Corrected30MinAnalyzer()
    booking = SimpleAutoBooking()
    
    target_date = "2025-09-24"
    target_time = 20  # 20:00
    duration = 2      # 2 часа
    
    print(f"\n🔍 Поиск свободных кортов на {target_date} в {target_time}:00...")
    
    # Анализируем доступные корты
    free_courts = analyzer.analyze_ground_courts_22h_corrected(target_date)
    
    if not free_courts:
        print("❌ Свободных кортов не найдено")
        return
    
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
        
        # Тестируем бронирование
        print("\n🤖 Тестирование автобронирования...")
        success, message = booking.auto_book_court(
            date=target_date,
            time_from=target_time,
            duration_hours=duration,
            simulation=True
        )
        
        if success:
            print("✅ Тест бронирования успешен!")
            print(f"📝 Результат: {message}")
        else:
            print("❌ Ошибка в тесте бронирования")
            print(f"📝 Ошибка: {message}")
    else:
        print(f"\n⚠️ Корт с длительностью {target_duration} не найден")
        print("📋 Доступные варианты:")
        for court in free_courts:
            duration_text = '2 часа' if court['time_display'] == '22:00-00:00' else '1.5 часа' if court['time_display'] == '22:30-00:00' else '1 час' if court['time_display'] == '23:00-00:00' else '30 мин'
            print(f"  • Корт №{court['court_number']}: {court['time_display']} ({duration_text})")
    
    print("\n" + "=" * 50)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 50)

if __name__ == "__main__":
    simple_test_sept24()
