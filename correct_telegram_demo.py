#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Правильная демонстрация Telegram уведомления о грунтовых кортах завтра в 22:00
"""

import sys
import os
from datetime import datetime, timedelta

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from final_monitor import FinalTennisMonitor

def correct_demo():
    """
    Правильная демонстрация уведомления о грунтовых кортах завтра в 22:00
    """
    
    print("🎾 ПРАВИЛЬНАЯ ДЕМОНСТРАЦИЯ TELEGRAM УВЕДОМЛЕНИЯ")
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
        
        # ПРАВИЛЬНАЯ фильтрация грунтовых кортов в 22:00
        # time_from хранится как число, а не строка!
        ground_slots_22h = []
        for slot in slots:
            court_type = slot.get('court_type', '')
            time_from = slot.get('time_from')  # Это число!
            
            # Проверяем, что это грунтовый корт и время 22:00
            if "Грунт" in court_type and time_from == 22:
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
            
            # Показываем детали
            print("\n📋 ДЕТАЛИ СВОБОДНЫХ СЛОТОВ:")
            for i, slot in enumerate(ground_slots_22h, 1):
                print(f"{i:2d}. 🏟️ {slot['court_type']} (Корт №{slot['court_number']})")
                print(f"    ⏰ {slot['time_from']}:00-{slot['time_to']}:00")
                print(f"    🆔 ID: {slot['court_id']}")
                print()
            
        else:
            print("\n❌ Свободных грунтовых кортов в 22:00 не найдено")
            
            # Показываем альтернативы
            print("\n🔍 АЛЬТЕРНАТИВЫ:")
            
            # Все грунтовые корты
            ground_slots = [slot for slot in slots if "Грунт" in slot.get('court_type', '')]
            print(f"🏟️ Всего грунтовых кортов: {len(ground_slots)}")
            
            # Группируем по времени
            time_groups = {}
            for slot in ground_slots:
                time_key = f"{slot['time_from']}-{slot['time_to']}"
                if time_key not in time_groups:
                    time_groups[time_key] = []
                time_groups[time_key].append(slot)
            
            print("\n📊 Доступные времена для грунтовых кортов:")
            for time_range, time_slots in sorted(time_groups.items()):
                print(f"  ⏰ {time_range}: {len(time_slots)} кортов")
            
            # Рекомендуем ближайшие вечерние времена
            evening_times = [20, 21, 22, 23]
            print("\n🌅 РЕКОМЕНДУЕМЫЕ ВЕЧЕРНИЕ ВРЕМЕНА:")
            for time_slot in evening_times:
                count = len([slot for slot in ground_slots 
                           if slot.get('time_from') == time_slot])
                if count > 0:
                    print(f"  ⏰ {time_slot}:00-{time_slot+1}:00 - {count} грунтовых кортов")
        
        print("\n" + "=" * 60)
        print("💡 ДЛЯ НАСТРОЙКИ TELEGRAM УВЕДОМЛЕНИЙ:")
        print("1. Создайте бота через @BotFather в Telegram")
        print("2. Получите Chat ID через @userinfobot")
        print("3. Создайте файл telegram_config.json с вашими данными:")
        print('   {"bot_token": "ваш_токен", "chat_id": "ваш_chat_id"}')
        print("4. Запустите: python send_telegram_notification.py")
        print("5. Выберите опцию 1 для отправки уведомления")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")


if __name__ == "__main__":
    correct_demo()
