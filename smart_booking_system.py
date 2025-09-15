#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Умная система бронирования с отложенным планированием
"""

import sys
import os
import json
from datetime import datetime, timedelta
import time

# Добавляем текущую директорию в путь
sys.path.insert(0, '/root/tennis-monitor')

from corrected_30min_analyzer import Corrected30MinAnalyzer
from simple_auto_booking import SimpleAutoBooking

class SmartBookingSystem:
    def __init__(self):
        self.analyzer = Corrected30MinAnalyzer()
        self.booking = SimpleAutoBooking()
        self.booking_requests_file = "booking_requests.json"
        
    def load_booking_requests(self):
        """Загрузка отложенных запросов на бронирование"""
        try:
            if os.path.exists(self.booking_requests_file):
                with open(self.booking_requests_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Ошибка загрузки запросов: {e}")
        return []
    
    def save_booking_requests(self, requests):
        """Сохранение отложенных запросов"""
        try:
            with open(self.booking_requests_file, 'w', encoding='utf-8') as f:
                json.dump(requests, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения запросов: {e}")
    
    def add_booking_request(self, date, time_from, duration_hours, description=""):
        """Добавление нового запроса на бронирование"""
        requests = self.load_booking_requests()
        
        new_request = {
            'id': len(requests) + 1,
            'date': date,
            'time_from': time_from,
            'duration_hours': duration_hours,
            'description': description,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'last_check': None,
            'attempts': 0
        }
        
        requests.append(new_request)
        self.save_booking_requests(requests)
        
        print(f"✅ Запрос на бронирование добавлен:")
        print(f"  📅 Дата: {date}")
        print(f"  ⏰ Время: {time_from}:00-{(time_from + duration_hours) % 24}:00")
        print(f"  📝 Описание: {description}")
        
        return new_request['id']
    
    def is_date_available(self, date):
        """Проверка доступности даты (в пределах 7 дней)"""
        try:
            free_courts = self.analyzer.analyze_ground_courts_22h_corrected(date)
            return free_courts is not None and len(free_courts) > 0
        except:
            return False
    
    def process_booking_request(self, request):
        """Обработка запроса на бронирование"""
        date = request['date']
        time_from = request['time_from']
        duration_hours = request['duration_hours']
        
        print(f"\n🔍 Обработка запроса #{request['id']}: {date} в {time_from}:00")
        
        # Обновляем время последней проверки
        request['last_check'] = datetime.now().isoformat()
        request['attempts'] += 1
        
        # Проверяем доступность даты
        if not self.is_date_available(date):
            print(f"  ⏳ Дата {date} еще недоступна (больше 7 дней)")
            request['status'] = 'waiting'
            return False, "Дата недоступна"
        
        print(f"  ✅ Дата {date} доступна, ищем свободные корты...")
        
        # Ищем доступные корты
        free_courts = self.analyzer.analyze_ground_courts_22h_corrected(date)
        
        if not free_courts:
            print(f"  ❌ Свободных кортов не найдено")
            request['status'] = 'failed'
            return False, "Свободных кортов не найдено"
        
        # Ищем корт с нужной длительностью
        target_duration = f"{time_from:02d}:00-{(time_from + duration_hours) % 24:02d}:00"
        target_court = None
        
        for court in free_courts:
            if court['time_display'] == target_duration:
                target_court = court
                break
        
        if not target_court:
            print(f"  ⚠️ Корт с длительностью {target_duration} не найден")
            request['status'] = 'failed'
            return False, f"Корт с длительностью {target_duration} не найден"
        
        print(f"  🎯 Найден корт №{target_court['court_number']}")
        
        # Выполняем бронирование
        print(f"  🤖 Выполнение бронирования...")
        success, message = self.booking.auto_book_court(
            date=date,
            time_from=time_from,
            duration_hours=duration_hours,
            simulation=False  # Реальное бронирование
        )
        
        if success:
            print(f"  ✅ Бронирование успешно!")
            request['status'] = 'completed'
            request['result'] = message
            return True, message
        else:
            print(f"  ❌ Ошибка бронирования: {message}")
            request['status'] = 'failed'
            request['error'] = message
            return False, message
    
    def check_and_process_requests(self):
        """Проверка и обработка всех отложенных запросов"""
        requests = self.load_booking_requests()
        
        if not requests:
            print("📋 Отложенных запросов нет")
            return
        
        print(f"📋 Найдено {len(requests)} отложенных запросов")
        
        for request in requests:
            if request['status'] in ['pending', 'waiting']:
                success, message = self.process_booking_request(request)
                
                # Сохраняем обновленный запрос
                self.save_booking_requests(requests)
                
                if success:
                    print(f"🎉 Запрос #{request['id']} выполнен успешно!")
                else:
                    print(f"⚠️ Запрос #{request['id']}: {message}")
    
    def show_requests_status(self):
        """Показ статуса всех запросов"""
        requests = self.load_booking_requests()
        
        if not requests:
            print("📋 Запросов на бронирование нет")
            return
        
        print(f"📋 СТАТУС ЗАПРОСОВ НА БРОНИРОВАНИЕ ({len(requests)} шт.)")
        print("=" * 70)
        
        for request in requests:
            status_emoji = {
                'pending': '⏳',
                'waiting': '🕐', 
                'completed': '✅',
                'failed': '❌'
            }.get(request['status'], '❓')
            
            print(f"{status_emoji} #{request['id']} | {request['date']} | {request['time_from']}:00-{(request['time_from'] + request['duration_hours']) % 24}:00")
            print(f"    Статус: {request['status']} | Попыток: {request['attempts']}")
            
            if request['status'] == 'completed' and 'result' in request:
                print(f"    Результат: {request['result']}")
            elif request['status'] == 'failed' and 'error' in request:
                print(f"    Ошибка: {request['error']}")
            
            if request['last_check']:
                last_check = datetime.fromisoformat(request['last_check'])
                print(f"    Последняя проверка: {last_check.strftime('%d.%m.%Y %H:%M')}")
            
            print()

def main():
    """Главная функция"""
    print("🎾 УМНАЯ СИСТЕМА БРОНИРОВАНИЯ")
    print("=" * 50)
    
    system = SmartBookingSystem()
    
    while True:
        print("\n📋 МЕНЮ:")
        print("1. Добавить запрос на бронирование")
        print("2. Проверить и обработать запросы")
        print("3. Показать статус запросов")
        print("4. Выход")
        
        choice = input("\nВыберите действие (1-4): ").strip()
        
        if choice == '1':
            print("\n📅 ДОБАВЛЕНИЕ ЗАПРОСА НА БРОНИРОВАНИЕ")
            print("-" * 40)
            
            date = input("Дата (YYYY-MM-DD): ").strip()
            time_from = int(input("Время начала (час, 0-23): "))
            duration_hours = int(input("Длительность (часы): "))
            description = input("Описание (необязательно): ").strip()
            
            # Проверяем доступность даты
            if system.is_date_available(date):
                print(f"\n✅ Дата {date} доступна, выполняем бронирование...")
                # Создаем временный запрос для немедленного выполнения
                temp_request = {
                    'id': 0,
                    'date': date,
                    'time_from': time_from,
                    'duration_hours': duration_hours,
                    'description': description,
                    'status': 'pending',
                    'created_at': datetime.now().isoformat(),
                    'last_check': None,
                    'attempts': 0
                }
                success, message = system.process_booking_request(temp_request)
                if success:
                    print(f"🎉 Бронирование выполнено: {message}")
                else:
                    print(f"❌ Ошибка: {message}")
            else:
                print(f"\n⏳ Дата {date} недоступна (больше 7 дней)")
                request_id = system.add_booking_request(date, time_from, duration_hours, description)
                print(f"📝 Запрос добавлен с ID #{request_id}")
                print("🔄 Запрос будет обработан автоматически, когда дата станет доступна")
        
        elif choice == '2':
            print("\n🔄 ПРОВЕРКА И ОБРАБОТКА ЗАПРОСОВ")
            print("-" * 40)
            system.check_and_process_requests()
        
        elif choice == '3':
            system.show_requests_status()
        
        elif choice == '4':
            print("👋 До свидания!")
            break
        
        else:
            print("❌ Неверный выбор")

if __name__ == "__main__":
    main()
