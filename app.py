# โค้ดที่แก้ไขแล้วสำหรับ app.py:
import requests
import pandas as pd
import random
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from fuzzywuzzy import process

app = Flask(__name__)
CORS(app)

# TMDB API Key ของคุณ
TMDB_API_KEY = 'b0dc5b38c69dceede50641f32c400d31'

# โหลด dataset เดิม (สมมติว่าไฟล์อยู่ในโฟลเดอร์เดียวกัน)
try:
    df_movies = pd.read_csv('movies.csv')
    df_ratings = pd.read_csv('ratings.csv')
except FileNotFoundError:
    print("Error: movies.csv or ratings.csv not found. Please ensure they are in the same directory.")
    df_movies = pd.DataFrame(columns=['movieId', 'title', 'genres'])
    df_ratings = pd.DataFrame(columns=['userId', 'movieId', 'rating', 'timestamp'])

if not df_ratings.empty:
    rating_mean = df_ratings.groupby('movieId')['rating'].mean().to_dict()
    df_movies['avg_rating'] = df_movies['movieId'].map(rating_mean)
else:
    df_movies['avg_rating'] = None

if not df_movies.empty and 'movieId' in df_movies.columns:
    df_movies.set_index('movieId', inplace=True)
    movie_genres_map = df_movies['genres'].to_dict()
    df_movies.reset_index(inplace=True)

# *** TMDB Genre ID Mapping ***
TMDB_GENRE_MAP = {
    28: 'Action', 12: 'Adventure', 16: 'Animation', 35: 'Comedy', 80: 'Crime',
    99: 'Documentary', 18: 'Drama', 10751: 'Family', 14: 'Fantasy', 36: 'History',
    27: 'Horror', 10402: 'Music', 9648: 'Mystery', 10749: 'Romance', 878: 'Science Fiction',
    10770: 'TV Movie', 53: 'Thriller', 10752: 'War', 37: 'Western'
}
TMDB_GENRE_NAMES_LOWER = {v.lower(): k for k, v in TMDB_GENRE_MAP.items()}


def map_tmdb_genres(genre_ids):
    if not genre_ids:
        return ''
    genres = [TMDB_GENRE_MAP.get(gid, '') for gid in genre_ids]
    return '|'.join(filter(None, genres))


def get_best_match(title, titles_list, cutoff=75):
    if not titles_list:
        return None
    match, score = process.extractOne(title, titles_list)
    return match if score >= cutoff else None

def get_best_match_row(title):
    if df_movies.empty or 'title' not in df_movies.columns:
        return None
    matched_title = get_best_match(title.lower(), df_movies['title'].str.lower().tolist())
    if matched_title:
        row = df_movies[df_movies['title'].str.lower().str.strip() == matched_title]
        if not row.empty:
            return row.iloc[0]
    return None

def search_local_by_genre(genres_list):
    if df_movies.empty:
        return []
        
    result = df_movies.copy()

    for genre in genres_list:
        genre_clean = genre.strip()
        if genre_clean:
            result = result[result['genres'].str.contains(genre_clean, case=False, na=False)]
            
    if result.empty:
        return []

    result = result.sort_values(by='avg_rating', ascending=False, na_position='last')
    
    result = result.head(5)
        
    movies = []
    for _, row in result.iterrows():
        title = row['title']
        genres = row['genres']
        avg_rating = round(row['avg_rating'], 2) if not pd.isna(row['avg_rating']) else ''
        movies.append({
            'title': title,
            'genre': genres,
            'rating': avg_rating,
            'description': '', 
            'poster': '',
            'more_info': ''
        })
    return movies


def search_tmdb_movies(keyword):
    """
    ค้นหาผ่าน TMDB API โดยรองรับ Keyword และ Genre ผสมกัน
    """
    
    # --- 1. แยก Keyword และ Genre ออกจากกัน ---
    parts = [p.strip().lower() for p in keyword.split(',') if p.strip()]
    
    actual_keywords = [] # คำค้นหาที่ไม่ใช่ Genre
    required_genres = [] # Genre ที่ผู้ใช้ต้องการ (เช่น 'romance', 'action')
    required_genre_ids = [] # Genre ID สำหรับการกรอง

    for part in parts:
        if part in TMDB_GENRE_NAMES_LOWER:
            required_genres.append(part)
            required_genre_ids.append(TMDB_GENRE_NAMES_LOWER[part])
        else:
            actual_keywords.append(part)
    
    # รวม Keyword กลับเป็น Query String สำหรับ TMDB
    tmdb_query = ' '.join(actual_keywords)
    
    # หากไม่มี Keyword เลย แต่มี Genre: ให้ทำการค้นหาด้วย Genre เท่านั้น (แบบเดิม)
    if not tmdb_query and required_genre_ids:
        # ใช้ TMDB Discovery API สำหรับการค้นหา Genre
        genres_param = ','.join(map(str, required_genre_ids))
        disc_url = f'https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genres_param}&sort_by=popularity.desc'
        r_disc = requests.get(disc_url)
        results = r_disc.json().get('results', [])
        
        # ใช้ Logic ของ Local Dataset หาก TMDB ค้นหาไม่เจอ
        if not results:
             return search_local_by_genre(required_genres) 
        
    # --- 2. ใช้ TMDB Search API สำหรับ Keyword (และดึง 2 หน้า) ---
    elif tmdb_query:
        keyword_terms = tmdb_query.split()
        if len(keyword_terms) > 3:
            # ใช้แค่ 3 คำแรกในการค้นหา TMDB API ถ้าคำค้นหายาวเกินไป
            tmdb_api_query = ' '.join(keyword_terms[:3])
        else:
            tmdb_api_query = tmdb_query
            
        all_results = []
        for page in range(1, 3): 
            url = f'https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={tmdb_api_query}&page={page}'
            r = requests.get(url)
            page_results = r.json().get('results', [])
            all_results.extend(page_results)
            if not page_results:
                break
        
        results = all_results
    else:
        # ไม่มีทั้ง Keyword และ Genre
        return []

    # 3. จัดการผลลัพธ์: กรองตาม Genre ที่ระบุ, Boosting, และเลือกอันดับต้นๆ
    
    if not results:
        return []

    # 3.1. [New Step] กรองผลลัพธ์ตาม Genre ที่ระบุ (ถ้ามี Keyword Search)
    if required_genres and tmdb_query:
        # ใช้ TMDB Genre ID ที่เป็นตัวเลขในการกรอง
        
        # TMDB คืน Genre ID มาเป็น list, เราต้องเช็คว่าทุก ID ที่ต้องการ (required_genre_ids)
        # อยู่ใน list ของหนังเรื่องนั้นหรือไม่ (ALL Logic)
        filtered_results = []
        for movie in results:
            movie_genre_ids = movie.get('genre_ids', [])
            
            # เช็คว่า Genre ID ที่ต้องการทั้งหมด ถูกรวมอยู่ใน Genre ID ของหนังเรื่องนี้หรือไม่
            is_valid_genre = all(req_id in movie_genre_ids for req_id in required_genre_ids)
            
            if is_valid_genre:
                filtered_results.append(movie)
        
        results = filtered_results


    # 3.2. กรองและเพิ่มคะแนน (Boosting)
    if not results:
        return []
        
    keyword_lower = tmdb_query 
    keyword_terms = keyword_lower.split() 
    keyword_phrase = keyword_lower 
    is_long_query = len(keyword_terms) > 3 

    def calculate_score(movie):
        title = movie.get('title', '').lower()
        overview = movie.get('overview', '').lower()
        score = movie.get('popularity', 0)
        term_score_boost = 0
        
        has_phrase_in_overview = keyword_phrase in overview
        
        if is_long_query:
            matching_terms_count = sum(1 for term in keyword_terms if term in overview)
            term_score_boost = matching_terms_count * 500.0
        else:
            has_all_terms_in_overview = all(term in overview for term in keyword_terms)
            term_score_boost = 2000.0 if has_all_terms_in_overview else 0

        if has_phrase_in_overview:
            score += 20000.0
        
        score += term_score_boost
        
        if keyword_phrase in title:
            score += 10000.0
            
        return score

    scored_results = []
    for movie in results:
        score = calculate_score(movie)
        scored_results.append((score, movie))
    
    scored_results.sort(key=lambda x: x[0], reverse=True)
    
    filtered_results = [movie for score, movie in scored_results]
    
    # 3.3. เลือก 5 อันดับแรกที่ถูก Boost แล้ว (ยกเลิกการสุ่ม)
    selected_movies = filtered_results[:5] 
    
    movies = []

    for movie in selected_movies: 
        title = movie.get('title', '')
        if not title:
            continue
        
        description = movie.get('overview', '')
        tmdb_genre_text = map_tmdb_genres(movie.get('genre_ids', []))
        
        avg_rating = ''
        matched_row = get_best_match_row(title)

        if matched_row is not None:
            avg_rating = round(matched_row['avg_rating'], 2) if not pd.isna(matched_row['avg_rating']) else ''
        
        poster_path = movie.get('poster_path', '')
        poster_url = f'https://image.tmdb.org/t/p/w500{poster_path}' if poster_path else ''
        more_info = f'https://www.themoviedb.org/movie/{movie.get("id")}'
        
        movies.append({
            'title': title,
            'genre': tmdb_genre_text, 
            'description': description,
            'rating': avg_rating if avg_rating else round(movie.get('vote_average', 0), 2), 
            'poster': poster_url,
            'more_info': more_info
        })

    return movies

def search_by_rating(expression):
    """ค้นหาภาพยนตร์ตาม rating เฉลี่ย"""
    pattern = r'rating\s*([<>]=?|=)\s*([0-9.]+)'
    m = re.match(pattern, expression.lower())
    if not m or df_movies.empty:
        return []
    op, val = m.groups()
    val = float(val)

    if op == '>':
        result = df_movies[df_movies['avg_rating'] > val]
    elif op == '<':
        result = df_movies[df_movies['avg_rating'] < val]
    elif op == '>=':
        result = df_movies[df_movies['avg_rating'] >= val]
    elif op == '<=':
        result = df_movies[df_movies['avg_rating'] <= val]
    else:
        result = df_movies[df_movies['avg_rating'] == val]

    result = result.head(5)
    
    movies = []
    for _, row in result.iterrows():
        title = row['title']
        genres = row['genres']
        avg_rating = round(row['avg_rating'], 2) if not pd.isna(row['avg_rating']) else ''
        movies.append({
            'title': title,
            'genre': genres,
            'rating': avg_rating,
            'description': '',
            'poster': '',
            'more_info': ''
        })
    return movies

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    keyword = data.get('keyword', '').strip()
    if not keyword:
        return jsonify({'movies': []})

    if keyword.lower().startswith('rating'):
        movies = search_by_rating(keyword)
    else:
        movies = search_tmdb_movies(keyword)

    return jsonify({'movies': movies})

if __name__ == '__main__':
    app.run(debug=True, port=5000)