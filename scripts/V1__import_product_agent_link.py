import pandas as pd
import mysql.connector
from datetime import datetime

DB_CONFIG = {
    'user': 'root',
    'password': '2121',
    'host': 'localhost',
    'database': 'agent_app',
    'charset': 'utf8mb4',
}


def connect_db():
    return mysql.connector.connect(**DB_CONFIG)


def load_excel(filepath):
    df = pd.read_excel(filepath)
    df = df.fillna('')

    print("🧠 Заголовки файла:", df.columns.tolist())

    df = df.rename(columns={
        'Наименование агента': 'AgentTitle',
        'Продукция': 'ProductTitle',
        'Дата реализации': 'SaleDate',
        'Количество продукции': 'ProductCount'
    })

    df['AgentTitle'] = df['AgentTitle'].astype(str).str.strip()
    df['ProductTitle'] = df['ProductTitle'].astype(str).str.strip()
    df['SaleDate'] = pd.to_datetime(df['SaleDate'], errors='coerce').dt.date
    df['ProductCount'] = pd.to_numeric(df['ProductCount'], errors='coerce').fillna(0).astype(int)

    return df


def get_agent_ids(cursor):
    cursor.execute("SELECT ID, Title FROM Agent")
    return {title: id for id, title in cursor.fetchall()}


def get_product_ids(cursor):
    cursor.execute("SELECT ID, Title, ArticleNumber FROM Product")
    by_title = {}
    by_article = {}
    for row in cursor.fetchall():
        pid, title, article = row
        by_title[title.strip()] = pid
        by_article[article.strip()] = pid
    return by_title, by_article


def insert_sales(cursor, df, agent_map, product_title_map, product_article_map):
    insert_sql = """
        INSERT INTO ProductSale (
            AgentID, ProductID, SaleDate, ProductCount
        ) VALUES (%s, %s, %s, %s)
    """

    for _, row in df.iterrows():
        agent_id = agent_map.get(row['AgentTitle'])
        product_id = product_title_map.get(row['ProductTitle']) or \
                     product_article_map.get(str(row['ProductTitle']))

        if not agent_id or not product_id:
            print(f"⚠️ Пропущена строка: агент '{row['AgentTitle']}' или продукт '{row['ProductTitle']}' не найден.")
            continue

        cursor.execute(insert_sql, (
            agent_id,
            product_id,
            row['SaleDate'],
            row['ProductCount']
        ))


def main():
    filepath = 'data/productsale_s_import.xlsx'
    df = load_excel(filepath)

    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            agent_map = get_agent_ids(cursor)
            product_title_map, product_article_map = get_product_ids(cursor)
            insert_sales(cursor, df, agent_map, product_title_map, product_article_map)
        conn.commit()
    finally:
        conn.close()

    print("✅ Продажи успешно загружены.")


if __name__ == '__main__':
    main()
