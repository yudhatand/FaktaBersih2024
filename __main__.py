import streamlit as st
from ui import UI
from db import Fake_news_database
from webscrapping import WebScraper
from model import Fake_news_detector


if __name__ == "__main__":
    host = "localhost"
    user = "root"
    password = "root"
    database = "Fake_news_analysis"

    # Database
    mydatabase = Fake_news_database(
        host=host,
        user=user,
        password=password,
        database=database
    )
    
    # UI
    model = Fake_news_detector('model.sav', 'vectorizer.sav', mydatabase)
    gui = UI(mydatabase, model)

    # scrap
    scrap = WebScraper()
    scrap.schedule_scraping()



 