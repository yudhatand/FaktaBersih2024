import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from db import Fake_news_database
from model import Fake_news_detector
import os
import time

class UI:
    def __init__(self, database: Fake_news_database, model: Fake_news_detector):
        self.db = database
        self.model = model
        self.set_page_config()
        self.menu()
    
    def set_page_config(self):
        st.set_page_config(page_title="FaktaBersih2024", initial_sidebar_state="auto", layout="wide", page_icon="Picture/LogofaktaBersih2024.png")

    def menu(self):
        st.markdown(
            """
            <style>

            [data-testid="stSidebar"][aria-expanded="true"]{
                min-width: 25%;
                max-width: 25%;
            }

            @media (max-width: 768px) {
                [data-testid="stSidebar"][aria-expanded="true"] {
                    max-width: 200px;
                }
            }

            </style>
            """,
            unsafe_allow_html=True,
        )   

        st.sidebar.image("Picture/FaktaBersih2024.png", use_column_width=True)
        with st.sidebar:
            selected = option_menu(
                menu_title="",
                options=[
                    "Home",
                    "Admin",
                    "About",
                ]
            )
        st.sidebar.image("Picture/NameNim2.png", use_column_width=True)

        if selected == "Home": 
            self.home()
            
        if selected == "Admin": 
            if st.session_state.get('admin_logged_in', False):
                admin_action = st.sidebar.selectbox(
                    "Admin Actions",
                    options=[
                        "Create",
                        "Update",
                        "Delete",
                        "Logout"
                    ]
                )
            
                if admin_action == "Create":
                    self.create_admin()
            
                elif admin_action == "Update":
                    self.update_admin()
                
                elif admin_action == "Delete":
                    self.delete_admin()
                
                elif admin_action == "Logout":
                    st.session_state.admin_logged_in = False
                    st.rerun()
            else:
                self.admin_login()

        if selected == "About": 
            self.about()

    def home(self):
        st.markdown("<h1 style='text-align: center; font-weight: bold;'>Pendeteksi Berita Palsu (Pilpres 2024)</h1>", unsafe_allow_html=True)

        home_title = st.text_input('News Title', placeholder='Enter the title of the news article here.', help="Provide a brief title to identify the news article.")
        home_text = st.text_area('News Text', placeholder='Enter the full text of the news article here.', help="Paste the entire text of the news article you want to verify.")

        home_title = home_title.replace('"', '').replace("'", '')
        home_text = home_text.replace('"', '').replace("'", '')

        # if st.button("DBupdate"):
        #     self.db.update_csv()
        
        if st.button("Check"):
            if not home_title and not home_text:
                st.error('Error: Title and Text are required.')

            elif not home_title:
                # only text
                existing_data = self.db.check_existing_data_text(home_text)
                if existing_data:
                    st.write('Prediction:', existing_data)
                else:
                    prediction = self.model.predict_label_one(home_text)
                    self.db.update_csv()

                    # st.write('Prediction:', prediction)
                    if prediction == 0:
                        result = "Fake"
                    else:
                        result = "Real"
                    st.write('Prediction:', result)
                    self.db.create_data(home_title, home_text, result)
                    self.db.update_csv()
                    self.model.train_model('Dataset.csv')

            elif not home_text:
                # only title
                existing_data = self.db.check_existing_data_title(home_title)
                if existing_data:
                    st.write('Prediction:', existing_data)
                else:
                    prediction = self.model.predict_label_one(home_title)
                    
                    # st.write('Prediction:', prediction)
                    if prediction == 0:
                        result = "Fake"
                    else:
                        result = "Real"
                    st.write('Prediction:', result)
                    self.db.create_data(home_title, home_text, result)
                    self.db.update_csv()
                    self.model.train_model('Dataset.csv')
 
            else:
                existing_data = self.db.check_existing_data_title_text(home_title, home_text)
                if existing_data:
                    st.write('Prediction:', existing_data)
                else:
                    prediction = self.model.predict_label(home_title, home_text)
                    self.model.train_model('Dataset.csv')

                    if prediction == 0:
                        result = "Fake"
                    else:
                        result = "Real"
                    st.write('Prediction:', result)
                    self.db.create_data(home_title, home_text, result)
                    self.db.update_csv()
        
        st.subheader("History:")
        history = st.radio(
                "Set how long history:",
                ('10', '50', '100', '500', '1000'),
                horizontal=True)
        
        limit = int(history)
        data = self.db.fetch_view_user(limit)

        column_names = [desc[0] for desc in self.db.cursor.description]
        data_plus_columns = [column_names] + data

        df = pd.DataFrame(data_plus_columns[1:], columns=data_plus_columns[0])
        df['News_ID'] = df['News_ID'].astype(str)
        df['News_Title'] = df['News_Title'].astype(str)
        df['News_Text'] = df['News_Text'].astype(str)
        df['Result'] = df['Result'].astype(str)
        st.write(df, index=False)
        st.write(""" """)
    
    def admin_login(self):
        st.markdown("<h1 style='text-align: center; font-weight: bold;'>Admin Login</h1>", unsafe_allow_html=True)
        # st.write("""# Admin Login""")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if self.db.authenticate_admin(username, password):
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Invalid username or password.")
        st.write(""" """)
        st.write(""" """)
        st.write(""" """)
        st.write(""" """)
    
    def about(self):
        st.markdown("<h1 style='text-align: center; font-weight: bold;'>About</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='font-weight: bold;'>What is Faktabersih2024?</h2>", unsafe_allow_html=True)
        st.write(""" Faktabersih2024 is a dedicated platform designed to combat misinformation and fake news surrounding the 2024 presidential election. 
                 Our mission is to provide voters with accurate, verified information by meticulously fact-checking news. Fostering a well-informed electorate, 
                 Faktabersih2024 aims to uphold the integrity of the democratic process and ensure that citizens can make decisions based on truth and transparency.""")
        
        st.markdown("<h2 style='font-weight: bold;'>How does it work?</h2>", unsafe_allow_html=True)
        st.write(""" Simply type in or paste in the Title or Text or Title and Text to the website input in Homepage and press Check, the result will appear within seconds.""")
        
        st.markdown("<h2 style='font-weight: bold;'>What can Faktabersih2024 check?</h2>", unsafe_allow_html=True)
        st.markdown("""
            <ul>
                <li>✔️ News with Title</li>
                <li>✔️ News with Text</li>
                <li>✔️ News with Title and Text</li>
            </ul>
        """, unsafe_allow_html=True)
        
        path = "model.sav"
        ti_m = os.path.getmtime(path)
        # take time
        m_ti = time.ctime(ti_m)
        # divide time
        t_obj = time.strptime(m_ti)
        # take needed time
        T_stamp = time.strftime("%Y-%m-%d", t_obj)

        st.markdown(f"""<h2 style='font-weight: bold;'>Model last update: {T_stamp}</h2>""", unsafe_allow_html=True)



    def show_view(self):
        st.subheader("News and Analysis Database:")
        data = self.db.fetch_view()

        column_names = [desc[0] for desc in self.db.cursor.description]
        data_plus_columns = [column_names] + data

        df = pd.DataFrame(data_plus_columns[1:], columns=data_plus_columns[0])
        df['News_ID'] = df['News_ID'].astype(str)
        df['News_Title'] = df['News_Title'].astype(str)
        df['News_Text'] = df['News_Text'].astype(str)
        df['Result'] = df['Result'].astype(str)
        st.write(df, index=False)

    def show_table(self):
        #  database view
        st.subheader("News Database:")
        # NEWS
        data = self.db.fetch_all_news()

        column_names = [desc[0] for desc in self.db.cursor.description]
        data_plus_columns = [column_names] + data

        df = pd.DataFrame(data_plus_columns[1:], columns=data_plus_columns[0])
        df['News_ID'] = df['News_ID'].astype(str)
        df['News_Title'] = df['News_Title'].astype(str)
        df['News_Text'] = df['News_Text'].astype(str)
        df['Date_Added'] = df['Date_Added'].astype(str)
        st.write(df, index=False)

        st.subheader("Analysis Database:")

        # ANALYSIS
        data = self.db.fetch_all_analysis()

        column_names = [desc[0] for desc in self.db.cursor.description]
        data_plus_columns = [column_names] + data

        df = pd.DataFrame(data_plus_columns[1:], columns=data_plus_columns[0])
        df['Analysis_ID'] = df['Analysis_ID'].astype(str)
        df['News_ID'] = df['News_ID'].astype(str)
        df['Result'] = df['Result'].astype(str)
        st.write(df, index=False)
    
    def create_admin(self):
        self.show_view()
        # create
        st.write("CREATE")
        Create_Title = st.text_input("Create Title")
        Create_Text = st.text_input("Create Text")
        Create_Analysis_result = st.selectbox("Result", ["Real", "Fake"])

        if st.button("Create"):
            existing_data = self.db.check_existing_data_title_text(Create_Title, Create_Text)
            if existing_data:
                st.error("Data with this title already exists.")
            else:
                self.db.create_data(Create_Title, Create_Text, Create_Analysis_result)
                st.success("Data successfully added")
                self.db.update_csv()
                self.model.train_model('Dataset.csv')
                st.rerun()
        st.write(""" """)
    
    def delete_admin(self):
        self.show_view()
        st.write("DELETE")
        Edit_what_ID = st.text_input("Delete ID")
        if st.button("Delete"):
            if self.db.check_ID(Edit_what_ID):
                self.db.delete_data(Edit_what_ID)
                st.success("Data sucessfully deleted")
                self.db.update_csv()
                self.model.train_model('Dataset.csv')
                st.rerun()
            else:
                st.error("No data with that ID")
                
        st.write(""" """)
        st.write(""" """)
        st.write(""" """)
        
    def update_admin(self):
        self.show_view()
        st.write("UPDATE")
        Edit_what_ID = st.text_input("ID Number")
        Update_Title = st.text_input("Update Title")
        Update_Text = st.text_input("Update Text")
        Update_Analysis_result = st.selectbox("Updated Result", ["Real", "Fake"])

        if st.button("Update"):
            if self.db.check_ID(Edit_what_ID):
                self.db.update_data(Edit_what_ID, Update_Title, Update_Text, Update_Analysis_result)
                st.success("Data successfully updated")
                self.db.update_csv() 
                self.model.train_model('Dataset.csv')
                st.rerun()
            else:
                st.error("No data with that ID")

       