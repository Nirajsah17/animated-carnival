// /src/config/db.js
import sqlite3 from "sqlite3";
import config from "./appConfig.js";

const db = new sqlite3.Database(config.dbFile, (err) => {
  if (err) {
    console.error("Error connecting to the database:", err.message);
  } else {
    console.log("Connected to SQLite database.");
  }
});

// Create User Table if not exists
db.serialize(() => {
  db.run(
    `CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT UNIQUE NOT NULL
    )`
  );
});

export default db;
