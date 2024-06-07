import datetime
import mysql.connector
import pandas as pd

dbconfig = {
    'host' : 'localhost',
    'user' : 'root',
    'password' : 'root',
    'database' : 'Fake_news_analysis'
}

class Fake_news_database:
    def __init__(self, host: str, database: str, user="root", password: str=""):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

        self.conn = self.connection()
        self.cursor = self.create_cursor()

    def connection(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
    
    def create_cursor(self):
        return self.conn.cursor()
    
    def close_connection(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()
    
    def execute_query(self, query):
        self.cursor.execute(query)
        if "SELECT" in query.upper():
            result = self.cursor.fetchall()
            return result
        else:
            self.commit()
    
    # Read
    def fetch_all_news(self):
        query = "SELECT * FROM News"
        news = self.execute_query(query)
        return news
    
    def fetch_all_analysis(self):
        query = "SELECT * FROM Analysis"
        analysis = self.execute_query(query)
        return analysis

    def fetch_view(self):
        query = """
            SELECT News.News_ID, News.News_Title, News.News_Text, Analysis.Result
            FROM News
            JOIN Analysis ON News.News_ID = Analysis.News_ID
        """
        data = self.execute_query(query)
        return data

    def fetch_view_user(self, limit):
        query = f"""
            SELECT News.News_ID, News.News_Title, News.News_Text, Analysis.Result
            FROM News
            JOIN Analysis ON News.News_ID = Analysis.News_ID
            ORDER BY News.News_ID DESC
            LIMIT {limit}
        """
        data = self.execute_query(query)
        return data

    # Check
    def check_ID(self, news_id):
        query = f"SELECT COUNT(*) FROM News WHERE News_ID = {news_id}"
        result = self.execute_query(query) 
        count = result[0][0]  
        return count > 0  

    def check_existing_data_title(self, title):
        query = f'SELECT * FROM News WHERE News_Title = "{title}"'
        result = self.execute_query(query)
        if result:
            news_id = result[0][0]
            analysis_query = f"SELECT Result FROM Analysis WHERE News_ID = {news_id}"
            analysis_result = self.execute_query(analysis_query)
            
            if analysis_result:
                return analysis_result[0][0]
        else:
            return None

    def check_existing_data_text(self, text):
        query = f'SELECT * FROM News WHERE News_Text = "{text}"'
        result = self.execute_query(query)
        if result:
            news_id = result[0][0]
            analysis_query = f"SELECT Result FROM Analysis WHERE News_ID = {news_id}"
            analysis_result = self.execute_query(analysis_query)
            
            if analysis_result:
                return analysis_result[0][0]
        else:
            return None

    def check_existing_data_title_text(self, title, text):
        query = f'SELECT * FROM News WHERE News_Title = "{title}" and News_Text = "{text}"'
        result = self.execute_query(query)
        if result:
            news_id = result[0][0]
            analysis_query = f"SELECT Result FROM Analysis WHERE News_ID = {news_id}"
            analysis_result = self.execute_query(analysis_query)
            
            if analysis_result:
                return analysis_result[0][0]
        else:
            return None

    # Create
    def create_data(self, title, text, analysis_result):
        # News
        current_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query_news = f"INSERT INTO News (News_Title, News_Text, Date_Added) VALUES ('{title}', '{text}', '{current_timestamp}')"
        
        self.cursor.execute(query_news)
        self.conn.commit()

        # Analysis
        news_id = self.cursor.lastrowid
        query_analysis = f"INSERT INTO Analysis (News_ID, Result) VALUES ('{news_id}', '{analysis_result}')"

        self.cursor.execute(query_analysis)
        self.conn.commit()

    # Delete
    def delete_data(self, news_id):
        query_news = f"DELETE FROM Analysis WHERE News_ID = {news_id}"
        query_analysis = f"DELETE FROM News WHERE News_ID = {news_id}"
        
        self.execute_query(query_news)
        self.execute_query(query_analysis)
    
    # Update
    def update_data(self, news_id, title, text, analysis_result):
        query_news = f"UPDATE News SET News_Title = '{title}', News_Text = '{text}' WHERE News_ID = {news_id}"
        query_analysis = f"UPDATE Analysis SET Result = '{analysis_result}' WHERE News_ID = {news_id}"

        # Execute the queries
        self.cursor.execute(query_news)
        self.cursor.execute(query_analysis)

        # Commit the transaction
        self.conn.commit()

    # Admin login
    def authenticate_admin(self, username, password):
        query = f"""SELECT * FROM Admin 
                    WHERE Username = '{username}' AND Password = '{password}'"""
        result = self.execute_query(query)
        return len(result) > 0
    
    def update_csv(self):
        news_data = self.fetch_all_news()
        analysis_data = self.fetch_all_analysis()

        df_news = pd.DataFrame(news_data, columns=['News_ID', 'News_Title', 'News_Text', 'Date_Added'])
        df_analysis = pd.DataFrame(analysis_data, columns=['Analysis_ID', 'News_ID', 'Result'])
        df = pd.merge(df_news, df_analysis, on='News_ID', how='left')

        # csv data
        df['Label'] = df['Result'].apply(lambda x: 1 if x == 'Real' else 0)

        # Drop
        df.drop(columns=['News_ID', 'Analysis_ID', 'Date_Added', 'Result'], inplace=True)
        df.to_csv('Dataset.csv', index=False)
        