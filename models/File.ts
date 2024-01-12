const mongoose = require("mongoose");

const FileSchema = new mongoose.Schema({
  fileName: {
    type: String,
    required: true,
  },
  mimeType: {
    type: String,
    required: true,
  },
  data: {
    type: String,
    required: true,
  },
});

const File = mongoose.model("File", FileSchema);

module.exports = File;
