#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Запуск автоматического мониторинга отложенных запросов
"""

import subprocess
import os
import time
from datetime import datetime

def start_monitoring():
    """Запуск мониторинга в фоновом режиме"""
    print("🚀 ЗАПУСК АВТОМАТИЧЕСКОГО МОНИТОРИНГА")
    print("=" * 50)
    
    # Проверяем, не запущен ли уже мониторинг
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'auto_monitor_requests.py' in result.stdout:
            print("⚠️ Мониторинг уже запущен")
            
            # Показываем PID
            lines = result.stdout.split('\n')
            for line in lines:
                if 'auto_monitor_requests.py' in line and 'grep' not in line:
                    parts = line.split()
                    if len(parts) > 1:
                        pid = parts[1]
                        print(f"📊 PID: {pid}")
                        break
            
            choice = input("Остановить текущий мониторинг и запустить новый? (y/n): ").strip().lower()
            if choice == 'y':
                subprocess.run(['pkill', '-f', 'auto_monitor_requests.py'])
                print("🛑 Старый мониторинг остановлен")
                time.sleep(2)
            else:
                print("❌ Запуск отменен")
                return
    except Exception as e:
        print(f"⚠️ Ошибка проверки: {e}")
    
    # Запускаем мониторинг в фоновом режиме
    print("🤖 Запуск мониторинга в фоновом режиме...")
    
    try:
        # Запускаем с nohup для работы в фоне
        process = subprocess.Popen([
            'nohup', 'python', 'auto_monitor_requests.py'
        ], stdout=open('monitoring.log', 'w'), stderr=subprocess.STDOUT)
        
        print(f"✅ Мониторинг запущен!")
        print(f"📊 PID: {process.pid}")
        print(f"📝 Лог: monitoring.log")
        print(f"📅 Время запуска: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        
        print(f"\n📋 ЧТО ДЕЛАЕТ МОНИТОРИНГ:")
        print(f"  • Проверяет отложенные запросы каждые 2 часа")
        print(f"  • Автоматически выполняет бронирование, когда дата становится доступна")
        print(f"  • Отправляет уведомления о результатах")
        
        print(f"\n🔍 КОМАНДЫ ДЛЯ УПРАВЛЕНИЯ:")
        print(f"  • Проверить статус: ps aux | grep auto_monitor_requests")
        print(f"  • Посмотреть лог: tail -f monitoring.log")
        print(f"  • Остановить: pkill -f auto_monitor_requests.py")
        
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")

if __name__ == "__main__":
    start_monitoring()
