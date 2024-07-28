import requests
import json
import sqlite3
from datetime import datetime


# Step 1: Send a GET request to the cat facts API
def fetch_cat_facts():
    url = "https://cat-fact.herokuapp.com/facts"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching cat facts: {response.status_code}")
        return None


# Step 2: Save the response as a JSON file
def save_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Cat facts saved to {filename}")


# Step 3: Create a SQLite database and table
def create_database():
    conn = sqlite3.connect('cat_facts.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cat_facts (
        id INTEGER PRIMARY KEY,
        fact TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    ''')

    conn.commit()
    return conn


# Step 4: Insert cat facts into the database
def insert_cat_facts(conn, facts):
    cursor = conn.cursor()

    for fact in facts:
        cursor.execute('''
        INSERT INTO cat_facts (fact, created_at)
        VALUES (?, ?)
        ''', (fact['text'], datetime.now().isoformat()))

    conn.commit()
    print(f"{len(facts)} cat facts inserted into the database")


# Step 5: Display saved cat facts in the terminal
def display_cat_facts(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cat_facts')
    facts = cursor.fetchall()

    print("\nSaved Cat Facts:")
    for fact in facts:
        print(f"ID: {fact[0]}")
        print(f"Fact: {fact[1]}")
        print(f"Created At: {fact[2]}")
        print("-" * 40)


def main():
    # Fetch cat facts
    cat_facts = fetch_cat_facts()

    if cat_facts:
        # Save as JSON
        save_json(cat_facts, 'cat_facts.json')

        # Create database and insert facts
        conn = create_database()
        insert_cat_facts(conn, cat_facts)

        # Display facts
        display_cat_facts(conn)

        conn.close()


if __name__ == "__main__":
    main()
