import db from "../config/databaseConfig.js";

const UserModel = {
  createUser: (name, email) => {
    return new Promise((resolve, reject) => {
      const query = "INSERT INTO users (name, email) VALUES (?, ?)";
      db.run(query, [name, email], function (err) {
        if (err) reject(err);
        else resolve({ id: this.lastID, name, email });
      });
    });
  },

  getAllUsers: () => {
    return new Promise((resolve, reject) => {
      const query = "SELECT * FROM users";
      db.all(query, [], (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });
  },

  getUserById: (id) => {
    return new Promise((resolve, reject) => {
      const query = "SELECT * FROM users WHERE id = ?";
      db.get(query, [id], (err, row) => {
        if (err) reject(err);
        else resolve(row);
      });
    });
  },
};

export default UserModel;
