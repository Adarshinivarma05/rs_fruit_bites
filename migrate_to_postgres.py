# migrate_to_postgres.py
"""
Migration script to transfer data from SQLite to PostgreSQL
Run this once to migrate your existing data
"""
import sqlite3
import psycopg2
from psycopg2.extras import execute_batch
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

SQLITE_DB = Path(__file__).resolve().parent / "data" / "rs_fruit_bites.db"
POSTGRES_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/rs_fruit_bites")

def migrate_data():
    """Migrate all data from SQLite to PostgreSQL"""
    
    if not SQLITE_DB.exists():
        print(f"SQLite database not found at {SQLITE_DB}")
        print("Skipping migration - will start with empty PostgreSQL database")
        return
    
    print("Starting migration from SQLite to PostgreSQL...")
    
    # Connect to both databases
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row
    postgres_conn = psycopg2.connect(POSTGRES_URL)
    
    sqlite_cur = sqlite_conn.cursor()
    postgres_cur = postgres_conn.cursor()
    
    try:
        # Migrate Customers
        print("\n1. Migrating customers...")
        sqlite_cur.execute("SELECT * FROM customers")
        customers = sqlite_cur.fetchall()
        
        if customers:
            customer_data = []
            for row in customers:
                customer_data.append((
                    row['name'],
                    row['area'] if 'area' in row.keys() else '',
                    row['mobile'] if 'mobile' in row.keys() else '',
                    row['subscription'] if 'subscription' in row.keys() else 'Basic',
                    row['custom_rate'] if 'custom_rate' in row.keys() else 0,
                    row['start_date'] if 'start_date' in row.keys() else None,
                    row['end_date'] if 'end_date' in row.keys() else None,
                    row['status'] if 'status' in row.keys() else 'active'
                ))
            
            execute_batch(postgres_cur, """
                INSERT INTO customers (name, area, mobile, subscription, custom_rate, start_date, end_date, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (name) DO NOTHING;
            """, customer_data)
            
            print(f"   ✓ Migrated {len(customers)} customers")
        else:
            print("   - No customers to migrate")
        
        # Migrate Attendance
        print("\n2. Migrating attendance records...")
        sqlite_cur.execute("SELECT * FROM attendance")
        attendance = sqlite_cur.fetchall()
        
        if attendance:
            attendance_data = []
            for row in attendance:
                attendance_data.append((
                    row['date'],
                    row['name'],
                    row['subscription'] if 'subscription' in row.keys() else '',
                    row['status'],
                    row['extra_bowls'] if 'extra_bowls' in row.keys() else 0
                ))
            
            execute_batch(postgres_cur, """
                INSERT INTO attendance (date, name, subscription, status, extra_bowls)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (date, name) DO NOTHING;
            """, attendance_data)
            
            print(f"   ✓ Migrated {len(attendance)} attendance records")
        else:
            print("   - No attendance records to migrate")
        
        # Migrate Payments
        print("\n3. Migrating payment records...")
        try:
            sqlite_cur.execute("SELECT * FROM payments")
            payments = sqlite_cur.fetchall()
            
            if payments:
                payment_data = []
                for row in payments:
                    payment_data.append((
                        row['date'],
                        row['name'],
                        row['amount'],
                        row['method'] if 'method' in row.keys() else 'Cash',
                        row['remarks'] if 'remarks' in row.keys() else '',
                        row['month'] if 'month' in row.keys() else ''
                    ))
                
                execute_batch(postgres_cur, """
                    INSERT INTO payments (date, name, amount, method, remarks, month)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, payment_data)
                
                print(f"   ✓ Migrated {len(payments)} payment records")
            else:
                print("   - No payment records to migrate")
        except sqlite3.OperationalError:
            print("   - No payments table found in SQLite")
        
        # Migrate Logs
        print("\n4. Migrating logs...")
        try:
            sqlite_cur.execute("SELECT * FROM logs")
            logs = sqlite_cur.fetchall()
            
            if logs:
                log_data = []
                for row in logs:
                    log_data.append((
                        row['action'],
                        row['details'] if 'details' in row.keys() else '',
                    ))
                
                execute_batch(postgres_cur, """
                    INSERT INTO logs (action, details)
                    VALUES (%s, %s);
                """, log_data)
                
                print(f"   ✓ Migrated {len(logs)} log entries")
            else:
                print("   - No logs to migrate")
        except sqlite3.OperationalError:
            print("   - No logs table found in SQLite")
        
        # Commit all changes
        postgres_conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        postgres_conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    
    finally:
        sqlite_cur.close()
        sqlite_conn.close()
        postgres_cur.close()
        postgres_conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("RS Fruit Bites - SQLite to PostgreSQL Migration")
    print("=" * 60)
    
    # First initialize PostgreSQL tables
    print("\nInitializing PostgreSQL database...")
    from app.postgres_db import init_db
    init_db()
    print("✓ PostgreSQL tables created")
    
    # Then migrate data
    migrate_data()
    
    print("\n" + "=" * 60)
    print("Migration process complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Verify the data in PostgreSQL")
    print("2. Update your .env file with correct DATABASE_URL")
    print("3. Run the Streamlit app: streamlit run streamlit_app.py")
