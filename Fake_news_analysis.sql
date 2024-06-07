Create database Fake_news_analysis;
use fake_news_analysis;

CREATE TABLE Admin (
    Admin_ID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(255) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL
);

CREATE TABLE News (
    News_ID INT AUTO_INCREMENT PRIMARY KEY,
    News_Title VARCHAR(255) NOT NULL,
    News_Text LONGTEXT NOT NULL,
    Date_Added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
 
CREATE TABLE Analysis (
    Analysis_ID INT AUTO_INCREMENT PRIMARY KEY,
    News_ID INT,
    Result ENUM('Fake', 'Real') NOT NULL,
    FOREIGN KEY (News_ID) REFERENCES News(News_ID)
);