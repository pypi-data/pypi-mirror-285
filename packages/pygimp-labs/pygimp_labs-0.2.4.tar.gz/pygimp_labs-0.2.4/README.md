
<p align="center">
<img src="https://huggingface.co/datasets/MakiAi/IconAssets/resolve/main/PyGIMP.png" width="100%">
<br>
<h1 align="center">PyGIMP</h1>
<h2 align="center">
  ～ Fusion of Python and GIMP ～
<br>
  <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/pygimp-labs">
<img alt="PyPI - Format" src="https://img.shields.io/pypi/format/pygimp-labs">
<img alt="PyPI - Implementation" src="https://img.shields.io/pypi/implementation/pygimp-labs">
<img alt="PyPI - Status" src="https://img.shields.io/pypi/status/pygimp-labs">
<img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dd/pygimp-labs">
<img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dw/pygimp-labs">
<a href="https://github.com/Sunwood-ai-labs/PyGIMP" title="Go to GitHub repo"><img src="https://img.shields.io/static/v1?label=PyGIMP&message=Sunwood-ai-labs&color=blue&logo=github"></a>
<img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/Sunwood-ai-labs/PyGIMP">
<a href="https://github.com/Sunwood-ai-labs/PyGIMP"><img alt="forks - Sunwood-ai-labs" src="https://img.shields.io/github/forks/PyGIMP/Sunwood-ai-labs?style=social"></a>
<a href="https://github.com/Sunwood-ai-labs/PyGIMP"><img alt="GitHub Last Commit" src="https://img.shields.io/github/last-commit/Sunwood-ai-labs/PyGIMP"></a>
<a href="https://github.com/Sunwood-ai-labs/PyGIMP"><img alt="GitHub Top Language" src="https://img.shields.io/github/languages/top/Sunwood-ai-labs/PyGIMP"></a>
<img alt="GitHub Release" src="https://img.shields.io/github/v/release/Sunwood-ai-labs/PyGIMP?color=red">
<img alt="GitHub Tag" src="https://img.shields.io/github/v/tag/Sunwood-ai-labs/PyGIMP?sort=semver&color=orange">
<img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/Sunwood-ai-labs/PyGIMP/publish-to-pypi.yml">
<br>
<p align="center">
  <a href="https://hamaruki.com/"><b>[🌐 Website]</b></a> •
  <a href="https://github.com/Sunwood-ai-labs"><b>[🐱 GitHub]</b></a>
  <a href="https://x.com/hAru_mAki_ch"><b>[🐦 Twitter]</b></a> •
  <a href="https://hamaruki.com/"><b>[🍀 Official Blog]</b></a>
</p>

</h2>

</p>

>[!IMPORTANT]
>このリポジトリのリリースノートやREADME、コミットメッセージの9割近くは[claude.ai](https://claude.ai/)や[ChatGPT4](https://chatgpt.com/)を活用した[AIRA](https://github.com/Sunwood-ai-labs/AIRA), [SourceSage](https://github.com/Sunwood-ai-labs/SourceSage), [Gaiah](https://github.com/Sunwood-ai-labs/Gaiah), [HarmonAI_II](https://github.com/Sunwood-ai-labs/HarmonAI_II)で生成しています。

# PyGIMP

## 🌟 Introduction

PyGIMPは、PythonプログラミングとGIMP（GNU Image Manipulation Program）の強力な機能を融合させたプロジェクトです。このツールキットを使用することで、開発者やデザイナーはPythonのシンプルさと柔軟性を活かしながら、GIMPの高度な画像処理機能にアクセスできます。

## 🎥 Demo

https://github.com/user-attachments/assets/bea57935-2f4a-46be-8932-a57a7151335d


## 🚀 Getting Started

PyGIMPを始めるためには、以下の手順に従ってください：

1. [GIMP](https://www.gimp.org/downloads/)をインストールします。
2. Pythonをインストールします（バージョン3.12以上を推奨）。
3. PyGIMPパッケージをダウンロードし、インストールします。
    ```bash
    pip install pygimp-labs
    ```
4. Pythonスクリプトを作成し、GIMPと連携させて様々な画像処理を行います。

```bash
(base) C:\Prj\PyGIMP>pygimp-labs
 ____           ____  ___  __  __  ____  
|  _ \  _   _  / ___||_ _||  \/  ||  _ \
| |_) || | | || |  _  | | | |\/| || |_) |
|  __/ | |_| || |_| | | | | |  | ||  __/
|_|     \__, | \____||___||_|  |_||_|
        |___/

2024-07-20 11:00:45.587 | INFO     | pygimp.cli:main:23 - プログラムを開始します
2024-07-20 11:00:45.588 | INFO     | pygimp.pygimp_core:execute_script:26 - GIMPスクリプトの実行を開始します

...

*******************
* GIMP Script End *
*******************
2024-07-20 11:00:48.498 | SUCCESS  | pygimp.pygimp_core:execute_script:55 - GIMPスクリプトの実行が完了しました
2024-07-20 11:00:48.498 | INFO     | pygimp.cli:main:32 - プログラムを終了します
  ___                    _       _            _  _
 / __| ___  _ __   _ __ | | ___ | |_  ___  __| || |
| (__ / _ \| '  \ | '_ \| |/ -_)|  _|/ -_)/ _` ||_|
 \___|\___/|_|_|_|| .__/|_|\___| \__|\___|\__,_|(_)
                  |_|

```


## 📝 Arguments

`pygimp-labs` コマンドは以下の引数を受け取ります。

| 引数 | 説明 | デフォルト値 |
|---|---|---|
| `--font_size` | テキストのフォントサイズ | `78` |
| `--input_image` | 入力画像のパス | `asset\input\input.png` |
| `--output_path` | 出力画像のパス | `asset\output\out2.png` |
| `--text` | 画像にオーバーレイするテキスト | `"GIMPを使用して\nCLIから画像に\nテキストをオーバーレイする方法"` |
| `--gimp` | GIMP実行ファイルのパス | `"gimp-console-2.10.exe"` |
| `--log` | ログファイルのパス | `"gimp_script.log"` |
| `--config` | 設定ファイルのパス | `"gimp_script_config.json"` |


## 📝 Updates

PyGIMPは継続的に改善されており、新機能やバグ修正が定期的にリリースされています。最新の更新内容は、リリースノートや公式リポジトリで確認できます。

## 🤝 Contributing

PyGIMPに貢献したい方は、以下の手順を実行してください：

1. プロジェクトをフォークします。
2. 新しいブランチを作成します。
3. 変更を加えた後、プルリクエストを提出します。
4. コードレビューが行われ、マージされるのを待ちます。

## 📄 License

このプロジェクトはMITライセンスのもとで提供されています。詳細はLICENSEファイルをご覧ください。

## 🙏 Acknowledgements

PyGIMPは、オープンソースコミュニティの協力によって成り立っています。プロジェクトに貢献してくださったすべての方々に感謝します。また、GIMPの開発チームにも感謝の意を表します。
