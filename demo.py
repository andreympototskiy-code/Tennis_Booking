#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация монитора теннисного сайта x19.spb.ru
"""

import sys
import os
from datetime import datetime, timedelta

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from final_monitor import FinalTennisMonitor

def demo():
    """Демонстрация возможностей монитора"""
    
    print("🎾 ДЕМОНСТРАЦИЯ МОНИТОРА ТЕННИСНОГО САЙТА x19.spb.ru")
    print("=" * 60)
    print("Автоматический поиск свободных слотов для бронирования")
    print("=" * 60)
    
    monitor = FinalTennisMonitor()
    
    # 1. Проверяем завтрашние слоты
    print("\n1️⃣ ПРОВЕРКА ЗАВТРАШНИХ СЛОТОВ")
    print("-" * 40)
    
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')
    print(f"📅 Дата: {tomorrow_str}")
    
    tomorrow_slots = monitor.get_tomorrow_slots()
    
    if tomorrow_slots:
        print(f"✅ Найдено {len(tomorrow_slots)} свободных слотов на завтра")
        
        # Показываем первые 5 слотов
        print("\n📋 Примеры свободных слотов:")
        for i, slot in enumerate(tomorrow_slots[:5]):
            print(f"  {i+1}. {slot['time_from']}-{slot['time_to']} - {slot['court_type']} (Корт №{slot['court_number']})")
        
        if len(tomorrow_slots) > 5:
            print(f"  ... и еще {len(tomorrow_slots) - 5} слотов")
    else:
        print("❌ Свободных слотов на завтра не найдено")
    
    # 2. Проверяем конкретную дату
    print("\n2️⃣ ПРОВЕРКА КОНКРЕТНОЙ ДАТЫ")
    print("-" * 40)
    
    test_date = "2025-09-16"
    print(f"📅 Дата: {test_date}")
    
    specific_slots = monitor.get_slots_for_date(test_date)
    
    if specific_slots:
        print(f"✅ Найдено {len(specific_slots)} свободных слотов на {test_date}")
        
        # Группируем по времени
        time_groups = {}
        for slot in specific_slots:
            time_key = f"{slot['time_from']}-{slot['time_to']}"
            if time_key not in time_groups:
                time_groups[time_key] = []
            time_groups[time_key].append(slot)
        
        print(f"\n📊 Статистика по времени:")
        for time_range, slots in sorted(time_groups.items()):
            court_types = set(slot['court_type'] for slot in slots)
            print(f"  ⏰ {time_range}: {len(slots)} слотов ({', '.join(court_types)})")
        
        # Показываем самые популярные времена
        popular_times = sorted(time_groups.items(), key=lambda x: len(x[1]), reverse=True)[:3]
        print(f"\n🏆 Самые популярные времена:")
        for i, (time_range, slots) in enumerate(popular_times, 1):
            print(f"  {i}. {time_range} - {len(slots)} свободных кортов")
    else:
        print("❌ Свободных слотов не найдено")
    
    # 3. Статистика по типам кортов
    print("\n3️⃣ СТАТИСТИКА ПО ТИПАМ КОРТОВ")
    print("-" * 40)
    
    if specific_slots:
        court_stats = {}
        for slot in specific_slots:
            court_type = slot['court_type']
            if court_type not in court_stats:
                court_stats[court_type] = 0
            court_stats[court_type] += 1
        
        print("📈 Доступность по типам покрытия:")
        for court_type, count in sorted(court_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  🏟️  {court_type}: {count} свободных слотов")
    
    # 4. Сохранение результатов
    print("\n4️⃣ СОХРАНЕНИЕ РЕЗУЛЬТАТОВ")
    print("-" * 40)
    
    all_slots = tomorrow_slots + specific_slots
    if all_slots:
        filename = f"demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        monitor.save_slots_to_file(all_slots, filename)
        print(f"💾 Результаты сохранены в файл: {filename}")
        
        # Показываем размер файла
        try:
            file_size = os.path.getsize(filename)
            print(f"📏 Размер файла: {file_size} байт")
        except:
            pass
    
    # 5. Заключение
    print("\n5️⃣ ЗАКЛЮЧЕНИЕ")
    print("-" * 40)
    
    total_slots = len(tomorrow_slots) + len(specific_slots)
    
    if total_slots > 0:
        print("🎉 Монитор успешно работает!")
        print(f"📊 Всего найдено: {total_slots} свободных слотов")
        print("✅ Система готова к использованию")
        print("\n💡 Рекомендации:")
        print("  • Запускайте мониторинг регулярно для отслеживания изменений")
        print("  • Используйте автоматический мониторинг для получения уведомлений")
        print("  • Сохраняйте результаты для анализа трендов")
    else:
        print("⚠️  Свободных слотов не найдено")
        print("💡 Возможные причины:")
        print("  • Все слоты заняты")
        print("  • Проблемы с доступом к сайту")
        print("  • Изменилась структура API")
    
    print("\n" + "=" * 60)
    print("🎾 Демонстрация завершена!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        demo()
    except KeyboardInterrupt:
        print("\n\n🛑 Демонстрация остановлена пользователем")
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
        print("Проверьте логи в файле final_monitor.log")
