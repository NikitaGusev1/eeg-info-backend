const dotenv = require("dotenv");
dotenv.config();

module.exports = {
  dbConnectionString: process.env.DB_CONNECTION_STRING,
  jwtSecretKey: process.env.JWT_SECRET_KEY,
};
