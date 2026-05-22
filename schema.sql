
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            faculty_name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comments TEXT,
            sentiment TEXT  -- NEW COLUMN FOR AI ANALYSIS
        );
        -- Insert a default admin
        INSERT INTO users (username, password, role) VALUES ('xyz', 'open', 'admin');
    