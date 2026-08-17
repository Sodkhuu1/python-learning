// server.js
const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");

const app = express();

// CORS: Vercel дээрх фронтоос request зөвшөөрнө
app.use(cors());

// JSON body
app.use(express.json());

// ==== MongoDB connection ====
// Railway дээр MONGO_URL env var ашиглана (эсвэл Atlas-ийн URL)
const MONGO_URL = process.env.MONGO_URL;
if (!MONGO_URL) {
  console.error("MONGO_URL is not set!");
  process.exit(1);
}

mongoose
  .connect(MONGO_URL)
  .then(() => console.log("MongoDB connected"))
  .catch((err) => console.error("Mongo error:", err));


// ==== Schema & Model ====
const itemSchema = new mongoose.Schema({
  text: { type: String, required: true },
});

const Item = mongoose.model("Item", itemSchema);

// ==== Routes ====

// Health check (Railway дээр шалгахад амар)
app.get("/", (req, res) => {
  res.json({ ok: true, message: "API is running" });
});

// GET /api/items
app.get("/api/items", async (req, res) => {
  try {
    const items = await Item.find().sort({ _id: -1 });
    res.json(items);
  } catch (err) {
    res.status(500).json({ error: "Server error" });
  }
});

// POST /api/items
app.post("/api/items", async (req, res) => {
  try {
    const { text } = req.body;
    if (!text || !text.trim()) {
      return res.status(400).json({ error: "text is required" });
    }

    const item = new Item({ text: text.trim() });
    await item.save();
    res.status(201).json(item);
  } catch (err) {
    res.status(500).json({ error: "Server error" });
  }
});

// ==== Start server ====
const PORT = process.env.PORT || 3000; // Railway өөрөө PORT өгнө
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
