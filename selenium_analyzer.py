#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium анализатор для рендеринга JavaScript и поиска занятых мест
"""

import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
except ImportError:
    print("❌ Selenium не установлен. Устанавливаем...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SeleniumTennisAnalyzer:
    def __init__(self):
        self.base_url = "https://x19.spb.ru"
        self.driver = None
        self.occupied_color = "#d1d1d1"
        
    def setup_driver(self):
        """Настраивает Chrome WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Запуск без GUI
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✅ Chrome WebDriver настроен")
            return True
        except Exception as e:
            print(f"❌ Ошибка настройки WebDriver: {e}")
            return False
    
    def get_rendered_page(self, date: str) -> Optional[str]:
        """Получает отрендеренную страницу для конкретной даты"""
        if not self.driver:
            if not self.setup_driver():
                return None
        
        try:
            url = f"{self.base_url}/bronirovanie/?date={date}"
            print(f"🌐 Загружаем страницу: {url}")
            
            self.driver.get(url)
            
            # Ждем загрузки Vue.js приложения
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.ID, "app")))
            
            # Дополнительная пауза для полной загрузки расписания
            time.sleep(3)
            
            # Получаем отрендеренный HTML
            html_content = self.driver.page_source
            
            # Сохраняем для анализа
            with open(f'rendered_schedule_{date}.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"💾 Отрендеренный HTML сохранен в: rendered_schedule_{date}.html")
            
            return html_content
            
        except TimeoutException:
            print(f"⏰ Таймаут загрузки страницы для {date}")
            return None
        except Exception as e:
            print(f"❌ Ошибка загрузки страницы для {date}: {e}")
            return None
    
    def find_occupied_cells(self, date: str) -> List[Dict]:
        """Находит занятые ячейки по CSS стилям"""
        html_content = self.get_rendered_page(date)
        if not html_content:
            return []
        
        try:
            # Ищем элементы с цветом фона #d1d1d1
            occupied_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                f"[style*='background: {self.occupied_color}'], [style*='background:{self.occupied_color}']"
            )
            
            print(f"🚫 Найдено {len(occupied_elements)} занятых ячеек по стилю background: {self.occupied_color}")
            
            occupied_cells = []
            for element in occupied_elements:
                try:
                    cell_info = {
                        'tag': element.tag_name,
                        'text': element.text.strip(),
                        'style': element.get_attribute('style'),
                        'class': element.get_attribute('class'),
                        'position': element.location,
                        'size': element.size
                    }
                    occupied_cells.append(cell_info)
                except Exception as e:
                    logger.warning(f"Ошибка получения информации об элементе: {e}")
            
            # Также ищем по другим возможным стилям
            alternative_selectors = [
                "[style*='background-color: #d1d1d1']",
                "[style*='background-color:#d1d1d1']",
                "[style*='background: #d1d1d1']",
                "[style*='background:#d1d1d1']",
                ".occupied",
                ".busy", 
                ".taken",
                ".booked"
            ]
            
            for selector in alternative_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"🎯 Найдено {len(elements)} элементов по селектору: {selector}")
            
            return occupied_cells
            
        except Exception as e:
            print(f"❌ Ошибка поиска занятых ячеек: {e}")
            return []
    
    def analyze_schedule_structure(self, date: str) -> Dict:
        """Анализирует структуру расписания"""
        html_content = self.get_rendered_page(date)
        if not html_content:
            return {}
        
        try:
            # Ищем таблицу расписания
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            print(f"📊 Найдено {len(tables)} таблиц")
            
            # Ищем div'ы с расписанием
            schedule_divs = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "div[class*='schedule'], div[class*='timetable'], div[class*='grid'], div[class*='court']"
            )
            print(f"📅 Найдено {len(schedule_divs)} div'ов с расписанием")
            
            # Ищем все элементы с цветом фона
            colored_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                "[style*='background']"
            )
            print(f"🎨 Найдено {len(colored_elements)} элементов с цветом фона")
            
            # Анализируем первые несколько элементов
            structure_info = {
                'tables_count': len(tables),
                'schedule_divs_count': len(schedule_divs),
                'colored_elements_count': len(colored_elements),
                'occupied_cells': self.find_occupied_cells(date)
            }
            
            return structure_info
            
        except Exception as e:
            print(f"❌ Ошибка анализа структуры: {e}")
            return {}
    
    def analyze_week_selenium(self, start_date: str = None) -> Dict[str, Dict]:
        """Анализирует неделю с помощью Selenium"""
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"📅 Selenium анализ свободных кортов на неделю с {start_date}")
        print("=" * 70)
        
        if not self.setup_driver():
            print("❌ Не удалось настроить WebDriver")
            return {}
        
        try:
            results = {}
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            
            for i in range(3):  # Анализируем первые 3 дня для тестирования
                current_date = start_dt + timedelta(days=i)
                date_str = current_date.strftime('%Y-%m-%d')
                date_display = current_date.strftime('%d.%m.%Y (%A)')
                
                print(f"\n📅 {date_display}")
                print("-" * 40)
                
                structure_info = self.analyze_schedule_structure(date_str)
                results[date_str] = {
                    'date_display': date_display,
                    'structure_info': structure_info
                }
                
                # Пауза между запросами
                time.sleep(2)
            
            return results
            
        finally:
            if self.driver:
                self.driver.quit()
                print("🔚 WebDriver закрыт")


def main():
    """Основная функция"""
    analyzer = SeleniumTennisAnalyzer()
    
    print("🎾 SELENIUM АНАЛИЗАТОР СВОБОДНЫХ КОРТОВ")
    print("=" * 60)
    print("🔍 Рендеринг JavaScript и поиск занятых мест")
    print("🎯 Цвет занятых мест: #d1d1d1")
    print("=" * 60)
    
    # Анализируем несколько дней
    results = analyzer.analyze_week_selenium()
    
    print("\n✅ Анализ завершен. Результаты:")
    print("=" * 50)
    
    for date_str, data in results.items():
        print(f"\n📅 {data['date_display']}")
        structure = data['structure_info']
        print(f"  • Таблиц: {structure.get('tables_count', 0)}")
        print(f"  • Div'ов расписания: {structure.get('schedule_divs_count', 0)}")
        print(f"  • Элементов с цветом: {structure.get('colored_elements_count', 0)}")
        print(f"  • Занятых ячеек: {len(structure.get('occupied_cells', []))}")
    
    print("\n📁 Проверьте файлы:")
    print("  • rendered_schedule_*.html - отрендеренные страницы")


if __name__ == "__main__":
    main()
