#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация Tennis Monitor v2.0 - Автоматическое бронирование
"""

import sys
import os
from datetime import datetime, timedelta

# Добавляем текущую директорию в путь
sys.path.insert(0, '/root/tennis-monitor')

from integrated_monitor_booking import IntegratedMonitorBooking

def demo_v2():
    """Демонстрация возможностей версии 2.0"""
    print("🎾 TENNIS MONITOR v2.0 - ДЕМОНСТРАЦИЯ")
    print("=" * 60)
    print("✨ Новые возможности:")
    print("  • Автоматическое бронирование теннисных кортов")
    print("  • Интегрированная система мониторинга и бронирования")
    print("  • Telegram уведомления о найденных кортах")
    print("  • Поддержка данных пользователя")
    print("  • Выбор 'Оплата в клубе'")
    print("=" * 60)
    
    # Инициализируем систему
    system = IntegratedMonitorBooking()
    
    # Тестируем на завтра
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"\n📅 Демонстрация на {tomorrow}")
    print("-" * 40)
    
    # 1. Мониторинг без автобронирования
    print("1️⃣ Мониторинг свободных кортов...")
    success, message = system.monitor_and_book(
        date=tomorrow,
        time_from=22,
        duration_hours=2,
        auto_book=False,
        simulation=True
    )
    
    if success:
        print("✅ Мониторинг завершен")
        if "Найден свободный корт" in message:
            print("🎯 Найден подходящий корт!")
        elif "Доступны частичные слоты" in message:
            print("⚠️ Доступны только частичные слоты")
    else:
        print("❌ Свободных кортов не найдено")
    
    print(f"\n📱 Telegram уведомление отправлено")
    
    # 2. Автоматическое бронирование
    if success and "Найден свободный корт" in message:
        print("\n2️⃣ Автоматическое бронирование...")
        booking_success, booking_message = system.monitor_and_book(
            date=tomorrow,
            time_from=22,
            duration_hours=2,
            auto_book=True,
            simulation=True
        )
        
        if booking_success:
            print("✅ Автобронирование завершено!")
            print(f"📱 Уведомление о бронировании отправлено")
        else:
            print("❌ Ошибка автобронирования")
    
    print("\n" + "=" * 60)
    print("🎯 ВОЗМОЖНОСТИ СИСТЕМЫ:")
    print("=" * 60)
    print("📊 Мониторинг:")
    print("  • Автоматический поиск свободных кортов")
    print("  • Анализ 30-минутных ячеек")
    print("  • Определение 2-часовых слотов")
    print("  • Группировка по физическим кортам")
    
    print("\n🤖 Автобронирование:")
    print("  • Автоматическое заполнение формы")
    print("  • Данные пользователя: Потоцкий Андрей")
    print("  • Телефон: +79313203496")
    print("  • Email: andrey.m.pototskiy@gmail.com")
    print("  • Оплата в клубе")
    
    print("\n📱 Telegram уведомления:")
    print("  • Уведомления о найденных кортах")
    print("  • Статус автобронирования")
    print("  • Ссылки для ручного бронирования")
    
    print("\n⚙️ Настройки:")
    print("  • Время: 22:00-00:00 (2 часа)")
    print("  • Тип корта: Грунт")
    print("  • Режим: Симуляция (безопасно)")
    print("  • Автобронирование: По запросу")
    
    print("\n" + "=" * 60)
    print("🚀 СИСТЕМА ГОТОВА К ИСПОЛЬЗОВАНИЮ!")
    print("=" * 60)

if __name__ == "__main__":
    demo_v2()
