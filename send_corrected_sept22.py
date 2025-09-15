#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отправка исправленных данных по 22 сентября в Telegram
"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, '/root/tennis-monitor')

from corrected_30min_analyzer import Corrected30MinAnalyzer
from telegram_notifier import TelegramNotifier, get_telegram_config

def main():
    # Получаем конфигурацию Telegram
    config = get_telegram_config()
    if not config:
        print('❌ Конфигурация Telegram не найдена!')
        return
    
    # Инициализируем мониторы
    analyzer = Corrected30MinAnalyzer()
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
    
    print(f'📅 Исправленный анализ свободных кортов на {date_display}')
    
    free_courts = analyzer.analyze_ground_courts_22h_corrected(date)
    
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
            court_groups[physical_court].append(court)
        
        # Формируем сообщение
        message = f'🎾 <b>ИСПРАВЛЕННЫЕ данные о свободных кортах</b>\n'
        message += f'📅 Дата: {date_display}\n'
        message += f'🏟️ Тип корта: Грунт\n'
        message += f'📊 Учтены 30-минутные ячейки\n'
        message += f'✅ Найдено: {len(free_courts)} кортов с доступными слотами\n\n'
        
        # Подсчитываем корты с разной длительностью
        full_2h_courts = [c for c in free_courts if c['time_display'] == '22:00-00:00']
        partial_1_5h_courts = [c for c in free_courts if c['time_display'] == '22:30-00:00']
        
        message += f'⏰ <b>2-часовые слоты (22:00-00:00): {len(full_2h_courts)} кортов</b>\n'
        message += f'⏰ <b>1.5-часовые слоты (22:30-00:00): {len(partial_1_5h_courts)} кортов</b>\n\n'
        
        for physical_court, courts in court_groups.items():
            message += f'🏟️ <b>{physical_court}</b>\n'
            for court in courts:
                time_display = court['time_display']
                duration = "2 часа" if time_display == '22:00-00:00' else "1.5 часа"
                message += f'  • Корт №{court["court_number"]} - {time_display} ({duration})\n'
            message += '\n'
        
        message += '🔗 <a href="https://x19.spb.ru/bronirovanie/">Забронировать</a>\n'
        message += '\n📝 <i>Данные исправлены с учетом 30-минутных ячеек</i>'
        
        print('📤 Отправка исправленного уведомления в Telegram...')
        success = notifier.send_message(message)
        
        if success:
            print('✅ Исправленное уведомление успешно отправлено в Telegram!')
            print(f'📊 Отправлена информация о {len(free_courts)} кортах')
            print(f'  • 2-часовые слоты: {len(full_2h_courts)}')
            print(f'  • 1.5-часовые слоты: {len(partial_1_5h_courts)}')
        else:
            print('❌ Ошибка отправки уведомления')
    else:
        print('❌ Свободных грунтовых кортов не найдено')

if __name__ == "__main__":
    main()
