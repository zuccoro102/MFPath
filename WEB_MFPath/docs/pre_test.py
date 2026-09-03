import time
import csv
import os
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# CSVファイルの保存先設定
csv_file = "voltage_pres_time.csv"

# I2CバスとADC(ADS1015)の初期化
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1015(i2c)

# ゲイン（測定レンジ）の設定
# GAIN = 1 のとき、測定レンジは ±4.096V となります。
# ただし、モジュール電源が3.3Vなので、実質の最大測定電圧は3.3Vまでです。
ads.gain = 1

# チャンネル0 (A0) と チャンネル1 (A1) の設定
chan0 = AnalogIn(ads, 0)
chan1 = AnalogIn(ads, 1)

# CSVファイルの初期化（ファイルがなければヘッダーを書き込む）
if not os.path.exists(csv_file):
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["datetime", "elapsed_time(s)", "A0_voltage(V)", "A1_voltage(V)"])

start_time = time.time()
print("電圧の測定とCSVへの保存を開始しました。（Ctrl+Cで終了）")

try:
    while True:
        # 現在の時刻を取得 (YYYY-MM-DD HH:MM:SS)
        # 時刻と経過時間の取得
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        elapsed_time = time.time() - start_time
        
        # 実際の電圧値（CSVには生の値をそのまま保存します）
        raw_v0 = chan0.voltage
        raw_v1 = chan1.voltage
        
        # 画面に表示
        print(f"[{current_time}] {raw_v0:.3f} {raw_v1:.3f} V")
        
        # CSVファイルに追記（生データを保存）
        with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([current_time, f"{elapsed_time:.2f}", raw_v0, raw_v1])
            
        # 10秒間待機
        time.sleep(10)

except KeyboardInterrupt:
    print("\n測定を終了しました。")
