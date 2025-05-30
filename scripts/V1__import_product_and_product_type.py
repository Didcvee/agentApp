import pandas as pd
import re
import mysql.connector
from decimal import Decimal
from collections import defaultdict

DB_CONFIG = {
    'user': 'root',
    'password': '2121',
    'host': 'localhost',
    'database': 'agent_app',
    'charset': 'utf8mb4',
}


def parse_price(price_str):
    """Убирает лишние символы и приводит цену к типу Decimal"""
    cleaned = re.sub(r'[^\d.,]', '', price_str)
    cleaned = cleaned.replace(',', '.')
    try:
        return round(Decimal(cleaned), 2)
    except:
        return Decimal('0.00')


def load_txt_to_dataframe(filepath):
    df = pd.read_csv(filepath, sep=',', skiprows=1, header=None,
                     names=[
                         "Title", "ProductType", "ArticleNumber",
                         "ProductionPersonCount", "ProductionWorkshopNumber",
                         "MinCostForAgent"
                     ])
    df['MinCostForAgent'] = df['MinCostForAgent'].apply(parse_price)
    df = df.fillna({'Description': '', 'Image': None})
    return df


def connect_db():
    return mysql.connector.connect(**DB_CONFIG)


def insert_product_types(cursor, product_types):
    type_to_id = {}
    for title in sorted(set(product_types)):
        cursor.execute(
            "INSERT IGNORE INTO ProductType (Title, DefectedPercent) VALUES (%s, %s)",
            (title.strip(), 0.0)
        )
    cursor.execute("SELECT ID, Title FROM ProductType")
    for row in cursor.fetchall():
        type_to_id[row[1]] = row[0]
    return type_to_id


def insert_products(cursor, df, type_to_id):
    insert_sql = """
        INSERT INTO Product (
            Title, ProductTypeID, ArticleNumber,
            Description, Image,
            ProductionPersonCount, ProductionWorkshopNumber,
            MinCostForAgent
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    for _, row in df.iterrows():
        cursor.execute(insert_sql, (
            str(row['Title']).strip(),
            type_to_id.get(str(row['ProductType']).strip()),
            str(row['ArticleNumber']).strip(),
            "",  # Description
            None,  # Image
            int(row['ProductionPersonCount']),
            int(row['ProductionWorkshopNumber']),
            row['MinCostForAgent']
        ))


def main():
    filepath = 'data/products_short_s_import.txt'
    df = load_txt_to_dataframe(filepath)

    conn = connect_db()
    try:
        with conn.cursor() as cursor:
            type_to_id = insert_product_types(cursor, df['ProductType'].unique())
            insert_products(cursor, df, type_to_id)
        conn.commit()
    finally:
        conn.close()
    print("Data import complete.")


if __name__ == '__main__':
    main()
