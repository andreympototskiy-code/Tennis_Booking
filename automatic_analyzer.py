#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматический анализатор свободных кортов через HTML и CSS
"""

import requests
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from bs4 import BeautifulSoup

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomaticTennisAnalyzer:
    def __init__(self):
        self.base_url = "https://x19.spb.ru"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Цвет занятых мест
        self.occupied_color = "#d1d1d1"
        
    def get_html_page(self, date: str) -> Optional[str]:
        """Получает HTML страницу для конкретной даты"""
        try:
            url = f"{self.base_url}/bronirovanie/?date={date}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Ошибка при получении HTML для даты {date}: {e}")
            return None
    
    def parse_html_schedule(self, html_content: str, date: str) -> Dict:
        """
        Парсит HTML расписание и находит занятые места по CSS стилям
        """
        print(f"🔍 Парсинг HTML расписания для {date}")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Сохраняем HTML для отладки
        with open(f'html_schedule_{date}.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"💾 HTML сохранен в: html_schedule_{date}.html")
        
        # Ищем таблицу расписания
        schedule_table = soup.find('table') or soup.find('div', class_=re.compile(r'schedule|timetable|grid'))
        
        if not schedule_table:
            print("❌ Таблица расписания не найдена")
            return {}
        
        print("✅ Таблица расписания найдена")
        
        # Анализируем ячейки с занятыми местами
        occupied_cells = schedule_table.find_all(attrs={'style': re.compile(r'background\s*:\s*#d1d1d1')})
        
        print(f"🚫 Найдено {len(occupied_cells)} занятых ячеек по стилю background: #d1d1d1")
        
        # Также ищем через CSS классы
        occupied_by_class = schedule_table.find_all(class_=re.compile(r'occupied|busy|taken|booked'))
        print(f"🚫 Найдено {len(occupied_by_class)} занятых ячеек по CSS классам")
        
        # Анализируем структуру таблицы
        rows = schedule_table.find_all('tr')
        print(f"📊 Найдено {len(rows)} строк в таблице")
        
        # Ищем все ячейки с цветом фона
        all_colored_cells = schedule_table.find_all(attrs={'style': re.compile(r'background')})
        print(f"🎨 Найдено {len(all_colored_cells)} ячеек с цветом фона")
        
        # Анализируем первые несколько ячеек для понимания структуры
        for i, cell in enumerate(all_colored_cells[:5]):
            style = cell.get('style', '')
            class_attr = cell.get('class', [])
            print(f"  Ячейка {i+1}: style='{style}', class='{class_attr}'")
        
        return {
            'total_rows': len(rows),
            'occupied_by_style': len(occupied_cells),
            'occupied_by_class': len(occupied_by_class),
            'all_colored_cells': len(all_colored_cells),
            'schedule_found': True
        }
    
    def analyze_ground_courts_automatic(self, date: str) -> List[Dict]:
        """
        Автоматически анализирует свободные грунтовые корты в 22:00-00:00
        """
        html_content = self.get_html_page(date)
        if not html_content:
            return []
        
        # Парсим HTML
        schedule_data = self.parse_html_schedule(html_content, date)
        
        # Пока что возвращаем пустой список, так как нужно проанализировать структуру
        # В реальной реализации здесь будет логика определения свободных кортов
        return []
    
    def analyze_week_automatic(self, start_date: str = None) -> Dict[str, Dict]:
        """
        Автоматически анализирует свободные корты на неделю
        """
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"📅 Автоматический анализ свободных грунтовых кортов на неделю с {start_date}")
        print("=" * 70)
        
        results = {}
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        
        for i in range(7):  # Анализируем 7 дней
            current_date = start_dt + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            date_display = current_date.strftime('%d.%m.%Y (%A)')
            
            print(f"\n📅 {date_display}")
            print("-" * 40)
            
            free_courts = self.analyze_ground_courts_automatic(date_str)
            results[date_str] = {
                'date_display': date_display,
                'free_courts': free_courts,
                'schedule_data': self.parse_html_schedule(self.get_html_page(date_str), date_str) if self.get_html_page(date_str) else {}
            }
        
        return results


def main():
    """Основная функция"""
    analyzer = AutomaticTennisAnalyzer()
    
    print("🎾 АВТОМАТИЧЕСКИЙ АНАЛИЗАТОР СВОБОДНЫХ КОРТОВ")
    print("=" * 60)
    print("🔍 Поиск занятых мест по CSS: background: #d1d1d1;")
    print("=" * 60)
    
    # Анализируем несколько дней для изучения структуры
    test_dates = [
        '2025-09-17',  # Среда
        '2025-09-18',  # Четверг  
        '2025-09-19',  # Пятница
    ]
    
    for date in test_dates:
        print(f"\n🔍 Анализ {date}")
        print("=" * 40)
        analyzer.analyze_ground_courts_automatic(date)
    
    print("\n✅ Анализ завершен. Проверьте файлы:")
    print("  • html_schedule_*.html - HTML страницы расписания")
    print("  • Проанализируйте структуру таблицы для создания парсера")


if __name__ == "__main__":
    main()
