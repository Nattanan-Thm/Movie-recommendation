document.getElementById('recommendButton').addEventListener('click', getRecommendations);
document.getElementById('keywordInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') getRecommendations();
});

function setGenre(genre) {
    document.getElementById('keywordInput').value = genre; 
    getRecommendations(); 
}

function getRecommendations() {
    const keyword = document.getElementById('keywordInput').value.trim();
    if (!keyword) {
        alert('Please enter a keyword or select a genre.');
        return;
    }

    // แสดงสถานะ Loading
    document.getElementById('featured-movie').innerHTML = '<div class="featured-movie-card" style="text-align: center;"><div class="featured-details" style="width: 100%; padding: 30px 0;">Loading recommendations for "' + keyword + '"...</div></div>';
    document.getElementById('suggested-movies').innerHTML = '';
    document.getElementById('suggested-section').style.display = 'none';

    // *** การเรียก API ไปยัง Backend ของคุณ (Flask) ***
    fetch('http://127.0.0.1:5000/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyword })
    })
    .then(res => {
        if (!res.ok) {
            throw new Error(`HTTP error! Status: ${res.status}`);
        }
        return res.json();
    })
    .then(data => {
        const movies = data.movies || [];
        
        // 1. จัดการกรณีไม่พบผลลัพธ์
        if (movies.length === 0) {
            document.getElementById('featured-movie').innerHTML = '<div class="featured-movie-card"><div class="featured-details" style="text-align: center; width: 100%;">No results found for "' + keyword + '". Please try a different term.</div></div>';
            return;
        }
        
        // 2. แสดง Featured movie (หนังเรื่องแรก)
        const featured = movies[0];
        document.getElementById('featured-movie').innerHTML = `
            <div class="featured-movie-card">
                <img class="featured-poster" src="${featured.poster || 'https://via.placeholder.com/170x250?text=No+Image'}" alt="${featured.title}">
                <div class="featured-details">
                    <div class="featured-title">${featured.title}</div>
                    ${featured.genre ? `<div class="featured-genre">${featured.genre}</div>` : ''}
                    <div class="featured-rating">Rating: ${featured.rating || '-'}</div>
                    <div class="featured-description">${featured.description || 'No description available.'}</div>
                    <button class="more-info-btn" onclick="window.open('${featured.more_info || '#'}', '_blank')">More Info</button>
                </div>
            </div>
        `;
        
        // 3. แสดง Suggested movies (หนังเรื่องที่ 2-5)
        const suggested = movies.slice(1, 5);
        if (suggested.length > 0) {
            document.getElementById('suggested-section').style.display = 'block';
            document.getElementById('suggested-movies').innerHTML = suggested.map(movie => `
                <div class="suggested-item">
                    <img class="suggested-poster" src="${movie.poster || 'https://via.placeholder.com/110x160?text=No+Image'}" alt="${movie.title}">
                    
                    <div class="suggested-details-wrapper">
                        <div class="suggested-title">${movie.title}</div>
                        ${movie.genre ? `<div class="suggested-genre">${movie.genre}</div>` : ''}
                        <div class="suggested-rating">Rating: ${movie.rating || '-'}</div>
                    </div>

                    <button class="suggested-more-btn" onclick="window.open('${movie.more_info || '#'}', '_blank')">More Info</button>
                </div>
            `).join('');
        } else {
            document.getElementById('suggested-section').style.display = 'none';
        }
    })
    .catch((error) => {
        console.error('Error fetching recommendations:', error);
        document.getElementById('featured-movie').innerHTML = '<div class="featured-movie-card"><div class="featured-details" style="text-align: center; width: 100%; color: #ff2d2d;">Connection Error: Could not reach the recommendation server. Please ensure the backend is running on http://127.0.0.1:5000.</div></div>';
        document.getElementById('suggested-section').style.display = 'none';
    });
}