#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный API анализатор с расширенным парсингом данных
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

class FinalAPIAnalyzer:
    def __init__(self):
        self.base_url = "https://x19.spb.ru"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_enhanced_api_data(self, date: str) -> Optional[Dict]:
        """Получает расширенные данные от API с дополнительным парсингом"""
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
                
                # Дополнительный анализ данных
                enhanced_data = self.enhance_api_data(data, date)
                return enhanced_data
            
            return None
                
        except Exception as e:
            logger.error(f"Ошибка при получении данных для даты {date}: {e}")
            return None
    
    def enhance_api_data(self, data: Dict, date: str) -> Dict:
        """Усиливает данные API дополнительным анализом"""
        enhanced = data.copy()
        
        # Анализируем структуру данных
        instructions = data.get('instructions', {})
        set_data = instructions.get('set', {})
        
        print(f"🔍 Анализ структуры данных для {date}")
        print(f"  • Инструкции: {list(instructions.keys())}")
        print(f"  • Набор данных: {list(set_data.keys())}")
        
        # Ищем все возможные поля с данными о занятости
        occupied_fields = []
        for key, value in set_data.items():
            if any(word in key.lower() for word in ['occupied', 'busy', 'taken', 'booked', 'reserved', 'schedule']):
                occupied_fields.append({
                    'field': key,
                    'type': type(value).__name__,
                    'length': len(value) if isinstance(value, (list, dict)) else 1,
                    'value': value
                })
        
        enhanced['occupied_fields'] = occupied_fields
        
        # Анализируем типы кортов
        court_types = set_data.get('court_types', [])
        enhanced['court_analysis'] = {
            'total_court_types': len(court_types),
            'court_types_info': []
        }
        
        for court_type in court_types:
            court_info = {
                'name': court_type.get('name'),
                'courts_count': len(court_type.get('courts', [])),
                'courts': court_type.get('courts', [])
            }
            enhanced['court_analysis']['court_types_info'].append(court_info)
        
        # Ищем данные о времени
        time_fields = []
        for key, value in set_data.items():
            if any(word in key.lower() for word in ['time', 'hour', 'schedule', 'slot']):
                time_fields.append({
                    'field': key,
                    'type': type(value).__name__,
                    'value': value
                })
        
        enhanced['time_fields'] = time_fields
        
        return enhanced
    
    def analyze_ground_courts_from_api(self, date: str) -> List[Dict]:
        """Анализирует грунтовые корты на основе API данных"""
        data = self.get_enhanced_api_data(date)
        if not data:
            return []
        
        # Получаем грунтовые корты
        instructions = data.get('instructions', {})
        set_data = instructions.get('set', {})
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
        
        # Анализируем занятые слоты - ищем во всех возможных полях
        occupied_slots = []
        occupied_fields = data.get('occupied_fields', [])
        
        for field_info in occupied_fields:
            field_value = field_info['value']
            if isinstance(field_value, list):
                occupied_slots.extend(field_value)
            elif isinstance(field_value, dict):
                occupied_slots.append(field_value)
        
        print(f"🚫 Найдено {len(occupied_slots)} занятых слотов во всех полях")
        
        # Сохраняем детальную информацию для анализа
        analysis_file = f'detailed_analysis_{date}.json'
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump({
                'date': date,
                'ground_courts': ground_courts,
                'occupied_slots': occupied_slots,
                'occupied_fields': occupied_fields,
                'time_fields': data.get('time_fields', []),
                'court_analysis': data.get('court_analysis', {})
            }, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Детальный анализ сохранен в: {analysis_file}")
        
        # Пока что возвращаем пустой список, так как нужно проанализировать структуру
        return []
    
    def analyze_week_final(self, start_date: str = None) -> Dict[str, Dict]:
        """Финальный анализ недели"""
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"📅 Финальный анализ свободных кортов на неделю с {start_date}")
        print("=" * 70)
        
        results = {}
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        
        for i in range(7):  # Анализируем 7 дней
            current_date = start_dt + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            date_display = current_date.strftime('%d.%m.%Y (%A)')
            
            print(f"\n📅 {date_display}")
            print("-" * 40)
            
            free_courts = self.analyze_ground_courts_from_api(date_str)
            results[date_str] = {
                'date_display': date_display,
                'free_courts': free_courts
            }
        
        return results


def main():
    """Основная функция"""
    analyzer = FinalAPIAnalyzer()
    
    print("🎾 ФИНАЛЬНЫЙ API АНАЛИЗАТОР СВОБОДНЫХ КОРТОВ")
    print("=" * 60)
    print("🔍 Расширенный анализ API данных")
    print("=" * 60)
    
    # Анализируем несколько дней для детального изучения структуры
    test_dates = ['2025-09-17', '2025-09-18', '2025-09-19']
    
    for date in test_dates:
        print(f"\n🔍 Детальный анализ {date}")
        print("=" * 50)
        analyzer.analyze_ground_courts_from_api(date)
    
    print("\n✅ Анализ завершен. Проверьте файлы:")
    print("  • detailed_analysis_*.json - детальный анализ структуры данных")
    print("  • Изучите поля occupied_fields и time_fields для создания парсера")


if __name__ == "__main__":
    main()
