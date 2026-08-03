const fs = require("fs");
const path = require("path");

exports.handler = async function (event, context) {
  const csvPath = path.join(__dirname, "..", "..", "outputs_project_1", "model_comparison.csv");

  try {
    const data = fs.readFileSync(csvPath, "utf8");
    const lines = data.trim().split(/\r?\n/);
    const headers = lines[0].split(",");
    const rows = lines.slice(1).map((line) => {
      const values = line.split(",");
      return Object.fromEntries(headers.map((h, i) => [h.trim(), (values[i] || "").trim()]));
    });
    return {
      statusCode: 200,
      body: JSON.stringify({ models: rows }),
    };
  } catch (err) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: err.message }),
    };
  }
};