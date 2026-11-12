// Loads the calculator's script from the built page into Node, without a browser.
const fs = require("fs"), path = require("path"), vm = require("vm");
module.exports = function load(file) {
  const html = fs.readFileSync(file || path.join(__dirname, "..", "Cost_Converter.html"), "utf8");
  const m = html.match(/<script>([\s\S]*)<\/script>/);
  if (!m) throw new Error("no script in page");
  const ctx = { console: console, URLSearchParams: URLSearchParams };
  vm.createContext(ctx);
  vm.runInContext(m[1], ctx);
  return ctx.HCC;
};
