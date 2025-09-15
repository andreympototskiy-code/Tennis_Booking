#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматический мониторинг теннисных слотов
Запускается каждые N минут и уведомляет о новых свободных слотах
"""

import time
import schedule
import json
from datetime import datetime, timedelta
from tennis_monitor import TennisMonitor
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class AutoTennisMonitor:
    def __init__(self):
        self.monitor = TennisMonitor()
        self.last_known_slots = {}
        self.notification_file = 'notifications.json'
        
    def load_last_slots(self):
        """Загружает последние известные слоты из файла"""
        try:
            with open(self.notification_file, 'r', encoding='utf-8') as f:
                self.last_known_slots = json.load(f)
        except FileNotFoundError:
            self.last_known_slots = {}
            logging.info("Файл с последними слотами не найден, начинаем с нуля")
    
    def save_last_slots(self):
        """Сохраняет текущие слоты в файл"""
        try:
            with open(self.notification_file, 'w', encoding='utf-8') as f:
                json.dump(self.last_known_slots, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Ошибка при сохранении слотов: {e}")
    
    def get_new_slots(self, date: str, current_slots: list) -> list:
        """
        Определяет новые свободные слоты по сравнению с последней проверкой
        
        Args:
            date: Дата в формате YYYY-MM-DD
            current_slots: Текущие свободные слоты
            
        Returns:
            Список новых слотов
        """
        new_slots = []
        
        if date not in self.last_known_slots:
            # Если это первая проверка для этой даты, все слоты считаются новыми
            self.last_known_slots[date] = []
            return current_slots
        
        last_slots = self.last_known_slots[date]
        
        # Создаем множества времени для быстрого сравнения
        current_times = {slot['time'] for slot in current_slots}
        last_times = {slot['time'] for slot in last_slots}
        
        # Находим новые слоты
        new_times = current_times - last_times
        for slot in current_slots:
            if slot['time'] in new_times:
                new_slots.append(slot)
        
        return new_slots
    
    def send_notification(self, new_slots: list, date: str):
        """
        Отправляет уведомление о новых свободных слотах
        
        Args:
            new_slots: Список новых слотов
            date: Дата в формате YYYY-MM-DD
        """
        if not new_slots:
            return
        
        print(f"\n🔔 УВЕДОМЛЕНИЕ! Найдены новые свободные слоты на {date}")
        print("=" * 60)
        
        for slot in new_slots:
            print(f"⏰ Время: {slot['time']}")
            print(f"📝 Информация: {slot['element_text']}")
            print("-" * 30)
        
        # Здесь можно добавить отправку email, telegram, SMS и т.д.
        logging.info(f"Найдено {len(new_slots)} новых свободных слотов на {date}")
    
    def check_date(self, date: str):
        """
        Проверяет свободные слоты для указанной даты
        
        Args:
            date: Дата в формате YYYY-MM-DD
        """
        logging.info(f"Проверяем слоты для даты: {date}")
        
        try:
            current_slots = self.monitor.get_slots_for_date(date)
            new_slots = self.get_new_slots(date, current_slots)
            
            if new_slots:
                self.send_notification(new_slots, date)
            
            # Обновляем последние известные слоты
            self.last_known_slots[date] = current_slots
            self.save_last_slots()
            
            # Выводим общую статистику
            print(f"📊 Статистика для {date}:")
            print(f"   Всего свободных слотов: {len(current_slots)}")
            print(f"   Новых слотов: {len(new_slots)}")
            
        except Exception as e:
            logging.error(f"Ошибка при проверке даты {date}: {e}")
    
    def check_tomorrow(self):
        """Проверяет свободные слоты на завтра"""
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_str = tomorrow.strftime('%Y-%m-%d')
        self.check_date(tomorrow_str)
    
    def check_specific_date(self, date_str: str):
        """Проверяет свободные слоты на конкретную дату"""
        self.check_date(date_str)
    
    def start_monitoring(self, check_interval_minutes: int = 10):
        """
        Запускает автоматический мониторинг
        
        Args:
            check_interval_minutes: Интервал проверки в минутах
        """
        logging.info(f"Запуск автоматического мониторинга с интервалом {check_interval_minutes} минут")
        
        # Загружаем последние известные слоты
        self.load_last_slots()
        
        # Планируем задачи
        schedule.every(check_interval_minutes).minutes.do(self.check_tomorrow)
        
        # Первоначальная проверка
        print("🎾 Запуск теннисного монитора...")
        print(f"⏰ Интервал проверки: {check_interval_minutes} минут")
        print("📅 Проверяем свободные слоты на завтра")
        print("=" * 50)
        
        self.check_tomorrow()
        
        print(f"\n✅ Мониторинг запущен! Следующая проверка через {check_interval_minutes} минут.")
        print("💡 Для остановки нажмите Ctrl+C")
        
        # Основной цикл
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Мониторинг остановлен пользователем")
            logging.info("Мониторинг остановлен пользователем")


def main():
    """Основная функция"""
    auto_monitor = AutoTennisMonitor()
    
    print("🎾 Автоматический мониторинг теннисных слотов x19.spb.ru")
    print("=" * 60)
    
    # Можно запустить разовую проверку или автоматический мониторинг
    choice = input("Выберите режим:\n1. Разовая проверка завтрашних слотов\n2. Автоматический мониторинг\n3. Проверка конкретной даты\nВведите номер (1-3): ").strip()
    
    if choice == "1":
        auto_monitor.load_last_slots()
        auto_monitor.check_tomorrow()
        
    elif choice == "2":
        try:
            interval = int(input("Введите интервал проверки в минутах (по умолчанию 10): ") or "10")
        except ValueError:
            interval = 10
        auto_monitor.start_monitoring(interval)
        
    elif choice == "3":
        date_input = input("Введите дату в формате YYYY-MM-DD (например, 2025-09-16): ").strip()
        auto_monitor.load_last_slots()
        auto_monitor.check_specific_date(date_input)
        
    else:
        print("Неверный выбор")


if __name__ == "__main__":
    main()
