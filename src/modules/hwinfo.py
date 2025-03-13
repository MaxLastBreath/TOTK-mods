import platform
import subprocess
import GPUtil


def get_cpu_info(log) -> [str, str]:  # type: ignore
    try:
        if platform.system() == "Windows":
            import wmi

            w = wmi.WMI()
            CPU = w.Win32_Processor()[0].Name
            FREQUENCY = w.Win32_PhysicalMemory()[0].ConfiguredClockSpeed
        elif platform.system() == "Darwin":
            CPU = subprocess.getoutput("sysctl -n machdep.cpu.brand_string")
            FREQUENCY = subprocess.getoutput(
                "echo $(system_profiler SPMemoryDataType | grep Speed | awk '{print $2}') | awk '{print $1}'"
            )
        elif platform.system() == "Linux":
            CPU = subprocess.getoutput(
                "lscpu | grep 'Model name' | cut -f 2 -d \":\" | awk '{$1=$1}1'"
            )
            FREQUENCY = "-"

    except Exception as e:
        CPU = "Undetected"
        FREQUENCY = "-"
        log.warning(f"The GPU was not detected, nothing to be concerned about. {e}")
    return CPU, FREQUENCY


def get_gpu_name(log) -> str:
    # Ignore GPU on MacOS
    if platform.system() == "Darwin":
        return ""

    try:
        # For NVIDIA GPU only
        gpus = GPUtil.getGPUs()
        gpu_name = gpus[0].name
        return gpu_name
    except Exception as e:
        return _get_gpu_name(log)


def _get_gpu_name(log) -> str:
    try:
        if platform.system() == "Windows":
            return (
                subprocess.run("wmic path win32_VideoController get name")
                .split("\n\n")[-2]
                .lstrip()
            )
        elif platform.system() == "Linux":
            GPU = (
                subprocess.getoutput("bash -c \"glxinfo | grep 'Device'\"")
                .split("(")[0]
                .lstrip()
                .replace("Device: ", "")
            )
            return GPU
    except Exception as e:
        log.warning(f"The GPU was not detected, nothing to be concerned about. {e}")
