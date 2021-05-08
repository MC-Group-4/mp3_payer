import sqlite3
class Database:

    def __init__(self):
        self.connection = sqlite3.connect('music.db')
        self.cursor = self.connection.cursor()

    def add_song(self,*song):
        sql = '''
        INSERT INTO songs(song_title, song_file, song_duration, artist_name, cover_art)
        VALUES(?,?,?,?,?)
        '''
        self.cursor.execute(sql, song)
        self.connection.commit()
        

    def get_songs(self):
        sql = '''
        SELECT * from songs
        '''
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def find_song_by_artist_name(self, artist_name):
        sql = '''
        SELECT * from songs where artist_name = ?
        '''
        self.cursor.execute(sql, (artist_name,))
        return self.cursor.fetchall()
        
    def find_song_by_id(self, id):
        sql = '''
        SELECT * FROM songs WHERE id = ?
        '''
        self.cursor.execute(sql, (id,))
        return self.cursor.fetchone()

    def find_song_by_song_title(self, song_title):
        sql = '''
        SELECT * FROM songs WHERE song_title = ?
        '''
        self.cursor.execute(sql, (song_title,))
        return self.cursor.fetchone()

    def update_song_title(self, song_title,  id):
        sql = '''
          UPDATE songs SET  song_title = ?, song_file = ? WHERE id = ?
        '''
        self.cursor.execute(sql, (song_title, f"{song_title}.mp3", id))
        self.connection.commit()

    def update_artist_name(self, artist_name,  id):
        sql = '''
          UPDATE songs SET  artist_name = ? WHERE id = ?
        '''
        self.cursor.execute(sql, (artist_name, id))
        self.connection.commit()

    def update_song_cover_art(self, id, cover_art):
        sql = '''
          UPDATE songs SET  cover_art = ? WHERE id = ?
        '''
        self.cursor.execute(sql, (cover_art, id))
        self.connection.commit()


    def delete_song(self, id):
        sql = "DELETE FROM songs WHERE id = ?"
        self.cursor.execute(sql, (id,))
        self.connection.commit()



# db = Database()
# for song in db.find_song_by_artist_name('Desiigner'):
#     print(song)
    # db.update_song_cover_art(song[0], 'desiigner.png')


    # sql = """
    #     CREATE TABLE IF NOT EXIST artists(
    #           id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         artist_name text primary key,
    #         cover_art text default "default.png"
    #     )
    # """
    # cursor.execute(sql)

    # sql = """
    #     CREATE TABLE IF NOT EXIST songs(
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         song_title text NOT NULL,
    #         song_file text NOT NULL UNIQUE,
    #         album_title text default 'unknown',
    #         song_duration real not null,
    #         artist_name text,
    #         cover_art text default 'default.png'
            
    #     )
    # """
    # cursor.execute(sql)