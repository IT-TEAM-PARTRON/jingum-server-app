const fs = require("fs");
const path = require("path");

const projectDir = __dirname;
const venvPython = process.platform === "win32"
  ? path.join(projectDir, ".venv", "Scripts", "python.exe")
  : path.join(projectDir, ".venv", "bin", "python");

const pythonInterpreter = process.env.JINGUM_PYTHON
  || (fs.existsSync(venvPython) ? venvPython : (process.platform === "win32" ? "python" : "python3"));

module.exports = {
  apps: [
    {
      name: "Jingum_Web",
      cwd: projectDir,
      script: path.join(projectDir, "serve.py"),
      interpreter: pythonInterpreter,
      instances: 1,
      autorestart: true,
      watch: false,
      min_uptime: "10s",
      max_restarts: 10,
      restart_delay: 3000,
      kill_timeout: 10000,
      time: true,
      env: {
        PYTHONUNBUFFERED: "1",
      },
    },
  ],
};
