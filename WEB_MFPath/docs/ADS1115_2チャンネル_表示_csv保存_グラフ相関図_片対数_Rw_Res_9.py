import time
import csv
import os
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import matplotlib.pyplot as plt

# CSVファイルの保存先設定
csv_file = "Voltage_Lin_correlation_f20_1.5V_0.02A_100-22ohm_1.6k_1115_2.csv"

# I2CバスとADC(ADS1015)の初期化
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

# ゲイン（測定レンジ）の設定
ads.gain = 1

# チャンネル1 (A0) と チャンネル2 (A1) の設定
chan1 = AnalogIn(ads, 1)
chan2 = AnalogIn(ads, 0)
chan3 = AnalogIn(ads, 2)
chan4 = AnalogIn(ads, 3)

# CSVファイルの初期化（ヘッダー書き込み）
if not os.path.exists(csv_file):
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["datetime", "A1_pressure(Pa)", "A0_Va(V)", "A2_Vw(V)", "A3_V1(V)"])

# グラフ用のデータ格納リスト
a1_voltages = []
a2_voltages = []

# --- 一時停止フラグの管理用変数 ---
is_paused = False

# グラフの初期設定
plt.ion()
fig, ax = plt.subplots()
line, = ax.plot([], [], marker='o', markersize=3, color='purple', linestyle='-')

ax.set_xscale('log')
ax.set_yscale('linear')
ax.set_xlabel('A1 Pressure (Pa) - Log Scale')
ax.set_ylabel('A0 Voltage (V) - Linear Scale')
ax.set_title('Real-time Correlation (A1 vs A0)')
ax.grid(True, which="both", ls="--")

# --- キーイベントハンドラ関数の定義 ---
def on_key(event):
    global is_paused
    if event.key == 's':
        if not is_paused:
            is_paused = True
            print("\n【保存・プロット一時停止】 画面表示のみ継続中... ('r' で再開)")
    elif event.key == 'r':
        if is_paused:
            is_paused = False
            print("\n【計測再開】 保存・プロットを再開します。")

# グラフウィンドウにキーイベントを紐付け
fig.canvas.mpl_connect('key_press_event', on_key)

print("A0, A1, A2, A3 の測定・CSV保存・両対数プロットを開始しました。")
print("電圧の測定とCSVへの保存を開始しました。（Ctrl+Cで終了）")
print("※ グラフ画面をアクティブにして 's' で停止、'r' で再開します。")

try:
    while plt.fignum_exists(fig.number):
        # 1. データの取得と変換（常に実行）
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        raw_v1 = chan1.voltage
        raw_v2 = chan2.voltage
        raw_v3 = chan3.voltage
        raw_v4 = chan4.voltage
        raw_v1 = 1.02 * 10 ** (raw_v1 * 6.29 - 11)

        # 2. 画面への表示（常に実行、一時停止中は末尾に [PAUSED] と表示）
        status_tag = " [PAUSED]" if is_paused else ""
        print(f"[{current_time}] {raw_v1:.4f} Pa {raw_v2:.4f} V(Va) {raw_v3:.4f} V(Vw) {raw_v4:.4f} V(V1){status_tag}")
        
        # --- 一時停止時の分岐点 ---
        if is_paused:
            # 一時停止中は、CSV保存とグラフ更新をスキップして、キー入力待ちのウェイトへ進む
            for _ in range(25):
                if not is_paused or not plt.fignum_exists(fig.number):
                    break
                plt.pause(0.2)
            continue

        # 3. グラフ表示用の電圧値計算（計測中のみ）
        graph_v1 = max(raw_v1, 1e-4)
        graph_v2 = max(raw_v2, -0.1)
        
        # 4. CSVファイルに追記（計測中のみ）
        with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([current_time, raw_v1, raw_v2, raw_v3, raw_v4])
        
        # 5. グラフ用リストへのデータ追加と更新（計測中のみ）
        a1_voltages.append(graph_v1)
        a2_voltages.append(graph_v2)
        line.set_data(a1_voltages, a2_voltages)
        
        ax.relim()
        ax.autoscale_view()
        plt.draw()
        
        # 5秒のウェイト（計測中のみ）
        for _ in range(25):
            if is_paused or not plt.fignum_exists(fig.number):
                break
            plt.pause(0.2)

except KeyboardInterrupt:
    print("\n測定を終了しました。")
finally:
    plt.ioff()
    plt.show()

