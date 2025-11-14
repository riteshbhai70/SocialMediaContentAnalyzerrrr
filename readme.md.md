# Social Media Content Analyzer

![Banner](./snapshoots/image1.png)

### Demo Video
Watch the working demo of **Social Media Content Analyzer** here:  
[![Watch Demo Video](https://img.shields.io/badge/Watch-Demo%20Video-blue?logo=loom)](https://www.loom.com/share/0ca46d1c195e4aeb941f8b538aeda69d)


---

## 🚀 Project Overview

**Social Media Content Analyzer** is a modern web-based tool designed to help content creators, marketers, and businesses analyze and improve the effectiveness of their social media posts.

It allows users to upload text-based content in **PDFs or images**, extract the text using **OCR (Optical Character Recognition)**, and perform **advanced content analysis**, including:

- **Engagement Analysis** – Sentiment, word count, unique words, actionable suggestions.
- **Readability Scores** – Flesch Reading Ease, Flesch-Kincaid Grade, SMOG Index.
- **Content Categorization** – Classifies content into Technology, Business, Lifestyle, Education, Entertainment, News, or General.
- **Platform-specific Recommendations** – Optimized suggestions for Twitter, Instagram, Facebook, LinkedIn.
- **Trending Topics & Hashtags** – Shows current trends and suggests relevant hashtags.
- **Word Frequency & Word Cloud Visualization** – Identify most-used words visually.

**Why use this project?**  
Social media success depends on engagement and reach. This tool automates content analysis, giving actionable insights to boost post visibility and effectiveness.

---

## 🛠 Features

- Upload PDF or image files and extract text using OCR.
- Generate engagement score and actionable improvement suggestions.
- Platform-specific content analysis (Twitter, Instagram, Facebook, LinkedIn).
- Generate word frequency charts and word clouds.
- Automatic content categorization with confidence scores.
- Fetch trending searches from social platforms and Google.
- Store and manage uploaded documents and analysis results in MySQL.
- Interactive and user-friendly dashboard for analytics.

---

## 🎯 Benefits

- **Content Creators & Marketers:** Know what type of content resonates most.
- **Businesses & Startups:** Improve social media presence and strategy.
- **Students & Researchers:** Analyze readability, sentiment, and engagement patterns.

---

## 🧰 Prerequisites

- **Python 3.11+**
- **MySQL Server**
- **Tesseract OCR**

### 🔗 Tesseract OCR Download & Setup

**1. Download and install Tesseract OCR:** [Tesseract OCR Download](https://github.com/UB-Mannheim/tesseract/wiki)  

**2. Add Tesseract installation path to your system environment variable**(PATH).  
   Example (Windows default):  
C:\Program Files\Tesseract-OCR\

go

**3. Test installation:**
```bash
tesseract --version
📥 Project Setup
1. Clone the repository
bash

git clone https://github.com/riteshbhai70/SocialMediaContentAnalyzer.git
cd SocialMediaContentAnalyzer
2. Create a virtual environment and activate it
bash

python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate
3. Install dependencies
bash

pip install -r requirements.txt

**4. Configure environment variables**
Create a .env file in the root directory with:

env

SECRET_KEY=your-super-secret-key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-db-password
DB_NAME=content_analyzer
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216

**5. Create the database and tables**
bash

python db_setup.py
6. Run the application
bash

python app.py
Open in browser: http://localhost:5000

🖼️ Screenshots / GIFs
Dashboard

Upload Page

Analysis Results

Word Cloud & Frequency Chart


Demo Video

📝 How to Use
Go to the Upload Page.

Upload a PDF or image containing your social media content.

Click Analyze to generate:

Engagement score

Sentiment analysis

Suggested improvements

Hashtags and trending topics

Word cloud & frequency chart

Review the results and implement recommendations to improve your posts.

⚠️ Notes
Supported file types: PDF, PNG, JPG, JPEG, GIF

Maximum file size: 16 MB (configurable in .env)

Ensure Tesseract OCR is installed and added to PATH for proper text extraction.

📦 Folder Structure
arduino

SocialMediaContentAnalyzer/
│
├─ app.py
├─ config.py
├─ db_setup.py
├─ requirements.txt
├─ .env
├─ templates/
│   ├─ index.html
│   ├─ upload.html
│   ├─ results.html
│   └─ trends.html
├─ static/
│   ├─ css/
│   ├─ js/
│   ├─ uploads/
│   └─ assets/    # images, screenshots, demo thumbnail
🤝 Credits
This project is open for personal and educational use.

If you use it in your projects or demos, please give credit:


Social Media Content Analyzer by RITESH KUMAR
GitHub: https://github.com/riteshbhai70/SocialMediaContentAnalyzer
📌 License
MIT License

**💡 Future Enhancements**
User authentication & multi-user support.

Real-time social media API integration for trending topics.

AI-powered content suggestions using GPT models.

Export results to PDF or CSV.

Mobile-friendly UI improvements.

