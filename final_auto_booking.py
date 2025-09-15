#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальная версия модуля автоматического бронирования теннисных кортов
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

class FinalAutoBooking:
    def __init__(self):
        self.base_url = "https://x19.spb.ru"
        self.booking_url = "https://x19.spb.ru/bronirovanie"
        self.initialize_url = "https://x19.spb.ru/bronirovanie/initialize"
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
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://x19.spb.ru/bronirovanie/',
            'X-Requested-With': 'XMLHttpRequest'
        })
        
    def get_initialize_data_raw(self, date: str) -> Optional[str]:
        """Получение сырых данных инициализации"""
        url = f"{self.initialize_url}?date={date}"
        logger.info(f"Загружаем данные инициализации: {url}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            if 'window.$INITIAL' in response.text:
                # Извлекаем JSON из JavaScript
                json_match = re.search(r'window\.\$INITIAL\s*=\s*({.*?});', response.text, re.DOTALL)
                if json_match:
                    return json_match.group(1)
                    
        except requests.RequestException as e:
            logger.error(f"Ошибка загрузки данных инициализации: {e}")
            
        return None
    
    def parse_court_data(self, json_str: str) -> Dict:
        """Парсинг данных кортов из JSON строки"""
        try:
            data = json.loads(json_str)
            
            # Извлекаем корты и блокировки
            instructions = data.get('instructions', {})
            set_data = instructions.get('set', {})
            
            court_types = set_data.get('court_types', [])
            time_blocked = set_data.get('time_blocked', [])
            
            # Ищем грунтовые корты
            ground_courts = []
            for court_type in court_types:
                if court_type.get('label') == 'grunt':
                    ground_courts.extend(court_type.get('courts', []))
            
            return {
                'ground_courts': ground_courts,
                'time_blocked': time_blocked
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            return {'ground_courts': [], 'time_blocked': []}
    
    def find_available_court(self, date: str, court_type: str = 'ground', 
                           time_from: int = 22, duration_hours: int = 2) -> Optional[Dict]:
        """Поиск доступного корта для бронирования"""
        logger.info(f"Поиск доступного корта на {date} в {time_from}:00 ({duration_hours}ч)")
        
        # Получаем сырые данные
        json_str = self.get_initialize_data_raw(date)
        if not json_str:
            logger.error("Не удалось получить данные инициализации")
            return None
        
        # Парсим данные кортов
        court_data = self.parse_court_data(json_str)
        ground_courts = court_data['ground_courts']
        time_blocked = court_data['time_blocked']
        
        if not ground_courts:
            logger.warning("Грунтовые корты не найдены")
            return None
        
        logger.info(f"Найдено {len(ground_courts)} грунтовых кортов")
        logger.info(f"Найдено {len(time_blocked)} занятых слотов")
        
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
                    'court_type': 'Грунт',
                    'time_from': time_from,
                    'time_to': (time_from + duration_hours) % 24,
                    'date': date
                }
        
        logger.warning("Свободных кортов не найдено")
        return None
    
    def _is_court_available(self, court_id: int, time_from: int, duration_hours: int, 
                          time_blocked: List[Dict]) -> bool:
        """Проверка доступности корта в указанное время"""
        # Преобразуем время в секунды от начала дня
        start_time = time_from * 3600  # 22:00 = 79200 секунд
        end_time = start_time + (duration_hours * 3600)  # 2 часа = 7200 секунд
        
        # Проверяем блокировки для этого корта
        for blocked in time_blocked:
            if blocked.get('court_id') == court_id:
                blocked_start = blocked.get('time_from', {}).get('totalSeconds', 0)
                blocked_end = blocked.get('time_to', {}).get('totalSeconds', 0)
                
                # Проверяем пересечение временных интервалов
                if not (end_time <= blocked_start or start_time >= blocked_end):
                    return False
        
        return True
    
    def get_csrf_token(self, date: str) -> Optional[str]:
        """Получение CSRF токена"""
        url = f"{self.booking_url}/?date={date}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # Ищем CSRF токен в HTML
            csrf_patterns = [
                r'<meta name="csrf-token" content="([^"]+)"',
                r'<input[^>]*name="[^"]*csrf[^"]*"[^>]*value="([^"]+)"',
                r'_token["\']?\s*:\s*["\']([^"]+)["\']'
            ]
            
            for pattern in csrf_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                if matches:
                    logger.info("CSRF токен найден")
                    return matches[0]
                    
        except requests.RequestException as e:
            logger.error(f"Ошибка получения CSRF токена: {e}")
        
        logger.warning("CSRF токен не найден")
        return None
    
    def prepare_booking_form_data(self, court_data: Dict) -> Dict:
        """Подготовка данных формы для бронирования"""
        logger.info("Подготовка данных формы бронирования...")
        
        # Формируем данные формы согласно структуре сайта
        form_data = {
            'date': court_data['date'],
            'order[type_id]': '1',  # Тип бронирования (обычно 1)
            'ordertime[0][court_id]': str(court_data['court_id']),
            'ordertime[0][time_from]': f"{court_data['time_from']:02d}:00:00",
            'ordertime[0][time_to]': f"{court_data['time_to']:02d}:00:00",
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
        
        # Получаем CSRF токен
        csrf_token = self.get_csrf_token(court_data['date'])
        
        # Подготавливаем данные формы
        form_data = self.prepare_booking_form_data(court_data)
        
        # Добавляем CSRF токен если найден
        if csrf_token:
            form_data['_token'] = csrf_token
        
        # Добавляем параметр тестового режима
        if test_mode:
            form_data['test_payment'] = '1'
        
        # Обновляем заголовки для POST запроса
        headers = self.session.headers.copy()
        headers.update({
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://x19.spb.ru',
            'Referer': f"https://x19.spb.ru/bronirovanie/?date={court_data['date']}"
        })
        
        # Отправляем запрос
        url = self.order_url
        if test_mode:
            url += "?test_payment=1"
        
        logger.info(f"Отправляем POST запрос на {url}")
        
        try:
            response = self.session.post(url, data=form_data, headers=headers)
            logger.info(f"Ответ сервера: {response.status_code}")
            logger.info(f"Размер ответа: {len(response.text)} символов")
            
            if response.status_code == 200:
                # Проверяем содержимое ответа
                response_text = response.text.lower()
                if 'успешно' in response_text or 'success' in response_text:
                    logger.info("Бронирование успешно!")
                    return True, "Бронирование успешно выполнено"
                elif 'ошибка' in response_text or 'error' in response_text:
                    logger.error("Ошибка бронирования")
                    return False, f"Ошибка бронирования: {response.text[:200]}"
                elif 'redirect' in response_text or 'location' in response_text:
                    logger.info("Перенаправление - возможно успешно")
                    return True, "Бронирование выполнено (перенаправление)"
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
    """Тестирование финального модуля бронирования"""
    booking = FinalAutoBooking()
    
    # Тестируем на завтра
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"🎾 Тестирование финального автоматического бронирования на {tomorrow}")
    print("=" * 70)
    
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
