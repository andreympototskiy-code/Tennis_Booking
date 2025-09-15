#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML анализатор для получения реальных данных о занятости кортов
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

class HTMLTennisAnalyzer:
    def __init__(self):
        self.base_url = "https://x19.spb.ru"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_html_data(self, date: str) -> Optional[str]:
        """Получает HTML страницу для конкретной даты"""
        try:
            url = f"{self.base_url}/bronirovanie/?date={date}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Ошибка при получении HTML для даты {date}: {e}")
            return None
    
    def extract_booking_data_from_html(self, html_content: str, date: str) -> Dict:
        """
        Извлекает данные о бронировании из HTML
        """
        print(f"🔍 Анализ HTML страницы для {date}")
        
        # Ищем различные паттерны данных в HTML
        patterns = {
            'occupied': [
                r'occupied\s*:\s*(\[.*?\])',
                r'busy\s*:\s*(\[.*?\])',
                r'taken\s*:\s*(\[.*?\])',
                r'booked\s*:\s*(\[.*?\])',
            ],
            'courts': [
                r'courts\s*:\s*(\[.*?\])',
                r'courtTypes\s*:\s*(\[.*?\])',
                r'court_types\s*:\s*(\[.*?\])',
            ],
            'schedule': [
                r'schedule\s*:\s*(\{.*?\})',
                r'timetable\s*:\s*(\{.*?\})',
            ]
        }
        
        extracted_data = {}
        
        for data_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, html_content, re.DOTALL)
                for match in matches:
                    try:
                        data = json.loads(match)
                        if data_type not in extracted_data:
                            extracted_data[data_type] = []
                        if isinstance(data, list):
                            extracted_data[data_type].extend(data)
                        else:
                            extracted_data[data_type].append(data)
                    except:
                        continue
        
        # Также ищем данные в script тегах
        script_matches = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL)
        for script in script_matches:
            # Ищем данные о занятости в JavaScript коде
            js_patterns = [
                r'var\s+\w*occupied\w*\s*=\s*(\[.*?\]);',
                r'let\s+\w*occupied\w*\s*=\s*(\[.*?\]);',
                r'const\s+\w*occupied\w*\s*=\s*(\[.*?\]);',
            ]
            
            for pattern in js_patterns:
                matches = re.findall(pattern, script, re.DOTALL)
                for match in matches:
                    try:
                        data = json.loads(match)
                        if 'occupied' not in extracted_data:
                            extracted_data['occupied'] = []
                        if isinstance(data, list):
                            extracted_data['occupied'].extend(data)
                    except:
                        continue
        
        print(f"📊 Извлечено данных:")
        for key, value in extracted_data.items():
            print(f"  • {key}: {len(value)} элементов")
        
        return extracted_data
    
    def analyze_ground_courts_from_html(self, date: str) -> List[Dict]:
        """
        Анализирует свободные грунтовые корты в 22:00-00:00 из HTML
        """
        html_content = self.get_html_data(date)
        if not html_content:
            return []
        
        # Извлекаем данные
        extracted_data = self.extract_booking_data_from_html(html_content, date)
        
        # Сохраняем HTML для анализа
        with open(f'html_debug_{date}.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"💾 HTML сохранен в: html_debug_{date}.html")
        
        # Сохраняем извлеченные данные
        with open(f'extracted_data_{date}.json', 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=2)
        print(f"💾 Данные сохранены в: extracted_data_{date}.json")
        
        # Пока что возвращаем пустой список, так как нужно проанализировать структуру данных
        return []
    
    def analyze_week_from_html(self, start_date: str = None) -> Dict[str, List[Dict]]:
        """
        Анализирует свободные корты на неделю из HTML
        """
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"📅 Анализ HTML страниц на неделю с {start_date}")
        print("=" * 70)
        
        results = {}
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        
        for i in range(7):  # Анализируем 7 дней
            current_date = start_dt + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            date_display = current_date.strftime('%d.%m.%Y (%A)')
            
            print(f"\n📅 {date_display}")
            print("-" * 40)
            
            free_courts = self.analyze_ground_courts_from_html(date_str)
            results[date_str] = {
                'date_display': date_display,
                'free_courts': free_courts,
                'extracted_data': self.extract_booking_data_from_html(self.get_html_data(date_str), date_str) if self.get_html_data(date_str) else {}
            }
        
        return results


def main():
    """Основная функция"""
    analyzer = HTMLTennisAnalyzer()
    
    print("🎾 HTML АНАЛИЗАТОР СВОБОДНЫХ КОРТОВ")
    print("=" * 60)
    
    # Анализируем несколько дней для изучения структуры данных
    test_dates = [
        '2025-09-17',  # Среда - из картинки видно 7 свободных кортов
        '2025-09-18',  # Четверг - все корты свободны
        '2025-09-19',  # Пятница - нет 2-часовых слотов
    ]
    
    for date in test_dates:
        print(f"\n🔍 Анализ {date}")
        print("=" * 40)
        analyzer.analyze_ground_courts_from_html(date)
    
    print("\n✅ Анализ завершен. Проверьте файлы:")
    print("  • html_debug_*.html - HTML страницы")
    print("  • extracted_data_*.json - извлеченные данные")


if __name__ == "__main__":
    main()
