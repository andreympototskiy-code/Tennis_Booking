#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация Telegram уведомлений без реальной отправки
"""

import sys
import os
from datetime import datetime, timedelta

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from final_monitor import FinalTennisMonitor

def demo_telegram_notification():
    """
    Демонстрация того, как будет выглядеть уведомление в Telegram
    """
    
    print("🎾 ДЕМОНСТРАЦИЯ TELEGRAM УВЕДОМЛЕНИЙ")
    print("=" * 60)
    print("Показываем, как будет выглядеть уведомление о свободных")
    print("грунтовых кортах завтра в 22:00")
    print("=" * 60)
    
    # Инициализируем монитор
    monitor = FinalTennisMonitor()
    
    # Получаем завтрашние слоты
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')
    
    print(f"\n📅 Проверяем свободные слоты на завтра: {tomorrow_str}")
    
    try:
        slots = monitor.get_tomorrow_slots()
        
        if not slots:
            print("❌ Свободных слотов на завтра не найдено")
            return
        
        print(f"✅ Найдено {len(slots)} свободных слотов на завтра")
        
        # Фильтруем грунтовые корты в 22:00
        ground_slots_22h = [slot for slot in slots 
                          if "Грунт" in slot.get('court_type', '') 
                          and slot.get('time_from') == '22']
        
        print(f"\n🏟️ Найдено {len(ground_slots_22h)} свободных грунтовых кортов в 22:00")
        
        if ground_slots_22h:
            # Показываем, как будет выглядеть уведомление
            print("\n📱 ТАК ВЫГЛЯДИТ УВЕДОМЛЕНИЕ В TELEGRAM:")
            print("=" * 50)
            
            message = f"🎾 <b>Свободные теннисные корты</b>\n"
            message += f"📅 Дата: {tomorrow_str}\n"
            message += f"🏟️ Тип корта: Грунт\n"
            message += f"⏰ Время: 22\n"
            message += f"✅ Найдено: {len(ground_slots_22h)} свободных слотов\n\n"
            
            message += f"⏰ <b>22-23</b>\n"
            for slot in ground_slots_22h:
                message += f"  🏟️ {slot['court_type']} (Корт №{slot['court_number']})\n"
            
            message += "\n🔗 <a href='https://x19.spb.ru/bronirovanie/'>Забронировать</a>"
            
            print(message)
            
            print("\n" + "=" * 50)
            print("📋 ДЕТАЛЬНАЯ ИНФОРМАЦИЯ О СЛОТАХ:")
            print("=" * 50)
            
            for i, slot in enumerate(ground_slots_22h, 1):
                print(f"{i:2d}. 🏟️ {slot['court_type']} (Корт №{slot['court_number']})")
                print(f"    ⏰ Время: {slot['time_from']}-{slot['time_to']}")
                print(f"    📅 Дата: {slot['date']}")
                print(f"    🆔 ID корта: {slot['court_id']}")
                print()
            
            print("✅ ВСЕ ГОТОВО К ОТПРАВКЕ В TELEGRAM!")
            print("\n💡 Для настройки Telegram уведомлений:")
            print("1. Следуйте инструкциям в файле TELEGRAM_SETUP.md")
            print("2. Создайте бота через @BotFather")
            print("3. Получите Chat ID через @userinfobot")
            print("4. Настройте файл telegram_config.json")
            print("5. Запустите: python send_telegram_notification.py")
            
        else:
            print("❌ Свободных грунтовых кортов в 22:00 не найдено")
            
            # Показываем альтернативы
            print("\n🔍 АЛЬТЕРНАТИВЫ:")
            
            # Грунтовые корты в другое время
            ground_slots = [slot for slot in slots if "Грунт" in slot.get('court_type', '')]
            if ground_slots:
                print(f"🏟️ Всего грунтовых кортов: {len(ground_slots)}")
                
                # Группируем по времени
                time_groups = {}
                for slot in ground_slots:
                    time_key = f"{slot['time_from']}-{slot['time_to']}"
                    if time_key not in time_groups:
                        time_groups[time_key] = []
                    time_groups[time_key].append(slot)
                
                print("📊 Доступные времена для грунтовых кортов:")
                for time_range, time_slots in sorted(time_groups.items()):
                    print(f"  ⏰ {time_range}: {len(time_slots)} кортов")
            
            # Ближайшие к 22:00 времена
            evening_times = ['20', '21', '22', '23']
            evening_slots = []
            for time_slot in evening_times:
                evening_slots.extend([slot for slot in ground_slots 
                                    if slot.get('time_from') == time_slot])
            
            if evening_slots:
                print(f"\n🌅 Ближайшие вечерние времена:")
                for time_slot in evening_times:
                    count = len([slot for slot in ground_slots 
                               if slot.get('time_from') == time_slot])
                    if count > 0:
                        print(f"  ⏰ {time_slot}:00 - {count} грунтовых кортов")
            
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")


def demo_all_notification_types():
    """
    Демонстрация всех типов уведомлений
    """
    
    print("\n🎾 ДЕМОНСТРАЦИЯ ВСЕХ ТИПОВ УВЕДОМЛЕНИЙ")
    print("=" * 60)
    
    monitor = FinalTennisMonitor()
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    try:
        slots = monitor.get_tomorrow_slots()
        
        if not slots:
            print("❌ Свободных слотов не найдено")
            return
        
        # Демонстрация различных фильтров
        filters = [
            {"name": "Грунтовые корты в 22:00", "court_type": "Грунт", "time": "22"},
            {"name": "Хардовые корты в 19:00", "court_type": "Хард", "time": "19"},
            {"name": "Все корты в 20:00", "court_type": None, "time": "20"},
            {"name": "Грунтовые корты весь день", "court_type": "Грунт", "time": None},
        ]
        
        for filter_info in filters:
            print(f"\n📋 {filter_info['name']}:")
            print("-" * 40)
            
            filtered_slots = slots.copy()
            
            if filter_info['court_type']:
                filtered_slots = [slot for slot in filtered_slots 
                                if filter_info['court_type'] in slot.get('court_type', '')]
            
            if filter_info['time']:
                filtered_slots = [slot for slot in filtered_slots 
                                if slot.get('time_from') == filter_info['time']]
            
            print(f"✅ Найдено: {len(filtered_slots)} слотов")
            
            if filtered_slots:
                # Показываем первые 5 слотов
                for i, slot in enumerate(filtered_slots[:5], 1):
                    print(f"  {i}. {slot['time_from']}-{slot['time_to']} - {slot['court_type']} (Корт №{slot['court_number']})")
                
                if len(filtered_slots) > 5:
                    print(f"  ... и еще {len(filtered_slots) - 5} слотов")
    
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")


def main():
    """Основная функция демонстрации"""
    
    demo_telegram_notification()
    
    input("\nНажмите Enter для показа всех типов уведомлений...")
    
    demo_all_notification_types()
    
    print("\n" + "=" * 60)
    print("🎾 Демонстрация завершена!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Демонстрация остановлена пользователем")
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
