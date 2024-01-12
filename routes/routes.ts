const express = require("express");
const UserModel = require("../models/User.ts");
const FileModel = require("../models/File.ts");
const app = express();
const router = express.Router();
const bcrypt = require("bcrypt");
const {
  generateToken,
  verifyToken,
  authenticateToken,
  generateRandomString,
  generateUniqueEmail,
} = require("../utils.ts");
const mongoose = require("../db");
const jwt = require("jsonwebtoken");
const { spawn } = require("child_process");
const path = require("path");

router.post("/addUser", authenticateToken, async (request, response) => {
  try {
    const { isAdmin } = request.user;
    if (isAdmin) {
      const firstName = request.body.firstName;
      const lastName = request.body.lastName;

      const password = generateRandomString();
      const saltRounds = 10;
      const hashedPassword = await bcrypt.hash(password, saltRounds);

      const existingEmails = await UserModel.find().distinct("email");

      const email = generateUniqueEmail(firstName, lastName, existingEmails);

      const user = new UserModel({
        firstName,
        lastName,
        email,
        password: hashedPassword,
      });

      await user.save();
      response.send({ email, password });
    } else {
      return response.status(401).json({ message: "Permisson denied" });
    }
  } catch (error) {
    response.status(500).send(error);
  }
});
router.get("/user", authenticateToken, async (request, response) => {
  try {
    const email = request.user.email;
    const user = await UserModel.findOne({ email });

    if (!user) {
      return response.status(404).send("User not found");
    }

    const userResponse = {
      email: user.email,
      firstName: user.name || user.firstName,
      lastName: user.lastName ?? "",
      isAdmin: user.isAdmin,
      assignedFiles: user.assignedFiles,
    };

    response.send(userResponse);
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
    const { email, file, fileName, mimeType } = request.body;
    // Create and save the file document
    const newFile = new FileModel({
      fileName,
      mimeType,
      data: file, // This is the base64 encoded data
    });

    const savedFile = await newFile.save();

    await UserModel.updateOne(
      { email: email },
      { $push: { assignedFiles: savedFile.fileName } }
    );

    response
      .status(200)
      .json({ message: "File assigned successfully", fileId: savedFile._id });
  } catch (error) {
    console.error("Error in /assignFiles endpoint:", error);
    response.status(500).json({ message: "Internal Server Error" });
  }
});

router.get("/download/:fileName", async (req, res) => {
  try {
    const fileName = req.params.fileName;
    const file = await FileModel.findOne({ fileName });

    if (!file) {
      return res.status(404).send("File not found");
    }

    const fileBuffer = Buffer.from(file.data, "base64");

    res.setHeader(
      "Content-Disposition",
      'attachment; filename="' + file.fileName + '"'
    );
    res.setHeader("Content-Type", file.mimeType);

    res.send(fileBuffer);
  } catch (error) {
    console.error("Error in file download route:", error);
    res.status(500).send("Internal Server Error");
  }
});

router.post("/findPeaks", authenticateToken, (request, response) => {
  try {
    const { data } = request.body;

    if (!Array.isArray(data)) {
      return response
        .status(400)
        .json({ success: false, error: "Invalid data format" });
    }

    const signals = data.map((dataset) => {
      return {
        signal: dataset.signal,
        samplingFrequency: dataset.samplingFrequency,
      };
    });

    const pythonScriptPath = path.join(
      __dirname,
      "..",
      "scripts",
      "find_peaks.py"
    );

    const pythonProcess = spawn("python3", [pythonScriptPath]);

    const inputData = { signals };
    const inputJSON = JSON.stringify(inputData);

    // Write to the standard input
    pythonProcess.stdin.write(inputJSON);
    pythonProcess.stdin.end();

    let result = "";
    let error = "";

    // Handle process termination
    pythonProcess.on("exit", (code) => {
      if (code === null) {
        console.error("Python process exited prematurely or with an error");
        response
          .status(500)
          .json({ success: false, error: "Internal Server Error" });
      } else {
        try {
          const parsedResult = JSON.parse(result);
          console.log(result);

          if (parsedResult && typeof parsedResult === "object") {
            response.json({
              success: true,
              data: parsedResult,
            });
          } else {
            console.error("Invalid JSON format in Python script output.");
            response
              .status(500)
              .json({ success: false, error: "Internal Server Error" });
          }
        } catch (err) {
          console.error("Error parsing JSON result:", err.message);
          response
            .status(500)
            .json({ success: false, error: "Internal Server Error" });
        }
      }
    });

    pythonProcess.stdout.on("data", (data) => {
      result += data;
    });

    pythonProcess.stderr.on("data", (data) => {
      error += data;
    });

    pythonProcess.on("error", (err) => {
      console.error(`Python process error: ${err.message}`);
      response
        .status(500)
        .json({ success: false, error: "Internal Server Error" });
    });
  } catch (err) {
    console.error("Error processing request:", err.message);
    response
      .status(500)
      .json({ success: false, error: "Internal Server Error" });
  }
});

module.exports = router;
