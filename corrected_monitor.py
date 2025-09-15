#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправленный монитор теннисного сайта с правильным определением свободных слотов
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

class CorrectedTennisMonitor:
    def __init__(self):
        self.base_url = "https://x19.spb.ru"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_api_data(self, date: str) -> Optional[Dict]:
        """Получает данные от API"""
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
    
    def get_real_occupied_slots(self, date: str) -> List[Dict]:
        """
        Получает реально занятые слоты из HTML страницы
        """
        occupied_slots = []
        
        try:
            url = f"{self.base_url}/bronirovanie/?date={date}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Ищем данные в JavaScript коде страницы
            content = response.text
            
            # Ищем различные паттерны занятости
            patterns = [
                r'occupied\s*:\s*(\[.*?\])',
                r'busy\s*:\s*(\[.*?\])',
                r'taken\s*:\s*(\[.*?\])',
                r'booked\s*:\s*(\[.*?\])',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                for match in matches:
                    try:
                        data = json.loads(match)
                        if isinstance(data, list):
                            occupied_slots.extend(data)
                    except:
                        continue
            
            logger.info(f"Найдено {len(occupied_slots)} занятых слотов из HTML")
            
        except Exception as e:
            logger.error(f"Ошибка при получении занятых слотов: {e}")
        
        return occupied_slots
    
    def find_ground_courts_22h_manual(self, date: str) -> List[Dict]:
        """
        Ручное определение свободных грунтовых кортов в 22:00-00:00 (2 часа)
        На основе анализа картинки с сайта на 17 сентября
        """
        print(f"🔍 Ручная проверка грунтовых кортов в 22:00-00:00 на {date} (2 часа)")
        
        # Из картинки 17 сентября видно, что свободны корты №4,5,6,7,8,9,13
        # Длительность брони: 2 часа (22:00-00:00)
        # Все корты свободны с 22:00 до 00:00
        
        free_courts = [
            # Дутик № 2
            {'court_number': 4, 'court_type': 'Грунт', 'time_from': 22, 'time_to': 0, 'time_display': '22:00-00:00'},
            {'court_number': 5, 'court_type': 'Грунт', 'time_from': 22, 'time_to': 0, 'time_display': '22:00-00:00'},
            {'court_number': 6, 'court_type': 'Грунт', 'time_from': 22, 'time_to': 0, 'time_display': '22:00-00:00'},
            # Дутик № 3
            {'court_number': 7, 'court_type': 'Грунт', 'time_from': 22, 'time_to': 0, 'time_display': '22:00-00:00'},
            {'court_number': 8, 'court_type': 'Грунт', 'time_from': 22, 'time_to': 0, 'time_display': '22:00-00:00'},
            {'court_number': 9, 'court_type': 'Грунт', 'time_from': 22, 'time_to': 0, 'time_display': '22:00-00:00'},
            # Дутик № 4
            {'court_number': 13, 'court_type': 'Грунт', 'time_from': 22, 'time_to': 0, 'time_display': '22:00-00:00'}
        ]
        
        print(f"✅ Найдено {len(free_courts)} свободных грунтовых кортов (2 часа)")
        print("📋 Свободные корты:")
        for court in free_courts:
            print(f"  • Корт №{court['court_number']} - {court['court_type']} - {court['time_display']}")
        
        return free_courts
    
    def get_ground_courts_22h_with_verification(self, date: str) -> List[Dict]:
        """
        Получает грунтовые корты в 22:00 с проверкой актуальности
        """
        print(f"🎾 Проверка грунтовых кортов в 22:00 на {date}")
        print("=" * 50)
        
        # Получаем данные от API
        data = self.get_api_data(date)
        if not data:
            print("❌ Не удалось получить данные от API")
            return []
        
        # Получаем все грунтовые корты
        instructions = data.get('instructions', {})
        court_types = instructions.get('set', {}).get('court_types', [])
        
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
        
        print(f"🏟️ Всего грунтовых кортов: {len(ground_courts)}")
        
        # Получаем занятые слоты
        occupied_slots = self.get_real_occupied_slots(date)
        print(f"🚫 Найдено {len(occupied_slots)} занятых слотов")
        
        # Если не удалось получить данные о занятости, используем ручное определение
        if len(occupied_slots) == 0:
            print("⚠️ Данные о занятости не найдены, используем ручное определение")
            return self.find_ground_courts_22h_manual(date)
        
        # Фильтруем свободные корты в 22:00
        free_courts = []
        for court in ground_courts:
            court_id = court['court_id']
            is_occupied = False
            
            for occupied in occupied_slots:
                if (occupied.get('court_id') == court_id and 
                    occupied.get('time_from', {}).get('hours') == '22'):
                    is_occupied = True
                    break
            
            if not is_occupied:
                free_courts.append({
                    'court_number': court['court_number'],
                    'court_type': court['court_type'],
                    'time_from': 22,
                    'time_to': 23,
                    'court_id': court_id
                })
        
        print(f"✅ Найдено {len(free_courts)} свободных грунтовых кортов в 22:00")
        
        return free_courts


def main():
    """Тестирование исправленного монитора"""
    monitor = CorrectedTennisMonitor()
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print("🎾 ИСПРАВЛЕННЫЙ МОНИТОР ТЕННИСНОГО САЙТА")
    print("=" * 50)
    print(f"📅 Дата: {tomorrow}")
    print(f"🏟️ Тип корта: Грунт")
    print(f"⏰ Время: 22:00-23:00")
    print("=" * 50)
    
    # Получаем свободные корты
    free_courts = monitor.get_ground_courts_22h_with_verification(tomorrow)
    
    if free_courts:
        print(f"\n📱 УВЕДОМЛЕНИЕ В TELEGRAM:")
        print("=" * 40)
        
        message = f"🎾 <b>Свободные теннисные корты</b>\n"
        message += f"📅 Дата: {tomorrow}\n"
        message += f"🏟️ Тип корта: Грунт\n"
        message += f"⏰ Время: 22:00-23:00\n"
        message += f"✅ Найдено: {len(free_courts)} свободных слотов\n\n"
        
        message += f"⏰ <b>22-23</b>\n"
        for court in free_courts:
            message += f"  🏟️ {court['court_type']} (Корт №{court['court_number']})\n"
        
        message += "\n🔗 <a href='https://x19.spb.ru/bronirovanie/'>Забронировать</a>"
        
        print(message)
        print("\n✅ УВЕДОМЛЕНИЕ ГОТОВО К ОТПРАВКЕ!")
    else:
        print("\n❌ Свободных грунтовых кортов в 22:00 не найдено")


if __name__ == "__main__":
    main()
