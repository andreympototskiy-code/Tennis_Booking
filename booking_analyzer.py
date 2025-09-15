#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализатор процесса бронирования теннисных кортов
"""

import requests
import json
import time
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, parse_qs
import re

class BookingAnalyzer:
    def __init__(self):
        self.base_url = "https://x19.spb.ru"
        self.booking_url = "https://x19.spb.ru/bronirovanie/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
    def analyze_booking_page(self, date="2025-09-22"):
        """Анализ страницы бронирования"""
        print(f"🔍 Анализ страницы бронирования на {date}")
        
        url = f"{self.booking_url}?date={date}"
        print(f"📡 Загружаем: {url}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            print(f"✅ Страница загружена: {response.status_code}")
            print(f"📏 Размер страницы: {len(response.text)} символов")
            
            # Сохраняем HTML для анализа
            filename = f"booking_page_{date.replace('-', '_')}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"💾 HTML сохранен в {filename}")
            
            return response.text
            
        except requests.RequestException as e:
            print(f"❌ Ошибка загрузки страницы: {e}")
            return None
    
    def find_booking_forms(self, html_content):
        """Поиск форм бронирования в HTML"""
        print("\n🔍 Поиск форм бронирования...")
        
        # Ищем формы
        form_patterns = [
            r'<form[^>]*>(.*?)</form>',
            r'<div[^>]*class="[^"]*form[^"]*"[^>]*>(.*?)</div>',
            r'<div[^>]*class="[^"]*booking[^"]*"[^>]*>(.*?)</div>',
        ]
        
        forms_found = []
        for pattern in form_patterns:
            matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
            if matches:
                forms_found.extend(matches)
        
        print(f"📋 Найдено {len(forms_found)} потенциальных форм")
        
        # Ищем кнопки бронирования
        booking_buttons = re.findall(
            r'<[^>]*(?:button|input|a)[^>]*(?:бронир|забронир|book)[^>]*>(.*?)</[^>]*>',
            html_content, re.DOTALL | re.IGNORECASE
        )
        
        print(f"🔘 Найдено {len(booking_buttons)} кнопок бронирования")
        
        # Ищем поля ввода
        input_fields = re.findall(
            r'<input[^>]*name="([^"]*)"[^>]*>',
            html_content, re.IGNORECASE
        )
        
        print(f"📝 Найдено {len(input_fields)} полей ввода:")
        for field in input_fields:
            print(f"  • {field}")
        
        return {
            'forms': forms_found,
            'buttons': booking_buttons,
            'inputs': input_fields
        }
    
    def find_api_endpoints(self, html_content):
        """Поиск API эндпоинтов для бронирования"""
        print("\n🔍 Поиск API эндпоинтов...")
        
        # Ищем JavaScript код с API вызовами
        api_patterns = [
            r'fetch\(["\']([^"\']+)["\']',
            r'axios\.[a-z]+\(["\']([^"\']+)["\']',
            r'\.post\(["\']([^"\']+)["\']',
            r'\.get\(["\']([^"\']+)["\']',
            r'url:\s*["\']([^"\']+)["\']',
            r'endpoint:\s*["\']([^"\']+)["\']',
        ]
        
        endpoints = set()
        for pattern in api_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            endpoints.update(matches)
        
        # Фильтруем только относительные URL
        booking_endpoints = []
        for endpoint in endpoints:
            if any(keyword in endpoint.lower() for keyword in ['book', 'reserv', 'order', 'pay']):
                booking_endpoints.append(endpoint)
        
        print(f"🎯 Найдено {len(booking_endpoints)} потенциальных эндпоинтов бронирования:")
        for endpoint in booking_endpoints:
            print(f"  • {endpoint}")
        
        return booking_endpoints
    
    def analyze_booking_flow(self, date="2025-09-22"):
        """Полный анализ процесса бронирования"""
        print(f"🎾 АНАЛИЗ ПРОЦЕССА БРОНИРОВАНИЯ")
        print("=" * 50)
        
        # 1. Загружаем страницу бронирования
        html_content = self.analyze_booking_page(date)
        if not html_content:
            return None
        
        # 2. Анализируем формы
        forms_data = self.find_booking_forms(html_content)
        
        # 3. Ищем API эндпоинты
        api_endpoints = self.find_api_endpoints(html_content)
        
        # 4. Ищем Vue.js компоненты
        vue_components = re.findall(
            r'<[^>]*v-[a-z-]+[^>]*>',
            html_content, re.IGNORECASE
        )
        print(f"\n⚡ Найдено {len(vue_components)} Vue.js директив")
        
        # 5. Ищем данные инициализации
        init_data_patterns = [
            r'window\.\$INITIAL\s*=\s*({.*?});',
            r'window\.\$DATA\s*=\s*({.*?});',
            r'window\.\$CONFIG\s*=\s*({.*?});',
        ]
        
        init_data = {}
        for pattern in init_data_patterns:
            matches = re.findall(pattern, html_content, re.DOTALL)
            if matches:
                try:
                    data = json.loads(matches[0])
                    init_data.update(data)
                    print(f"✅ Найдены данные инициализации")
                except json.JSONDecodeError:
                    print(f"⚠️ Не удалось распарсить данные инициализации")
        
        return {
            'html_content': html_content,
            'forms': forms_data,
            'api_endpoints': api_endpoints,
            'vue_components': vue_components,
            'init_data': init_data
        }
    
    def test_booking_endpoints(self, endpoints):
        """Тестирование найденных эндпоинтов"""
        print("\n🧪 Тестирование эндпоинтов...")
        
        for endpoint in endpoints:
            print(f"\n🔍 Тестируем: {endpoint}")
            
            # Пробуем GET запрос
            try:
                response = self.session.get(endpoint)
                print(f"  GET {response.status_code}: {len(response.text)} символов")
                
                # Если это JSON
                if 'application/json' in response.headers.get('content-type', ''):
                    try:
                        data = response.json()
                        print(f"  📊 JSON данные: {len(str(data))} символов")
                    except:
                        pass
                        
            except requests.RequestException as e:
                print(f"  ❌ GET ошибка: {e}")
            
            # Пробуем POST запрос
            try:
                test_data = {
                    'test': 'booking_analyzer',
                    'date': '2025-09-22',
                    'court_id': 1,
                    'time': '22:00'
                }
                response = self.session.post(endpoint, json=test_data)
                print(f"  POST {response.status_code}: {len(response.text)} символов")
                
            except requests.RequestException as e:
                print(f"  ❌ POST ошибка: {e}")

def main():
    analyzer = BookingAnalyzer()
    
    # Анализируем процесс бронирования
    booking_data = analyzer.analyze_booking_flow("2025-09-22")
    
    if booking_data:
        print("\n🎯 РЕЗУЛЬТАТЫ АНАЛИЗА:")
        print("=" * 50)
        print(f"📋 Формы: {len(booking_data['forms']['forms'])}")
        print(f"🔘 Кнопки: {len(booking_data['forms']['buttons'])}")
        print(f"📝 Поля ввода: {len(booking_data['forms']['inputs'])}")
        print(f"🎯 API эндпоинты: {len(booking_data['api_endpoints'])}")
        print(f"⚡ Vue компоненты: {len(booking_data['vue_components'])}")
        
        # Тестируем найденные эндпоинты
        if booking_data['api_endpoints']:
            analyzer.test_booking_endpoints(booking_data['api_endpoints'])
    
    print("\n✅ Анализ завершен!")

if __name__ == "__main__":
    main()
