#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API анализатор для получения реальных данных о занятости кортов
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

class APITennisAnalyzer:
    def __init__(self):
        self.base_url = "https://x19.spb.ru"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_booking_api_data(self, date: str) -> Optional[Dict]:
        """Получает данные от API бронирования"""
        try:
            # Попробуем разные возможные API endpoints
            api_endpoints = [
                f"{self.base_url}/api/booking?date={date}",
                f"{self.base_url}/api/schedule?date={date}",
                f"{self.base_url}/api/courts?date={date}",
                f"{self.base_url}/bronirovanie/api?date={date}",
                f"{self.base_url}/api/bookings?date={date}",
            ]
            
            for endpoint in api_endpoints:
                try:
                    print(f"🔍 Пробуем API: {endpoint}")
                    response = self.session.get(endpoint, timeout=10)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            print(f"✅ Получены данные от API: {endpoint}")
                            return data
                        except json.JSONDecodeError:
                            print(f"⚠️ Ответ не JSON от: {endpoint}")
                            continue
                    else:
                        print(f"❌ HTTP {response.status_code} от: {endpoint}")
                        
                except Exception as e:
                    print(f"❌ Ошибка запроса к {endpoint}: {e}")
                    continue
            
            print("❌ Все API endpoints недоступны")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при получении API данных для даты {date}: {e}")
            return None
    
    def analyze_network_requests(self, date: str) -> Dict:
        """Анализирует сетевые запросы страницы"""
        try:
            url = f"{self.base_url}/bronirovanie/?date={date}"
            print(f"🔍 Анализ сетевых запросов для {date}")
            
            # Получаем HTML страницу
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Ищем возможные API endpoints в JavaScript коде
            api_patterns = [
                r'fetch\s*\(\s*[\'"`]([^\'"`]*api[^\'"`]*)[\'"`]',
                r'axios\.[get|post]\s*\(\s*[\'"`]([^\'"`]*api[^\'"`]*)[\'"`]',
                r'\.get\s*\(\s*[\'"`]([^\'"`]*api[^\'"`]*)[\'"`]',
                r'\.post\s*\(\s*[\'"`]([^\'"`]*api[^\'"`]*)[\'"`]',
                r'url\s*:\s*[\'"`]([^\'"`]*api[^\'"`]*)[\'"`]',
                r'endpoint\s*:\s*[\'"`]([^\'"`]*api[^\'"`]*)[\'"`]',
            ]
            
            found_endpoints = set()
            for pattern in api_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    if match.startswith('/'):
                        full_url = f"{self.base_url}{match}"
                    elif match.startswith('http'):
                        full_url = match
                    else:
                        full_url = f"{self.base_url}/{match}"
                    found_endpoints.add(full_url)
            
            print(f"🎯 Найдено {len(found_endpoints)} возможных API endpoints:")
            for endpoint in found_endpoints:
                print(f"  • {endpoint}")
            
            # Ищем данные в JavaScript переменных
            js_data_patterns = [
                r'var\s+(\w*data\w*)\s*=\s*(\{.*?\});',
                r'let\s+(\w*data\w*)\s*=\s*(\{.*?\});',
                r'const\s+(\w*data\w*)\s*=\s*(\{.*?\});',
                r'window\.(\w*data\w*)\s*=\s*(\{.*?\});',
            ]
            
            found_data = {}
            for pattern in js_data_patterns:
                matches = re.findall(pattern, html_content, re.DOTALL)
                for var_name, var_value in matches:
                    try:
                        # Пробуем распарсить как JSON
                        if var_value.strip().startswith('{'):
                            data = json.loads(var_value)
                            found_data[var_name] = data
                            print(f"✅ Найдены данные в переменной: {var_name}")
                    except:
                        continue
            
            return {
                'found_endpoints': list(found_endpoints),
                'found_data': found_data,
                'html_length': len(html_content)
            }
            
        except Exception as e:
            logger.error(f"Ошибка анализа сетевых запросов: {e}")
            return {}
    
    def test_api_endpoints(self, date: str, endpoints: List[str]) -> Dict:
        """Тестирует найденные API endpoints"""
        results = {}
        
        for endpoint in endpoints:
            try:
                # Заменяем плейсхолдеры на реальную дату
                test_url = endpoint.replace('{date}', date).replace('{DATE}', date)
                
                print(f"🧪 Тестируем: {test_url}")
                response = self.session.get(test_url, timeout=10)
                
                results[test_url] = {
                    'status_code': response.status_code,
                    'content_type': response.headers.get('content-type', ''),
                    'content_length': len(response.text),
                    'success': response.status_code == 200
                }
                
                if response.status_code == 200:
                    print(f"  ✅ HTTP {response.status_code}, {len(response.text)} байт")
                    
                    # Пробуем распарсить как JSON
                    try:
                        json_data = response.json()
                        results[test_url]['json_data'] = json_data
                        print(f"  📊 JSON данные получены, ключи: {list(json_data.keys()) if isinstance(json_data, dict) else 'не dict'}")
                    except:
                        print(f"  ⚠️ Не JSON данные")
                else:
                    print(f"  ❌ HTTP {response.status_code}")
                    
            except Exception as e:
                results[test_url] = {
                    'error': str(e),
                    'success': False
                }
                print(f"  ❌ Ошибка: {e}")
        
        return results
    
    def analyze_week_api(self, start_date: str = None) -> Dict[str, Dict]:
        """Анализирует неделю через API"""
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"📅 API анализ свободных кортов на неделю с {start_date}")
        print("=" * 70)
        
        results = {}
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        
        # Сначала анализируем сетевые запросы для первого дня
        first_date = start_dt.strftime('%Y-%m-%d')
        network_analysis = self.analyze_network_requests(first_date)
        
        print(f"\n🔍 Анализ сетевых запросов для {first_date}")
        print("-" * 50)
        print(f"📊 HTML длина: {network_analysis.get('html_length', 0)} символов")
        print(f"🎯 Найдено endpoints: {len(network_analysis.get('found_endpoints', []))}")
        print(f"📋 Найдено данных: {len(network_analysis.get('found_data', {}))}")
        
        # Тестируем найденные endpoints
        if network_analysis.get('found_endpoints'):
            print(f"\n🧪 Тестирование найденных endpoints:")
            print("-" * 50)
            endpoint_results = self.test_api_endpoints(first_date, network_analysis['found_endpoints'])
            
            # Сохраняем результаты
            with open(f'api_test_results_{first_date}.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'network_analysis': network_analysis,
                    'endpoint_results': endpoint_results
                }, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Результаты сохранены в: api_test_results_{first_date}.json")
        
        # Анализируем каждый день
        for i in range(3):  # Анализируем первые 3 дня
            current_date = start_dt + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            date_display = current_date.strftime('%d.%m.%Y (%A)')
            
            print(f"\n📅 {date_display}")
            print("-" * 40)
            
            # Получаем данные от API
            api_data = self.get_booking_api_data(date_str)
            
            results[date_str] = {
                'date_display': date_display,
                'api_data': api_data,
                'api_available': api_data is not None
            }
            
            if api_data:
                print(f"✅ API данные получены, ключи: {list(api_data.keys()) if isinstance(api_data, dict) else 'не dict'}")
            else:
                print("❌ API данные недоступны")
        
        return results


def main():
    """Основная функция"""
    analyzer = APITennisAnalyzer()
    
    print("🎾 API АНАЛИЗАТОР СВОБОДНЫХ КОРТОВ")
    print("=" * 60)
    print("🔍 Поиск API endpoints и анализ данных")
    print("=" * 60)
    
    # Анализируем неделю через API
    results = analyzer.analyze_week_api()
    
    print("\n✅ Анализ завершен. Результаты:")
    print("=" * 50)
    
    for date_str, data in results.items():
        print(f"\n📅 {data['date_display']}")
        print(f"  • API доступен: {'✅' if data['api_available'] else '❌'}")
        if data['api_data']:
            api_data = data['api_data']
            if isinstance(api_data, dict):
                print(f"  • Ключи данных: {list(api_data.keys())}")
            else:
                print(f"  • Тип данных: {type(api_data)}")
    
    print("\n📁 Проверьте файлы:")
    print("  • api_test_results_*.json - результаты тестирования API")


if __name__ == "__main__":
    main()
