#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализатор свободных кортов на неделю
"""

import requests
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeeklyTennisAnalyzer:
    def __init__(self):
        self.base_url = "https://x19.spb.ru"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_api_data(self, date: str) -> Optional[Dict]:
        """Получает данные от API для конкретной даты"""
        try:
            # Получаем HTML страницу для timestamp
            page_url = f"{self.base_url}/bronirovanie/?date={date}"
            page_response = self.session.get(page_url, timeout=10)
            page_response.raise_for_status()
            
            # Извлекаем timestamp
            timestamp_match = re.search(r'initialize\?date=[^&]+&_=(\d+)', page_response.text)
            timestamp = timestamp_match.group(1) if timestamp_match else str(int(datetime.now().timestamp()))
            
            # Запрашиваем данные API
            api_url = f"{self.base_url}/bronirovanie/initialize?date={date}&_={timestamp}"
            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()
            
            # Парсим JavaScript код
            content = response.text
            initial_match = re.search(r'var initial = ({.*?});', content, re.DOTALL)
            
            if initial_match:
                json_str = initial_match.group(1)
                data = json.loads(json_str)
                return data
            
            return None
                
        except Exception as e:
            logger.error(f"Ошибка при получении данных для даты {date}: {e}")
            return None
    
    def analyze_ground_courts_22h(self, date: str) -> List[Dict]:
        """
        Анализирует свободные грунтовые корты в 22:00-00:00 (2 часа) для конкретной даты
        """
        print(f"🔍 Анализ грунтовых кортов в 22:00-00:00 на {date}")
        
        # Получаем данные от API
        data = self.get_api_data(date)
        if not data:
            print(f"❌ Не удалось получить данные для {date}")
            return []
        
        # Извлекаем информацию о кортах
        instructions = data.get('instructions', {})
        set_data = instructions.get('set', {})
        
        # Получаем грунтовые корты
        court_types = set_data.get('court_types', [])
        ground_courts = []
        
        for court_type in court_types:
            if court_type.get('name') == 'Грунт':
                courts = court_type.get('courts', [])
                for court in courts:
                    ground_courts.append({
                        'court_id': court.get('id'),
                        'court_number': court.get('number'),
                        'court_type': 'Грунт'
                    })
        
        print(f"🏟️ Найдено {len(ground_courts)} грунтовых кортов")
        
        # Получаем занятые слоты
        occupied_slots = set_data.get('occupied', [])
        print(f"🚫 Найдено {len(occupied_slots)} занятых слотов")
        
        # Анализируем свободные 2-часовые слоты в 22:00-00:00
        free_courts = []
        
        for court in ground_courts:
            court_id = court['court_id']
            court_number = court['court_number']
            
            # Проверяем, свободен ли корт в 22:00-23:00 и 23:00-00:00
            slot_22_23_occupied = False
            slot_23_24_occupied = False
            
            for occupied in occupied_slots:
                if occupied.get('court_id') == court_id:
                    time_from = occupied.get('time_from', {})
                    if isinstance(time_from, dict):
                        hours = time_from.get('hours', '')
                        if hours == '22':
                            slot_22_23_occupied = True
                        elif hours == '23':
                            slot_23_24_occupied = True
                    elif isinstance(time_from, (int, str)):
                        time_str = str(time_from)
                        if time_str == '22':
                            slot_22_23_occupied = True
                        elif time_str == '23':
                            slot_23_24_occupied = True
            
            # Если оба слота свободны, то есть 2-часовой слот
            if not slot_22_23_occupied and not slot_23_24_occupied:
                free_courts.append({
                    'court_number': court_number,
                    'court_type': 'Грунт',
                    'time_display': '22:00-00:00',
                    'court_id': court_id
                })
        
        print(f"✅ Найдено {len(free_courts)} свободных 2-часовых слотов в 22:00-00:00")
        
        return free_courts
    
    def analyze_week(self, start_date: str = None) -> Dict[str, List[Dict]]:
        """
        Анализирует свободные корты на неделю
        """
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"📅 Анализ свободных грунтовых кортов на неделю с {start_date}")
        print("=" * 70)
        
        results = {}
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        
        for i in range(7):  # Анализируем 7 дней
            current_date = start_dt + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            date_display = current_date.strftime('%d.%m.%Y (%A)')
            
            print(f"\n📅 {date_display}")
            print("-" * 40)
            
            free_courts = self.analyze_ground_courts_22h(date_str)
            results[date_str] = {
                'date_display': date_display,
                'free_courts': free_courts
            }
            
            if free_courts:
                # Группируем по физическим кортам
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
                
                print(f"🏟️ Доступно {len(free_courts)} кортов:")
                for physical_court, court_numbers in court_groups.items():
                    print(f"  • {physical_court}: корты {', '.join(map(str, court_numbers))}")
            else:
                print("❌ Свободных 2-часовых слотов в 22:00-00:00 нет")
        
        return results
    
    def generate_weekly_report(self, results: Dict[str, List[Dict]]) -> str:
        """
        Генерирует отчет по свободным кортам на неделю
        """
        report = "🎾 ОТЧЕТ ПО СВОБОДНЫМ ГРУНТОВЫМ КОРТАМ НА НЕДЕЛЮ\n"
        report += "=" * 60 + "\n"
        report += "⏰ Время: 22:00-00:00 (2 часа)\n"
        report += "🏟️ Тип корта: Грунт\n\n"
        
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


def main():
    """Основная функция"""
    analyzer = WeeklyTennisAnalyzer()
    
    print("🎾 АНАЛИЗАТОР СВОБОДНЫХ КОРТОВ НА НЕДЕЛЮ")
    print("=" * 60)
    
    # Анализируем неделю начиная с сегодня
    results = analyzer.analyze_week()
    
    # Генерируем отчет
    report = analyzer.generate_weekly_report(results)
    print("\n" + report)
    
    # Сохраняем отчет в файл
    with open('weekly_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("💾 Отчет сохранен в файл: weekly_report.txt")


if __name__ == "__main__":
    main()
