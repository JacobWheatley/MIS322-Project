import sqlite3
import os

DATABASE_FILENAME = "inventory_management_v1.db" # You can name this whatever you like

def create_connection(db_file):
    """ Create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"SQLite version: {sqlite3.sqlite_version}")
        print(f"Successfully connected to database: {os.path.abspath(db_file)}")
        # Enable foreign key constraint enforcement
        conn.execute("PRAGMA foreign_keys = ON;")
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables(conn):
    """ Create tables from the SQL statements """
    # SQL statements adapted for SQLite
    # INTEGER PRIMARY KEY implies AUTOINCREMENT for SQLite if the column is an alias for ROWID
    # We will use this standard SQLite behavior.
    sql_create_user_account_table = """
    CREATE TABLE IF NOT EXISTS UserAccount (
        UserID INTEGER PRIMARY KEY,
        FullName VARCHAR(255) NOT NULL,
        Role VARCHAR(100),
        Username VARCHAR(100) NOT NULL UNIQUE,
        PasswordHash VARCHAR(255) NOT NULL,
        AccessLevel VARCHAR(50)
    );"""

    sql_create_production_line_table = """
    CREATE TABLE IF NOT EXISTS ProductionLine (
        ProductionLineID INTEGER PRIMARY KEY,
        LineName VARCHAR(255) NOT NULL UNIQUE,
        Status VARCHAR(50)
    );"""

    sql_create_production_batch_table = """
    CREATE TABLE IF NOT EXISTS ProductionBatch (
        BatchID INTEGER PRIMARY KEY,
        ProductionLineID INT NOT NULL,
        ShiftDate DATE NOT NULL,
        ShiftType VARCHAR(50),
        QuantityProduced INT NOT NULL CHECK (QuantityProduced >= 0),
        CreatedByUserID INT,
        CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ProductionLineID) REFERENCES ProductionLine(ProductionLineID) ON DELETE CASCADE,
        FOREIGN KEY (CreatedByUserID) REFERENCES UserAccount(UserID) ON DELETE SET NULL
    );""" # Added ON DELETE clauses for referential integrity

    sql_create_inventory_item_table = """
    CREATE TABLE IF NOT EXISTS InventoryItem (
        InventoryItemID INTEGER PRIMARY KEY,
        ItemType VARCHAR(100),
        ItemName VARCHAR(255) NOT NULL UNIQUE,
        QuantityInStock INT NOT NULL DEFAULT 0 CHECK (QuantityInStock >= 0),
        ReorderThreshold INT DEFAULT 0 CHECK (ReorderThreshold >= 0),
        LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );"""

    sql_create_inventory_transaction_table = """
    CREATE TABLE IF NOT EXISTS InventoryTransaction (
        TransactionID INTEGER PRIMARY KEY,
        InventoryItemID INT NOT NULL,
        BatchID INT,
        QuantityChange INT NOT NULL,
        Reason VARCHAR(255),
        TransactionDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UpdatedByUserID INT,
        FOREIGN KEY (InventoryItemID) REFERENCES InventoryItem(InventoryItemID) ON DELETE CASCADE,
        FOREIGN KEY (BatchID) REFERENCES ProductionBatch(BatchID) ON DELETE SET NULL,
        FOREIGN KEY (UpdatedByUserID) REFERENCES UserAccount(UserID) ON DELETE SET NULL
    );"""

    sql_create_defect_type_table = """
    CREATE TABLE IF NOT EXISTS DefectType (
        DefectTypeID INTEGER PRIMARY KEY,
        DefectName VARCHAR(255) NOT NULL UNIQUE
    );"""

    sql_create_defect_log_table = """
    CREATE TABLE IF NOT EXISTS DefectLog (
        DefectID INTEGER PRIMARY KEY,
        BatchID INT NOT NULL,
        DefectTypeID INT NOT NULL,
        SeverityLevel VARCHAR(50),
        DefectDescription TEXT,
        LoggedByUserID INT,
        DateLogged TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (BatchID) REFERENCES ProductionBatch(BatchID) ON DELETE CASCADE,
        FOREIGN KEY (DefectTypeID) REFERENCES DefectType(DefectTypeID) ON DELETE RESTRICT,
        FOREIGN KEY (LoggedByUserID) REFERENCES UserAccount(UserID) ON DELETE SET NULL
    );"""

    sql_create_return_reason_table = """
    CREATE TABLE IF NOT EXISTS ReturnReason (
        ReturnReasonID INTEGER PRIMARY KEY,
        ReasonDescription VARCHAR(255) NOT NULL UNIQUE
    );"""

    sql_create_return_log_table = """
    CREATE TABLE IF NOT EXISTS ReturnLog (
        ReturnID INTEGER PRIMARY KEY,
        CustomerID INT,
        BatchID INT,
        ReturnReasonID INT,
        DateReturned TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        Notes TEXT,
        ProcessedByUserID INT,
        FOREIGN KEY (BatchID) REFERENCES ProductionBatch(BatchID) ON DELETE SET NULL,
        FOREIGN KEY (ReturnReasonID) REFERENCES ReturnReason(ReturnReasonID) ON DELETE SET NULL,
        FOREIGN KEY (ProcessedByUserID) REFERENCES UserAccount(UserID) ON DELETE SET NULL
    );"""

    try:
        cursor = conn.cursor()
        print("Creating table UserAccount...")
        cursor.execute(sql_create_user_account_table)
        print("Creating table ProductionLine...")
        cursor.execute(sql_create_production_line_table)
        print("Creating table ProductionBatch...")
        cursor.execute(sql_create_production_batch_table)
        print("Creating table InventoryItem...")
        cursor.execute(sql_create_inventory_item_table)
        print("Creating table InventoryTransaction...")
        cursor.execute(sql_create_inventory_transaction_table)
        print("Creating table DefectType...")
        cursor.execute(sql_create_defect_type_table)
        print("Creating table DefectLog...")
        cursor.execute(sql_create_defect_log_table)
        print("Creating table ReturnReason...")
        cursor.execute(sql_create_return_reason_table)
        print("Creating table ReturnLog...")
        cursor.execute(sql_create_return_log_table)
        conn.commit()
        print("All tables created successfully (if they didn't already exist).")
    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")

def main():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Join it with the desired database filename
    db_path = os.path.join(script_dir, DATABASE_FILENAME)

    # Create a database connection
    conn = create_connection(db_path)

    # Create tables
    if conn is not None:
        create_tables(conn)
        # You can add some sample data insertion here if you want
        # Example: add_sample_data(conn)
        conn.close()
        print(f"Database setup complete. File saved at: {db_path}")
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()