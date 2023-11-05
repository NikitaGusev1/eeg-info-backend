const express = require("express");
const UserModel = require("../models/User.ts");
const app = express();
const router = express.Router();
const bcrypt = require("bcrypt");
const { generateToken, verifyToken } = require("../utils.ts");
const mongoose = require("../db");

router.post("/add_user", async (request, response) => {
  const saltRounds = 10;
  const hashedPassword = await bcrypt.hash(request.body.password, saltRounds);

  const user = new UserModel({
    ...request.body,
    password: hashedPassword,
  });

  try {
    await user.save();
    response.send(user);
  } catch (error) {
    response.status(500).send(error);
  }
});

router.get("/users", async (request, response) => {
  const users = await UserModel.find({});

  try {
    response.send(users);
  } catch (error) {
    response.status(500).send(error);
  }
});

router.post("/login", async (req, res) => {
  const { email, password } = req.body;

  try {
    const user = await UserModel.findOne({ email });

    if (!user) {
      return res.status(401).json({ message: "Invalid credentials" });
    }

    bcrypt.compare(password, user.password, (err, passwordMatch) => {
      if (err) {
        return res.status(500).json({ message: "Server error" });
      }

      if (passwordMatch) {
        const token = generateToken(user);
        res.json({ token });
      } else {
        res.status(401).json({ message: "Invalid credentials" });
      }
    });
  } catch (error) {
    console.error("Error authenticating user:", error);
    res.status(500).json({ message: "Server error" });
  }
});

module.exports = router;
