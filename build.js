const fs = require("fs");
const path = require("path");

const DIST = path.join(__dirname, "dist");
const PUBLIC = path.join(__dirname, "public");
const OUTPUTS = path.join(__dirname, "outputs_project_1");
const MODEL_STRUCT = path.join(__dirname, "model_structure.json");

function copyDir(src, dest) {
  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }
  const entries = fs.readdirSync(src, { withFileTypes: true });
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

function minifyJS(content) {
  return content
    .replace(/\/\/.*$/gm, "")
    .replace(/\/\*[\s\S]*?\*\//g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function minifyCSS(content) {
  return content
    .replace(/\/\*[\s\S]*?\*\//g, "")
    .replace(/\s+/g, " ")
    .trim();
}

if (fs.existsSync(DIST)) {
  fs.rmSync(DIST, { recursive: true });
}
fs.mkdirSync(DIST, { recursive: true });

const html = fs.readFileSync(path.join(PUBLIC, "index.html"), "utf8");
fs.writeFileSync(path.join(DIST, "index.html"), html);

const css = fs.readFileSync(path.join(PUBLIC, "style.css"), "utf8");
fs.writeFileSync(path.join(DIST, "style.css"), minifyCSS(css));

let js = fs.readFileSync(path.join(PUBLIC, "script.js"), "utf8");
js = js.replace(
  /fetch\("\/api\//g,
  'fetch("/.netlify/functions/'
);
fs.writeFileSync(path.join(DIST, "script.js"), minifyJS(js));

copyDir(OUTPUTS, path.join(DIST, "outputs"));

if (fs.existsSync(MODEL_STRUCT)) {
  fs.copyFileSync(MODEL_STRUCT, path.join(DIST, "model_structure.json"));
}

console.log("Build complete. Dist folder ready for Netlify deployment.");