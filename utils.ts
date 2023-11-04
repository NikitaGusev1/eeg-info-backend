const { jwtSecretKey } = require("./config");

const jwt = require("jsonwebtoken");

function generateToken(user) {
  const payload = {
    id: user.id,
    username: user.username,
  };

  return jwt.sign(payload, jwtSecretKey, { expiresIn: "72h" });
}

function verifyToken(token) {
  try {
    return jwt.verify(token, jwtSecretKey);
  } catch (error) {
    return null;
  }
}

function authenticateToken(req, res, next) {
  const token = req.header("Authorization");

  if (!token) {
    return res.status(401).json({ message: "Unauthorized" });
  }

  const user = verifyToken(token);
  if (!user) {
    return res.status(403).json({ message: "Invalid token" });
  }

  req.user = user;
  next();
}

module.exports = { generateToken, verifyToken };
