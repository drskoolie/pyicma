import sqlite3

class HadithDatabase:
    def __init__(self, db_name='db/hadith.db'):
        # Initialize and connect to the SQLite database
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.setup_tables()

    def setup_tables(self):
        # Create Hadiths, Narrators, and Isnads tables if they don't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Hadiths (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matn TEXT NOT NULL,
                comments TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Narrators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT,
                death_date DATE,
                reliability TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Isnads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hadith_id INTEGER NOT NULL,
                narrator_id INTEGER NOT NULL,
                next_narrator_id INTEGER,
                position_in_chain INTEGER,
                FOREIGN KEY (hadith_id) REFERENCES Hadiths(id),
                FOREIGN KEY (narrator_id) REFERENCES Narrators(id),
                FOREIGN KEY (next_narrator_id) REFERENCES Narrators(id)
            )
        ''')

        self.conn.commit()

    def add_hadith(self, matn, comments):
        # Insert a new hadith into the Hadiths table
        self.cursor.execute('''
            INSERT INTO Hadiths (matn, comments)
            VALUES (?, ?)
        ''', (matn, comments))
        self.conn.commit()
        return self.cursor.lastrowid  # Return the new hadith's ID

    def add_narrator(self, name, location=None, death_date=None, reliability=None):
        # Insert a new narrator into the Narrators table
        self.cursor.execute('''
            INSERT INTO Narrators (name, location, death_date, reliability)
            VALUES (?, ?, ?, ?)
        ''', (name, location, death_date, reliability))
        self.conn.commit()
        return self.cursor.lastrowid  # Return the new narrator's ID

    def link_narrators_in_isnad(self, hadith_id, narrators):
        # Link narrators in an isnad chain for a given hadith
        prev_narrator_id = None

        for position, narrator in enumerate(narrators):
            # Insert each narrator into the Isnads table, linking to the previous one
            narrator_id = self.add_narrator(
                narrator['name'], narrator.get('location'),
                narrator.get('death_date'), narrator.get('reliability')
            )

            # Insert into Isnads table
            self.cursor.execute('''
                INSERT INTO Isnads (hadith_id, narrator_id, next_narrator_id, position_in_chain)
                VALUES (?, ?, ?, ?)
            ''', (hadith_id, narrator_id, None, position))

            # Update the previous narrator to point to the current one
            if prev_narrator_id is not None:
                self.cursor.execute('''
                    UPDATE Isnads
                    SET next_narrator_id = ?
                    WHERE hadith_id = ? AND narrator_id = ?
                ''', (narrator_id, hadith_id, prev_narrator_id))

            prev_narrator_id = narrator_id

        self.conn.commit()

    def get_hadith_with_isnad(self, hadith_id):
        # Retrieve the hadith with its isnad chain
        self.cursor.execute('''
            SELECT h.matn, h.comments, n.name, n.location, i.position_in_chain
            FROM Hadiths h
            JOIN Isnads i ON h.id = i.hadith_id
            JOIN Narrators n ON i.narrator_id = n.id
            WHERE h.id = ?
            ORDER BY i.position_in_chain
        ''', (hadith_id,))
        
        return self.cursor.fetchall()

    def close(self):
        # Close the connection when done
        self.conn.close()


# Example usage
if __name__ == "__main__":
    db = HadithDatabase()

    # Add a hadith
    hadith_id = db.add_hadith(
        "This is the matn of the hadith", "This is a comment from the last narrator"
    )

    # Add narrators and link them in an isnad chain
    narrators = [
        {"name": "Narrator 1", "location": "Medina", "death_date": "680", "reliability": "Sahih"},
        {"name": "Narrator 2", "location": "Kufa", "death_date": "700", "reliability": "Sahih"},
        {"name": "Narrator 3", "location": "Basra", "death_date": "720", "reliability": "Hasan"}
    ]
    db.link_narrators_in_isnad(hadith_id, narrators)

    # Query and print the hadith with its isnad
    hadith_data = db.get_hadith_with_isnad(hadith_id)
    for row in hadith_data:
        print(row)

    # Close the database connection
    db.close()
