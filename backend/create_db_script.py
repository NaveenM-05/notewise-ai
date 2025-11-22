import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configuration
password = "Gok@01"  # Your specific password
db_name = "notewise_db"

def try_create_db(port):
    print(f"Attempting to connect to PostgreSQL on port {port}...")
    try:
        # Connect to the default 'postgres' database to create a new one
        con = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password=password,
            host="localhost",
            port=port
        )
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        
        # Check if DB exists
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
        exists = cur.fetchone()
        
        if not exists:
            print(f"Creating database '{db_name}'...")
            cur.execute(f"CREATE DATABASE {db_name}")
            print(f"✅ SUCCESS! Database '{db_name}' created on port {port}.")
        else:
            print(f"✅ Database '{db_name}' already exists on port {port}.")
            
        cur.close()
        con.close()
        return True
    except psycopg2.OperationalError as e:
        print(f"❌ Could not connect to port {port}. (Password might be wrong or server is not on this port).")
        return False

if __name__ == "__main__":
    # Try standard port 5432 first
    if not try_create_db("5432"):
        print("\nTrying alternate port 5433 (since you have two versions installed)...")
        # Try alternate port 5433 (common when multiple versions are installed)
        if try_create_db("5433"):
            print(f"\nIMPORTANT: Update your .env file to use PORT 5433!")
        else:
            print("\n❌ Failed on both ports. Please verify your password is exactly 'Gok@01'.")
    else:
        print(f"\nIMPORTANT: Ensure your .env file uses PORT 5432.")