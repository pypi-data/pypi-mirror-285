import argparse
import json
from art import text2art
from loguru import logger
from .pygimp_core import PyGIMP

def main():
    parser = argparse.ArgumentParser(description="PyGIMP Text Image Creator")

    with open("gimp_script_config.json", 'r', encoding='utf-8') as f:
        config = json.load(f)

    for arg_name, arg_value in config["arguments"].items():
        parser.add_argument(f"--{arg_name}", help=f"Value for {arg_name}", default=arg_value)

    parser.add_argument("--gimp", default="gimp-console-2.10.exe", help="Path to GIMP executable")
    parser.add_argument("--log", default="gimp_script.log", help="Path to the log file")
    parser.add_argument("--config", default="gimp_script_config.json", help="Path to the configuration file")

    args = parser.parse_args()

    print(text2art("PyGIMP"))
    logger.info("プログラムを開始します")

    pygimp = PyGIMP(args.gimp, args.log, args.config)

    # Update config with command line arguments
    config_update = {k: v for k, v in vars(args).items() if k in config["arguments"]}
    pygimp.update_config(**config_update)
    pygimp.execute_script()

    logger.info("プログラムを終了します")
    print(text2art("Completed!", font="small"))


if __name__ == "__main__":
    main()
