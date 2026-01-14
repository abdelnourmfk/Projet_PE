"""Synthetic traffic generator (normal + SYN flood) -> CSV
Columns: ts, src_ip, dst_ip, src_port, dst_port, flags, length
"""
import csv
import random
import time
import ipaddress
from typing import List, Tuple

def _random_ip():
    # Generate a random IPv4 in a private range
    return str(ipaddress.IPv4Address(random.randint(0x0A000000, 0x0AFFFFFF)))

def generate_synthetic_traffic(output_csv: str, duration_seconds: int = 60, pps: int = 50,
                               attack_windows: List[Tuple[int,int,str]] = None, seed: int = 42):
    """Generate synthetic traffic and write to CSV.

    attack_windows: list of tuples (start_sec, duration_sec, attack_type)
    attack_type: 'syn_single_src' or 'syn_many_src'
    """
    random.seed(seed)
    if attack_windows is None:
        attack_windows = []

    start_time = time.time()
    end_time = start_time + duration_seconds
    ts = start_time

    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ts","src_ip","dst_ip","src_port","dst_port","flags","length"])

        while ts < end_time:
            # decide current second bucket
            sec_idx = int(ts - start_time)
            # check if in attack window
            attack_type = None
            for (s,d,t) in attack_windows:
                if s <= sec_idx < s + d:
                    attack_type = t
                    break

            if attack_type is None:
                # normal traffic: pps packets uniformly
                packets = pps
                for _ in range(packets):
                    src = _random_ip()
                    dst = str(ipaddress.IPv4Address("192.168.0." + str(random.randint(1,254))))
                    sport = random.randint(1024,65535)
                    dport = random.choice([80,443,53,22,8080])
                    flags = random.choice(["", "A", "P", "PA", "S"])  # include occasional S
                    length = random.randint(60,1500)
                    writer.writerow([f"{ts:.6f}", src, dst, sport, dport, flags, length])
            else:
                # attack: intensify SYNs
                if attack_type == 'syn_single_src':
                    attacker = "10.0.0.99"
                    packets = pps * 50
                    for _ in range(packets):
                        dst = str(ipaddress.IPv4Address("192.168.0." + str(random.randint(1,254))))
                        sport = random.randint(1024,65535)
                        dport = 80
                        flags = "S"
                        length = random.randint(40,60)
                        writer.writerow([f"{ts:.6f}", attacker, dst, sport, dport, flags, length])
                elif attack_type == 'syn_many_src':
                    packets = pps * 40
                    for _ in range(packets):
                        src = _random_ip()
                        dst = str(ipaddress.IPv4Address("192.168.0." + str(random.randint(1,254))))
                        sport = random.randint(1024,65535)
                        dport = 80
                        flags = "S"
                        length = random.randint(40,60)
                        writer.writerow([f"{ts:.6f}", src, dst, sport, dport, flags, length])

            ts += 1.0  # step per second

if __name__ == "__main__":
    # quick demo: 120s with an attack from t=30 to t=60
    generate_synthetic_traffic("data/demo_traffic.csv", duration_seconds=120, pps=50,
                               attack_windows=[(30,30,'syn_single_src')])
    print("Generated data/demo_traffic.csv")
