#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная демонстрация Telegram уведомлений о свободных грунтовых кортах завтра в 22:00
"""

import sys
import os
from datetime import datetime, timedelta

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from final_monitor import FinalTennisMonitor
from telegram_notifier import TelegramNotifier

def final_demo():
    """
    Финальная демонстрация уведомления о грунтовых кортах завтра в 22:00
    """
    
    print("🎾 ФИНАЛЬНАЯ ДЕМОНСТРАЦИЯ TELEGRAM УВЕДОМЛЕНИЙ")
    print("=" * 70)
    print("Показываем, как будет выглядеть уведомление о свободных")
    print("грунтовых кортах завтра в 22:00-23:00")
    print("=" * 70)
    
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
        
        # Используем исправленный фильтр
        notifier = TelegramNotifier("dummy_token", "dummy_chat_id")
        ground_slots_22h = notifier._filter_slots(slots, court_type="Грунт", time_filter="22")
        
        print(f"🏟️ Грунтовые корты в 22:00: {len(ground_slots_22h)} слотов")
        
        if ground_slots_22h:
            print("\n📱 УВЕДОМЛЕНИЕ В TELEGRAM:")
            print("=" * 60)
            
            # Формируем сообщение как в Telegram
            message = notifier._format_slots_message(
                ground_slots_22h, 
                tomorrow, 
                court_type="Грунт", 
                time_filter="22"
            )
            
            print(message)
            
            print("\n" + "=" * 60)
            print("✅ УВЕДОМЛЕНИЕ ГОТОВО К ОТПРАВКЕ!")
            
            # Показываем детали
            print("\n📋 ДЕТАЛИ СВОБОДНЫХ СЛОТОВ:")
            for i, slot in enumerate(ground_slots_22h, 1):
                print(f"{i:2d}. 🏟️ {slot['court_type']} (Корт №{slot['court_number']})")
                print(f"    ⏰ {slot['time_from']}:00-{slot['time_to']}:00")
                print(f"    🆔 ID корта: {slot['court_id']}")
                print(f"    📅 Дата: {slot['date']}")
                print()
            
            print("🎉 ОТЛИЧНЫЕ НОВОСТИ!")
            print(f"📊 Найдено {len(ground_slots_22h)} свободных грунтовых кортов в 22:00")
            print("🏆 Это значит, что у вас есть отличный выбор для вечерней игры!")
            
        else:
            print("\n❌ Свободных грунтовых кортов в 22:00 не найдено")
            
            # Показываем альтернативы
            print("\n🔍 АЛЬТЕРНАТИВЫ:")
            
            # Все грунтовые корты
            ground_slots = [slot for slot in slots if "Грунт" in slot.get('court_type', '')]
            print(f"🏟️ Всего грунтовых кортов: {len(ground_slots)}")
            
            # Ближайшие вечерние времена
            evening_times = ["21", "23"]
            print("\n🌅 БЛИЖАЙШИЕ ВЕЧЕРНИЕ ВРЕМЕНА:")
            for time_slot in evening_times:
                evening_slots = notifier._filter_slots(slots, court_type="Грунт", time_filter=time_slot)
                if evening_slots:
                    print(f"  ⏰ {time_slot}:00-{int(time_slot)+1}:00 - {len(evening_slots)} грунтовых кортов")
        
        print("\n" + "=" * 70)
        print("💡 ДЛЯ НАСТРОЙКИ TELEGRAM УВЕДОМЛЕНИЙ:")
        print("=" * 70)
        print("1. 📱 Создайте бота через @BotFather в Telegram")
        print("   • Отправьте /newbot")
        print("   • Введите имя бота (например: 'Теннис Монитор')")
        print("   • Введите username (например: 'tennis_monitor_bot')")
        print("   • Скопируйте токен бота")
        print()
        print("2. 🆔 Получите Chat ID через @userinfobot")
        print("   • Отправьте любое сообщение боту")
        print("   • Скопируйте ваш Chat ID")
        print()
        print("3. ⚙️ Создайте файл telegram_config.json:")
        print('   {"bot_token": "ваш_токен", "chat_id": "ваш_chat_id"}')
        print()
        print("4. 🚀 Запустите уведомления:")
        print("   python send_telegram_notification.py")
        print("   Выберите опцию 1 для отправки уведомления")
        print()
        print("5. 📋 Для автоматических уведомлений добавьте в crontab:")
        print("   30 21 * * * cd /root/tennis-monitor && python send_telegram_notification.py <<< '1'")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")


if __name__ == "__main__":
    final_demo()
