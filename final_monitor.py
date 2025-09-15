#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный монитор теннисного сайта x19.spb.ru
Анализирует данные из API и находит свободные слоты
"""

import requests
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Tuple
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('final_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class FinalTennisMonitor:
    def __init__(self):
        self.base_url = "https://x19.spb.ru"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://x19.spb.ru/bronirovanie/'
        })
        
    def get_api_data(self, date: str) -> Optional[Dict]:
        """
        Получает данные от API для указанной даты
        
        Args:
            date: Дата в формате YYYY-MM-DD
            
        Returns:
            Словарь с данными или None при ошибке
        """
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
            logging.info(f"Запрос к API: {api_url}")
            
            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()
            
            # Парсим JavaScript код
            content = response.text
            initial_match = re.search(r'var initial = ({.*?});', content, re.DOTALL)
            
            if initial_match:
                json_str = initial_match.group(1)
                data = json.loads(json_str)
                logging.info(f"Успешно получены данные для даты {date}")
                return data
            else:
                logging.error("Не удалось найти данные initial в ответе API")
                return None
                
        except Exception as e:
            logging.error(f"Ошибка при получении данных для даты {date}: {e}")
            return None
    
    def extract_time_slots(self, data: Dict) -> List[Dict]:
        """
        Извлекает все возможные временные слоты из данных
        
        Args:
            data: Данные от API
            
        Returns:
            Список временных слотов
        """
        time_slots = []
        
        try:
            instructions = data.get('instructions', {})
            time_list = instructions.get('set', {}).get('time_list', [])
            
            for i in range(0, len(time_list), 2):
                if i + 1 < len(time_list):
                    time_from = time_list[i].get('time_from', {})
                    time_to = time_list[i + 1].get('time_to', {})
                    
                    if time_from and time_to:
                        time_slots.append({
                            'index': i,
                            'time_from': time_from.get('hours', ''),
                            'time_to': time_to.get('hours', ''),
                            'time_from_value': time_from.get('value', ''),
                            'time_to_value': time_to.get('value', '')
                        })
            
            logging.info(f"Извлечено {len(time_slots)} временных слотов")
            
        except Exception as e:
            logging.error(f"Ошибка при извлечении временных слотов: {e}")
        
        return time_slots
    
    def extract_court_types(self, data: Dict) -> Dict[int, Dict]:
        """
        Извлекает информацию о типах кортов
        
        Args:
            data: Данные от API
            
        Returns:
            Словарь с информацией о типах кортов
        """
        court_types = {}
        
        try:
            instructions = data.get('instructions', {})
            court_types_data = instructions.get('set', {}).get('court_types', [])
            
            for court_type in court_types_data:
                court_id = court_type.get('id')
                court_types[court_id] = {
                    'id': court_id,
                    'name': court_type.get('name', ''),
                    'short': court_type.get('short', ''),
                    'courts': court_type.get('courts', [])
                }
            
            logging.info(f"Извлечено {len(court_types)} типов кортов")
            
        except Exception as e:
            logging.error(f"Ошибка при извлечении типов кортов: {e}")
        
        return court_types
    
    def extract_occupied_slots(self, data: Dict) -> Set[Tuple[int, int]]:
        """
        Извлекает информацию о занятых слотах
        
        Args:
            data: Данные от API
            
        Returns:
            Множество кортежей (court_id, time_index) занятых слотов
        """
        occupied_slots = set()
        
        try:
            instructions = data.get('instructions', {})
            occupied_data = instructions.get('set', {}).get('occupied', [])
            
            for slot in occupied_data:
                court_id = slot.get('court_id')
                time_from = slot.get('time_from', {})
                
                # Находим индекс времени
                time_list = instructions.get('set', {}).get('time_list', [])
                time_value = time_from.get('value', '')
                
                for i, time_item in enumerate(time_list):
                    if time_item.get('time_from', {}).get('value') == time_value:
                        occupied_slots.add((court_id, i))
                        break
            
            logging.info(f"Найдено {len(occupied_slots)} занятых слотов")
            
        except Exception as e:
            logging.error(f"Ошибка при извлечении занятых слотов: {e}")
        
        return occupied_slots
    
    def find_available_slots(self, date: str) -> List[Dict]:
        """
        Находит все свободные слоты для указанной даты
        
        Args:
            date: Дата в формате YYYY-MM-DD
            
        Returns:
            Список свободных слотов
        """
        available_slots = []
        
        try:
            # Получаем данные от API
            data = self.get_api_data(date)
            if not data:
                return available_slots
            
            # Извлекаем компоненты
            time_slots = self.extract_time_slots(data)
            court_types = self.extract_court_types(data)
            occupied_slots = self.extract_occupied_slots(data)
            
            # Генерируем все возможные комбинации корт-время
            for court_type_id, court_type_info in court_types.items():
                for court in court_type_info['courts']:
                    court_id = court.get('id')
                    court_number = court.get('number', '')
                    
                    for time_slot in time_slots:
                        time_index = time_slot['index']
                        
                        # Проверяем, не занят ли слот
                        if (court_id, time_index) not in occupied_slots:
                            available_slots.append({
                                'date': date,
                                'court_id': court_id,
                                'court_number': court_number,
                                'court_type': court_type_info['name'],
                                'court_type_short': court_type_info['short'],
                                'time_from': time_slot['time_from'],
                                'time_to': time_slot['time_to'],
                                'time_from_value': time_slot['time_from_value'],
                                'time_to_value': time_slot['time_to_value'],
                                'status': 'available'
                            })
            
            logging.info(f"Найдено {len(available_slots)} свободных слотов для даты {date}")
            
        except Exception as e:
            logging.error(f"Ошибка при поиске свободных слотов для даты {date}: {e}")
        
        return available_slots
    
    def get_tomorrow_slots(self) -> List[Dict]:
        """
        Получает свободные слоты на завтра
        
        Returns:
            Список свободных слотов на завтра
        """
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_str = tomorrow.strftime('%Y-%m-%d')
        
        logging.info(f"Проверяем свободные слоты на завтра: {tomorrow_str}")
        return self.find_available_slots(tomorrow_str)
    
    def get_slots_for_date(self, date: str) -> List[Dict]:
        """
        Получает свободные слоты для указанной даты
        
        Args:
            date: Дата в формате YYYY-MM-DD
            
        Returns:
            Список свободных слотов для указанной даты
        """
        logging.info(f"Проверяем свободные слоты на дату: {date}")
        return self.find_available_slots(date)
    
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
        print("=" * 80)
        
        # Группируем по времени
        slots_by_time = {}
        for slot in slots:
            time_key = f"{slot['time_from']} - {slot['time_to']}"
            if time_key not in slots_by_time:
                slots_by_time[time_key] = []
            slots_by_time[time_key].append(slot)
        
        for time_range, time_slots in sorted(slots_by_time.items()):
            print(f"\n⏰ {time_range}")
            print("-" * 40)
            
            for slot in time_slots:
                print(f"  🏟️  {slot['court_type']} (Корт №{slot['court_number']})")
        
        print("\n" + "=" * 80)
    
    def save_slots_to_file(self, slots: List[Dict], filename: str = None):
        """
        Сохраняет найденные слоты в файл
        
        Args:
            slots: Список слотов для сохранения
            filename: Имя файла (по умолчанию auto-generated)
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"available_slots_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(slots, f, ensure_ascii=False, indent=2)
            
            logging.info(f"Слоты сохранены в файл: {filename}")
            
        except Exception as e:
            logging.error(f"Ошибка при сохранении файла {filename}: {e}")


def main():
    """Основная функция для тестирования финального монитора"""
    monitor = FinalTennisMonitor()
    
    print("🎾 Финальный монитор теннисного сайта x19.spb.ru")
    print("=" * 60)
    
    # Проверяем завтрашние слоты
    print("\n1️⃣ Проверяем свободные слоты на завтра...")
    tomorrow_slots = monitor.get_tomorrow_slots()
    monitor.print_available_slots(tomorrow_slots)
    
    # Проверяем конкретную дату (16 сентября 2025)
    print("\n2️⃣ Проверяем свободные слоты на 16 сентября 2025...")
    specific_date_slots = monitor.get_slots_for_date("2025-09-16")
    monitor.print_available_slots(specific_date_slots)
    
    # Сохраняем результаты
    all_slots = tomorrow_slots + specific_date_slots
    if all_slots:
        monitor.save_slots_to_file(all_slots)


if __name__ == "__main__":
    main()
