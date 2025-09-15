#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интегрированная система мониторинга и автоматического бронирования
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Добавляем текущую директорию в путь
sys.path.insert(0, '/root/tennis-monitor')

from corrected_30min_analyzer import Corrected30MinAnalyzer
from telegram_notifier import TelegramNotifier, get_telegram_config
from simple_auto_booking import SimpleAutoBooking

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegratedMonitorBooking:
    def __init__(self):
        self.analyzer = Corrected30MinAnalyzer()
        self.booking = SimpleAutoBooking()
        
        # Telegram конфигурация
        self.telegram_config = get_telegram_config()
        if self.telegram_config:
            self.notifier = TelegramNotifier(
                self.telegram_config['bot_token'], 
                self.telegram_config['chat_id']
            )
        else:
            self.notifier = None
            logger.warning("Telegram конфигурация не найдена")
    
    def monitor_and_book(self, date: str, time_from: int = 22, duration_hours: int = 2,
                        auto_book: bool = False, simulation: bool = True) -> Tuple[bool, str]:
        """Мониторинг и автоматическое бронирование"""
        logger.info(f"🎾 Интегрированный мониторинг и бронирование на {date}")
        
        # 1. Анализируем доступные корты
        free_courts = self.analyzer.analyze_ground_courts_22h_corrected(date)
        
        if not free_courts:
            message = f"❌ На {date} нет свободных грунтовых кортов в {time_from}:00"
            logger.info(message)
            
            # Отправляем уведомление об отсутствии кортов
            if self.notifier:
                self.notifier.send_message(message)
            
            return False, message
        
        # 2. Ищем корт с нужной длительностью
        target_duration = f"{time_from:02d}:00-{(time_from + duration_hours) % 24:02d}:00"
        target_court = None
        
        for court in free_courts:
            if court['time_display'] == target_duration:
                target_court = court
                break
        
        if not target_court:
            message = f"⚠️ На {date} нет кортов с полным {duration_hours}-часовым слотом в {time_from}:00"
            logger.info(message)
            
            # Отправляем уведомление о частичных слотах
            if self.notifier:
                partial_message = self._format_partial_slots_message(date, free_courts)
                self.notifier.send_message(partial_message)
            
            return False, message
        
        # 3. Отправляем уведомление о найденном корте
        message = self._format_court_found_message(date, target_court)
        logger.info(f"✅ Найден свободный корт: {target_court['court_number']}")
        
        if self.notifier:
            self.notifier.send_message(message)
        
        # 4. Автоматическое бронирование (если включено)
        if auto_book:
            logger.info("🤖 Запуск автоматического бронирования...")
            success, booking_message = self.booking.auto_book_court(
                date=date,
                time_from=time_from,
                duration_hours=duration_hours,
                simulation=simulation
            )
            
            if success:
                booking_notification = f"🎯 АВТОБРОНИРОВАНИЕ: {booking_message}"
                logger.info(booking_notification)
                
                if self.notifier:
                    self.notifier.send_message(booking_notification)
                
                return True, booking_notification
            else:
                error_notification = f"❌ ОШИБКА АВТОБРОНИРОВАНИЯ: {booking_message}"
                logger.error(error_notification)
                
                if self.notifier:
                    self.notifier.send_message(error_notification)
                
                return False, error_notification
        else:
            return True, message
    
    def _format_court_found_message(self, date: str, court: Dict) -> str:
        """Форматирование сообщения о найденном корте"""
        date_display = datetime.strptime(date, '%Y-%m-%d').strftime('%d.%m.%Y')
        
        message = f"🎾 <b>Найден свободный корт!</b>\n"
        message += f"📅 Дата: {date_display}\n"
        message += f"🏟️ Корт №{court['court_number']} - {court['court_type']}\n"
        message += f"⏰ Время: {court['time_display']}\n"
        message += f"💰 Оплата в клубе\n\n"
        message += f"🔗 <a href='https://x19.spb.ru/bronirovanie/?date={date}'>Забронировать</a>"
        
        return message
    
    def _format_partial_slots_message(self, date: str, courts: List[Dict]) -> str:
        """Форматирование сообщения о частичных слотах"""
        date_display = datetime.strptime(date, '%Y-%m-%d').strftime('%d.%m.%Y')
        
        message = f"⚠️ <b>Доступны частичные слоты</b>\n"
        message += f"📅 Дата: {date_display}\n"
        message += f"🏟️ Тип корта: Грунт\n\n"
        
        # Группируем по физическим кортам
        court_groups = {}
        for court in courts:
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
        
        for physical_court, courts_info in court_groups.items():
            message += f"🏟️ <b>{physical_court}</b>\n"
            for court_info in courts_info:
                duration = '2 часа' if court_info['time_display'] == '22:00-00:00' else '1.5 часа' if court_info['time_display'] == '22:30-00:00' else '1 час' if court_info['time_display'] == '23:00-00:00' else '30 мин'
                message += f"  • Корт №{court_info['court_number']} - {court_info['time_display']} ({duration})\n"
            message += "\n"
        
        message += f"🔗 <a href='https://x19.spb.ru/bronirovanie/?date={date}'>Забронировать</a>"
        
        return message
    
    def monitor_week(self, start_date: str, time_from: int = 22, duration_hours: int = 2,
                    auto_book: bool = False, simulation: bool = True) -> Dict[str, Tuple[bool, str]]:
        """Мониторинг недели с возможностью автобронирования"""
        logger.info(f"📅 Недельный мониторинг с {start_date}")
        
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        results = {}
        
        for i in range(7):  # Неделя
            current_date = (start_dt + timedelta(days=i)).strftime('%Y-%m-%d')
            logger.info(f"📊 Проверяем {current_date}")
            
            success, message = self.monitor_and_book(
                date=current_date,
                time_from=time_from,
                duration_hours=duration_hours,
                auto_book=auto_book,
                simulation=simulation
            )
            
            results[current_date] = (success, message)
            
            # Небольшая задержка между запросами
            if i < 6:
                import time
                time.sleep(1)
        
        return results

def main():
    """Тестирование интегрированной системы"""
    system = IntegratedMonitorBooking()
    
    # Тестируем на завтра
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"🎾 Тестирование интегрированной системы на {tomorrow}")
    print("=" * 70)
    
    # Мониторинг без автобронирования
    success, message = system.monitor_and_book(
        date=tomorrow,
        time_from=22,
        duration_hours=2,
        auto_book=False,
        simulation=True
    )
    
    print(f"Результат: {message}")
    
    # Если есть свободный корт, предлагаем автобронирование
    if success and "Найден свободный корт" in message:
        print("\n🤖 Запуск автобронирования...")
        booking_success, booking_message = system.monitor_and_book(
            date=tomorrow,
            time_from=22,
            duration_hours=2,
            auto_book=True,
            simulation=True
        )
        print(f"Результат бронирования: {booking_message}")

if __name__ == "__main__":
    main()
