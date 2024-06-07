import re
import os
import sys
import csv
import time
import random
import requests
import schedule
import datetime
import pandas as pd
import mysql.connector
from bs4 import BeautifulSoup
sys.setrecursionlimit(10**6)
csv.field_size_limit(1000000000)
 
class WebScraper:
    def check_and_take_date(self):
        month_names = {
            "January": "Januari",
            "February": "Februari",
            "March": "Maret",
            "April": "April",
            "May": "Mei",
            "June": "Juni",
            "July": "Juli",
            "August": "Agustus",
            "September": "September",
            "October": "Oktober",
            "November": "November",
            "December": "Desember"
        }
            
        today_date = datetime.date.today()
        formatted_date = today_date.strftime("%d %B %Y")

        if formatted_date.startswith("0"):
            formatted_date = formatted_date[1:]
        
        for eng_month, ind_month in month_names.items():
            formatted_date = formatted_date.replace(eng_month, ind_month)

        return formatted_date
    
    def check_and_take_date_detik(self):
        today_date = datetime.date.today()
        formatted_date = today_date.strftime("%m/%d/%Y")
        return formatted_date
    
    def check_and_take_date_kominfo(self):
        today_date = datetime.date.today()
        formatted_date = today_date.strftime("%d %m-%Y")
        return formatted_date
    
    def filter_ads(self, soup, ad_classes):
        ad_divs = soup.find_all(class_= ad_classes) 
        for ad_div in ad_divs:
            ad_div.extract()
    
    def filter_text(self, text):
        unwanted_texts = ['Dapatkan update berita pilihan dan breaking news setiap hari dari Kompas.com. Mari bergabung di Grup Telegram "Kompas.com News Update", caranya klik link https://t.me/kompascomupdate, kemudian join. Anda harus install aplikasi Telegram terlebih dulu di ponsel.', "Baca juga:", "JAKARTA, KOMPAS.com - ", 'Jakarta (ANTARA/JACX) – ', 'Jakarta (ANTARA) -', 'Penjelasan :'
                          ,'KATEGORI: HOAKS', 'Link counter:', 'Kategori: Hoaks', 'Link Counter:']
        filtered_text = text
        for unwanted_text in unwanted_texts:
            filtered_text = filtered_text.replace(unwanted_text, '')
        return filtered_text
    
    def insert_to_database(self, news_title, news_text, result):
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="Fake_news_analysis"
        )
        cursor = conn.cursor()

        insert_news_query = "INSERT INTO News (News_Title, News_Text) VALUES (%s, %s)"
        cursor.execute(insert_news_query, (news_title, news_text))
        news_id = cursor.lastrowid

        insert_analysis_query = "INSERT INTO Analysis (News_ID, Result) VALUES (%s, %s)"
        cursor.execute(insert_analysis_query, (news_id, result))

        conn.commit()
        conn.close()  

    def clean_kompas(self): 
        def filter_title(text):
            filtered_text = text
            filtered_text = text.replace("'", "").replace('"', '')
            filtered_text = ' '.join(filtered_text.split())
            return filtered_text.strip()
        
        def filter_text(text):
            filtered_text = text
            filtered_text = filtered_text.replace("'", "").replace('"', '')
            filtered_text = ' '.join(filtered_text.split())
            filtered_text = re.sub(r'http\S+', '', filtered_text)
            return filtered_text.strip()

        def filter_csv(input_file, output_file):
            with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                    writer = csv.writer(outfile)
                    for row in reader:
                        row[0] = filter_title(row[0])
                        row[1] = filter_text(row[1])
                        self.insert_to_database(row[0], row[1], 'Real')
                        writer.writerow(row)

        input_train = 'Scheduled_webscrapping/Raw_Dataset/kompas.csv'
        output_train = 'Scheduled_webscrapping/Cleaned_Dataset/kompas.csv'
        filter_csv(input_train, output_train) 
 
    def clean_detik(self):
        def filter_title(text):
            filtered_text = text
            filtered_text = text.replace("'", "").replace('"', '')
            filtered_text = ' '.join(filtered_text.split())
            return filtered_text.strip()
        
        def filter_text_2(text):
            filtered_text = text
            filtered_text = ' '.join(filtered_text.split())
            unwanted_texts = ['Simak berita selengkapnya di halaman selanjutnya. Halaman 1 2 Selanjutnya', ': Halaman 1 2 3 Selanjutnya']

            for unwanted_text in unwanted_texts:
                filtered_text = filtered_text.replace(unwanted_text, '')
            
            filtered_text = filtered_text.replace("'", "").replace('"', '')
            return filtered_text.strip()

        def filter_csv_detik_2(input_file, output_file):
            with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                    writer = csv.writer(outfile)
                    for row in reader:
                        row[0] = filter_title(row[0])
                        row[1] = filter_text_2(row[1])
                        self.insert_to_database(row[0], row[1], 'Real')
                        writer.writerow(row)

        input_file = 'Scheduled_webscrapping/Raw_Dataset/detik.csv'
        output_file = 'Scheduled_webscrapping/Cleaned_Dataset/detik.csv'
        filter_csv_detik_2(input_file, output_file)

    def clean_antara(self):
        def filter_text(text):
            filtered_text = text
            filtered_text = text.replace("'", "").replace('"', '')
            filtered_text = ' '.join(filtered_text.split())
            return filtered_text.strip()
        
        def remove_salah_from_title(text):
            unwanted_strings = ['Hoaks! ', 'Disinformasi! ', 'Misinformasi! ']
            for unwanted_string in unwanted_strings:
                text = text.replace(unwanted_string, '')
            text = text.replace("'", "").replace('"', '')
            return text.strip() 

        def filter_csv(input_file, output_file):
            with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                    writer = csv.writer(outfile)
                    for row in reader:
                        row[0] = remove_salah_from_title(row[0])
                        row[1] = filter_text(row[1])
                        self.insert_to_database(row[0], row[1], 'Fake')
                        writer.writerow(row)
        
        input_file = 'Scheduled_webscrapping/Raw_Dataset/antara.csv'
        output_file = 'Scheduled_webscrapping/Cleaned_Dataset/antara.csv'
        filter_csv(input_file, output_file)

    def scrap_kompas(self):
        kompas_csv_file = open('Scheduled_webscrapping/Raw_Dataset/kompas.csv', 'w', newline='', encoding='utf-8')
        kompas_csv_writer = csv.writer(kompas_csv_file)
        kompas_csv_writer.writerow(['Title', 'Text'])

        num_pages = 3
        target_dates = self.check_and_take_date()

        for page in range(1, num_pages + 1):
            url = f"https://pemilu.kompas.com/news?page={page}"
            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'html.parser')

            titles = soup.find_all('h3', class_='listTitle')
            links = soup.find_all('a', attrs={'href': re.compile("^http://(?:regional|nasional|megapolitan)")})

            for title, link in zip(titles, links):
                title_text = title.text.strip()
                title_date_element = title.find_next(class_='titleDate')
                if title_date_element:
                    title_date = title_date_element.text.strip()
                
                url = link.get('href')
                if title_date in target_dates:
                    news_page = requests.get(url)
                    news_soup = BeautifulSoup(news_page.content, 'html.parser')
                    self.filter_ads(news_soup, 'inner-link-baca-juga')

                    text_content = news_soup.find('div', class_='read__content')
                    if text_content:
                        text = text_content.text.strip()
                        text = self.filter_text(text)
                    kompas_csv_writer.writerow([title_text, text])

        kompas_csv_file.close()
        self.clean_kompas()
    
    def scrap_detik(self):
        detik_csv_file = open('Scheduled_webscrapping/Raw_Dataset/detik.csv', 'w', newline='', encoding='utf-8')
        detik_csv_writer = csv.writer(detik_csv_file)
        detik_csv_writer.writerow(['Title', 'Text'])  

        # List of target dates
        target_dates = [self.check_and_take_date_detik()]

        # DETIK
        for target_date in target_dates:
            page = 1
            while page <= 2:  
            # while True:
                url = f"https://news.detik.com/pemilu/indeks/{page}?date={target_date}"
                page_content = requests.get(url)
                soup = BeautifulSoup(page_content.text, 'html.parser')

                # Title
                titles = soup.find_all('h3', class_='media__title')

                self.filter_ads(soup, 'media__image')

                # Link
                links = soup.find_all('a', class_='media__link')

                # Check if there are no more news articles for the current date
                if not titles:
                    break

                for title, link in zip(titles, links):
                    title_text = title.text.strip()
                    url = link.get('href')

                    ''' Content '''
                    '''================================================================'''
                    # Link content
                    news_page = requests.get(url)
                    news_soup = BeautifulSoup(news_page.content, 'html.parser')

                    # Filter out advertisement divs
                    self.filter_ads(news_soup, 'parallaxindetail scrollpage')
                    self.filter_ads(news_soup, 'staticdetail_container')
                    self.filter_ads(news_soup, 'lihatjg')
                    self.filter_ads(news_soup, 'detail__body-tag mgt-16')

                    text_content = news_soup.find('div', class_='detail__body-text itp_bodycontent')
                    '''================================================================'''

                    if text_content:
                        text = text_content.text.strip()
                        detik_csv_writer.writerow([title_text, text])
                
                page += 1

        detik_csv_file.close()
        self.clean_detik()

    def scrap_antara(self):
        def extract_titles_and_urls(soup):
            return soup.find_all(class_='post_title post_title_medium')

        def extract_title(entry):
            title_text = entry.text.strip()
            return title_text

        def extract_url(entry):
            url_tag = entry.find('a')
            if url_tag:
                return url_tag.get('href')
            else:
                return ""
            
        def extract_text(url):
            news_page = requests.get(url)
            news_soup = BeautifulSoup(news_page.content, 'html.parser')

            # remove bold
            bold_texts = news_soup.find_all('b')
            for bold_text in bold_texts:
                bold_text.extract()

            text_content = news_soup.find('div', class_='wrap__article-detail-content post-content')
            self.filter_ads(news_soup , "text-muted mt-2 small")

            if text_content:
                text1 = text_content.text.strip()
                text = self.filter_text(text1)
                return text
            else:
                return "News content not found for: " + url

        def extract_complete_date(date_element):
            span_element = date_element.text.strip()
            if span_element:
                if "jam lalu" in span_element:
                    return span_element

        antara_csv_file = open('Scheduled_webscrapping/Raw_Dataset/antara.csv', 'w', newline='', encoding='utf-8')
        antara_csv_writer = csv.writer(antara_csv_file)
        antara_csv_writer.writerow(['Title', 'Text'])  

        target_dates = self.check_and_take_date()
        num_pages = 2
        for page in range(1, num_pages + 1):
            url = f"https://www.antaranews.com/slug/anti-hoax/{page}"
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')

            entries = extract_titles_and_urls(soup)
            self.filter_ads(soup, 'col-md-4')
            date_elements = soup.find_all(class_='text-secondary')

            # Keywords
            keywords = ["anies", "prabowo", "presiden", "cawapres", "pemilu", "ganjar", "caslon", "gibran", "tps", "mahfud", "muhaimin", "cak imin", "kpu", "pilpres", "amin"]  # Add more keywords as needed

            for entry, date_element in zip(entries, date_elements):
                title = extract_title(entry)
                url = extract_url(entry)
                keyword_found = False
                for keyword in keywords:
                    if keyword in title.lower() and keyword in url.lower():
                        keyword_found = True
                        break
                if keyword_found:
                    text = extract_text(url)
                    date_extract = extract_complete_date(date_element) 
                    if date_extract == target_dates:
                        antara_csv_writer.writerow([title, text])  
                else:
                    continue

        antara_csv_file.close()
        self.clean_antara()

    def scrap_kominfo(self):
        def extract_titles_and_urls(soup):
            return soup.find_all('a', class_='title')

        def extract_title(entry):
            title_text = entry.text.strip()
            if '[HOAKS]' in title_text:
                title_text = title_text.replace('[HOAKS]', '').strip()
            return title_text

        def extract_url(entry):
            return "https://www.kominfo.go.id" + entry['href']
            
        def extract_text(url):
            news_page = requests.get(url)
            news_soup = BeautifulSoup(news_page.content, 'html.parser')
            
            list_texts = news_soup.find_all('ul')
            for list_text in list_texts:
                list_text.extract()
            
            text_content = news_soup.find('div', class_='typography-block')
            self.filter_ads(news_soup,'O0')

            if text_content:
                text1 = text_content.text.strip()
                text = self.filter_text(text1)
                return text
            else:
                return "News content not found for: " + url

        def extract_complete_date(date_element):
            day = date_element.find('span').text.strip()
            month_year = date_element.text.strip().split()[-1]
            return f"{day}-{month_year}"

        kominfo_csv_file = open('Scheduled_webscrapping/Raw_Dataset/kominfo.csv', 'w', newline='', encoding='utf-8')
        kominfo_csv_writer = csv.writer(kominfo_csv_file)
        kominfo_csv_writer.writerow(['Title', 'Text'])  

        target_date = self.check_and_take_date_kominfo()
        num_pages = 5
        for page in range(1, num_pages + 1):
            url = f"https://www.kominfo.go.id/search?search=hoax&page={page}"
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')

            entries = extract_titles_and_urls(soup)
            self.filter_ads(soup, 'col-md-3 wow fadeInRight animated animated')
            self.filter_ads(soup, 'clearfix')
            date_elements = soup.find_all(class_='date')

            # Keywords
            keywords = ["anies", "prabowo", "presiden", "cawapres", "pemilu", "ganjar", "caslon", "gibran", "tps", "mahfud", "muhaimin", "cak imin", "kpu", "pilpres", "amin"]  # Add more keywords as needed

            # training
            for entry, date_element in zip(entries, date_elements):
                title = extract_title(entry)
                url = extract_url(entry)
                keyword_found = False
                for keyword in keywords:
                    if keyword in title.lower() and keyword in url.lower():
                        keyword_found = True
                        break
                if keyword_found:
                    text = extract_text(url)
                    complete_date = extract_complete_date(date_element)
                    if complete_date == target_date:
                        self.insert_to_database( title, text, 'Fake')
                        kominfo_csv_writer.writerow([title, text])  
                else:
                    continue

        kominfo_csv_file.close()

    def schedule_scraping(self):
        schedule.every().day.at('23:00').do(self.scrap_kompas)
        schedule.every().day.at('23:00:30').do(self.scrap_detik)
        schedule.every().day.at('23:01:00').do(self.scrap_antara)
        schedule.every().day.at('23:01:30').do(self.scrap_kominfo)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def run_scraper():
        scrap = WebScraper()
        scrap.schedule_scraping()