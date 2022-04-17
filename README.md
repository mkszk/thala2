# thala2
このライブラリは、動画素材へ字幕・ナレーションを追加するのを助けます。


## Demo
実際に作成した動画です。

https://youtu.be/IyIFvMwNEXM

## Description

現在の機能は以下の通りです。

- 素材読み込み
    - 動画
    - 音声
    - 画像
- 字幕およびナレーションの生成
- 動画のサイズや長さの調整


### 素材読み込み

動画・音声・画像といった素材を読み込みます。
対応しているファイル形式については依存先ライブラリ次第です。

- 動画：MoviePyの対応しているファイル形式
- 音声：MoviePyの対応しているファイル形式
- 画像：OpenCVの対応しているファイル形式


### 字幕およびナレーションの生成

字幕はPILライブラリを用いて生成しています。

ナレーションは以下のTTS用ライブラリを使用して生成します。

- VOICEVOX（デフォルト音声：四国めたんノーマル）
- gTTS

thala2.Audioの初期化時にTTS用ライブラリを指定した場合はそのライブラリを使用します。
TTS用ライブラリを指定しなかった場合は、
localhostでVOICEVOXエンジンが動いているのを検出したならそれを使用し、
検出しないならgTTSを使用します。

## 語源

Thalaは『指輪物語』のエルフ語で<del>「映像」</del>という意味だそうです。

検索して参考にしたサイトが誤訳していたのに気づきました。
英語のエルフ語辞書によるとThalaは形容詞の「堅い」という意味だそうです。
「film」ではなく「firm」！


## Requirement

依存先のソフトウェアはrequirements.txtを参照してください。


## Usage

 1. 実行パスにImageMagickとFFmpegを含めるか、
    環境変数にImageMagickとFFmpegを指定してください。
    これはMoviePyでの依存先の指定法に従っています。
 2. python tests/xml2mp4.py tests/files/subtitles.xml


## Install

zipをダウンロードして適当に配置してください。


## Contribution

 1. フォークする（http://github.com/mkszk/voicedub）
 2. Featureブランチを作る（git checkout -b my-new-feature）
 3. コミットする（git commit -am 'Add some feature'）
 4. 公開リポジトリにプッシュする（git push origin my-new-feature）
 5. プルリクエストを送る


## Licence

[MIT](https://github.com/tcnksm/tool/blob/master/LICENCE)

## Author

[mkszk](https://github.com/mkszk)
