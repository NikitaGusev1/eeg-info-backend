const { dbConnectionString } = require("./config");
const mongoose = require("mongoose");

mongoose.connect(dbConnectionString);

const db = mongoose.connection;

db.on("error", console.error.bind(console, "MongoDB connection error:"));
db.once("open", () => {});

module.exports = mongoose;
