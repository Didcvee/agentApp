import pandas as pd
import mysql.connector
import re

DB_CONFIG = {
    'user': 'root',
    'password': '2121',
    'host': 'localhost',
    'database': 'agent_app',
    'charset': 'utf8mb4',
}


def connect_db():
    return mysql.connector.connect(**DB_CONFIG)


def clean_priority(value):
    # Примеры: "329 в приоритете на поставку", "Приоритет = 156", "201"
    digits = re.findall(r'\d+', str(value))
    return int(digits[0]) if digits else 0


def clean_email(value):
    # Примеры: "email: varvara15@belousov.ru"
    match = re.search(r'[\w\.-]+@[\w\.-]+', str(value))
    return match.group(0) if match else ''


def clean_phone(value):
    # Примеры: "phone: (35222) 46-54-74"
    cleaned = re.sub(r'(phone:|\s+)', '', str(value), flags=re.IGNORECASE)
    return cleaned.strip()


def load_csv(filepath):
    df = pd.read_csv(filepath, sep=';', encoding='utf-8')
    df = df.fillna('')

    df = df.rename(columns={
        'Тип агента': 'AgentType',
        'Наименование агента': 'Title',
        'Электронная почта агента': 'Email',
        'Телефон агента': 'Phone',
        'Логотип агента': 'Logo',
        'Юридический адрес': 'Address',
        'Приоритет': 'Priority',
        'Директор': 'DirectorName',
        'ИНН': 'INN',
        'КПП': 'KPP'
    })

    df['AgentType'] = df['AgentType'].astype(str).str.strip()
    df['Title'] = df['Title'].astype(str).str.strip()
    df['Email'] = df['Email'].apply(clean_email)
    df['Phone'] = df['Phone'].apply(clean_phone)
    df['Logo'] = df['Logo'].astype(str).str.strip()
    df['Address'] = df['Address'].astype(str).str.strip()
    df['Priority'] = df['Priority'].apply(clean_priority)
    df['DirectorName'] = df['DirectorName'].astype(str).str.strip()
    df['INN'] = df['INN'].astype(str).str.strip()
    df['KPP'] = df['KPP'].astype(str).str.strip()

    return df


def insert_agent_types(cursor, types):
    cursor.execute("SELECT Title, ID FROM AgentType")
    existing = {title: id for title, id in cursor.fetchall()}

    for t in set(types):
        t = t.strip()
        if t not in existing:
            cursor.execute("INSERT INTO AgentType (Title, Image) VALUES (%s, %s)", (t, None))
    cursor.execute("SELECT Title, ID FROM AgentType")
    return {title: id for title, id in cursor.fetchall()}


def insert_agents(cursor, df, type_to_id):
    insert_sql = """
        INSERT INTO Agent (
            Title, AgentTypeID, Address,
            INN, KPP, DirectorName,
            Phone, Email, Logo, Priority
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for _, row in df.iterrows():
        cursor.execute(insert_sql, (
            row['Title'],
            type_to_id.get(row['AgentType']),
            row['Address'],
            row['INN'],
            row['KPP'],
            row['DirectorName'],
            row['Phone'],
            row['Email'],
            row['Logo'],
            row['Priority']
        ))


def main():
    filepath = 'data/agents_s_import.csv'
    df = load_csv(filepath)

    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            type_to_id = insert_agent_types(cursor, df['AgentType'].unique())
            insert_agents(cursor, df, type_to_id)
        conn.commit()
    finally:
        conn.close()

    print("✅ Импорт агентов завершён.")


if __name__ == '__main__':
    main()