const express = require("express");
const UserModel = require("../models/User.ts");
const app = express();
const router = express.Router();

router.post("/add_user", async (request, response) => {
  const user = new UserModel(request.body);

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

module.exports = router;
