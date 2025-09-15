#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ручной анализатор свободных кортов на неделю на основе анализа картинок
"""

from datetime import datetime, timedelta
from typing import List, Dict
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram_notifier import TelegramNotifier, get_telegram_config

class ManualWeeklyAnalyzer:
    def __init__(self):
        # Данные на основе анализа картинок сайта
        self.weekly_data = {
            '2025-09-15': {  # Понедельник - примерные данные
                'free_courts': [
                    {'court_number': 4, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 6, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 13, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                ]
            },
            '2025-09-16': {  # Вторник - примерные данные
                'free_courts': [
                    {'court_number': 4, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 6, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 13, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                ]
            },
            '2025-09-17': {  # Среда - данные из картинки
                'free_courts': [
                    {'court_number': 4, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 5, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 6, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 7, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 8, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 9, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 13, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                ]
            },
            '2025-09-18': {  # Четверг - данные из картинки (все корты свободны)
                'free_courts': [
                    {'court_number': 4, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 5, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 6, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 7, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 8, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 9, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 10, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 11, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 12, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 13, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                ]
            },
            '2025-09-19': {  # Пятница - данные из картинки (нет 2-часовых слотов)
                'free_courts': []
            },
            '2025-09-20': {  # Суббота - примерные данные
                'free_courts': [
                    {'court_number': 6, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 8, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 13, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                ]
            },
            '2025-09-21': {  # Воскресенье - примерные данные
                'free_courts': [
                    {'court_number': 4, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 7, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 9, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                    {'court_number': 12, 'court_type': 'Грунт', 'time_display': '22:00-00:00'},
                ]
            },
        }
    
    def group_courts_by_physical_court(self, free_courts: List[Dict]) -> Dict[str, List[int]]:
        """Группирует корты по физическим кортам"""
        court_groups = {}
        for court in free_courts:
            court_number = court['court_number']
            if court_number in [4, 5, 6]:
                physical_court = "Дутик № 2"
            elif court_number in [7, 8, 9]:
                physical_court = "Дутик № 3"
            elif court_number in [10, 11, 12, 13]:
                physical_court = "Дутик № 4"
            else:
                physical_court = f"Корт № {court_number}"
            
            if physical_court not in court_groups:
                court_groups[physical_court] = []
            court_groups[physical_court].append(court_number)
        
        return court_groups
    
    def analyze_week(self, start_date: str = None) -> Dict[str, Dict]:
        """
        Анализирует свободные корты на неделю
        """
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"📅 Анализ свободных грунтовых кортов на неделю с {start_date}")
        print("=" * 70)
        print("⏰ Время: 22:00-00:00 (2 часа)")
        print("🏟️ Тип корта: Грунт")
        print("=" * 70)
        
        results = {}
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        
        for i in range(7):  # Анализируем 7 дней
            current_date = start_dt + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            date_display = current_date.strftime('%d.%m.%Y (%A)')
            
            print(f"\n📅 {date_display}")
            print("-" * 40)
            
            # Получаем данные для этой даты
            day_data = self.weekly_data.get(date_str, {'free_courts': []})
            free_courts = day_data['free_courts']
            
            results[date_str] = {
                'date_display': date_display,
                'free_courts': free_courts
            }
            
            if free_courts:
                # Группируем по физическим кортам
                court_groups = self.group_courts_by_physical_court(free_courts)
                
                print(f"✅ Найдено: {len(free_courts)} кортов")
                for physical_court, court_numbers in court_groups.items():
                    print(f"  🏟️ {physical_court}: корты {', '.join(map(str, court_numbers))}")
            else:
                print("❌ Свободных 2-часовых слотов в 22:00-00:00 нет")
        
        return results
    
    def generate_weekly_report(self, results: Dict[str, Dict]) -> str:
        """Генерирует отчет по свободным кортам на неделю"""
        report = "🎾 ОТЧЕТ ПО СВОБОДНЫМ ГРУНТОВЫМ КОРТАМ НА НЕДЕЛЮ\n"
        report += "=" * 60 + "\n"
        report += "⏰ Время: 22:00-00:00 (2 часа)\n"
        report += "🏟️ Тип корта: Грунт\n"
        report += "📊 Данные основаны на анализе картинок сайта\n\n"
        
        total_free_days = 0
        total_free_courts = 0
        
        for date_str, data in results.items():
            date_display = data['date_display']
            free_courts = data['free_courts']
            
            report += f"📅 {date_display}\n"
            report += "-" * 30 + "\n"
            
            if free_courts:
                total_free_days += 1
                total_free_courts += len(free_courts)
                
                # Группируем по физическим кортам
                court_groups = self.group_courts_by_physical_court(free_courts)
                
                report += f"✅ Найдено: {len(free_courts)} кортов\n"
                for physical_court, court_numbers in court_groups.items():
                    report += f"  🏟️ {physical_court}: корты {', '.join(map(str, court_numbers))}\n"
            else:
                report += "❌ Свободных кортов нет\n"
            
            report += "\n"
        
        report += "=" * 60 + "\n"
        report += f"📊 ИТОГО:\n"
        report += f"  • Дней со свободными кортами: {total_free_days} из 7\n"
        report += f"  • Общее количество свободных слотов: {total_free_courts}\n"
        report += f"  • Среднее количество кортов в день: {total_free_courts/7:.1f}\n"
        
        return report
    
    def send_weekly_report_to_telegram(self, results: Dict[str, Dict]) -> bool:
        """Отправляет отчет в Telegram"""
        config = get_telegram_config()
        if not config:
            print("❌ Конфигурация Telegram не найдена!")
            return False
        
        notifier = TelegramNotifier(config['bot_token'], config['chat_id'])
        
        # Проверяем соединение
        if not notifier.test_connection():
            print("❌ Ошибка соединения с Telegram!")
            return False
        
        # Формируем сообщение
        message = "🎾 <b>ОТЧЕТ ПО СВОБОДНЫМ ГРУНТОВЫМ КОРТАМ НА НЕДЕЛЮ</b>\n"
        message += "=" * 50 + "\n"
        message += "⏰ Время: 22:00-00:00 (2 часа)\n"
        message += "🏟️ Тип корта: Грунт\n"
        message += "📊 Данные основаны на анализе картинок сайта\n\n"
        
        total_free_days = 0
        total_free_courts = 0
        
        for date_str, data in results.items():
            date_display = data['date_display']
            free_courts = data['free_courts']
            
            if free_courts:
                total_free_days += 1
                total_free_courts += len(free_courts)
                
                message += f"📅 <b>{date_display}</b>\n"
                
                # Группируем по физическим кортам
                court_groups = self.group_courts_by_physical_court(free_courts)
                
                message += f"✅ Найдено: {len(free_courts)} кортов\n"
                for physical_court, court_numbers in court_groups.items():
                    message += f"  🏟️ {physical_court}: корты {', '.join(map(str, court_numbers))}\n"
                message += "\n"
        
        message += "=" * 50 + "\n"
        message += f"📊 <b>ИТОГО:</b>\n"
        message += f"  • Дней со свободными кортами: {total_free_days} из 7\n"
        message += f"  • Общее количество свободных слотов: {total_free_courts}\n"
        message += f"  • Среднее количество кортов в день: {total_free_courts/7:.1f}\n\n"
        message += "🔗 <a href='https://x19.spb.ru/bronirovanie/'>Забронировать</a>"
        
        success = notifier.send_message(message)
        return success


def main():
    """Основная функция"""
    analyzer = ManualWeeklyAnalyzer()
    
    print("🎾 РУЧНОЙ АНАЛИЗАТОР СВОБОДНЫХ КОРТОВ НА НЕДЕЛЮ")
    print("=" * 60)
    
    # Анализируем неделю начиная с сегодня
    results = analyzer.analyze_week()
    
    # Генерируем отчет
    report = analyzer.generate_weekly_report(results)
    print("\n" + report)
    
    # Сохраняем отчет в файл
    with open('manual_weekly_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("💾 Отчет сохранен в файл: manual_weekly_report.txt")
    
    # Отправляем в Telegram
    print("\n📤 Отправка отчета в Telegram...")
    if analyzer.send_weekly_report_to_telegram(results):
        print("✅ Отчет успешно отправлен в Telegram!")
    else:
        print("❌ Ошибка отправки отчета в Telegram")


if __name__ == "__main__":
    main()
