const { jwtSecretKey } = require("./config");

const jwt = require("jsonwebtoken");

function generateToken(user) {
  const payload = {
    email: user.email,
    isAdmin: user.isAdmin,
  };

  return jwt.sign(payload, jwtSecretKey, { expiresIn: "1h" });
}

function verifyToken(token) {
  try {
    return jwt.verify(token, jwtSecretKey);
  } catch (error) {
    return null;
  }
}

function authenticateToken(req, res, next) {
  const tokenWithPrefix = req.header("Authorization");
  const token = tokenWithPrefix.replace("Bearer ", "");

  if (!token) {
    return res.status(401).json({ message: "Unauthorized" });
  }

  try {
    const user = jwt.verify(token, jwtSecretKey);
    req.user = user;
    next();
  } catch (error) {
    res.status(403).json({ message: "Invalid token" });
  }
}

module.exports = { generateToken, verifyToken, authenticateToken };
