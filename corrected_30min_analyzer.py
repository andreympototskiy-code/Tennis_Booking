#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправленный анализатор с учетом 30-минутных ячеек
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

class Corrected30MinAnalyzer:
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
    
    def analyze_ground_courts_22h_corrected(self, date: str) -> List[Dict]:
        """
        Правильно анализирует свободные грунтовые корты с учетом 30-минутных ячеек
        """
        print(f"🔍 Исправленный анализ грунтовых кортов на {date}")
        print("📊 Учитываем 30-минутные ячейки")
        
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
        
        # Определяем 30-минутные слоты для 22:00-00:00
        # 22:00-22:30, 22:30-23:00, 23:00-23:30, 23:30-00:00
        target_slots = [
            {'start_hour': 22, 'start_min': 0, 'end_hour': 22, 'end_min': 30},   # 22:00-22:30
            {'start_hour': 22, 'start_min': 30, 'end_hour': 23, 'end_min': 0},   # 22:30-23:00
            {'start_hour': 23, 'start_min': 0, 'end_hour': 23, 'end_min': 30},   # 23:00-23:30
            {'start_hour': 23, 'start_min': 30, 'end_hour': 0, 'end_min': 0},    # 23:30-00:00
        ]
        
        free_courts = []
        
        for court in ground_courts:
            court_id = court['court_id']
            court_number = court['court_number']
            
            # Проверяем каждый 30-минутный слот
            slot_status = {}
            for i, slot in enumerate(target_slots):
                slot_name = f"{slot['start_hour']:02d}:{slot['start_min']:02d}-{slot['end_hour']:02d}:{slot['end_min']:02d}"
                slot_status[slot_name] = True  # По умолчанию свободен
                
                # Проверяем, не занят ли этот слот
                for blocked in time_blocked:
                    if blocked.get('court_id') == court_id:
                        time_from = blocked.get('time_from', {})
                        time_to = blocked.get('time_to', {})
                        
                        from_hours = time_from.get('hours', 0)
                        from_minutes = time_from.get('minutes', 0)
                        to_hours = time_to.get('hours', 0)
                        to_minutes = time_to.get('minutes', 0)
                        
                        # Проверяем пересечение с нашим слотом
                        if self.slots_overlap(
                            slot['start_hour'], slot['start_min'],
                            slot['end_hour'], slot['end_min'],
                            from_hours, from_minutes,
                            to_hours, to_minutes
                        ):
                            slot_status[slot_name] = False
                            break
            
            # Определяем доступные слоты
            available_slots = []
            
            # Проверяем полный 2-часовой слот (22:00-00:00)
            if all(slot_status.values()):
                available_slots.append('22:00-00:00')
            
            # Проверяем частичные слоты
            if slot_status['22:30-23:00'] and slot_status['23:00-23:30'] and slot_status['23:30-00:00']:
                available_slots.append('22:30-00:00')
            
            if slot_status['23:00-23:30'] and slot_status['23:30-00:00']:
                available_slots.append('23:00-00:00')
            
            if slot_status['23:30-00:00']:
                available_slots.append('23:30-00:00')
            
            # Добавляем корт, если есть доступные слоты
            if available_slots:
                # Выбираем самый длинный доступный слот
                best_slot = max(available_slots, key=lambda x: self.get_slot_duration(x))
                
                free_courts.append({
                    'court_number': court_number,
                    'court_type': 'Грунт',
                    'time_display': best_slot,
                    'court_id': court_id,
                    'all_available_slots': available_slots
                })
                
                print(f"  ✅ Корт №{court_number}: {best_slot} (доступны: {', '.join(available_slots)})")
            else:
                print(f"  ❌ Корт №{court_number}: занят")
        
        print(f"✅ Найдено {len(free_courts)} кортов с доступными слотами")
        
        return free_courts
    
    def slots_overlap(self, start1_h, start1_m, end1_h, end1_m, start2_h, start2_m, end2_h, end2_m):
        """Проверяет пересечение двух временных слотов"""
        # Конвертируем в минуты от начала дня
        start1_minutes = start1_h * 60 + start1_m
        end1_minutes = end1_h * 60 + end1_m
        start2_minutes = start2_h * 60 + start2_m
        end2_minutes = end2_h * 60 + end2_m
        
        # Обрабатываем случай с полуночью (00:00)
        if end1_minutes == 0:
            end1_minutes = 24 * 60  # 24:00
        if end2_minutes == 0:
            end2_minutes = 24 * 60  # 24:00
        
        # Проверяем пересечение
        return not (end1_minutes <= start2_minutes or end2_minutes <= start1_minutes)
    
    def get_slot_duration(self, slot_str: str) -> float:
        """Возвращает длительность слота в часах"""
        if slot_str == '22:00-00:00':
            return 2.0
        elif slot_str == '22:30-00:00':
            return 1.5
        elif slot_str == '23:00-00:00':
            return 1.0
        elif slot_str == '23:30-00:00':
            return 0.5
        else:
            return 0.0


def main():
    """Основная функция"""
    analyzer = Corrected30MinAnalyzer()
    
    print("🎾 ИСПРАВЛЕННЫЙ АНАЛИЗАТОР С 30-МИНУТНЫМИ ЯЧЕЙКАМИ")
    print("=" * 60)
    print("🔍 Правильно учитываем 30-минутные слоты")
    print("=" * 60)
    
    # Тестируем на 22 сентября
    date = '2025-09-22'
    date_display = '22.09.2025 (Воскресенье)'
    
    print(f"📅 Анализ свободных кортов на {date_display}")
    print("-" * 50)
    
    free_courts = analyzer.analyze_ground_courts_22h_corrected(date)
    
    if free_courts:
        print(f"\n✅ ИТОГО: {len(free_courts)} кортов с доступными слотами")
        
        # Группируем по физическим кортам
        court_groups = {}
        for court in free_courts:
            court_number = court['court_number']
            if court_number in [4, 5, 6]:
                physical_court = 'Дутик № 2'
            elif court_number in [7, 8, 9]:
                physical_court = 'Дутик № 3'
            elif court_number in [10, 11, 12, 13]:
                physical_court = 'Дутик № 4'
            else:
                physical_court = f'Корт № {court_number}'
            
            if physical_court not in court_groups:
                court_groups[physical_court] = []
            court_groups[physical_court].append(court)
        
        print("\n🏟️ Свободные корты:")
        for physical_court, courts in court_groups.items():
            print(f"\n{physical_court}:")
            for court in courts:
                print(f"  • Корт №{court['court_number']} - {court['time_display']}")
                if len(court['all_available_slots']) > 1:
                    print(f"    (также доступны: {', '.join(court['all_available_slots'][1:])})")
    else:
        print("\n❌ Свободных кортов нет")


if __name__ == "__main__":
    main()
