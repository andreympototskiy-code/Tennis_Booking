#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Монитор теннисного сайта бронирования x19.spb.ru
Автоматически проверяет свободные слоты на указанную дату
"""

import requests
from bs4 import BeautifulSoup
import datetime
import time
import json
import re
from typing import List, Dict, Optional
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tennis_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class TennisMonitor:
    def __init__(self):
        self.base_url = "https://x19.spb.ru/bronirovanie/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_page_content(self, date: str) -> Optional[str]:
        """
        Получает содержимое страницы бронирования для указанной даты
        
        Args:
            date: Дата в формате YYYY-MM-DD
            
        Returns:
            HTML содержимое страницы или None при ошибке
        """
        try:
            url = f"{self.base_url}?date={date}"
            logging.info(f"Запрос к URL: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            logging.info(f"Успешно получена страница для даты {date}")
            return response.text
            
        except requests.RequestException as e:
            logging.error(f"Ошибка при запросе страницы для даты {date}: {e}")
            return None
    
    def parse_available_slots(self, html_content: str, date: str) -> List[Dict]:
        """
        Парсит HTML и извлекает информацию о свободных слотах
        
        Args:
            html_content: HTML содержимое страницы
            date: Дата в формате YYYY-MM-DD
            
        Returns:
            Список словарей с информацией о свободных слотах
        """
        available_slots = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Ищем элементы с временными слотами
            # Обычно свободные слоты имеют белый фон или специальный класс
            time_slots = soup.find_all(['div', 'span', 'td'], class_=re.compile(r'time|slot|free|available', re.I))
            
            # Альтернативный поиск по тексту времени
            if not time_slots:
                time_slots = soup.find_all(text=re.compile(r'\d{1,2}:\d{2}'))
            
            logging.info(f"Найдено {len(time_slots)} потенциальных временных слотов")
            
            for slot in time_slots:
                try:
                    # Извлекаем время из текста или атрибутов
                    time_text = slot.get_text(strip=True) if hasattr(slot, 'get_text') else str(slot).strip()
                    
                    # Проверяем, что это время в формате HH:MM
                    time_match = re.search(r'(\d{1,2}:\d{2})', time_text)
                    if time_match:
                        time_str = time_match.group(1)
                        
                        # Проверяем, свободен ли слот (белый фон или отсутствие класса "занято")
                        is_available = True
                        
                        # Проверяем классы родительского элемента
                        parent = slot.parent if hasattr(slot, 'parent') else slot
                        if parent and hasattr(parent, 'get'):
                            classes = parent.get('class', [])
                            if any('busy' in cls.lower() or 'occupied' in cls.lower() or 'taken' in cls.lower() for cls in classes):
                                is_available = False
                        
                        # Проверяем стили
                        if parent and hasattr(parent, 'get'):
                            style = parent.get('style', '')
                            if 'background-color: gray' in style.lower() or 'background: gray' in style.lower():
                                is_available = False
                        
                        if is_available:
                            available_slots.append({
                                'date': date,
                                'time': time_str,
                                'element_text': time_text,
                                'status': 'available'
                            })
                            
                except Exception as e:
                    logging.warning(f"Ошибка при обработке слота: {e}")
                    continue
            
            # Если не нашли слоты стандартным способом, попробуем найти по структуре таблицы
            if not available_slots:
                available_slots = self._parse_table_slots(soup, date)
            
            logging.info(f"Найдено {len(available_slots)} свободных слотов для даты {date}")
            
        except Exception as e:
            logging.error(f"Ошибка при парсинге HTML для даты {date}: {e}")
        
        return available_slots
    
    def _parse_table_slots(self, soup: BeautifulSoup, date: str) -> List[Dict]:
        """
        Альтернативный метод парсинга через поиск в таблицах
        """
        available_slots = []
        
        try:
            # Ищем таблицы с расписанием
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    
                    for cell in cells:
                        text = cell.get_text(strip=True)
                        
                        # Ищем время в формате HH:MM
                        time_match = re.search(r'(\d{1,2}:\d{2})', text)
                        if time_match:
                            time_str = time_match.group(1)
                            
                            # Проверяем, не занят ли слот
                            is_available = not any([
                                'занято' in text.lower(),
                                'busy' in text.lower(),
                                'taken' in text.lower()
                            ])
                            
                            # Проверяем стили ячейки
                            style = cell.get('style', '')
                            if 'background-color: gray' in style.lower():
                                is_available = False
                            
                            if is_available:
                                available_slots.append({
                                    'date': date,
                                    'time': time_str,
                                    'element_text': text,
                                    'status': 'available'
                                })
                                
        except Exception as e:
            logging.error(f"Ошибка при парсинге таблиц: {e}")
        
        return available_slots
    
    def get_tomorrow_slots(self) -> List[Dict]:
        """
        Получает свободные слоты на завтра
        
        Returns:
            Список свободных слотов на завтра
        """
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        tomorrow_str = tomorrow.strftime('%Y-%m-%d')
        
        logging.info(f"Проверяем свободные слоты на завтра: {tomorrow_str}")
        
        html_content = self.get_page_content(tomorrow_str)
        if html_content:
            return self.parse_available_slots(html_content, tomorrow_str)
        
        return []
    
    def get_slots_for_date(self, date: str) -> List[Dict]:
        """
        Получает свободные слоты для указанной даты
        
        Args:
            date: Дата в формате YYYY-MM-DD
            
        Returns:
            Список свободных слотов для указанной даты
        """
        logging.info(f"Проверяем свободные слоты на дату: {date}")
        
        html_content = self.get_page_content(date)
        if html_content:
            return self.parse_available_slots(html_content, date)
        
        return []
    
    def save_slots_to_file(self, slots: List[Dict], filename: str = None):
        """
        Сохраняет найденные слоты в файл
        
        Args:
            slots: Список слотов для сохранения
            filename: Имя файла (по умолчанию auto-generated)
        """
        if not filename:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"available_slots_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(slots, f, ensure_ascii=False, indent=2)
            
            logging.info(f"Слоты сохранены в файл: {filename}")
            
        except Exception as e:
            logging.error(f"Ошибка при сохранении файла {filename}: {e}")
    
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
        print("-" * 50)
        
        for slot in slots:
            print(f"📅 Дата: {slot['date']}")
            print(f"⏰ Время: {slot['time']}")
            print(f"📝 Информация: {slot['element_text']}")
            print("-" * 30)


def main():
    """Основная функция для тестирования монитора"""
    monitor = TennisMonitor()
    
    print("🎾 Монитор теннисного сайта x19.spb.ru")
    print("=" * 50)
    
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
