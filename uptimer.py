#!/usr/bin/env python3
"""uptimer - System uptime, load, and resource monitor."""
import os, time, argparse, json, sys, subprocess

def get_uptime():
    if sys.platform == 'darwin':
        out = subprocess.check_output(['sysctl', '-n', 'kern.boottime'], text=True)
        import re
        m = re.search(r'sec = (\d+)', out)
        if m:
            boot = int(m.group(1))
            return time.time() - boot
    elif sys.platform == 'linux':
        with open('/proc/uptime') as f:
            return float(f.read().split()[0])
    return 0

def get_load():
    return os.getloadavg()

def fmt_duration(seconds):
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    mins = int((seconds % 3600) // 60)
    parts = []
    if days: parts.append(f"{days}d")
    if hours: parts.append(f"{hours}h")
    parts.append(f"{mins}m")
    return ' '.join(parts)

def main():
    p = argparse.ArgumentParser(description='System uptime and load')
    p.add_argument('-w', '--watch', action='store_true')
    p.add_argument('-i', '--interval', type=int, default=5)
    p.add_argument('-j', '--json', action='store_true')
    args = p.parse_args()

    def show():
        uptime = get_uptime()
        load1, load5, load15 = get_load()
        cpus = os.cpu_count() or 1
        
        if args.json:
            print(json.dumps({
                'uptime_seconds': int(uptime), 'uptime_human': fmt_duration(uptime),
                'load_1m': load1, 'load_5m': load5, 'load_15m': load15,
                'cpus': cpus, 'load_pct': round(load1 / cpus * 100, 1)
            }))
        else:
            pct = load1 / cpus * 100
            bar = '█' * min(int(pct / 5), 20) + '░' * max(20 - int(pct / 5), 0)
            print(f"  Uptime:  {fmt_duration(uptime)}")
            print(f"  Load:    [{bar}] {pct:.0f}%")
            print(f"  Avg:     {load1:.2f} (1m)  {load5:.2f} (5m)  {load15:.2f} (15m)")
            print(f"  CPUs:    {cpus}")

    if args.watch:
        try:
            while True:
                print(f"\033[2J\033[H[{time.strftime('%H:%M:%S')}]")
                show()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            pass
    else:
        show()

if __name__ == '__main__':
    main()
