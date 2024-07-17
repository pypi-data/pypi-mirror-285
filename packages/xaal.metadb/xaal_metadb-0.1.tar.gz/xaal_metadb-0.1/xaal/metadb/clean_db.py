from xaal.lib import AsyncEngine, tools
from xaal.schemas import devices 
from xaal.monitor import Monitor

import asyncio 

PACKAGE_NAME = "xaal.metadb"


def main():
    eng = AsyncEngine()
    dev = devices.basic()
    eng.add_device(dev)
    mon = Monitor(dev)
    cfg = tools.load_cfg(PACKAGE_NAME)

    async def cleanup():
        print("Gathering devices informations..")
        while 1:
            if mon.boot_finished:
                break
            await asyncio.sleep(0.1)
    
        print(f"Found {len(mon.devices)}")
        for cfg_entry in cfg['devices']:
            addr = tools.get_uuid(cfg_entry)
            target = mon.devices.get_with_addr(addr)
            if target == None:
                print(f"Unknow target {cfg_entry}")


        eng.shutdown()
    

    eng.on_start(cleanup)
    eng.run()


if __name__ == '__main__':
    main()
