#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отправка данных по 21 сентября для 2-часового слота в Telegram
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
    
    # Анализируем 21 сентября
    date = '2025-09-21'
    date_display = '21.09.2025 (Воскресенье)'
    
    print(f'📅 Анализ свободных кортов на {date_display}')
    print('🎯 Ищем только 2-часовые слоты (22:00-00:00)')
    
    free_courts = analyzer.analyze_ground_courts_22h_corrected(date)
    
    # Фильтруем только 2-часовые слоты
    full_2h_courts = [court for court in free_courts if court['time_display'] == '22:00-00:00']
    
    if full_2h_courts:
        # Группируем по физическим кортам
        court_groups = {}
        for court in full_2h_courts:
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
        message = f'🎾 <b>Свободные теннисные корты (2 часа)</b>\n'
        message += f'📅 Дата: {date_display}\n'
        message += f'🏟️ Тип корта: Грунт\n'
        message += f'⏰ Время: 22:00-00:00 (2 часа)\n'
        message += f'📊 Учтены 30-минутные ячейки\n'
        message += f'✅ Найдено: {len(full_2h_courts)} кортов с полным 2-часовым слотом\n\n'
        
        for physical_court, court_numbers in court_groups.items():
            message += f'🏟️ <b>{physical_court}</b>\n'
            for court_num in court_numbers:
                message += f'  • Корт №{court_num} - 22:00-00:00\n'
            message += '\n'
        
        message += '🔗 <a href="https://x19.spb.ru/bronirovanie/">Забронировать</a>\n'
        message += '\n📝 <i>Показаны только корты с полным 2-часовым слотом</i>'
        
        print('📤 Отправка уведомления в Telegram...')
        success = notifier.send_message(message)
        
        if success:
            print('✅ Уведомление успешно отправлено в Telegram!')
            print(f'📊 Отправлена информация о {len(full_2h_courts)} кортах с полным 2-часовым слотом')
            print('\n🏟️ Свободные корты:')
            for physical_court, court_numbers in court_groups.items():
                print(f'  • {physical_court}: корты {', '.join(map(str, court_numbers))}')
        else:
            print('❌ Ошибка отправки уведомления')
    else:
        print('❌ Нет кортов с полным 2-часовым слотом')
        
        # Отправляем уведомление об отсутствии 2-часовых слотов
        message = f'❌ На {date_display} нет кортов с полным 2-часовым слотом (22:00-00:00)\n\n'
        message += '🔍 Возможно доступны частичные слоты:\n'
        message += '  • 1.5 часа (22:30-00:00)\n'
        message += '  • 1 час (23:00-00:00)\n'
        message += '  • 30 мин (23:30-00:00)\n\n'
        message += '🔗 Проверить: https://x19.spb.ru/bronirovanie/'
        
        success = notifier.send_message(message)
        if success:
            print('✅ Уведомление об отсутствии 2-часовых слотов отправлено')
        else:
            print('❌ Ошибка отправки уведомления')

if __name__ == "__main__":
    main()
