import requests
from threading import Thread
import sys
import pyfiglet


domain = sys.argv[1]
subdomain_path = sys.argv[2]
timeout = float(sys.argv[3])
thread_num = int(sys.argv[4])

thread_list = []


def scan(*subList):
    to = timeout
    for sub in subList:
        sub_domains = f"http://{sub.strip()}.{domain}" 

        try:
            requests.get(sub_domains, timeout=to)
        except requests.ConnectionError:
            pass
        else:
            print("Valid domain: ",sub_domains)


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
