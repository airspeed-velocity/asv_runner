import os
import sys

ON_PYPY = hasattr(sys, "pypy_version_info")

if sys.platform.startswith("win"):
    import ctypes.wintypes

    SIZE_T = ctypes.c_size_t

    class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("cb", ctypes.wintypes.DWORD),
            ("PageFaultCount", ctypes.wintypes.DWORD),
            ("PeakWorkingSetSize", SIZE_T),
            ("WorkingSetSize", SIZE_T),
            ("QuotaPeakPagedPoolUsage", SIZE_T),
            ("QuotaPagedPoolUsage", SIZE_T),
            ("QuotaPeakNonPagedPoolUsage", SIZE_T),
            ("QuotaNonPagedPoolUsage", SIZE_T),
            ("PagefileUsage", SIZE_T),
            ("PeakPagefileUsage", SIZE_T),
        ]

    GetCurrentProcess = ctypes.windll.kernel32.GetCurrentProcess
    GetCurrentProcess.argtypes = []
    GetCurrentProcess.restype = ctypes.wintypes.HANDLE

    GetProcessMemoryInfo = ctypes.windll.psapi.GetProcessMemoryInfo
    GetProcessMemoryInfo.argtypes = (
        ctypes.wintypes.HANDLE,
        ctypes.POINTER(PROCESS_MEMORY_COUNTERS),
        ctypes.wintypes.DWORD,
    )
    GetProcessMemoryInfo.restype = ctypes.wintypes.BOOL

    def get_maxrss():
        proc_hnd = GetCurrentProcess()
        counters = PROCESS_MEMORY_COUNTERS()
        info = GetProcessMemoryInfo(
            proc_hnd, ctypes.byref(counters), ctypes.sizeof(counters)
        )
        if info == 0:
            raise ctypes.WinError()
        return counters.PeakWorkingSetSize

    if ctypes.sizeof(ctypes.c_void_p) == ctypes.sizeof(ctypes.c_uint64):
        DWORD_PTR = ctypes.c_uint64
    elif ctypes.sizeof(ctypes.c_void_p) == ctypes.sizeof(ctypes.c_uint32):
        DWORD_PTR = ctypes.c_uint32

    SetProcessAffinityMask = ctypes.windll.kernel32.SetProcessAffinityMask
    SetProcessAffinityMask.argtypes = [ctypes.wintypes.HANDLE, DWORD_PTR]
    SetProcessAffinityMask.restype = bool

    GetCurrentProcess = ctypes.windll.kernel32.GetCurrentProcess
    GetCurrentProcess.argtypes = []
    GetCurrentProcess.restype = ctypes.wintypes.HANDLE

    def set_cpu_affinity(affinity_list):
        """Set CPU affinity to CPUs listed (numbered 0...n-1)"""
        mask = 0
        for num in affinity_list:
            mask |= 2**num

        # Pseudohandle, doesn't need to be closed
        handle = GetCurrentProcess()
        ok = SetProcessAffinityMask(handle, mask)
        if not ok:
            raise RuntimeError("SetProcessAffinityMask failed")

else:
    try:
        import resource

        # POSIX
        if sys.platform == "darwin":

            def get_maxrss():
                # OSX getrusage returns maxrss in bytes
                # https://developer.apple.com/library/mac/documentation/Darwin/Reference/ManPages/man2/getrusage.2.html
                return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

        else:

            def get_maxrss():
                # Linux, *BSD return maxrss in kilobytes
                return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024

    except ImportError:
        pass

    def set_cpu_affinity(affinity_list):
        """Set CPU affinity to CPUs listed (numbered 0...n-1)"""
        if hasattr(os, "sched_setaffinity"):
            os.sched_setaffinity(0, affinity_list)
        else:
            import psutil

            p = psutil.Process()
            if hasattr(p, "cpu_affinity"):
                p.cpu_affinity(affinity_list)
