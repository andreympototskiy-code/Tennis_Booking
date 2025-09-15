#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для отправки уведомлений в Telegram
"""

import requests
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        """
        Инициализация Telegram уведомлений
        
        Args:
            bot_token: Токен Telegram бота
            chat_id: ID чата для отправки сообщений
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """
        Отправляет сообщение в Telegram
        
        Args:
            text: Текст сообщения
            parse_mode: Режим парсинга (HTML или Markdown)
            
        Returns:
            True если сообщение отправлено успешно
        """
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                logger.info("Сообщение успешно отправлено в Telegram")
                return True
            else:
                logger.error(f"Ошибка отправки в Telegram: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения в Telegram: {e}")
            return False
    
    def send_tennis_slots_notification(self, slots: List[Dict], date: str, court_type: str = None, time_filter: str = None) -> bool:
        """
        Отправляет уведомление о свободных теннисных слотах
        
        Args:
            slots: Список свободных слотов
            date: Дата
            court_type: Тип корта для фильтрации
            time_filter: Время для фильтрации
            
        Returns:
            True если уведомление отправлено успешно
        """
        if not slots:
            return self.send_message(f"❌ Свободных слотов не найдено на {date}")
        
        # Фильтруем слоты по типу корта и времени
        filtered_slots = self._filter_slots(slots, court_type, time_filter)
        
        if not filtered_slots:
            return self.send_message(f"❌ Свободных слотов {court_type} в {time_filter} не найдено на {date}")
        
        # Формируем сообщение
        message = self._format_slots_message(filtered_slots, date, court_type, time_filter)
        
        return self.send_message(message)
    
    def _filter_slots(self, slots: List[Dict], court_type: str = None, time_filter: str = None) -> List[Dict]:
        """
        Фильтрует слоты по типу корта и времени
        
        Args:
            slots: Список слотов
            court_type: Тип корта
            time_filter: Время для фильтрации (строка вида "22" или "22:00")
            
        Returns:
            Отфильтрованный список слотов
        """
        filtered = slots.copy()
        
        if court_type:
            filtered = [slot for slot in filtered if court_type.lower() in slot.get('court_type', '').lower()]
        
        if time_filter:
            # Ищем слоты, которые начинаются в указанное время
            # time_from может быть как строкой, так и числом
            try:
                # Пытаемся извлечь час из time_filter
                if ':' in time_filter:
                    hour = int(time_filter.split(':')[0])
                else:
                    hour = int(time_filter)
                
                # Фильтруем по времени (time_from может быть строкой или числом)
                filtered = [slot for slot in filtered 
                           if (slot.get('time_from') == hour or 
                               slot.get('time_from') == f"{hour:02d}" or
                               str(slot.get('time_from')) == str(hour))]
                
            except (ValueError, TypeError):
                # Если не удалось распарсить время, пропускаем фильтрацию
                pass
        
        return filtered
    
    def _format_slots_message(self, slots: List[Dict], date: str, court_type: str = None, time_filter: str = None) -> str:
        """
        Форматирует сообщение о слотах
        
        Args:
            slots: Список слотов
            date: Дата
            court_type: Тип корта
            time_filter: Время
            
        Returns:
            Отформатированное сообщение
        """
        message = f"🎾 <b>Свободные теннисные корты</b>\n"
        message += f"📅 Дата: {date}\n"
        
        if court_type:
            message += f"🏟️ Тип корта: {court_type}\n"
        
        if time_filter:
            message += f"⏰ Время: {time_filter}\n"
        
        message += f"✅ Найдено: {len(slots)} свободных слотов\n\n"
        
        # Группируем по времени
        time_groups = {}
        for slot in slots:
            time_key = f"{slot['time_from']}-{slot['time_to']}"
            if time_key not in time_groups:
                time_groups[time_key] = []
            time_groups[time_key].append(slot)
        
        for time_range, time_slots in sorted(time_groups.items()):
            message += f"⏰ <b>{time_range}</b>\n"
            for slot in time_slots:
                message += f"  🏟️ {slot['court_type']} (Корт №{slot['court_number']})\n"
            message += "\n"
        
        message += "🔗 <a href='https://x19.spb.ru/bronirovanie/'>Забронировать</a>"
        
        return message
    
    def test_connection(self) -> bool:
        """
        Проверяет соединение с Telegram API
        
        Returns:
            True если соединение работает
        """
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                bot_info = result.get('result', {})
                logger.info(f"Telegram бот подключен: @{bot_info.get('username', 'unknown')}")
                return True
            else:
                logger.error(f"Ошибка подключения к Telegram: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при проверке соединения с Telegram: {e}")
            return False


def get_telegram_config() -> Optional[Dict]:
    """
    Получает конфигурацию Telegram из файла или переменных окружения
    
    Returns:
        Словарь с конфигурацией или None
    """
    config = {}
    
    # Пытаемся загрузить из файла
    try:
        with open('telegram_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info("Конфигурация Telegram загружена из файла")
        return config
    except FileNotFoundError:
        pass
    
    # Пытаемся получить из переменных окружения
    import os
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if bot_token and chat_id:
        config = {
            'bot_token': bot_token,
            'chat_id': chat_id
        }
        logger.info("Конфигурация Telegram загружена из переменных окружения")
        return config
    
    logger.warning("Конфигурация Telegram не найдена")
    return None


def create_telegram_config_template():
    """Создает шаблон файла конфигурации Telegram"""
    template = {
        "bot_token": "YOUR_BOT_TOKEN_HERE",
        "chat_id": "YOUR_CHAT_ID_HERE",
        "instructions": {
            "bot_token": "Токен вашего Telegram бота (получить у @BotFather)",
            "chat_id": "ID чата для отправки уведомлений (получить у @userinfobot)"
        }
    }
    
    with open('telegram_config_template.json', 'w', encoding='utf-8') as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    
    print("📝 Создан шаблон конфигурации: telegram_config_template.json")
    print("📋 Инструкции:")
    print("1. Получите токен бота у @BotFather в Telegram")
    print("2. Получите ID чата у @userinfobot")
    print("3. Скопируйте telegram_config_template.json в telegram_config.json")
    print("4. Заполните ваши данные в telegram_config.json")


if __name__ == "__main__":
    # Тестирование модуля
    config = get_telegram_config()
    
    if not config:
        print("❌ Конфигурация Telegram не найдена")
        create_telegram_config_template()
    else:
        notifier = TelegramNotifier(config['bot_token'], config['chat_id'])
        
        if notifier.test_connection():
            print("✅ Соединение с Telegram работает")
            
            # Тестовое сообщение
            test_message = "🎾 Тест уведомлений теннисного монитора\n✅ Система работает корректно"
            if notifier.send_message(test_message):
                print("✅ Тестовое сообщение отправлено")
            else:
                print("❌ Ошибка отправки тестового сообщения")
        else:
            print("❌ Ошибка соединения с Telegram")
