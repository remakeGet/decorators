import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def logger(path):
    def __logger(old_function):
        def new_function(*args, **kwargs):
            # Записываем время вызова функции
            call_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Получаем имя функции
            func_name = old_function.__name__
            
            # Формируем строку с аргументами
            args_str = ', '.join([str(arg) for arg in args])
            kwargs_str = ', '.join([f"{key}={value}" for key, value in kwargs.items()])
            all_args = ', '.join(filter(None, [args_str, kwargs_str]))
            
            # Вызываем оригинальную функцию
            result = old_function(*args, **kwargs)
            
            # Формируем запись для лога
            log_entry = (
                f"{call_time} - Вызвана функция: {func_name}\n"
                f"Аргументы: {all_args}\n"
                f"Результат: {result}\n"
                f"{'-'*50}\n"
            )
            
            # Записываем в файл
            with open(path, 'a', encoding='utf-8') as log_file:
                log_file.write(log_entry)
            
            return result
        
        return new_function
    return __logger

KEYWORDS = ['python', 'web', 'data', 'API', 'алгоритм']
URL = 'https://habr.com/ru/articles/'
@logger('habr_scraper.log')
def scrape_habr():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # селектор для статей
        articles = soup.find_all('article', class_='tm-articles-list__item')
        
        results = []
        
        for article in articles:
            # Извлекаем заголовок
            title_elem = article.find('h2', class_='tm-title tm-title_h2')
            if not title_elem:
                continue
                
            title = title_elem.text.strip()
            link = title_elem.find('a')['href']
            if not link.startswith('https://'):
                link = f'https://habr.com{link}'
            
            # Извлекаем дату
            time_elem = article.find('time')
            if not time_elem:
                continue
                
            pub_date = datetime.strptime(time_elem['datetime'], '%Y-%m-%dT%H:%M:%S.%fZ')
            
            # Извлекаем текст превью
            preview_elem = article.find('div', class_='article-formatted-body')
            if not preview_elem:
                continue
                
            preview_text = preview_elem.text.lower()
            
            # Проверяем ключевые слова
            if any(keyword.lower() in preview_text for keyword in KEYWORDS):
                results.append({
                    'date': pub_date.strftime('%d.%m.%Y'),
                    'title': title,
                    'link': link
                })
        
        if results:
            print("Найденные статьи:")
            for article in results:
                print(f"{article['date']} – {article['title']} – {article['link']}")
        else:
            print("Статей с ключевыми словами не найдено.")
            
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == '__main__':
    scrape_habr()
