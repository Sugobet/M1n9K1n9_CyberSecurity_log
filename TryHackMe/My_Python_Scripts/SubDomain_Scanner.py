import requests
from threading import Thread
import sys
import pyfiglet


domain = sys.argv[1]
subdomain_path = sys.argv[2]
timeout = float(sys.argv[3])
thread_num = int(sys.argv[4])

fuck_length = str(input('Input Fuck length (split ","):')).split(',')

thread_list = []


def scan(*subList):
    to = timeout
    for sub in subList:
        b_domains = f"http://{domain}"
        sub_d = f'{sub.strip()}.{domain}'
        headers = {'Host': sub_d}

        try:
            res = requests.get(b_domains, headers=headers, allow_redirects=False, timeout=to)
            if fuck_length == []:
                print(f'length:{len(res.text)}')
            elif str(len(res.text)) not in fuck_length:
                print(f"Length:{len(res.text)} :Valid domain:{sub_d}")
        except Exception:
            pass


if __name__ == "__main__":
    print(pyfiglet.figlet_format("Sugobet \n"))

    sub_list = open(f"{subdomain_path}").read()
    subList = sub_list.splitlines()

    length = len(subList)
    step = int(length / thread_num) + 1
    for start in range(0, length, step):
        sl = subList[start:start + step]
        t = Thread(target=scan, args=(sl))
        thread_list.append(t)
        t.start()
    
    for t in thread_list:
        t.join()
    
    print("Done!")
