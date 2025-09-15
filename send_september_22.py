#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отправка данных по 22 сентября в Telegram
"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, '/root/tennis-monitor')

from real_time_analyzer import RealTimeTennisAnalyzer
from telegram_notifier import TelegramNotifier, get_telegram_config

def main():
    # Получаем конфигурацию Telegram
    config = get_telegram_config()
    if not config:
        print('❌ Конфигурация Telegram не найдена!')
        return
    
    # Инициализируем мониторы
    analyzer = RealTimeTennisAnalyzer()
    notifier = TelegramNotifier(config['bot_token'], config['chat_id'])
    
    # Проверяем соединение с Telegram
    print('🔗 Проверка соединения с Telegram...')
    if not notifier.test_connection():
        print('❌ Ошибка соединения с Telegram!')
        return
    
    print('✅ Соединение с Telegram установлено')
    
    # Анализируем 22 сентября
    date = '2025-09-22'
    date_display = '22.09.2025 (Воскресенье)'
    
    print(f'📅 Анализ свободных кортов на {date_display}')
    
    free_courts = analyzer.analyze_ground_courts_22h_real(date)
    
    if free_courts:
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
            court_groups[physical_court].append(court_number)
        
        # Формируем сообщение
        message = f'🎾 <b>Свободные теннисные корты</b>\n'
        message += f'📅 Дата: {date_display}\n'
        message += f'🏟️ Тип корта: Грунт\n'
        message += f'⏰ Время: 22:00-00:00 (2 часа)\n'
        message += f'✅ Найдено: {len(free_courts)} свободных слотов\n\n'
        
        for physical_court, court_numbers in court_groups.items():
            message += f'🏟️ <b>{physical_court}</b>\n'
            for court_num in court_numbers:
                message += f'  • Корт №{court_num} - 22:00-00:00\n'
            message += '\n'
        
        message += '🔗 <a href="https://x19.spb.ru/bronirovanie/">Забронировать</a>'
        
        print('📤 Отправка уведомления в Telegram...')
        success = notifier.send_message(message)
        
        if success:
            print('✅ Уведомление успешно отправлено в Telegram!')
            print(f'📊 Отправлена информация о {len(free_courts)} свободных кортах')
        else:
            print('❌ Ошибка отправки уведомления')
    else:
        print('❌ Свободных грунтовых кортов в 22:00-00:00 не найдено')
        
        # Отправляем уведомление об отсутствии слотов
        message = f'❌ Свободных грунтовых кортов в 22:00-00:00 на {date_display} не найдено\n\n'
        message += '🔗 Проверить: https://x19.spb.ru/bronirovanie/'
        
        success = notifier.send_message(message)
        if success:
            print('✅ Уведомление об отсутствии слотов отправлено')
        else:
            print('❌ Ошибка отправки уведомления')

if __name__ == "__main__":
    main()
