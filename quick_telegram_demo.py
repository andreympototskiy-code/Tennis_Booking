#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрая демонстрация Telegram уведомления о грунтовых кортах завтра в 22:00
"""

import sys
import os
from datetime import datetime, timedelta

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from final_monitor import FinalTennisMonitor

def quick_demo():
    """
    Быстрая демонстрация уведомления о грунтовых кортах завтра в 22:00
    """
    
    print("🎾 БЫСТРАЯ ДЕМОНСТРАЦИЯ TELEGRAM УВЕДОМЛЕНИЯ")
    print("=" * 60)
    print("Показываем уведомление о свободных грунтовых кортах завтра в 22:00")
    print("=" * 60)
    
    monitor = FinalTennisMonitor()
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"📅 Дата: {tomorrow}")
    print(f"🏟️ Тип корта: Грунт")
    print(f"⏰ Время: 22:00-23:00")
    
    try:
        slots = monitor.get_tomorrow_slots()
        
        if not slots:
            print("\n❌ Свободных слотов на завтра не найдено")
            return
        
        print(f"\n✅ Найдено {len(slots)} свободных слотов на завтра")
        
        # Фильтруем грунтовые корты в 22:00
        ground_slots_22h = []
        for slot in slots:
            if ("Грунт" in slot.get('court_type', '') and 
                slot.get('time_from') == '22'):
                ground_slots_22h.append(slot)
        
        print(f"🏟️ Грунтовые корты в 22:00: {len(ground_slots_22h)} слотов")
        
        if ground_slots_22h:
            print("\n📱 УВЕДОМЛЕНИЕ В TELEGRAM:")
            print("=" * 50)
            
            # Формируем сообщение как в Telegram
            message = f"🎾 <b>Свободные теннисные корты</b>\n"
            message += f"📅 Дата: {tomorrow}\n"
            message += f"🏟️ Тип корта: Грунт\n"
            message += f"⏰ Время: 22:00-23:00\n"
            message += f"✅ Найдено: {len(ground_slots_22h)} свободных слотов\n\n"
            
            message += f"⏰ <b>22-23</b>\n"
            for slot in ground_slots_22h:
                message += f"  🏟️ {slot['court_type']} (Корт №{slot['court_number']})\n"
            
            message += "\n🔗 <a href='https://x19.spb.ru/bronirovanie/'>Забронировать</a>"
            
            print(message)
            
            print("\n" + "=" * 50)
            print("✅ УВЕДОМЛЕНИЕ ГОТОВО К ОТПРАВКЕ!")
            
        else:
            print("\n❌ Свободных грунтовых кортов в 22:00 не найдено")
            
            # Показываем ближайшие альтернативы
            print("\n🔍 БЛИЖАЙШИЕ АЛЬТЕРНАТИВЫ:")
            
            # Ищем грунтовые корты в вечернее время
            evening_times = ['21', '22', '23']
            for time_slot in evening_times:
                count = len([slot for slot in slots 
                           if "Грунт" in slot.get('court_type', '') 
                           and slot.get('time_from') == time_slot])
                if count > 0:
                    print(f"  ⏰ {time_slot}:00-{int(time_slot)+1}:00 - {count} грунтовых кортов")
            
            # Если нет вечерних, показываем любые грунтовые
            ground_slots = [slot for slot in slots if "Грунт" in slot.get('court_type', '')]
            if ground_slots:
                print(f"\n🏟️ Всего грунтовых кортов: {len(ground_slots)}")
                
                # Группируем по времени
                time_groups = {}
                for slot in ground_slots:
                    time_key = f"{slot['time_from']}-{slot['time_to']}"
                    if time_key not in time_groups:
                        time_groups[time_key] = 0
                    time_groups[time_key] += 1
                
                print("📊 Доступные времена:")
                for time_range, count in sorted(time_groups.items()):
                    print(f"  ⏰ {time_range}: {count} кортов")
        
        print("\n" + "=" * 60)
        print("💡 ДЛЯ НАСТРОЙКИ TELEGRAM УВЕДОМЛЕНИЙ:")
        print("1. Создайте бота через @BotFather в Telegram")
        print("2. Получите Chat ID через @userinfobot")
        print("3. Создайте файл telegram_config.json")
        print("4. Запустите: python send_telegram_notification.py")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")


if __name__ == "__main__":
    quick_demo()
