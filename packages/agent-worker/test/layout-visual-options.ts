/**
 * Visual layout options comparison
 *
 * Run: bun run test/layout-visual-options.ts
 */

import chalk from "chalk";

// Sample messages
const messages = [
  { time: "01:17:13", from: "workflow", content: "Running workflow: test-simple" },
  { time: "01:17:13", from: "workflow", content: "Agents: alice, bob" },
  { time: "01:17:14", from: "system", content: "Test workflow started\n\n@alice - Please ask @bob a question.\n\n@bob - Please answer." },
  { time: "01:17:20", from: "alice", content: "@bob What are AI agents?" },
  { time: "01:17:25", from: "bob", content: "@alice AI agents are autonomous software entities that perceive their environment and take actions." },
];

console.log("=".repeat(80));
console.log("VISUAL LAYOUT OPTIONS");
console.log("=".repeat(80));
console.log();

// ==================== Option 1: Clean & Bold ====================
console.log("━".repeat(80));
console.log("📌 Option 1: Clean & Bold (recommended)");
console.log("━".repeat(80));
console.log();

messages.forEach((msg, i) => {
  const lines = msg.content.split("\n");
  if (i === 0 || messages[i-1]?.from !== msg.from) {
    console.log(`${chalk.dim(msg.time)} ${chalk.bold.cyan(msg.from)}`);
  } else {
    console.log(`${" ".repeat(8)} ${chalk.dim("│")}`);
  }
  lines.forEach(line => {
    console.log(`         ${chalk.dim("│")} ${line}`);
  });
});

console.log();
console.log();

// ==================== Option 2: Box Style ====================
console.log("━".repeat(80));
console.log("📦 Option 2: Box Style (elegant)");
console.log("━".repeat(80));
console.log();

messages.forEach((msg, i) => {
  const lines = msg.content.split("\n");
  if (i === 0 || messages[i-1]?.from !== msg.from) {
    console.log(`${chalk.dim(msg.time)} ${chalk.cyan("┃")} ${chalk.bold.cyan(msg.from)}`);
  } else {
    console.log(`${" ".repeat(8)} ${chalk.cyan("┃")}`);
  }
  lines.forEach(line => {
    console.log(`         ${chalk.cyan("┃")} ${line}`);
  });
});

console.log();
console.log();

// ==================== Option 3: Dot Indicator ====================
console.log("━".repeat(80));
console.log("🎯 Option 3: Dot Indicator (modern)");
console.log("━".repeat(80));
console.log();

messages.forEach((msg, i) => {
  const lines = msg.content.split("\n");
  const colors = [chalk.cyan, chalk.yellow, chalk.magenta, chalk.green];
  const color = colors[["workflow", "system", "alice", "bob"].indexOf(msg.from)] || chalk.cyan;

  if (i === 0 || messages[i-1]?.from !== msg.from) {
    console.log(`${chalk.dim(msg.time)} ${color("●")} ${chalk.bold(msg.from)}`);
  } else {
    console.log(`${" ".repeat(8)} ${chalk.dim("│")}`);
  }
  lines.forEach(line => {
    console.log(`         ${chalk.dim("│")} ${line}`);
  });
});

console.log();
console.log();

// ==================== Option 4: Arrow Style ====================
console.log("━".repeat(80));
console.log("➤ Option 4: Arrow Style (dynamic)");
console.log("━".repeat(80));
console.log();

messages.forEach((msg, i) => {
  const lines = msg.content.split("\n");
  if (i === 0 || messages[i-1]?.from !== msg.from) {
    console.log(`${chalk.dim(msg.time)} ${chalk.cyan("▶")} ${chalk.bold.cyan(msg.from)}`);
  } else {
    console.log(`${" ".repeat(8)} ${chalk.dim("│")}`);
  }
  lines.forEach(line => {
    console.log(`         ${chalk.dim("│")} ${line}`);
  });
});

console.log();
console.log();

// ==================== Option 5: Compact ====================
console.log("━".repeat(80));
console.log("📝 Option 5: Compact (space-efficient)");
console.log("━".repeat(80));
console.log();

messages.forEach((msg, i) => {
  const lines = msg.content.split("\n");
  if (i === 0 || messages[i-1]?.from !== msg.from) {
    console.log(`${chalk.dim(msg.time)} ${chalk.cyan(msg.from)}`);
  }
  lines.forEach(line => {
    console.log(`         ${line}`);
  });
});

console.log();
console.log();

// ==================== Option 6: Double Line ====================
console.log("━".repeat(80));
console.log("║ Option 6: Double Line (strong separation)");
console.log("━".repeat(80));
console.log();

messages.forEach((msg, i) => {
  const lines = msg.content.split("\n");
  if (i === 0 || messages[i-1]?.from !== msg.from) {
    console.log(`${chalk.dim(msg.time)} ${chalk.cyan("║")} ${chalk.bold.cyan(msg.from)}`);
  } else {
    console.log(`${" ".repeat(8)} ${chalk.cyan("║")}`);
  }
  lines.forEach(line => {
    console.log(`         ${chalk.cyan("║")} ${line}`);
  });
});

console.log();
console.log();

console.log("━".repeat(80));
console.log("💡 RECOMMENDATIONS");
console.log("━".repeat(80));
console.log();
console.log("🏆 Best overall: Option 1 (Clean & Bold)");
console.log("   - Simple, readable, works on any terminal");
console.log("   - Clear hierarchy with bold sender names");
console.log();
console.log("🎨 Most elegant: Option 2 (Box Style)");
console.log("   - Thicker separator (┃) for better visual separation");
console.log("   - Professional look");
console.log();
console.log("⚡ Most modern: Option 3 (Dot Indicator)");
console.log("   - Colored dots match sender");
console.log("   - Clean, GitHub-style feel");
console.log();
console.log("=".repeat(80));
