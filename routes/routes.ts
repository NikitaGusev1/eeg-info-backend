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
const jwt = require("jsonwebtoken");

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

router.post("/renewToken", (request, response) => {
  try {
    const userData = {
      email: request.user.email,
    };

    const newToken = jwt.sign(userData, jwtSecretKey, { expiresIn: "1h" });

    response.json({ token: newToken });
  } catch (error) {
    response.status(403).json({ message: "Invalid token" });
  }
});

router.post("/assignFiles", authenticateToken, async (request, response) => {
  try {
    const { isAdmin } = request.user;
    if (isAdmin) {
      const { files, email } = request.body;
      console.log(email, files);
      const assignee = await UserModel.findOne({ email });

      if (!assignee) {
        return response.status(404).json({ message: "User not found" });
      }

      const updatedAssignedFiles = [...assignee.assignedFiles, ...files];

      await UserModel.findOneAndUpdate(
        { email },
        { assignedFiles: updatedAssignedFiles },
        { new: true }
      );

      response.status(200).json({ message: "Files assigned successfully" });
    } else {
      response.status(403).json({ message: "Permission denied" });
    }
  } catch {
    response.status(500).json({ message: "Server error" });
  }
});

module.exports = router;
