#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Реальный анализатор свободных кортов на основе time_blocked данных
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

class RealTimeTennisAnalyzer:
    def __init__(self):
        self.base_url = "https://x19.spb.ru"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_real_api_data(self, date: str) -> Optional[Dict]:
        """Получает реальные данные от API"""
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
    
    def analyze_ground_courts_22h_real(self, date: str) -> List[Dict]:
        """
        Реально анализирует свободные грунтовые корты в 22:00-00:00 (2 часа)
        """
        print(f"🔍 Реальный анализ грунтовых кортов в 22:00-00:00 на {date}")
        
        # Получаем данные от API
        data = self.get_real_api_data(date)
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
        
        # Получаем ЗАНЯТЫЕ слоты из time_blocked
        time_blocked = set_data.get('time_blocked', [])
        print(f"🚫 Найдено {len(time_blocked)} занятых слотов в time_blocked")
        
        # Анализируем свободные 2-часовые слоты в 22:00-00:00
        free_courts = []
        
        for court in ground_courts:
            court_id = court['court_id']
            court_number = court['court_number']
            
            # Проверяем, свободен ли корт в 22:00-23:00 и 23:00-00:00
            slot_22_23_occupied = False
            slot_23_24_occupied = False
            
            for blocked in time_blocked:
                if blocked.get('court_id') == court_id:
                    time_from = blocked.get('time_from', {})
                    time_to = blocked.get('time_to', {})
                    
                    # Получаем часы начала и окончания
                    from_hours = time_from.get('hours', 0)
                    to_hours = time_to.get('hours', 0)
                    
                    # Проверяем пересечение с нашими слотами
                    # Слот 22:00-23:00 (hours 22-23)
                    if (from_hours <= 22 and to_hours > 22) or (from_hours < 23 and to_hours >= 23):
                        slot_22_23_occupied = True
                    
                    # Слот 23:00-00:00 (hours 23-0)
                    if (from_hours <= 23 and to_hours > 23) or (from_hours < 24 and to_hours >= 24):
                        slot_23_24_occupied = True
                    
                    # Также проверяем точные совпадения
                    if from_hours == 22:
                        slot_22_23_occupied = True
                    if from_hours == 23:
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
    
    def analyze_week_real(self, start_date: str = None) -> Dict[str, Dict]:
        """Реально анализирует свободные корты на неделю"""
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"📅 Реальный анализ свободных грунтовых кортов на неделю с {start_date}")
        print("=" * 70)
        print("⏰ Время: 22:00-00:00 (2 часа)")
        print("🏟️ Тип корта: Грунт")
        print("🔍 Данные из time_blocked API")
        print("=" * 70)
        
        results = {}
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        
        for i in range(7):  # Анализируем 7 дней
            current_date = start_dt + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            date_display = current_date.strftime('%d.%m.%Y (%A)')
            
            print(f"\n📅 {date_display}")
            print("-" * 40)
            
            free_courts = self.analyze_ground_courts_22h_real(date_str)
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
    
    def generate_real_weekly_report(self, results: Dict[str, Dict]) -> str:
        """Генерирует реальный отчет по свободным кортам на неделю"""
        report = "🎾 РЕАЛЬНЫЙ ОТЧЕТ ПО СВОБОДНЫМ ГРУНТОВЫМ КОРТАМ НА НЕДЕЛЮ\n"
        report += "=" * 60 + "\n"
        report += "⏰ Время: 22:00-00:00 (2 часа)\n"
        report += "🏟️ Тип корта: Грунт\n"
        report += "🔍 Данные получены из time_blocked API\n\n"
        
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
    analyzer = RealTimeTennisAnalyzer()
    
    print("🎾 РЕАЛЬНЫЙ АНАЛИЗАТОР СВОБОДНЫХ КОРТОВ")
    print("=" * 60)
    print("🔍 Используем данные time_blocked из API")
    print("🎯 Находим свободные 2-часовые слоты в 22:00-00:00")
    print("=" * 60)
    
    # Анализируем неделю начиная с сегодня
    results = analyzer.analyze_week_real()
    
    # Генерируем отчет
    report = analyzer.generate_real_weekly_report(results)
    print("\n" + report)
    
    # Сохраняем отчет в файл
    with open('real_weekly_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("💾 Отчет сохранен в файл: real_weekly_report.txt")


if __name__ == "__main__":
    main()
