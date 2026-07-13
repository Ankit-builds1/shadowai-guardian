const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const source = fs.readFileSync(path.join(__dirname, "content.js"), "utf8");

assert.equal(source.includes("panel.innerHTML"), false, "panels must not render dynamic HTML");
assert.equal(source.includes("textContent"), true, "panels must render result text safely");
assert.equal(source.includes("insertAdjacentHTML"), false, "HTML insertion is not allowed");

console.log("content safety tests passed");
