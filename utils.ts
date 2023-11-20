const { jwtSecretKey } = require("./config");

const jwt = require("jsonwebtoken");

function generateToken(user) {
  const payload = {
    email: user.email,
    isAdmin: user.isAdmin,
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

function generateRandomString() {
  const lowercaseLetters = "abcdefghijklmnopqrstuvwxyz";
  const uppercaseLetters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  const specialCharacters = "!@#$%^&*()_+{}|:<>?-=[];,./";

  const randomUppercase =
    uppercaseLetters[Math.floor(Math.random() * uppercaseLetters.length)];

  const randomSpecialChar =
    specialCharacters[Math.floor(Math.random() * specialCharacters.length)];

  const randomChars = Array.from(
    { length: 8 },
    () => lowercaseLetters[Math.floor(Math.random() * lowercaseLetters.length)]
  );

  const allChars = randomChars.concat(randomUppercase, randomSpecialChar);
  const shuffledChars = allChars.sort(() => Math.random() - 0.5);

  const randomString = shuffledChars.join("");

  return randomString;
}

function generateUniqueEmail(firstName, lastName, existingEmails) {
  const baseEmail = `${firstName.toLowerCase()}.${lastName.toLowerCase()}@eeg.com`;
  let generatedEmail = baseEmail;
  let counter = 1;

  while (existingEmails.includes(generatedEmail)) {
    generatedEmail = `${firstName.toLowerCase()}.${lastName.toLowerCase()}${counter}@eeg.com`;
    counter++;
  }

  return generatedEmail;
}

module.exports = {
  generateToken,
  verifyToken,
  authenticateToken,
  generateRandomString,
  generateUniqueEmail,
};
