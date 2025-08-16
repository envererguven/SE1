document.getElementById('insertForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        singer: document.getElementById('singer').value,
        song_name: document.getElementById('song_name').value,
        genre: document.getElementById('genre').value,
        lyrics: document.getElementById('lyrics').value
    };
    const response = await fetch('http://localhost:5000/insert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    const result = await response.json();
    document.getElementById('insertResult').innerText = JSON.stringify(result);
});

document.getElementById('searchBtn').addEventListener('click', async () => {
    const query = document.getElementById('query').value;
    const type = document.getElementById('type').value;
    const genre = document.getElementById('genreFilter').value;
    let url = `http://localhost:5000/search?q=${encodeURIComponent(query)}&type=${type}`;
    if (genre) url += `&genre=${encodeURIComponent(genre)}`;
    
    const response = await fetch(url);
    const data = await response.json();
    const resultsDiv = document.getElementById('searchResults');
    resultsDiv.innerHTML = '';
    data.results.forEach(result => {
        const div = document.createElement('div');
        div.className = 'result';
        div.innerHTML = `
            <strong>${result.song_name}</strong> by ${result.singer} (${result.genre})<br>
            Lyrics: ${result.lyrics_snippet}<br>
            Score: ${result.score.toFixed(2)}
        `;
        resultsDiv.appendChild(div);
    });
});
