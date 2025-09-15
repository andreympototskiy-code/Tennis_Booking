#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенный модуль автоматического бронирования
Использует существующий анализатор для поиска свободных кортов
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Добавляем текущую директорию в путь
sys.path.insert(0, '/root/tennis-monitor')

from corrected_30min_analyzer import Corrected30MinAnalyzer

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleAutoBooking:
    def __init__(self):
        self.analyzer = Corrected30MinAnalyzer()
        
        # Данные пользователя
        self.user_data = {
            'name': 'Потоцкий Андрей',
            'phone': '+79313203496',
            'email': 'andrey.m.pototskiy@gmail.com',
            'payment_type': 'club'  # Оплата в клубе
        }
    
    def find_available_court(self, date: str, time_from: int = 22, duration_hours: int = 2) -> Optional[Dict]:
        """Поиск доступного корта используя существующий анализатор"""
        logger.info(f"Поиск доступного корта на {date} в {time_from}:00 ({duration_hours}ч)")
        
        # Используем существующий анализатор
        free_courts = self.analyzer.analyze_ground_courts_22h_corrected(date)
        
        if not free_courts:
            logger.warning("Свободных кортов не найдено")
            return None
        
        # Ищем корт с нужной длительностью
        target_duration = f"{time_from:02d}:00-{(time_from + duration_hours) % 24:02d}:00"
        
        for court in free_courts:
            if court['time_display'] == target_duration:
                logger.info(f"Найден свободный корт №{court['court_number']}")
                return {
                    'court_id': court['court_number'],  # Используем номер как ID
                    'court_number': court['court_number'],
                    'court_type': 'Грунт',
                    'time_from': time_from,
                    'time_to': (time_from + duration_hours) % 24,
                    'date': date,
                    'time_display': court['time_display']
                }
        
        logger.warning(f"Корт с длительностью {target_duration} не найден")
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
    
    def simulate_booking(self, court_data: Dict) -> Tuple[bool, str]:
        """Симуляция бронирования (для тестирования)"""
        logger.info(f"Симуляция бронирования корта №{court_data['court_number']}")
        
        # Подготавливаем данные формы
        form_data = self.prepare_booking_form_data(court_data)
        
        # Симулируем успешное бронирование
        logger.info("✅ Симуляция: Бронирование успешно выполнено")
        return True, f"Корт №{court_data['court_number']} успешно забронирован на {court_data['time_display']} (СИМУЛЯЦИЯ)"
    
    def auto_book_court(self, date: str, time_from: int = 22, duration_hours: int = 2,
                       simulation: bool = True) -> Tuple[bool, str]:
        """Автоматическое бронирование корта"""
        logger.info(f"Начинаем автоматическое бронирование на {date}")
        
        # 1. Ищем доступный корт
        court_data = self.find_available_court(date, time_from, duration_hours)
        if not court_data:
            return False, "Свободных кортов не найдено"
        
        # 2. Выполняем бронирование
        if simulation:
            success, message = self.simulate_booking(court_data)
        else:
            # Здесь будет реальное бронирование
            success, message = False, "Реальное бронирование пока не реализовано"
        
        if success:
            logger.info(f"✅ Бронирование успешно! Корт №{court_data['court_number']}")
            return True, message
        else:
            logger.error(f"❌ Ошибка бронирования: {message}")
            return False, message

def main():
    """Тестирование упрощенного модуля бронирования"""
    booking = SimpleAutoBooking()
    
    # Тестируем на завтра
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"🎾 Тестирование упрощенного автоматического бронирования на {tomorrow}")
    print("=" * 70)
    
    # Тестовое бронирование
    success, message = booking.auto_book_court(
        date=tomorrow,
        time_from=22,
        duration_hours=2,
        simulation=True
    )
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

if __name__ == "__main__":
    main()
