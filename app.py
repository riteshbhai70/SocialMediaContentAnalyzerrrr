import os
import PyPDF2
from PIL import Image
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import re
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import json
from datetime import datetime
import uuid
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import textstat
import numpy as np
from wordcloud import WordCloud
from dotenv import load_dotenv
import tempfile
import shutil

import requests
import base64
# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()  # Temporary directory
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size



ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename):
    """Generate unique filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    name, ext = os.path.splitext(original_filename)
    return f"{timestamp}_{name}{ext}"

# Enhanced Engagement Rules
ENGAGEMENT_RULES = {
    'questions': [
        "Ask more thought-provoking questions to engage readers",
        "Include a clear call-to-action question",
        "Use rhetorical questions to spark curiosity"
    ],
    'hashtags': [
        "Add 3-5 relevant hashtags for better discoverability",
        "Research trending hashtags in your niche",
        "Create a branded hashtag for consistency"
    ],
    'length': [
        "Ideal social media post length: 150-300 characters",
        "Consider breaking long content into a thread",
        "Use bullet points or numbered lists for readability"
    ],
    'sentiment': [
        "Use more positive and emotional language",
        "Incorporate power words that evoke emotion",
        "Add relevant emojis to convey tone"
    ],
    'structure': [
        "Start with a compelling hook or headline",
        "Use line breaks to improve mobile readability",
        "Include statistics or data to build credibility"
    ]
}

def extract_text_from_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text.strip() if text.strip() else "No text could be extracted from the PDF"
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"


# def extract_text_from_image(file_path):
#     """Extract text from image - OCR disabled in production"""
#     return "Image OCR is temporarily disabled. Please upload PDF files for text analysis. (OCR requires system dependencies that are not available in this deployment environment)"

# # Also add at the top of your file:
# OCR_ENABLED = False  # Set to False for Render deployment




def extract_text_from_image(file_path):
    """Use free OCR API"""
    try:
        # Convert image to base64
        with open(file_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode()
        
        # Use free OCR.space API
        payload = {
            'base64Image': f'data:image/jpeg;base64,{base64_image}',
            'apikey': 'K89977995688957',  # Free API key
            'language': 'eng'
        }
        
        response = requests.post('https://api.ocr.space/parse/image', data=payload)
        result = response.json()
        
        if result['IsErroredOnProcessing']:
            return "OCR processing failed"
        
        parsed_results = result.get('ParsedResults', [])
        if parsed_results:
            return parsed_results[0].get('ParsedText', 'No text found')
        return "No text found"
    
    except Exception as e:
        return f"OCR Error: {str(e)}"




def generate_word_frequency(text, top_n=15):
    """Generate word frequency analysis"""
    if not text or "Error" in text or "No text" in text:
        return [], []
    
    # Clean and tokenize text
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word.isalnum() and len(word) > 2 and word not in stop_words]
    
    # Count frequency
    word_freq = Counter(words)
    top_words = word_freq.most_common(top_n)
    
    return [word for word, freq in top_words], [freq for word, freq in top_words]

def generate_wordcloud_image(text):
    """Generate word cloud image as base64"""
    if not text or "Error" in text or "No text" in text:
        return None
    
    try:
        # Generate word cloud
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            max_words=100,
            colormap='viridis',
            contour_width=1,
            contour_color='steelblue'
        ).generate(text)
        
        # Convert to base64
        img_buffer = io.BytesIO()
        wordcloud.to_image().save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_data = base64.b64encode(img_buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_data}"
    except Exception as e:
        print(f"Word cloud error: {e}")
        return None

def generate_frequency_chart(words, frequencies):
    """Generate frequency chart as base64"""
    if not words:
        return None
    
    try:
        plt.figure(figsize=(12, 6))
        colors = plt.cm.viridis(np.linspace(0, 1, len(words)))
        bars = plt.barh(words, frequencies, color=colors)
        plt.title('Top 15 Most Frequent Words', fontsize=14, fontweight='bold')
        plt.xlabel('Frequency', fontweight='bold')
        plt.gca().invert_yaxis()
        
        # Add value labels on bars
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                    f'{int(width)}', ha='left', va='center', fontweight='bold')
        
        plt.tight_layout()
        
        # Convert to base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='PNG', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        img_data = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{img_data}"
    except Exception as e:
        print(f"Chart error: {e}")
        return None

def advanced_text_analysis(text):
    """Perform advanced text analysis"""
    if not text or "Error" in text or "No text" in text:
        return {}
    
    analysis = {}
    
    try:
        # Readability scores
        analysis['flesch_reading_ease'] = textstat.flesch_reading_ease(text)
        analysis['flesch_kincaid_grade'] = textstat.flesch_kincaid_grade(text)
        analysis['smog_index'] = textstat.smog_index(text)
        analysis['coleman_liau_index'] = textstat.coleman_liau_index(text)
        analysis['automated_readability_index'] = textstat.automated_readability_index(text)
        
        # Text statistics
        analysis['avg_sentence_length'] = textstat.avg_sentence_length(text)
        analysis['avg_syllables_per_word'] = textstat.avg_syllables_per_word(text)
        analysis['difficult_words'] = textstat.difficult_words(text)
        analysis['total_words'] = len(word_tokenize(text))
        analysis['total_sentences'] = len(sent_tokenize(text))
        analysis['total_characters'] = len(text)
        
        # Sentiment breakdown
        blob = TextBlob(text)
        analysis['subjectivity'] = blob.sentiment.subjectivity
        analysis['polarity'] = blob.sentiment.polarity
        
        # Additional metrics
        analysis['avg_words_per_sentence'] = analysis['total_words'] / max(analysis['total_sentences'], 1)
        analysis['lexical_diversity'] = len(set(word_tokenize(text.lower()))) / max(analysis['total_words'], 1)
        
    except Exception as e:
        print(f"Advanced analysis error: {e}")
    
    return analysis

def get_content_category(text):
    """Categorize content based on keywords"""
    categories = {
        'Technology': ['tech', 'software', 'code', 'programming', 'ai', 'machine learning', 'data', 'computer', 'digital', 'app'],
        'Business': ['business', 'startup', 'entrepreneur', 'marketing', 'sales', 'strategy', 'company', 'finance', 'investment'],
        'Lifestyle': ['life', 'health', 'wellness', 'fitness', 'travel', 'food', 'hobby', 'home', 'family', 'personal'],
        'Education': ['learn', 'education', 'study', 'knowledge', 'tutorial', 'course', 'school', 'university', 'training'],
        'Entertainment': ['movie', 'music', 'game', 'fun', 'entertainment', 'show', 'film', 'song', 'artist'],
        'News': ['news', 'update', 'report', 'breaking', 'current', 'events', 'politics', 'world']
    }
    
    text_lower = text.lower()
    scores = {}
    
    for category, keywords in categories.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        scores[category] = score
    
    best_category = max(scores.items(), key=lambda x: x[1])[0] if max(scores.values()) > 0 else 'General'
    confidence = min(100, max(scores.values()) * 20)  # Simple confidence calculation
    
    return best_category, confidence

def platform_specific_analysis(text):
    """Provide platform-specific recommendations"""
    word_count = len(word_tokenize(text))
    char_count = len(text)
    
    platforms = {
        'Twitter': {
            'ideal_length': 280,
            'current_length': char_count,
            'status': 'Perfect' if char_count <= 280 else 'Too Long',
            'score': min(100, max(0, 100 - (max(0, char_count - 280) / 280 * 100))),
            'suggestion': 'Perfect for Twitter!' if char_count <= 280 else f'Reduce by {char_count-280} characters for Twitter',
            'icon': 'twitter',
            'color': '#1DA1F2'
        },
        'Instagram': {
            'ideal_length': 125,
            'current_length': char_count,
            'status': 'Great' if char_count <= 125 else 'Consider shortening',
            'score': min(100, max(0, 100 - (max(0, char_count - 125) / 125 * 100))),
            'suggestion': 'Great caption length!' if char_count <= 125 else 'Ideal Instagram captions are shorter (125 chars)',
            'icon': 'instagram',
            'color': '#E4405F'
        },
        'Facebook': {
            'ideal_length': 40,
            'current_length': word_count,
            'status': 'Optimal' if word_count <= 40 else 'Good',
            'score': min(100, max(0, 100 - (max(0, word_count - 40) / 40 * 100))),
            'suggestion': 'Perfect for Facebook engagement!' if word_count <= 40 else 'Consider shorter posts for better engagement',
            'icon': 'facebook',
            'color': '#1877F2'
        },
        'LinkedIn': {
            'ideal_length': 100,
            'current_length': word_count,
            'status': 'Professional' if word_count >= 50 else 'Too short',
            'score': min(100, max(0, (word_count / 100) * 100)),
            'suggestion': 'Professional length' if word_count >= 50 else 'Add more professional insights',
            'icon': 'linkedin',
            'color': '#0A66C2'
        }
    }
    
    return platforms

def optimal_posting_times():
    """Suggest optimal posting times based on analytics"""
    return {
        'Twitter': ['9:00 AM', '12:00 PM', '3:00 PM', '5:00 PM'],
        'Instagram': ['11:00 AM', '1:00 PM', '3:00 PM', '5:00 PM'],
        'Facebook': ['9:00 AM', '1:00 PM', '3:00 PM'],
        'LinkedIn': ['7:30 AM', '10:30 AM', '12:00 PM', '5:30 PM']
    }

def analyze_engagement(text):
    """Analyze text and provide engagement suggestions"""
    if not text or "Error" in text or "No text" in text:
        return {
            'engagement_score': 0,
            'sentiment_score': 0,
            'word_count': 0,
            'sentence_count': 0,
            'unique_words': 0,
            'suggestions': ["Unable to analyze: No text content found"],
            'recommended_hashtags': []
        }
    
    try:
        blob = TextBlob(text)
        sentiment_score = blob.sentiment.polarity
        
        words = word_tokenize(text)
        word_count = len(words)
        sentences = sent_tokenize(text)
        sentence_count = len(sentences)
        
        stop_words = set(stopwords.words('english'))
        filtered_words = [word.lower() for word in words if word.isalnum() and word.lower() not in stop_words]
        unique_words = len(set(filtered_words))
        
        # Enhanced engagement scoring
        engagement_score = min(100, max(0, 
            (sentiment_score + 1) * 20 +  # Sentiment: 40 points max
            min(word_count / 15, 25) +    # Length: 25 points max
            min(unique_words / 8, 20) +   # Vocabulary: 20 points max
            (15 if sentence_count > 2 else 5)  # Structure: 15 points
        ))
        
        suggestions = generate_suggestions(text, sentiment_score, word_count, filtered_words)
        
        return {
            'engagement_score': round(engagement_score, 2),
            'sentiment_score': round(sentiment_score, 2),
            'word_count': word_count,
            'sentence_count': sentence_count,
            'unique_words': unique_words,
            'suggestions': suggestions,
            'recommended_hashtags': generate_hashtags(filtered_words)
        }
    except Exception as e:
        print(f"Engagement analysis error: {e}")
        return {
            'engagement_score': 0,
            'sentiment_score': 0,
            'word_count': 0,
            'sentence_count': 0,
            'unique_words': 0,
            'suggestions': ["Error in analysis"],
            'recommended_hashtags': []
        }
def generate_suggestions(text, sentiment_score, word_count, keywords):
    """Generate engagement improvement suggestions"""
    suggestions = []
    
    # Length-based suggestions
    if word_count < 40:
        suggestions.append("Consider adding more detail and context to your content")
    elif word_count > 400:
        suggestions.append("Content is quite long. Consider breaking it into multiple posts")
    
    # Sentiment-based suggestions
    if sentiment_score < -0.2:
        suggestions.append("Try using more positive language to improve engagement")
    elif sentiment_score > 0.6:
        suggestions.append("Great positive tone! This should resonate well with audiences")
    
    # Question detection
    if '?' not in text:
        suggestions.append(ENGAGEMENT_RULES['questions'][0])
    
    # Hashtag suggestions
    hashtag_count = len(re.findall(r'#\w+', text))
    if hashtag_count < 2:
        suggestions.append(ENGAGEMENT_RULES['hashtags'][0])
    elif hashtag_count > 8:
        suggestions.append("Consider reducing hashtags to 3-5 most relevant ones")
    
    # Structure suggestions
    if len(text.split('\n')) < 2:
        suggestions.append(ENGAGEMENT_RULES['structure'][1])
    
    # Reading level suggestions
    try:
        flesch_score = textstat.flesch_reading_ease(text)
        if flesch_score < 60:
            suggestions.append("Consider simplifying language for better readability")
    except:
        pass
    
    # Ensure we have suggestions
    if not suggestions:
        suggestions.append("Add a clear call-to-action to improve engagement")
        suggestions.append("Include relevant statistics or data points")
        suggestions.append("Consider adding visual elements to complement your text")
    
    return suggestions[:5]

def generate_hashtags(keywords):
    """Generate relevant hashtags based on content"""
    if not keywords:
        return []
    
    category_keywords = {
        'technology': ['tech', 'digital', 'innovation', 'ai', 'software', 'programming', 'coding', 'development', 'computer'],
        'business': ['business', 'entrepreneur', 'startup', 'success', 'marketing', 'sales', 'growth', 'strategy', 'leadership'],
        'lifestyle': ['life', 'lifestyle', 'motivation', 'inspiration', 'daily', 'health', 'wellness', 'happiness', 'mindfulness'],
        'education': ['learning', 'education', 'knowledge', 'tips', 'howto', 'tutorial', 'study', 'skills', 'training'],
        'travel': ['travel', 'adventure', 'explore', 'wanderlust', 'vacation', 'journey', 'destination'],
        'food': ['food', 'recipe', 'cooking', 'delicious', 'restaurant', 'culinary', 'nutrition', 'healthy']
    }
    
    hashtags = []
    text_combined = ' '.join([str(k).lower() for k in keywords])
    
    # Find relevant categories
    matched_categories = []
    for category, words in category_keywords.items():
        if any(word in text_combined for word in words):
            matched_categories.append(category)
            hashtags.extend([category.capitalize(), 'Tips'])
    
    # Add context-based hashtags
    if matched_categories:
        primary_category = matched_categories[0]
        category_hashtags = {
            'technology': ['Tech', 'DigitalTransformation', 'FutureTech', 'Innovation'],
            'business': ['Entrepreneurship', 'BusinessGrowth', 'SuccessMindset', 'StartupLife'],
            'lifestyle': ['LifeHacks', 'PersonalGrowth', 'Mindfulness', 'SelfImprovement'],
            'education': ['Learning', 'SkillDevelopment', 'KnowledgeShare', 'EducationForAll'],
            'travel': ['TravelGram', 'AdventureTime', 'ExploreWorld', 'Wanderlust'],
            'food': ['Foodie', 'Delicious', 'CulinaryArts', 'FoodLover']
        }
        hashtags.extend(category_hashtags.get(primary_category, []))
    
    # Add general popular hashtags
    general_hashtags = ['SocialMedia', 'Content', 'Engagement', 'DigitalMarketing', 'OnlinePresence', 'ContentCreation']
    hashtags.extend(general_hashtags[:3])
    
    return list(set(hashtags))[:10]  # Return up to 10 unique hashtags

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

@app.route('/analyze', methods=['POST'])
def analyze_content():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('upload_page'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('upload_page'))
    
    if file and allowed_file(file.filename):
        # Generate unique filename with timestamp
        original_filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        file_extension = unique_filename.rsplit('.', 1)[1].lower()
        
        # Extract text based on file type
        if file_extension == 'pdf':
            extracted_text = extract_text_from_pdf(file_path)
        else:
            extracted_text = extract_text_from_image(file_path)
        
        # Basic engagement analysis
        analysis_results = analyze_engagement(extracted_text)
        
        # Advanced analytics
        word_freq_words, word_freq_counts = generate_word_frequency(extracted_text, 15)
        wordcloud_image = generate_wordcloud_image(extracted_text)
        frequency_chart = generate_frequency_chart(word_freq_words, word_freq_counts)
        advanced_analysis = advanced_text_analysis(extracted_text)
        content_category, category_confidence = get_content_category(extracted_text)
        platform_analysis = platform_specific_analysis(extracted_text)
        optimal_times = optimal_posting_times()
        
        # Clean up uploaded file immediately after processing
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"File cleanup error: {e}")
        
        # Use mock trending searches (no database needed)
        trending_searches = get_all_trending_searches()
        zipped_data = list(zip(word_freq_words, word_freq_counts))
        
        return render_template('results.html', 
                            zipped_data=zipped_data,
                            trending_searches=trending_searches,
                            results=analysis_results,
                            text_preview=extracted_text[:1200] + "..." if len(extracted_text) > 1200 else extracted_text,
                            filename=unique_filename,
                            original_filename=original_filename,
                            # Advanced analytics
                            word_freq_words=word_freq_words,
                            word_freq_counts=word_freq_counts,
                            wordcloud_image=wordcloud_image,
                            frequency_chart=frequency_chart,
                            advanced_analysis=advanced_analysis,
                            content_category=content_category,
                            category_confidence=category_confidence,
                            platform_analysis=platform_analysis,
                            optimal_times=optimal_times,
                            extracted_text_length=len(extracted_text))
    
    flash('Invalid file type. Please upload PDF, PNG, JPG, or JPEG files.', 'error')
    return redirect(url_for('upload_page'))

@app.route('/api/copy-hashtags', methods=['POST'])
def copy_hashtags():
    """API endpoint to copy hashtags to clipboard"""
    data = request.get_json()
    hashtags = data.get('hashtags', [])
    
    if not hashtags:
        return jsonify({'error': 'No hashtags provided'}), 400
    
    hashtags_text = ' '.join([f'#{tag}' for tag in hashtags])
    return jsonify({'hashtags_text': hashtags_text, 'count': len(hashtags)})

@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('upload_page'))

@app.errorhandler(500)
def internal_error(error):
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('upload_page'))

# Mock trending searches (no API calls needed)
def get_twitter_trends():
    return ["AI Innovations", "Tech News", "Digital Marketing", "Content Creation", "Social Media Tips"]

def get_google_trends():
    return ["Latest Tech", "Business Strategies", "Market Trends", "Innovation", "Digital Transformation"]

def get_instagram_trends():
    return ["InstagramReels", "TrendingNow", "ViralContent", "SocialMediaTips", "ContentCreator"]

def get_linkedin_trends():
    return ["Remote Work", "Career Growth", "Professional Development", "Industry Insights", "Business Leadership"]

def get_all_trending_searches():
    """Get trending searches from all platforms (mock data)"""
    return {
        'twitter': {
            'name': 'Twitter',
            'trends': get_twitter_trends(),
            'icon': 'twitter',
            'color': '#1DA1F2'
        },
        'instagram': {
            'name': 'Instagram',
            'trends': get_instagram_trends(),
            'icon': 'instagram',
            'color': '#E4405F'
        },
        'linkedin': {
            'name': 'LinkedIn',
            'trends': get_linkedin_trends(),
            'icon': 'linkedin',
            'color': '#0A66C2'
        },
        'google': {
            'name': 'Google Trends',
            'trends': get_google_trends(),
            'icon': 'google',
            'color': '#4285F4'
        }
    }

@app.route('/api/trends')
def get_trends_api():
    """API endpoint to get trending searches"""
    trends = get_all_trending_searches()
    return jsonify(trends)

@app.route('/trends')
def trends_page():
    """Page showing all trending searches"""
    trending_searches = get_all_trending_searches()
    return render_template('trends.html', trending_searches=trending_searches)

# Clean up temporary directory on app shutdown
import atexit

def cleanup_temp_folder():
    try:
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            shutil.rmtree(app.config['UPLOAD_FOLDER'])
    except Exception as e:
        print(f"Cleanup error: {e}")

atexit.register(cleanup_temp_folder)

if __name__ == '__main__':
    # Create temporary upload folder
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    print("✓ Social Media Content Analyzer is running!")
    print("✓ Database-free version")
    print("✓ Temporary file storage enabled")
    print("✓ Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
