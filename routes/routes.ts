const express = require("express");
const UserModel = require("../models/User.ts");
const app = express();
const router = express.Router();
const bcrypt = require("bcrypt");
const {
  generateToken,
  verifyToken,
  authenticateToken,
} = require("../utils.ts");
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
router.get("/user", authenticateToken, async (request, response) => {
  const email = request.user.email;
  const user = await UserModel.find({ email });

  try {
    response.send(user);
  } catch (error) {
    response.status(500).send(error);
  }
});

router.post("/login", async (request, response) => {
  const { email, password } = request.body;

  try {
    const user = await UserModel.findOne({ email });

    if (!user) {
      return response.status(401).json({ message: "Invalid credentials" });
    }

    bcrypt.compare(password, user.password, (err, passwordMatch) => {
      if (err) {
        return response.status(500).json({ message: "Server error" });
      }

      if (passwordMatch) {
        const token = generateToken(user);
        response.json({ token, name: user.name });
      } else {
        response.status(401).json({ message: "Invalid credentials" });
      }
    });
  } catch (error) {
    console.error("Error authenticating user:", error);
    response.status(500).json({ message: "Server error" });
  }
});

module.exports = router;
