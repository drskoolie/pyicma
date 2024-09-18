import csv
import hashlib
import sqlite3

class HadithDatabase:
    def __init__(self, db_name='data/hadith.db'):
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
                link TEXT
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

        # Create a table to store the CSV hash
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS CsvHash (
                id INTEGER PRIMARY KEY,
                hash_value TEXT NOT NULL
            )
        ''')

        self.conn.commit()

    # -------------
    # CSV Functions
    # -------------
    def compute_file_hash(self, file_path="data/narrators.csv"):
        hasher = hashlib.sha256()

        with open(file_path, 'rb') as f:
            for block in iter(lambda: f.read(4096), b''):
                hasher.update(block)

        return hasher.hexdigest()

    def get_stored_hash(self):
        # Retrieve the stored hash value from the database
        self.cursor.execute('SELECT hash_value FROM CsvHash WHERE id = 1')
        result = self.cursor.fetchone()
        return result[0] if result else None

    def store_new_hash(self, hash_value):
        # Store or update the hash value in the database
        self.cursor.execute('INSERT OR REPLACE INTO CsvHash (id, hash_value) VALUES (1, ?)', (hash_value,))
        self.conn.commit()

    def read_narrators_from_csv(self, file_path="data/narrators.csv"):
        # Read the narrators from a CSV file and insert them into the database
        new_hash = self.compute_file_hash(file_path)
        stored_hash = self.get_stored_hash()

        if stored_hash == new_hash:
            print("No changes in the CSV file. Skipping update.")
            return
        else:
            print("CSV file has changed. Updating the database...")

        self.truncate_narrators()

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.add_narrator(
                    name=row['name'], 
                    location=row['location'], 
                    death_date=row['death_date'], 
                    link=row['link']
                )

        self.store_new_hash(new_hash)


    # --------
    # Narrator
    # --------
    def check_narrator_in_db(self, name):
        # Check if the narrator exists in the database by name
        query = "SELECT id FROM Narrators WHERE name = ?"
        self.cursor.execute(query, (name,))
        result = self.cursor.fetchone()
        
        return result is not None  # Return True if found, False otherwise

    def truncate_narrators(self):
        # Remove all records from the Narrators table
        self.cursor.execute('DELETE FROM Narrators')
        self.conn.commit()

    def add_hadith(self, matn, comments):
        # Insert a new hadith into the Hadiths table
        self.cursor.execute('''
            INSERT INTO Hadiths (matn, comments)
            VALUES (?, ?)
        ''', (matn, comments))
        self.conn.commit()
        return self.cursor.lastrowid  # Return the new hadith's ID

    def add_narrator(self, name, location=None, death_date=None, link=None):
        # Insert a new narrator into the Narrators table
        self.cursor.execute('''
            INSERT INTO Narrators (name, location, death_date, link)
            VALUES (?, ?, ?, ?)
        ''', (name, location, death_date, link))
        self.conn.commit()
        return self.cursor.lastrowid  # Return the new narrator's ID

    def link_narrators_in_isnad(self, hadith_id, narrators):
        # Link narrators in an isnad chain for a given hadith using only their names
        prev_narrator_id = None

        for position, narrator_name in enumerate(narrators):
            # Find the narrator by name in the database
            self.cursor.execute('SELECT id FROM Narrators WHERE name = ?', (narrator_name,))
            result = self.cursor.fetchone()

            if not result:
                print(f"Error: Narrator '{narrator_name}' not found in the database.")
                return  # Stop if any narrator is missing

            narrator_id = result[0]

            # Insert into Isnads table, linking narrators in the isnad chain
            self.cursor.execute('''
                INSERT INTO Isnads (hadith_id, narrator_id, next_narrator_id, position_in_chain)
                VALUES (?, ?, ?, ?)
            ''', (hadith_id, narrator_id, None, position))

            # If there's a previous narrator, update the next_narrator_id of the previous one
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

    # Read narrators from the CSV file
    db.read_narrators_from_csv()

    # Add a hadith
    hadith_id = db.add_hadith(
        "This is the matn of the hadith", "This is a comment from the last narrator"
    )

    # Add narrators and link them in an isnad chain
    narrators = ["List1", "List2" ]
    db.link_narrators_in_isnad(hadith_id, narrators)

    # Query and print the hadith with its isnad
    hadith_data = db.get_hadith_with_isnad(hadith_id)
    for row in hadith_data:
        print(row)

    # Close the database connection
    db.close()

