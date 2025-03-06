from modules.GameManager.FileManager import *
from modules.logger import *
import pyperclip
import os
import re

def copy(manager):
    if manager.Curr_Benchmark is None:
        return
    
    patch_info = manager.ultracam_beyond.get("Keys", [""])
    resolution = manager.UserChoices["resolution"].get()
    shadows = int(manager.UserChoices["shadow resolution"].get().split("x")[0])

    system_os = "MacOS" if platform.system() == "Darwin" else platform.system()
    benchmark_result = (
        f"## **{manager.Curr_Benchmark}** Tears Of The Kingdom on {system_os}\n"
    )

    if platform.system() != "Darwin":
        benchmark_result += f"- **{gpu_name}**\n"
    benchmark_result += (
        f"- **{CPU}**\n"
        f"- **{total_memory}** GB RAM at **{FREQUENCY}** MHz\n"
        f"- **{resolution}** and Shadows: **{shadows}**, FPS CAP: **{manager.UserChoices['fps'].get()}**\n"
        f"## Results:\n"
        f"- Total Frames **{manager.benchmarks[manager.Curr_Benchmark]['Total Frames']}**\n"
        f"- Average FPS **{manager.benchmarks[manager.Curr_Benchmark]['Average FPS']}**\n"
        f"- 1% Lows **{manager.benchmarks[manager.Curr_Benchmark]['1% Low FPS']}** FPS\n"
        f"- 0.1% Lows **{manager.benchmarks[manager.Curr_Benchmark]['0.1% Lowest FPS']}** FPS\n"
    )

    pyperclip.copy(benchmark_result)

def load_last_benchmark(self, name):
    self.maincanvas.itemconfig("benchmark-label", text=name)
    self.Curr_Benchmark = name

    if name is None:
        return


    self.maincanvas.itemconfig(
        "benchmark_info",
        text=f"TOTAL Frames - {self.benchmarks[name]['Total Frames']} Frames\n"
        f"Average - {self.benchmarks[name]['Average FPS']} FPS\n"
        f"1% Lowest FPS - {self.benchmarks[name]['1% Low FPS']} FPS\n"
        f"0.1% Lowest FPS - {self.benchmarks[name]['0.1% Lowest FPS']} FPS\n",
    )


def load_benchmark(self):
    benchmark_file = os.path.join(FileManager.sdmc_dir, "TOTKBenchmark.txt")
    print(benchmark_file)
    Last_Found = None

    try:
        with open(benchmark_file, "r") as benchmarks:
            for line in benchmarks:
                match = re.search(r"BENCHMARK FOR (\w+) COMPLETED", line)

                if not match:
                    continue

                BenchmarkName = match.group(1)
                    
                next_line = next(benchmarks).strip()
                pattern = r"(\d+(\.\d+)?)"
                frames = re.findall(pattern, next_line)
                numbers = [
                    float(num[0]) if "." in num[0] else int(num[0])
                    for num in frames
                ]
                if numbers[2] == 1:
                    numbers.pop(2)
                if numbers[3] == 0.1:
                    numbers.pop(3)
                self.benchmarks[BenchmarkName] = {
                    "Total Frames": numbers[0],
                    "Average FPS": numbers[1],
                    "1% Low FPS": numbers[2],
                    "0.1% Lowest FPS": numbers[3],
                }
                Last_Found = BenchmarkName
        load_last_benchmark(self, Last_Found)
    except Exception as e:
        log.error(f"Benchmark Failed. {e}")
