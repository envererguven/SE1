import requests
import os

INGEST_URL = os.getenv("INGEST_URL", "http://ingestion:8000") + "/insert"

samples = [
    {"singer": "The Beatles", "song_name": "Hey Jude", "genre": "Rock", "lyrics": "Hey Jude, don't make it bad..."},
    {"singer": "The Beatles", "song_name": "Let It Be", "genre": "Rock", "lyrics": "When I find myself in times of trouble..."},
    {"singer": "Adele", "song_name": "Hello", "genre": "Pop", "lyrics": "Hello, it's me..."},
    {"singer": "Adele", "song_name": "Rolling in the Deep", "genre": "Pop", "lyrics": "There's a fire starting in my heart..."},
    {"singer": "Ed Sheeran", "song_name": "Shape of You", "genre": "Pop", "lyrics": "The club isn't the best place to find a lover..."},
    {"singer": "Ed Sheeran", "song_name": "Perfect", "genre": "Pop", "lyrics": "I found a love for me..."},
    {"singer": "Taylor Swift", "song_name": "Shake It Off", "genre": "Pop", "lyrics": "I shake it off, I shake it off..."},
    {"singer": "Taylor Swift", "song_name": "Blank Space", "genre": "Pop", "lyrics": "Got a long list of ex-lovers..."},
    {"singer": "Bob Dylan", "song_name": "Blowin' in the Wind", "genre": "Folk", "lyrics": "How many roads must a man walk down..."},
    {"singer": "Bob Dylan", "song_name": "Like a Rolling Stone", "genre": "Folk", "lyrics": "Once upon a time you dressed so fine..."},
    {"singer": "Michael Jackson", "song_name": "Thriller", "genre": "Pop", "lyrics": "It's close to midnight..."},
    {"singer": "Michael Jackson", "song_name": "Billie Jean", "genre": "Pop", "lyrics": "She was more like a beauty queen..."},
    {"singer": "Queen", "song_name": "Bohemian Rhapsody", "genre": "Rock", "lyrics": "Is this the real life? Is this just fantasy?..."},
    {"singer": "Queen", "song_name": "We Will Rock You", "genre": "Rock", "lyrics": "Buddy, you're a boy, make a big noise..."},
    {"singer": "Beyoncé", "song_name": "Halo", "genre": "R&B", "lyrics": "Remember those walls I built..."},
    {"singer": "Beyoncé", "song_name": "Single Ladies", "genre": "R&B", "lyrics": "If you like it then you shoulda put a ring on it..."},
    {"singer": "Elvis Presley", "song_name": "Hound Dog", "genre": "Rock", "lyrics": "You ain't nothin' but a hound dog..."},
    {"singer": "Elvis Presley", "song_name": "Jailhouse Rock", "genre": "Rock", "lyrics": "The warden threw a party in the county jail..."},
    {"singer": "Madonna", "song_name": "Like a Virgin", "genre": "Pop", "lyrics": "I made it through the wilderness..."},
    {"singer": "Madonna", "song_name": "Vogue", "genre": "Pop", "lyrics": "Strike a pose..."},
]

for sample in samples:
    requests.post(INGEST_URL, json=sample)
print("Sample data inserted.")
