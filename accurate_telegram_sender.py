#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Точная отправка уведомлений в Telegram о свободных грунтовых кортах завтра в 22:00
"""

import sys
import os
from datetime import datetime, timedelta

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from final_monitor import FinalTennisMonitor
from telegram_notifier import TelegramNotifier, get_telegram_config

def send_accurate_notification():
    """
    Отправляет точное уведомление о свободных грунтовых кортах завтра в 22:00
    """
    
    print("🎾 ТОЧНАЯ ОТПРАВКА УВЕДОМЛЕНИЯ О ГРУНТОВЫХ КОРТАХ")
    print("=" * 60)
    print("Проверяем актуальные данные и отправляем уведомление")
    print("=" * 60)
    
    # Получаем конфигурацию Telegram
    config = get_telegram_config()
    if not config:
        print("❌ Конфигурация Telegram не найдена!")
        return False
    
    # Инициализируем монитор и уведомления
    monitor = FinalTennisMonitor()
    notifier = TelegramNotifier(config['bot_token'], config['chat_id'])
    
    # Проверяем соединение с Telegram
    print("🔗 Проверка соединения с Telegram...")
    if not notifier.test_connection():
        print("❌ Ошибка соединения с Telegram!")
        return False
    
    print("✅ Соединение с Telegram установлено")
    
    # Получаем завтрашние слоты
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')
    
    print(f"📅 Проверяем свободные слоты на завтра: {tomorrow_str}")
    
    try:
        slots = monitor.get_tomorrow_slots()
        
        if not slots:
            print("❌ Свободных слотов на завтра не найдено")
            return False
        
        print(f"✅ Найдено {len(slots)} свободных слотов на завтра")
        
        # Фильтруем грунтовые корты в 22:00-23:00
        ground_slots_22h = []
        for slot in slots:
            if ('Грунт' in slot.get('court_type', '') and 
                slot.get('time_from') == 22 and 
                slot.get('time_to') == 23):
                ground_slots_22h.append(slot)
        
        print(f"🏟️ Грунтовые корты в 22:00-23:00: {len(ground_slots_22h)}")
        
        if ground_slots_22h:
            print("\n📋 Свободные грунтовые корты в 22:00-23:00:")
            for i, slot in enumerate(ground_slots_22h, 1):
                print(f"  {i}. Корт №{slot['court_number']} - {slot['court_type']}")
            
            # Отправляем уведомление
            print("\n📤 Отправка уведомления в Telegram...")
            
            success = notifier.send_tennis_slots_notification(
                slots=slots,
                date=tomorrow_str,
                court_type="Грунт",
                time_filter="22"
            )
            
            if success:
                print("✅ Уведомление успешно отправлено в Telegram!")
                print(f"📊 Отправлена информация о {len(ground_slots_22h)} свободных грунтовых кортах")
                return True
            else:
                print("❌ Ошибка отправки уведомления")
                return False
                
        else:
            print("❌ Свободных грунтовых кортов в 22:00-23:00 не найдено")
            
            # Показываем альтернативы
            print("\n🔍 АЛЬТЕРНАТИВЫ:")
            
            # Все грунтовые корты
            ground_slots = [slot for slot in slots if 'Грунт' in slot.get('court_type', '')]
            print(f"🏟️ Всего грунтовых кортов: {len(ground_slots)}")
            
            # Ближайшие вечерние времена
            evening_times = [20, 21, 23]
            print("\n🌅 Ближайшие вечерние времена:")
            for time_slot in evening_times:
                evening_slots = [slot for slot in ground_slots 
                               if slot.get('time_from') == time_slot]
                if evening_slots:
                    print(f"  ⏰ {time_slot}:00-{time_slot+1}:00 - {len(evening_slots)} грунтовых кортов")
            
            # Отправляем уведомление о том, что слотов нет
            message = f"❌ Свободных грунтовых кортов в 22:00-23:00 на {tomorrow_str} не найдено\n\n"
            message += "🔍 Доступные альтернативы:\n"
            for time_slot in evening_times:
                evening_slots = [slot for slot in ground_slots 
                               if slot.get('time_from') == time_slot]
                if evening_slots:
                    message += f"⏰ {time_slot}:00-{time_slot+1}:00 - {len(evening_slots)} кортов\n"
            
            message += "\n🔗 Проверить: https://x19.spb.ru/bronirovanie/"
            
            success = notifier.send_message(message)
            if success:
                print("✅ Уведомление об отсутствии слотов отправлено")
                return True
            else:
                print("❌ Ошибка отправки уведомления")
                return False
            
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        return False

def main():
    """Основная функция"""
    
    print("🎾 Точная отправка уведомлений о грунтовых кортах")
    print("=" * 50)
    
    while True:
        print("\nВыберите действие:")
        print("1. Отправить уведомление о грунтовых кортах завтра в 22:00")
        print("2. Проверить данные без отправки")
        print("3. Тест соединения с Telegram")
        print("4. Выход")
        
        choice = input("\nВведите номер (1-4): ").strip()
        
        if choice == "1":
            send_accurate_notification()
            
        elif choice == "2":
            # Проверка данных без отправки
            monitor = FinalTennisMonitor()
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
            print(f"\n🔍 Проверка данных на завтра: {tomorrow}")
            
            slots = monitor.get_tomorrow_slots()
            if slots:
                ground_slots_22h = [slot for slot in slots 
                                  if ('Грунт' in slot.get('court_type', '') and 
                                      slot.get('time_from') == 22 and 
                                      slot.get('time_to') == 23)]
                
                print(f"✅ Всего слотов: {len(slots)}")
                print(f"🏟️ Грунтовых кортов в 22:00-23:00: {len(ground_slots_22h)}")
                
                if ground_slots_22h:
                    print("\n📋 Свободные корты:")
                    for slot in ground_slots_22h:
                        print(f"  • Корт №{slot['court_number']}")
                else:
                    print("❌ Свободных грунтовых кортов в 22:00-23:00 не найдено")
            else:
                print("❌ Слоты не найдены")
                
        elif choice == "3":
            config = get_telegram_config()
            if config:
                notifier = TelegramNotifier(config['bot_token'], config['chat_id'])
                if notifier.test_connection():
                    print("✅ Соединение с Telegram работает")
                else:
                    print("❌ Ошибка соединения с Telegram")
            else:
                print("❌ Конфигурация Telegram не найдена")
                
        elif choice == "4":
            print("👋 До свидания!")
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
