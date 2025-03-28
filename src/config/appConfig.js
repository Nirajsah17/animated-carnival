import dotenv from "dotenv";
import path from "path";

dotenv.config({ path: path.resolve(process.cwd(), "env/.env") });

const config = {
  port: process.env.PORT || 3000,
  dbFile: process.env.DB_FILE || "./data/database.sqlite",
};

export default config;
