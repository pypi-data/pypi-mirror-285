import subprocess
import ffmpeg
import sys

_installed = False

def is_ffmpeg_installed():
    global _installed
    if _installed == True:
        return True
    try:
        # FFmpegがインストールされているかを確認
        result = subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _installed = True
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False

def install_ffmpeg(sync=False):
    if is_ffmpeg_installed():
        return

    # # パッケージリストを更新
    # subprocess.Popen(["apt-get", "update"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # FFmpegをインストール
    if sync:
        subprocess.run(["apt-get", "install", "-y", "ffmpeg"], check=True)
        print("FFmpeg installation complete.")    
    else:
        subprocess.Popen(["apt-get", "install", "-y", "ffmpeg"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("FFmpeg installation started in the background.")

def create_video(uuid0, framerate, filename):
    install_ffmpeg(sync=True)
    print(f'!ffmpeg -y -framerate {framerate} -i canvas{uuid0}/frame%04d.png -vcodec libx264 -pix_fmt yuv420p {filename}')
    # FFmpegコマンドを実行し、stderrをキャプチャ
    process = (
        ffmpeg
        .input(f'canvas{uuid0}/frame%04d.png', framerate=framerate)
        .output(filename, vcodec='libx264', pix_fmt='yuv420p')
        .run_async(pipe_stdout=True, pipe_stderr=True, overwrite_output=True)
    )

    # ストリームを読み取ってstderrを表示
    stdout, stderr = process.communicate()
    # print('@', stdout, stderr)

    # 標準エラー出力を表示
    if stderr:
        filename = filename.replace('.', '_')
        with open(f'{filename}_log.txt', 'w') as f:
            f.write(stderr.decode('utf-8'))
