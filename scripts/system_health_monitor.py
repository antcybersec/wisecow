#!/usr/bin/env python3
"""
System Health Monitoring Script (PS2 - Objective 1)
Monitors CPU, memory, disk usage, and high process count; alerts on threshold breach.
"""

from __future__ import annotations

import argparse
import datetime as dt
import logging
import sys

try:
    import psutil
except ImportError:
    print("Install psutil: pip install psutil", file=sys.stderr)
    sys.exit(1)

DEFAULT_THRESHOLDS = {
    "cpu_percent": 80.0,
    "memory_percent": 85.0,
    "disk_percent": 90.0,
    "max_processes": 500,
}


def check_cpu(threshold: float) -> tuple[bool, str]:
    usage = psutil.cpu_percent(interval=1)
    ok = usage <= threshold
    msg = f"CPU usage: {usage:.1f}% (threshold: {threshold}%)"
    return ok, msg


def check_memory(threshold: float) -> tuple[bool, str]:
    mem = psutil.virtual_memory()
    ok = mem.percent <= threshold
    msg = f"Memory usage: {mem.percent:.1f}% ({mem.used // (1024**2)} MiB / {mem.total // (1024**2)} MiB, threshold: {threshold}%)"
    return ok, msg


def check_disk(threshold: float, path: str = "/") -> tuple[bool, str]:
    disk = psutil.disk_usage(path)
    ok = disk.percent <= threshold
    msg = f"Disk usage [{path}]: {disk.percent:.1f}% (threshold: {threshold}%)"
    return ok, msg


def check_processes(threshold: int) -> tuple[bool, str]:
    count = len(psutil.pids())
    ok = count <= threshold
    msg = f"Running processes: {count} (threshold: {threshold})"
    return ok, msg


def run_checks(thresholds: dict[str, float | int], disk_path: str) -> list[tuple[str, bool, str]]:
    checks = [
        ("CPU", *check_cpu(float(thresholds["cpu_percent"]))),
        ("Memory", *check_memory(float(thresholds["memory_percent"]))),
        ("Disk", *check_disk(float(thresholds["disk_percent"]), disk_path)),
        ("Processes", *check_processes(int(thresholds["max_processes"]))),
    ]
    return [(name, ok, msg) for name, ok, msg in checks]


def main() -> int:
    parser = argparse.ArgumentParser(description="Linux system health monitor")
    parser.add_argument("--log-file", default="", help="Optional log file path")
    parser.add_argument("--disk-path", default="/", help="Mount point to check disk usage")
    parser.add_argument("--cpu-threshold", type=float, default=DEFAULT_THRESHOLDS["cpu_percent"])
    parser.add_argument("--memory-threshold", type=float, default=DEFAULT_THRESHOLDS["memory_percent"])
    parser.add_argument("--disk-threshold", type=float, default=DEFAULT_THRESHOLDS["disk_percent"])
    parser.add_argument("--process-threshold", type=int, default=DEFAULT_THRESHOLDS["max_processes"])
    args = parser.parse_args()

    thresholds = {
        "cpu_percent": args.cpu_threshold,
        "memory_percent": args.memory_threshold,
        "disk_percent": args.disk_threshold,
        "max_processes": args.process_threshold,
    }

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if args.log_file:
        handlers.append(logging.FileHandler(args.log_file))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=handlers,
    )
    log = logging.getLogger("health-monitor")

    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
    log.info("=== System Health Check @ %s ===", timestamp)

    alerts = 0
    for name, ok, msg in run_checks(thresholds, args.disk_path):
        if ok:
            log.info("[%s] OK - %s", name, msg)
        else:
            log.warning("[%s] ALERT - %s", name, msg)
            alerts += 1

    if alerts:
        log.error("Health check finished with %d alert(s).", alerts)
        return 1

    log.info("All metrics within thresholds.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
