import subprocess
import os
import json
from loguru import logger

class PyGIMP:
    def __init__(self, gimp_executable="gimp-console-2.10.exe", log_file="gimp_script.log", config_file="gimp_script_config.json"):
        self.gimp_executable = gimp_executable
        logger.add(log_file, rotation="500 KB")
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def update_config(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.config["arguments"]:
                self.config["arguments"][key] = value

        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def execute_script(self):
        logger.info("GIMPスクリプトの実行を開始します")

        script_path = self.config["script_path"]
        logger.info(f"スクリプトパス: {script_path}")

        with open(script_path, 'r', encoding='utf-8') as file:
            script_content = file.read()

        commands = [
            self.gimp_executable,
            "--batch-interpreter",
            "python-fu-eval",
            "--batch",
            script_content,
        ]
        full_command = ' '.join(commands)
        logger.info(f"実行コマンド: {full_command[:30]} ...")

        process = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        output = stdout.decode().strip()
        error = stderr.decode().strip()

        logger.info(f"GIMPの標準出力:\n{output}")

        if process.returncode != 0:
            logger.error(f"GIMPスクリプトの実行が失敗しました。終了コード: {process.returncode}")
        else:
            logger.success("GIMPスクリプトの実行が完了しました")

        return output, error
