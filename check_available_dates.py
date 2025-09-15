#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка доступных дат для бронирования
"""

import sys
import os
from datetime import datetime, timedelta

# Добавляем текущую директорию в путь
sys.path.insert(0, '/root/tennis-monitor')

from corrected_30min_analyzer import Corrected30MinAnalyzer

def check_available_dates():
    """Проверка доступных дат"""
    print("📅 ПРОВЕРКА ДОСТУПНЫХ ДАТ")
    print("=" * 50)
    
    analyzer = Corrected30MinAnalyzer()
    
    # Проверяем даты на неделю вперед
    today = datetime.now()
    
    for i in range(10):  # 10 дней вперед
        check_date = (today + timedelta(days=i)).strftime('%Y-%m-%d')
        date_display = (today + timedelta(days=i)).strftime('%d.%m.%Y')
        
        print(f"\n🔍 Проверяем {date_display} ({check_date})...")
        
        try:
            free_courts = analyzer.analyze_ground_courts_22h_corrected(check_date)
            
            if free_courts:
                print(f"  ✅ Доступно: {len(free_courts)} кортов")
                
                # Проверяем доступность в 20:00
                target_duration = "20:00-22:00"
                available_20h = [court for court in free_courts if court['time_display'] == target_duration]
                
                if available_20h:
                    print(f"  🎯 В 20:00-22:00: {len(available_20h)} кортов")
                    for court in available_20h:
                        print(f"    • Корт №{court['court_number']}")
                else:
                    print(f"  ⚠️ В 20:00-22:00: нет доступных кортов")
            else:
                print(f"  ❌ Недоступно или нет свободных кортов")
                
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
    
    print("\n" + "=" * 50)
    print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
    print("=" * 50)

if __name__ == "__main__":
    check_available_dates()
