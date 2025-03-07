from modules.GameManager.FileManager import *
from modules.logger import *
from modules.GameManager.PatchInfo import PatchInfo
import pyperclip
import os
import re

class Benchmark:
    _manager = None
    _filemgr = None
    _patchInfo: PatchInfo = None

    _selected_benchmark = None
    _benchmarks: dict = {}

    __benchmark_version = None
    __benchmark_support = None
    __benchmark_file = None

    _benchmark_info_tag: str = "benchmark-info"
    _benchmark_label_tag: str = "benchmark-label"

    __benchmark_name_none: str = "No Benchmark Detected"
    __benchmark_name_nosupport: str = "Benchmarks Not Supported"

    _benchmark_text :str = (f"Turn on Direct Keyboard.\n"
                            f"Press G after loading in game.\n"
                            f"Select your Benchmark in Advanced Settings.\n"
                            f"Clicking this text copies your results.\n")
    
    _benchmark_none :str = (f"This game doesn't support\n"
                            f"UltraCam Benchmark Features\n")

    @classmethod
    def Initialize(cls, manager, filemanager):
        from modules.FrontEnd.FrontEnd import Manager, FileManager
        
        cls._manager: Manager = manager
        cls._filemgr: FileManager = filemanager
        cls._patchInfo: PatchInfo = manager._patchInfo
        cls.ReloadBenchmarkInfo()

    @classmethod
    def __benchmarkInfo(cls, BenchmarkName = None):
        
        if cls.__benchmark_support is False:
            BenchmarkName = cls.__benchmark_name_nosupport
            cls._manager.maincanvas.itemconfig(cls._benchmark_label_tag, text=cls.__benchmark_name_nosupport)
            return cls._benchmark_none

        # set to None
        if BenchmarkName is None:
            BenchmarkName = cls.__benchmark_name_none
            cls._manager.maincanvas.itemconfig(cls._benchmark_label_tag, text=cls.__benchmark_name_none)
            return cls._benchmark_text

        cls._manager.maincanvas.itemconfig(cls._benchmark_label_tag, text=BenchmarkName)

        text = (f"TOTAL Frames - {cls._benchmarks[BenchmarkName]['Total Frames']} Frames\n"
                f"Average - {cls._benchmarks[BenchmarkName]['Average FPS']} FPS\n"
                f"1% Lowest FPS - {cls._benchmarks[BenchmarkName]['1% Low FPS']} FPS\n"
                f"0.1% Lowest FPS - {cls._benchmarks[BenchmarkName]['0.1% Lowest FPS']} FPS\n")

        return text

    @classmethod
    def ReloadBenchmarkInfo(cls):
        cls._benchmarks = {}
        cls._selected_benchmark = None
        cls._patchInfo = cls._manager._patchInfo
        cls.__benchmark_version = cls._patchInfo.Benchmark_Version
        cls.__benchmark_support = cls._patchInfo.Support_Benchmark
        cls.__benchmark_file = os.path.join(FileManager.sdmc_dir, cls._patchInfo.Benchmarks_File)
        cls.load_benchmark()

    @classmethod
    def load_last_benchmark(cls, BenchmarkName):
        cls._selected_benchmark = BenchmarkName

        cls._manager.maincanvas.itemconfig(
            cls._benchmark_info_tag,
            text=cls.__benchmarkInfo(BenchmarkName)
        )

    @classmethod
    def read_benchmark_file_v0(cls):
        "Benchmark UltraCam Version 0 read and load structures."

        Last_Found = None
        with open(cls.__benchmark_file, "r") as benchmarks:
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
                cls._benchmarks[BenchmarkName] = {
                    "Total Frames": numbers[0],
                    "Average FPS": numbers[1],
                    "1% Low FPS": numbers[2],
                    "0.1% Lowest FPS": numbers[3],
                }
                Last_Found = BenchmarkName
        
        cls._selected_benchmark = Last_Found

    @classmethod
    def read_benchmark_file_v1(cls):
        return None # not implemented.
    
    @classmethod
    def load_benchmark(cls):
        log.info("Loading Benchmark Reader")

        # return early
        if (not os.path.exists(cls.__benchmark_file)):
            cls.load_last_benchmark(None)
            log.warning(f"Benchmark File Not Found. {cls.__benchmark_file}")
            return
        
        if (cls.__benchmark_version == 0):
            cls.read_benchmark_file_v0()
        else :
            cls.read_benchmark_file_v1()
        
        cls.load_last_benchmark(cls._selected_benchmark)

    @classmethod
    def copy(cls):
        if cls._selected_benchmark is None:
            return
        
        resolution = cls._manager.UserChoices["resolution"].get()
        shadows = int(cls._manager.UserChoices["shadow resolution"].get().split("x")[0])
        
        system_os = "MacOS" if platform.system() == "Darwin" else platform.system()

        benchmark_result = (
            f"## **{cls._selected_benchmark}** Tears Of The Kingdom on {system_os}\n"
        )

        if platform.system() != "Darwin":
            benchmark_result += f"- **{gpu_name}**\n"

        benchmark_result += (
            f"- **{CPU}**\n"
            f"- **{total_memory}** GB RAM at **{FREQUENCY}** MHz\n"
            f"- **{resolution}** and Shadows: **{shadows}**, FPS CAP: **{cls._manager.UserChoices['fps'].get()}**\n"
            f"## Results:\n"
            f"- Total Frames **{cls._benchmarks[cls._selected_benchmark]['Total Frames']}**\n"
            f"- Average FPS **{cls._benchmarks[cls._selected_benchmark]['Average FPS']}**\n"
            f"- 1% Lows **{cls._benchmarks[cls._selected_benchmark]['1% Low FPS']}** FPS\n"
            f"- 0.1% Lows **{cls._benchmarks[cls._selected_benchmark]['0.1% Lowest FPS']}** FPS\n"
        )
            
        pyperclip.copy(benchmark_result)
        

