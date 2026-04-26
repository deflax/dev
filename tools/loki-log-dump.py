import time
import sys
import collections
import json
import httpx
from urllib.parse import urlencode

arg_names = ['command', 'since', 'limit']
args = dict(zip(arg_names, sys.argv))
Arg_list = collections.namedtuple('Arg_list', arg_names)
args = Arg_list(*(args.get(arg, None) for arg in arg_names))

if args[1] is None:
    print('no arg')
    exit(1)

if args[2] is not None:
    limit = int(args[2])
else:
    limit = 5000

loki_url="http://10.233.28.172:3100"
nspace = 'deflax'
app = 'data-streamer'

query = '{app="' + app + '",namespace="' + nspace + '"}'

step = 10

headers = {
    "Content-Type": "application/json"
}

index = int(args[1])
eod = int(time.time())

logfile = nspace + '-' + app + str(eod) + '.log'

print ('] query loki from ' + str(args[1]) + ' to ' + str(eod), end='')
while True:
    print ('\n] dumping range [' + str(index) + ' .. ' + str(int(index) + step) + '] step=' + str(step), end='')
    if int(index) + step >= eod:
        print('] end of stream')
        break

    payload = {
        "query": query,
        "direction": "forward",
        "limit": limit,
        "start": index,
        "end": int(index) + step
        }

    r = httpx.get(loki_url + '/loki/api/v1/query_range', headers=headers, params=urlencode(payload))
    #print("text:-", r.text)

    if r.status_code != 200:
        print(f"Error: {r.status_code}")
        exit()
    
    try:
        batch = r.json()["data"]["result"][0]
    except IndexError:
        step *= 2
        if step > 8192:
            step = 8192
        index = int(index) + int(step)
        continue

    itemcount = len(batch["values"])
    print(' items=' + str(itemcount), end='')

    #rerun the cycle with smaller window size
    if int(itemcount) == limit:
        step = step // 2
        time.sleep(1)
        continue

    #dump values to log
    for item in batch["values"]:
        log = json.loads(item[1])
        line = log["log"]
        raw_log = repr(line)[1:-1]
        #print(log["time"] + " " + raw_log)
        with open(logfile, 'a') as the_log_file:
            the_log_file.write(log["time"] + " " + line)

    #move the query window starting point
    index = int(index) + int(step)
        
    if int(itemcount) < limit:
        step = int(step + 2) 

