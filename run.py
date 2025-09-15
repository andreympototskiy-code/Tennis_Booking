#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой запуск монитора теннисного сайта
"""

import sys
import os
from datetime import datetime, timedelta

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from final_monitor import FinalTennisMonitor

def main():
    """Простой интерфейс для запуска монитора"""
    
    print("🎾 Монитор теннисного сайта x19.spb.ru")
    print("=" * 50)
    
    monitor = FinalTennisMonitor()
    
    while True:
        print("\nВыберите действие:")
        print("1. Проверить свободные слоты на завтра")
        print("2. Проверить свободные слоты на конкретную дату")
        print("3. Проверить свободные слоты на 16 сентября 2025")
        print("4. Выход")
        
        choice = input("\nВведите номер (1-4): ").strip()
        
        if choice == "1":
            print("\n🔍 Проверяем свободные слоты на завтра...")
            slots = monitor.get_tomorrow_slots()
            monitor.print_available_slots(slots)
            
            if slots:
                save = input("\n💾 Сохранить результаты в файл? (y/n): ").strip().lower()
                if save == 'y':
                    monitor.save_slots_to_file(slots)
            
        elif choice == "2":
            date_input = input("\n📅 Введите дату в формате YYYY-MM-DD (например, 2025-09-16): ").strip()
            
            try:
                # Проверяем формат даты
                datetime.strptime(date_input, '%Y-%m-%d')
                print(f"\n🔍 Проверяем свободные слоты на {date_input}...")
                slots = monitor.get_slots_for_date(date_input)
                monitor.print_available_slots(slots)
                
                if slots:
                    save = input("\n💾 Сохранить результаты в файл? (y/n): ").strip().lower()
                    if save == 'y':
                        monitor.save_slots_to_file(slots)
                        
            except ValueError:
                print("❌ Неверный формат даты! Используйте YYYY-MM-DD")
                
        elif choice == "3":
            print("\n🔍 Проверяем свободные слоты на 16 сентября 2025...")
            slots = monitor.get_slots_for_date("2025-09-16")
            monitor.print_available_slots(slots)
            
            if slots:
                save = input("\n💾 Сохранить результаты в файл? (y/n): ").strip().lower()
                if save == 'y':
                    monitor.save_slots_to_file(slots)
            
        elif choice == "4":
            print("\n👋 До свидания!")
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
        print("Проверьте логи в файле final_monitor.log")
