import sqlite3


def checkSetup():
    conn = sqlite3.connect('gas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='instructors'")
    result = cursor.fetchone()
    conn.close()
    if result is None:
        return False
    return True


def setup():
    conn = sqlite3.connect('gas.db')
    cursor = conn.cursor()
    create_instructors_table = """
        CREATE TABLE IF NOT EXISTS instructors (
          id INTEGER PRIMARY KEY,
          name TEXT NOT NULL,
          hours INTEGER NOT NULL,
          schedule TEXT NOT NULL,
          active BOOLEAN NOT NULL DEFAULT 1 CHECK (
            active IN (0, 1)
          )
        );
    """
    create_rooms_table = """
        CREATE TABLE IF NOT EXISTS rooms (
          id INTEGER PRIMARY KEY,
          name TEXT NOT NULL,
          type TEXT NOT NULL,
          schedule TEXT NOT NULL,
          active BOOLEAN NOT NULL DEFAULT 1 CHECK (
            active IN (0, 1)
          )
        );
    """
    create_subjects_table = """
        CREATE TABLE IF NOT EXISTS subjects (
          id INTEGER PRIMARY KEY,
          name TEXT NOT NULL,
          hours REAL NOT NULL,
          code TEXT NOT NULL,
          description TEXT NOT NULL,
          instructors TEXT NOT NULL,
          divisible BOOLEAN NOT NULL DEFAULT 1 CHECK (
            divisible IN (0, 1)
          ),
          type TEXT NOT NULL
        );
    """
    create_sections_table = """
        CREATE TABLE IF NOT EXISTS sections (
          id INTEGER PRIMARY KEY,
          name TEXT NOT NULL,
          schedule TEXT NOT NULL,
          subjects TEXT NOT NULL,
          active BOOLEAN NOT NULL DEFAULT 1 CHECK (
            active IN (0, 1)
          ),
          stay BOOLEAN NOT NULL DEFAULT 0 CHECK (
            active IN (0, 1)
          )
        );
    """
    create_sharing_table = """
        CREATE TABLE IF NOT EXISTS sharings (
          id INTEGER PRIMARY KEY,
          subjectId INTEGER NOT NULL,
          sections TEXT NOT NULL,
          final BOOLEAN NOT NULL DEFAULT 0 CHECK (
            final IN (0, 1)
          )
        );
    """
    create_results_table = """
        CREATE TABLE IF NOT EXISTS results (
          id INTEGER PRIMARY KEY,
          content BLOB NOT NULL,
          timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """
    cursor.execute(create_instructors_table)
    cursor.execute(create_rooms_table)
    cursor.execute(create_subjects_table)
    cursor.execute(create_sections_table)
    cursor.execute(create_sharing_table)
    cursor.execute(create_results_table)
    conn.commit()
    conn.close()


def getConnection():
    return sqlite3.connect('gas.db')
