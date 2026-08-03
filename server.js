const express = require("express");
const path = require("path");
const { spawn } = require("child_process");
const fs = require("fs");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

app.post("/api/predict", (req, res) => {
  const python = spawn("python3", ["predict.py"]);

  let stdoutData = "";
  let stderrData = "";

  python.stdout.on("data", (data) => {
    stdoutData += data.toString();
  });

  python.stderr.on("data", (data) => {
    stderrData += data.toString();
  });

  python.on("close", (code) => {
    if (code !== 0) {
      return res.status(500).json({ error: "Prediction failed: " + stderrData });
    }
    try {
      const result = JSON.parse(stdoutData);
      if (result.error) {
        return res.status(400).json(result);
      }
      res.json(result);
    } catch (parseError) {
      res.status(500).json({ error: "Failed to parse prediction result" });
    }
  });

  python.on("error", (err) => {
    res.status(500).json({ error: "Failed to start Python: " + err.message });
  });

  python.stdin.write(JSON.stringify(req.body));
  python.stdin.end();
});

app.get("/api/model-info", (req, res) => {
  const csvPath = path.join(__dirname, "outputs_project_1", "model_comparison.csv");
  fs.readFile(csvPath, "utf8", (err, data) => {
    if (err) {
      return res.status(500).json({ error: "Could not read model comparison data" });
    }
    const lines = data.trim().split(/\r?\n/);
    const headers = lines[0].split(",");
    const rows = lines.slice(1).map((line) => {
      const values = line.split(",");
      return Object.fromEntries(headers.map((h, i) => [h.trim(), (values[i] || "").trim()]));
    });
    res.json({ models: rows });
  });
});

app.get("/api/download/:filename", (req, res) => {
  const filename = req.params.filename;
  const safeName = path.basename(filename);
  const filePath = path.join(__dirname, "outputs_project_1", safeName);

  if (!fs.existsSync(filePath)) {
    return res.status(404).json({ error: "File not found" });
  }

  const ext = path.extname(safeName).toLowerCase();
  let contentType = "application/octet-stream";
  if (ext === ".png") contentType = "image/png";
  else if (ext === ".csv") contentType = "text/csv";
  else if (ext === ".pdf") contentType = "application/pdf";

  res.setHeader("Content-Type", contentType);
  res.setHeader("Content-Disposition", 'attachment; filename="' + safeName + '"');
  fs.createReadStream(filePath).pipe(res);
});

app.listen(PORT, () => {
  console.log("Server running at http://localhost:" + PORT);
});