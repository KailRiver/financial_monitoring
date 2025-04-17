
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            entity_type TEXT,
            operation_date TEXT,
            transaction_type TEXT,
            comment TEXT,
            amount REAL,
            status TEXT,
            sender_bank TEXT,
            account TEXT,
            recipient_bank TEXT,
            recipient_inn TEXT,
            recipient_account TEXT,
            category TEXT,
            recipient_phone TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        