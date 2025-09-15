#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль автоматического бронирования теннисных кортов
"""

import requests
import json
import time
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse, parse_qs
import re
from typing import Dict, List, Optional, Tuple
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoBooking:
    def __init__(self):
        self.base_url = "https://x19.spb.ru"
        self.booking_url = "https://x19.spb.ru/bronirovanie"
        self.order_url = "https://x19.spb.ru/bronirovanie/order/add"
        
        # Данные пользователя
        self.user_data = {
            'name': 'Потоцкий Андрей',
            'phone': '+79313203496',
            'email': 'andrey.m.pototskiy@gmail.com',
            'payment_type': 'club'  # Оплата в клубе
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://x19.spb.ru/bronirovanie/'
        })
        
    def get_booking_page(self, date: str) -> Optional[str]:
        """Получение страницы бронирования"""
        url = f"{self.booking_url}/?date={date}"
        logger.info(f"Загружаем страницу бронирования: {url}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            logger.info(f"Страница загружена: {response.status_code}")
            return response.text
        except requests.RequestException as e:
            logger.error(f"Ошибка загрузки страницы: {e}")
            return None
    
    def extract_csrf_token(self, html_content: str) -> Optional[str]:
        """Извлечение CSRF токена из HTML"""
        # Ищем различные варианты CSRF токенов
        csrf_patterns = [
            r'<meta name="csrf-token" content="([^"]+)"',
            r'<input[^>]*name="[^"]*csrf[^"]*"[^>]*value="([^"]+)"',
            r'_token["\']?\s*:\s*["\']([^"]+)["\']',
            r'csrf["\']?\s*:\s*["\']([^"]+)["\']'
        ]
        
        for pattern in csrf_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                logger.info(f"Найден CSRF токен: {matches[0][:20]}...")
                return matches[0]
        
        logger.warning("CSRF токен не найден")
        return None
    
    def extract_booking_data(self, html_content: str) -> Dict:
        """Извлечение данных для бронирования из HTML"""
        logger.info("Извлечение данных для бронирования...")
        
        # Ищем данные инициализации
        init_data_pattern = r'window\.\$INITIAL\s*=\s*({.*?});'
        matches = re.findall(init_data_pattern, html_content, re.DOTALL)
        
        if matches:
            try:
                init_data = json.loads(matches[0])
                logger.info("Данные инициализации извлечены")
                return init_data
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка парсинга данных инициализации: {e}")
        
        return {}
    
    def find_available_court(self, date: str, court_type: str = 'ground', 
                           time_from: int = 22, duration_hours: int = 2) -> Optional[Dict]:
        """Поиск доступного корта для бронирования"""
        logger.info(f"Поиск доступного корта на {date} в {time_from}:00 ({duration_hours}ч)")
        
        # Получаем данные инициализации
        html_content = self.get_booking_page(date)
        if not html_content:
            return None
        
        init_data = self.extract_booking_data(html_content)
        if not init_data:
            return None
        
        # Ищем свободные корты
        courts = init_data.get('courts', [])
        time_blocked = init_data.get('time_blocked', [])
        
        # Фильтруем корты по типу
        ground_courts = [court for court in courts if 'грунт' in court.get('type', {}).get('name', '').lower()]
        
        if not ground_courts:
            logger.warning("Грунтовые корты не найдены")
            return None
        
        logger.info(f"Найдено {len(ground_courts)} грунтовых кортов")
        
        # Проверяем доступность каждого корта
        for court in ground_courts:
            court_id = court.get('id')
            court_number = court.get('number')
            
            if not court_id:
                continue
            
            # Проверяем, свободен ли корт в нужное время
            if self._is_court_available(court_id, time_from, duration_hours, time_blocked):
                logger.info(f"Найден свободный корт №{court_number} (ID: {court_id})")
                return {
                    'court_id': court_id,
                    'court_number': court_number,
                    'court_type': court.get('type', {}).get('name', 'Грунт'),
                    'time_from': time_from,
                    'time_to': (time_from + duration_hours) % 24,
                    'date': date
                }
        
        logger.warning("Свободных кортов не найдено")
        return None
    
    def _is_court_available(self, court_id: int, time_from: int, duration_hours: int, 
                          time_blocked: List[Dict]) -> bool:
        """Проверка доступности корта в указанное время"""
        # Преобразуем время в 30-минутные слоты
        start_slot = time_from * 2  # 22:00 = 44-й слот
        end_slot = start_slot + (duration_hours * 2)  # 2 часа = 4 слота
        
        # Проверяем блокировки для этого корта
        for blocked in time_blocked:
            if blocked.get('court_id') == court_id:
                blocked_time = blocked.get('time')
                if blocked_time and start_slot <= blocked_time < end_slot:
                    return False
        
        return True
    
    def prepare_booking_form_data(self, court_data: Dict) -> Dict:
        """Подготовка данных формы для бронирования"""
        logger.info("Подготовка данных формы бронирования...")
        
        # Формируем данные формы
        form_data = {
            'date': court_data['date'],
            'order[type_id]': '1',  # Тип бронирования (обычно 1)
            f'ordertime[0][court_id]': str(court_data['court_id']),
            f'ordertime[0][time_from]': str(court_data['time_from']),
            f'ordertime[0][time_to]': str(court_data['time_to']),
            # Данные пользователя
            'order[name]': self.user_data['name'],
            'order[phone]': self.user_data['phone'],
            'order[email]': self.user_data['email'],
            'order[payment_type]': self.user_data['payment_type']
        }
        
        logger.info(f"Данные формы подготовлены: {len(form_data)} полей")
        return form_data
    
    def submit_booking(self, court_data: Dict, test_mode: bool = True) -> Tuple[bool, str]:
        """Отправка заявки на бронирование"""
        logger.info(f"Отправка заявки на бронирование корта №{court_data['court_number']}")
        
        # Получаем страницу для извлечения CSRF токена
        html_content = self.get_booking_page(court_data['date'])
        if not html_content:
            return False, "Не удалось загрузить страницу бронирования"
        
        csrf_token = self.extract_csrf_token(html_content)
        
        # Подготавливаем данные формы
        form_data = self.prepare_booking_form_data(court_data)
        
        # Добавляем CSRF токен если найден
        if csrf_token:
            form_data['_token'] = csrf_token
        
        # Добавляем параметр тестового режима
        if test_mode:
            form_data['test_payment'] = '1'
        
        # Отправляем запрос
        url = self.order_url
        if test_mode:
            url += "?test_payment=1"
        
        logger.info(f"Отправляем POST запрос на {url}")
        
        try:
            response = self.session.post(url, data=form_data)
            logger.info(f"Ответ сервера: {response.status_code}")
            
            if response.status_code == 200:
                # Проверяем содержимое ответа
                if 'успешно' in response.text.lower() or 'success' in response.text.lower():
                    logger.info("Бронирование успешно!")
                    return True, "Бронирование успешно выполнено"
                elif 'ошибка' in response.text.lower() or 'error' in response.text.lower():
                    logger.error("Ошибка бронирования")
                    return False, f"Ошибка бронирования: {response.text[:200]}"
                else:
                    logger.warning("Неопределенный ответ сервера")
                    return False, f"Неопределенный ответ: {response.text[:200]}"
            else:
                logger.error(f"HTTP ошибка: {response.status_code}")
                return False, f"HTTP ошибка: {response.status_code}"
                
        except requests.RequestException as e:
            logger.error(f"Ошибка отправки запроса: {e}")
            return False, f"Ошибка отправки: {str(e)}"
    
    def auto_book_court(self, date: str, court_type: str = 'ground', 
                       time_from: int = 22, duration_hours: int = 2,
                       test_mode: bool = True) -> Tuple[bool, str]:
        """Автоматическое бронирование корта"""
        logger.info(f"Начинаем автоматическое бронирование на {date}")
        
        # 1. Ищем доступный корт
        court_data = self.find_available_court(date, court_type, time_from, duration_hours)
        if not court_data:
            return False, "Свободных кортов не найдено"
        
        # 2. Отправляем заявку на бронирование
        success, message = self.submit_booking(court_data, test_mode)
        
        if success:
            logger.info(f"✅ Бронирование успешно! Корт №{court_data['court_number']}")
            return True, f"Корт №{court_data['court_number']} успешно забронирован на {court_data['time_from']}:00-{court_data['time_to']}:00"
        else:
            logger.error(f"❌ Ошибка бронирования: {message}")
            return False, message

def main():
    """Тестирование модуля бронирования"""
    booking = AutoBooking()
    
    # Тестируем на завтра
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"🎾 Тестирование автоматического бронирования на {tomorrow}")
    print("=" * 60)
    
    # Тестовое бронирование
    success, message = booking.auto_book_court(
        date=tomorrow,
        court_type='ground',
        time_from=22,
        duration_hours=2,
        test_mode=True
    )
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

if __name__ == "__main__":
    main()
