const fs = require("fs");
const path = require("path");

exports.handler = async function (event, context) {
  const filename = event.queryStringParameters.filename;
  if (!filename) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: "Missing filename parameter" }),
    };
  }
  const safeName = path.basename(filename);
  const filePath = path.join(__dirname, "..", "..", "outputs_project_1", safeName);

  if (!fs.existsSync(filePath)) {
    return {
      statusCode: 404,
      body: JSON.stringify({ error: "File not found" }),
    };
  }

  const ext = path.extname(safeName).toLowerCase();
  let contentType = "application/octet-stream";
  if (ext === ".png") contentType = "image/png";
  else if (ext === ".csv") contentType = "text/csv";
  else if (ext === ".pdf") contentType = "application/pdf";
  else if (ext === ".joblib") contentType = "application/octet-stream";

  const fileBuffer = fs.readFileSync(filePath);

  return {
    statusCode: 200,
    headers: {
      "Content-Type": contentType,
      "Content-Disposition": 'attachment; filename="' + safeName + '"',
    },
    body: fileBuffer.toString("base64"),
    isBase64Encoded: true,
  };
};