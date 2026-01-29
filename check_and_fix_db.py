#!/usr/bin/env python3
"""
Check and fix database schema for total_amount columns
"""
import pymysql
import sys

# Database connection details
DB_CONFIG = {
    'host': 'localhost',
    'port': 3307,
    'user': 'root',
    'password': 'WYz@Dessert2025',
    'database': 'dessert_pos'
}

def check_and_add_columns():
    try:
        # Connect to database
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("Connected to database successfully!")

        # Check purchase_orders table
        print("\n1. Checking purchase_orders table...")
        cursor.execute("DESCRIBE purchase_orders")
        columns = [row[0] for row in cursor.fetchall()]
        print(f"   Current columns: {columns}")

        if 'total_amount' not in columns:
            print("   -> Adding total_amount column to purchase_orders...")
            cursor.execute("""
                ALTER TABLE purchase_orders
                ADD COLUMN total_amount DECIMAL(10, 2) DEFAULT 0.00
                COMMENT 'Total amount for the entire purchase order in dollars'
            """)
            conn.commit()
            print("   -> Successfully added total_amount to purchase_orders!")
        else:
            print("   -> total_amount column already exists in purchase_orders")

        # Check purchase_order_items table
        print("\n2. Checking purchase_order_items table...")
        cursor.execute("DESCRIBE purchase_order_items")
        columns = [row[0] for row in cursor.fetchall()]
        print(f"   Current columns: {columns}")

        if 'total_amount' not in columns:
            print("   -> Adding total_amount column to purchase_order_items...")
            cursor.execute("""
                ALTER TABLE purchase_order_items
                ADD COLUMN total_amount DECIMAL(10, 2) DEFAULT 0.00
                COMMENT 'Total amount for this purchase item in dollars'
            """)
            conn.commit()
            print("   -> Successfully added total_amount to purchase_order_items!")
        else:
            print("   -> total_amount column already exists in purchase_order_items")

        # Update existing records
        print("\n3. Updating existing records...")
        cursor.execute("UPDATE purchase_orders SET total_amount = 0.00 WHERE total_amount IS NULL")
        cursor.execute("UPDATE purchase_order_items SET total_amount = 0.00 WHERE total_amount IS NULL")
        conn.commit()
        print("   -> Updated existing records")

        # Verify the changes
        print("\n4. Verification:")
        cursor.execute("DESCRIBE purchase_orders")
        print("   purchase_orders columns:")
        for row in cursor.fetchall():
            print(f"      {row[0]}: {row[1]}")

        cursor.execute("DESCRIBE purchase_order_items")
        print("   purchase_order_items columns:")
        for row in cursor.fetchall():
            print(f"      {row[0]}: {row[1]}")

        cursor.close()
        conn.close()

        print("\n✅ Database schema update completed successfully!")
        print("Please restart your backend server: ./venv/bin/uvicorn main:app --reload")

    except pymysql.Error as e:
        print(f"\n❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_and_add_columns()
