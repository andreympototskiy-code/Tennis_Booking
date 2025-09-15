#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Монитор теннисного сайта через API endpoints
"""

import requests
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class APITennisMonitor:
    def __init__(self):
        self.base_url = "https://x19.spb.ru"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://x19.spb.ru/bronirovanie/'
        })
        
    def get_initialize_data(self, date: str) -> Optional[Dict]:
        """
        Получает данные инициализации для указанной даты
        
        Args:
            date: Дата в формате YYYY-MM-DD
            
        Returns:
            Словарь с данными или None при ошибке
        """
        try:
            # Сначала получаем HTML страницу, чтобы получить правильный timestamp
            page_url = f"{self.base_url}/bronirovanie/?date={date}"
            page_response = self.session.get(page_url, timeout=10)
            page_response.raise_for_status()
            
            # Извлекаем timestamp из JavaScript кода
            timestamp_match = re.search(r'initialize\?date=[^&]+&_=(\d+)', page_response.text)
            if not timestamp_match:
                logging.warning("Не удалось найти timestamp в HTML")
                timestamp = int(datetime.now().timestamp())
            else:
                timestamp = timestamp_match.group(1)
            
            # Запрашиваем данные инициализации
            init_url = f"{self.base_url}/bronirovanie/initialize?date={date}&_={timestamp}"
            logging.info(f"Запрос к API: {init_url}")
            
            response = self.session.get(init_url, timeout=10)
            response.raise_for_status()
            
            # Пытаемся распарсить как JSON
            try:
                data = response.json()
                logging.info(f"Успешно получены данные инициализации для даты {date}")
                return data
            except json.JSONDecodeError:
                # Если не JSON, возможно это JavaScript код
                content = response.text
                logging.info(f"Получен JavaScript код, длина: {len(content)}")
                
                # Сохраняем для анализа
                with open(f'api_response_{date}.js', 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return self._parse_javascript_data(content, date)
            
        except requests.RequestException as e:
            logging.error(f"Ошибка при запросе API для даты {date}: {e}")
            return None
    
    def _parse_javascript_data(self, js_content: str, date: str) -> Optional[Dict]:
        """
        Парсит JavaScript код и извлекает данные
        
        Args:
            js_content: JavaScript код
            date: Дата для логирования
            
        Returns:
            Словарь с данными или None
        """
        try:
            # Ищем переменную window.$INITIAL
            initial_match = re.search(r'window\.\$INITIAL\s*=\s*(\{.*?\});', js_content, re.DOTALL)
            if initial_match:
                initial_data = initial_match.group(1)
                logging.info("Найдены данные window.$INITIAL")
                
                # Сохраняем для анализа
                with open(f'initial_data_{date}.json', 'w', encoding='utf-8') as f:
                    f.write(initial_data)
                
                try:
                    data = json.loads(initial_data)
                    return data
                except json.JSONDecodeError as e:
                    logging.warning(f"Не удалось распарсить JSON: {e}")
                    return None
            
            # Ищем другие структуры данных
            time_map_match = re.search(r'time_map\s*:\s*(\[.*?\])', js_content, re.DOTALL)
            time_list_match = re.search(r'time_list\s*:\s*(\[.*?\])', js_content, re.DOTALL)
            
            if time_map_match or time_list_match:
                logging.info("Найдены данные time_map или time_list")
                return {
                    'time_map': json.loads(time_map_match.group(1)) if time_map_match else [],
                    'time_list': json.loads(time_list_match.group(1)) if time_list_match else []
                }
            
            logging.warning("Не удалось найти структурированные данные в JavaScript")
            return None
            
        except Exception as e:
            logging.error(f"Ошибка при парсинге JavaScript: {e}")
            return None
    
    def parse_available_slots_from_api(self, data: Dict, date: str) -> List[Dict]:
        """
        Извлекает информацию о свободных слотах из API данных
        
        Args:
            data: Данные от API
            date: Дата в формате YYYY-MM-DD
            
        Returns:
            Список свободных слотов
        """
        available_slots = []
        
        try:
            if not data:
                return available_slots
            
            # Анализируем структуру данных
            logging.info(f"Ключи в данных: {list(data.keys())}")
            
            # Ищем time_map и time_list
            time_map = data.get('time_map', [])
            time_list = data.get('time_list', [])
            
            if time_map and time_list:
                logging.info(f"Найдено {len(time_map)} типов кортов и {len(time_list)} временных слотов")
                
                for court_type_index, court_type in enumerate(time_map):
                    if isinstance(court_type, dict):
                        court_name = court_type.get('name', f'Корт {court_type_index + 1}')
                        logging.info(f"Обрабатываем корт: {court_name}")
                        
                        # Ищем свободные слоты для этого типа корта
                        for time_index, time_slot in enumerate(time_list):
                            if time_index % 2 == 0 and time_index + 1 < len(time_list):
                                time_from = time_slot.get('time_from', {})
                                time_to = time_list[time_index + 1].get('time_to', {})
                                
                                time_from_str = time_from.get('hours', '')
                                time_to_str = time_to.get('hours', '')
                                
                                if time_from_str and time_to_str:
                                    # Проверяем, свободен ли слот
                                    # Логика зависит от структуры данных
                                    is_available = self._check_slot_availability(data, court_type_index, time_index)
                                    
                                    if is_available:
                                        available_slots.append({
                                            'date': date,
                                            'time_from': time_from_str,
                                            'time_to': time_to_str,
                                            'court_name': court_name,
                                            'court_type_id': court_type.get('id'),
                                            'status': 'available'
                                        })
            
            # Альтернативный поиск по другим структурам
            if not available_slots:
                available_slots = self._parse_alternative_structures(data, date)
            
            logging.info(f"Найдено {len(available_slots)} свободных слотов для даты {date}")
            
        except Exception as e:
            logging.error(f"Ошибка при парсинге API данных для даты {date}: {e}")
        
        return available_slots
    
    def _check_slot_availability(self, data: Dict, court_type_index: int, time_index: int) -> bool:
        """
        Проверяет доступность конкретного слота
        
        Args:
            data: Данные от API
            court_type_index: Индекс типа корта
            time_index: Индекс времени
            
        Returns:
            True если слот свободен
        """
        try:
            # Ищем информацию о занятости в различных структурах
            # Это может быть в time_occupied, time_busy, time_available и т.д.
            
            occupied_data = data.get('time_occupied', [])
            if occupied_data and court_type_index < len(occupied_data):
                court_occupied = occupied_data[court_type_index]
                if time_index < len(court_occupied):
                    return not court_occupied[time_index]
            
            # Альтернативные проверки
            busy_data = data.get('time_busy', [])
            if busy_data and court_type_index < len(busy_data):
                court_busy = busy_data[court_type_index]
                if time_index < len(court_busy):
                    return not court_busy[time_index]
            
            # Если нет данных о занятости, считаем свободным
            return True
            
        except Exception as e:
            logging.warning(f"Ошибка при проверке доступности слота: {e}")
            return True
    
    def _parse_alternative_structures(self, data: Dict, date: str) -> List[Dict]:
        """
        Альтернативный парсинг данных
        
        Args:
            data: Данные от API
            date: Дата в формате YYYY-MM-DD
            
        Returns:
            Список свободных слотов
        """
        available_slots = []
        
        try:
            # Ищем любые структуры с временем
            for key, value in data.items():
                if isinstance(value, list) and 'time' in key.lower():
                    logging.info(f"Найдена временная структура: {key}")
                    
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            time_from = item.get('time_from', item.get('from', ''))
                            time_to = item.get('time_to', item.get('to', ''))
                            
                            if time_from and time_to:
                                available_slots.append({
                                    'date': date,
                                    'time_from': str(time_from),
                                    'time_to': str(time_to),
                                    'court_name': f'Слот {i+1}',
                                    'status': 'available',
                                    'source': key
                                })
            
        except Exception as e:
            logging.error(f"Ошибка при альтернативном парсинге: {e}")
        
        return available_slots
    
    def get_tomorrow_slots(self) -> List[Dict]:
        """
        Получает свободные слоты на завтра
        
        Returns:
            Список свободных слотов на завтра
        """
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_str = tomorrow.strftime('%Y-%m-%d')
        
        logging.info(f"Проверяем свободные слоты на завтра через API: {tomorrow_str}")
        
        data = self.get_initialize_data(tomorrow_str)
        if data:
            return self.parse_available_slots_from_api(data, tomorrow_str)
        
        return []
    
    def get_slots_for_date(self, date: str) -> List[Dict]:
        """
        Получает свободные слоты для указанной даты
        
        Args:
            date: Дата в формате YYYY-MM-DD
            
        Returns:
            Список свободных слотов для указанной даты
        """
        logging.info(f"Проверяем свободные слоты на дату через API: {date}")
        
        data = self.get_initialize_data(date)
        if data:
            return self.parse_available_slots_from_api(data, date)
        
        return []
    
    def print_available_slots(self, slots: List[Dict]):
        """
        Выводит найденные свободные слоты в консоль
        
        Args:
            slots: Список свободных слотов
        """
        if not slots:
            print("❌ Свободных слотов не найдено")
            return
        
        print(f"\n✅ Найдено {len(slots)} свободных слотов:")
        print("-" * 60)
        
        for slot in slots:
            print(f"📅 Дата: {slot['date']}")
            print(f"⏰ Время: {slot['time_from']} - {slot['time_to']}")
            print(f"🏟️  Корты: {slot['court_name']}")
            if 'source' in slot:
                print(f"📊 Источник: {slot['source']}")
            print("-" * 30)


def main():
    """Основная функция для тестирования API монитора"""
    monitor = APITennisMonitor()
    
    print("🎾 API Монитор теннисного сайта x19.spb.ru")
    print("=" * 50)
    
    # Проверяем завтрашние слоты
    print("\n1️⃣ Проверяем свободные слоты на завтра через API...")
    tomorrow_slots = monitor.get_tomorrow_slots()
    monitor.print_available_slots(tomorrow_slots)
    
    # Проверяем конкретную дату (16 сентября 2025)
    print("\n2️⃣ Проверяем свободные слоты на 16 сентября 2025 через API...")
    specific_date_slots = monitor.get_slots_for_date("2025-09-16")
    monitor.print_available_slots(specific_date_slots)


if __name__ == "__main__":
    main()
