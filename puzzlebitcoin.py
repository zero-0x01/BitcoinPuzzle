import random
import secp256k1 as ice
from concurrent.futures import ThreadPoolExecutor
import concurrent


priv_count = 0
error_count = 0
loop_count = 0
base = ('1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvvZ')

def create_random_subranges(min_range, max_range, length):
    # convert hex strings to integers
    min_int = int(min_range, 16)
    max_int = int(max_range, 16)

        # choose a random starting point within the range
    start = random.randint(min_int, max_int - length)

        # calculate the end point based on the length
    end = start + length

        # convert integers to hex strings
    start_hex = hex(start)[2:].zfill(64)
    end_hex = hex(end)[2:].zfill(64)

        # add the subrange to the list
    subrange = f"{start_hex}:{end_hex}"

    return subrange

def Address_check(address):
    global base
    global error_count
    try:
        if address in base:
            return True
        else:
            return False    
    except :
        error_count += 1

def worker(key):
    global priv_count
    global error_count
    global loop_count
    priv_count += 1

    priv = hex(key)[2:].zfill(64)
    Caddress = ice.privatekey_to_address(0,True,key)
    Uaddress = ice.privatekey_to_address(0,False,key)
    if Address_check(Caddress) == True or Address_check(Uaddress) == True:
        print(f"\nPrivate key: {str(priv)} | Compressed Address: {str(Caddress)} | Uncompressed Address: {str(Uaddress)}")
        with open("Found.txt",'a') as f:
            f.write(f"\nPrivate key: {str(priv)} | Compressed Address: {str(Caddress)} | Uncompressed Address: {str(Uaddress)}")
    else:
      print(f"Private key: {str(priv)} | private keys : {str(priv_count)} | Error: {str(error_count)} | Loop: {str(loop_count)} ",end='\r')


def main():
   global loop_count
   min = "0000000000000000000000000000000000000000000000080000000000000000"
   max = "00000000000000000000000000000000000000000000000fffffffffffffffff"
   count = 5000
   thread_count = 50
   with ThreadPoolExecutor(max_workers=thread_count) as executor:
       while True:
       	    loop_count += 1
            subrange = create_random_subranges(min,max,count).split(':')
            start = int(subrange[0],16)
            stop = int(subrange[1],16)
            futures = []
            for i in range(start,stop):
                future = executor.submit(worker, i)
                futures.append(future)
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    print(f"Exception in worker: {exc}")
                        
if __name__ == '__main__':
   main()
