from aiohomekit import Controller
from aiohomekit.model import ServicesTypes
import functools
import pprint
import asyncio

from functools import lru_cache

# default aiohomekit pairing file aiohomekit.__main__
import pathlib
XDG_DATA_HOME = pathlib.Path.home() / ".local" / "share"
DEFAULT_PAIRING_FILE = XDG_DATA_HOME / "aiohomekit" / "pairing.json"


@lru_cache
def get_pairing():
    ct = Controller()
    ct.load_data(DEFAULT_PAIRING_FILE)
    pa = list(ct.pairings.values())[0]
    print("Conneted")
    return pa


async def test():
    characteristics=[]
    pa = get_pairing()

    r = await pa.list_pairings()
    print(r)

    r = await pa.list_accessories_and_characteristics()
    for k in r:
        #pprint.pp(k['services'])
        aid = k['aid']
        print(f"{aid}")
        for service in k['services']:
            s_type = service['type']
            s_iid = service['iid']
            print(f"{s_iid} {ServicesTypes.get_short(s_type)}")
            for charac in service['characteristics']:
                c_iid = charac.get('iid',None)
                desc = charac.get('description',None)
                value = charac.get('value',None)
                unit = charac.get('unit',None)
                print(f"  =>{c_iid} {desc} : {value} {unit}")
                if desc in ['ContactSensorState','MotionDetected','On']:
                    characteristics.append((aid,c_iid))
                
            
            #pprint.pp(service)
        print("="*78)
    return characteristics

def handler(data):
    print(data)


async def start():
    tmp = await test()
    await listen(tmp)


async def listen(characteristics):
    pa = get_pairing()
    pa.dispatcher_connect(handler)
    results = await pa.subscribe(characteristics)
    print(results)


async def foo():
    while 1:
        print("Foo")
        await asyncio.sleep(10)



def main():
    tasks = [ asyncio.ensure_future(start()),
              asyncio.ensure_future(foo()), ]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))

try:
    main()
except KeyboardInterrupt:
    print("Bye bye")

