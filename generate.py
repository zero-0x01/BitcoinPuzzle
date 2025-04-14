import secp256k1 as ice 
from bloomfilter import BloomFilter

COINS = {
    'BTC' : [0,((0,True),(0,False),(1,True),(2,True))],
    'ETH' : [None],
    'DOGE' : [16,((0,True),(0,False))],
    'LTC' : [21,((0,True),(0,False),(1,True),(2,True))],
    'DASH' : [12,((0,True),(0,False))]
}
ENDPOINTS = {
    'BTC' : 'https://bitcoin.atomicwallet.io/address/',
    'Eth' : 'https://ethereum.atomicwallet.io/address/',
    'DOGE' : 'https://dogecoin.atomicwallet.io/address/',
    'LTC' : 'https://litecoin.atomicwallet.io/address/',
    'DASH' : 'https://dash.atomicwallet.io/address/'
}

FOUND = 0
ERROR = 0
TK = 0
SP = 0

class Generator:
    def __init__(self,coins,EndPoints=None,BF_file=None,AD_file=None):
        self.coins = coins
        self.endpoints = EndPoints
        if BF_file != None:
            try:
                with open(BF_file,'rb') as f:
                    self.bf_file = BloomFilter.load(f)
            except:
                print(f"Error: Failed to open bf file!")
        if AD_file != None:
            self.ad_file = AD_file

    def Generate(self,coin,pv_int,mode=1):
        cn = self.coins[coin]
        cn_all = self.coins
        Context = {}
        private_hex = str(hex(pv_int)[2:].zfill(64))

        if mode == 1:
            if cn == None:
                Address = ice.privatekey_to_ETH_address(pv_int)
                Context[private_hex] = {'Eth Address':str(Address)}

            else:
                code = cn[0]
                types = cn[1]
                Addresses = []

                for type in types:
                    address = ice.privatekey_to_coinaddress(code,type[0],type[1],pv_int)
                    Addresses.append(address)

                if len(Addresses) == 2:
                    Context[private_hex] = {'Compressed Address':str(Addresses[0]),'Uncompressed Address':str(Addresses[1])}

                elif len(Addresses) == 4:
                    Context[private_hex] = {'Compressed Address':str(Addresses[0]),'Uncompressed Address':str(Addresses[1]),'P2SH Address':str(Addresses[2]),'BCH1 Address':str(Addresses[3])}
        if mode == 2 :
            Context[private_hex] = {}
            Addresses = []
            for cns in cn_all:
                if cn_all[cns][0] == None:
                    Address = ice.privatekey_to_ETH_address(pv_int)
                    Context[private_hex].update({'Eth':str(Address)})
                elif cn_all[cns][0] != None:
                    code = cn_all[cns][0]
                    types = cn_all[cns][1]
                    for type in types:
                        address = ice.privatekey_to_coinaddress(code,type[0],type[1],pv_int)
                        Addresses.append(address)
                    if len(Addresses) == 2:
                        Context[private_hex].update({cns:{'Compressed Address':str(Addresses[0]),'Uncompressed Address':str(Addresses[1])}})
                    elif len(Addresses) == 4:
                        Context[private_hex].update({cns:{'Compressed Address':str(Addresses[0]),'Uncompressed Address':str(Addresses[1]),'P2SH Address':str(Addresses[2]),'BCH1 Address':str(Addresses[3])}})
                Addresses = []
        return Context
    
    def Context_to_list(self,context):
        values = list(list(context.values())[0].values())
        return values
    
    def Check_in_bloom(self,Addresses,BF_file):
        try:
            with open(BF_file,'rb') as f:
                bf_file = BloomFilter.load(f)
        except:
            print(f"Error: Failed to open bf file!")
        if Addresses in bf_file:
            return True
        else:
            return False 
    
    def Check_group_in_bloom(self,Addresses):
        for address in Addresses:
            if address in self.bf_file:
                return address
            else:
                return False
    
    def read_next_line(self,ad_file):
        file_path = ad_file
        with open(file_path, 'r') as file:
            while True:
                line = file.readline()
                if not line:
                    break
                yield line
    

def main():
    global COINS
    bf_file = input("Enter your Bf file: ")
    add_file = input("Enter your target file: ")
    GN = Generator(COINS,bf_file,add_file)
    pv_keys = GN.read_next_line(add_file)
    for pv in pv_keys:
        pv = pv.strip().split(' ')[0]
        pv_int = int(pv,16)
        cont = GN.Generate('BTC',pv_int)
        cont_l = GN.Context_to_list(cont)
        for cn in cont_l:
            if GN.Check_in_bloom(cn,bf_file) :
                print(f"Address: {str(cn)} | Private key: {str(pv)}")
            else:
                print(f"Private Key : {str(pv)}",end='\r')

if __name__ == '__main__':
    main()

def online_multi_check(coin,address):
    global ENDPOINTS
    endpoint = ENDPOINTS[coin]
    Flag = False
    resp = requests.get(f"{endpoint}{address}")
    pattern = r'<td[^>]*>(.*?)<\/td>'
    match = re.findall(pattern, resp.text,flags=re.S)
    Balance = match[5].split(" ")[0]
    Tx = match[7]
    if int(Balance) > 0 or int(Tx) > 0:
        Flag = True
    return Balance,Tx,Flag

def Context_balance_add(context):
    k = next(iter(context.keys()))
    for kys in context[k]:
        if kys != 'Eth':
            for kys2 in context[k][kys]:
                address = context[k][kys][kys2]
                balance,tx,flag = online_multi_check(kys,address)
                context[k][kys][kys2] = context[k][kys][kys2].split(',')
                context[k][kys][kys2].append([int(balance),int(tx)])
                # if flag == True:
                #     print_win(context)
                # elif flag == False:
                #     print_details(context)
                
                    
        if kys == 'Eth':
            address = context[k][kys]
            balance,tx = online_multi_check(kys,address)
            context[k][kys] = context[k][kys].split(',')
            context[k][kys].append([int(balance),int(tx)])
    return context

def print_win(context):
    global FOUND
    k = next(iter(context.keys()))
    
    if next(iter(context[k].keys())) == 'BTC' :
        print(f"\033[{1+int(FOUND)};1H", end="")
        print(f"[ Bitcoin | Address: {context[k]['BTC']['Address'][0]} | Balance: {str(context[k]['BTC']['Address'][1][0])} | Tx: {str(context[k]['BTC']['Address'][1][0])}")
    elif next(iter(context[k].keys())) == 'Eth':
        print(f"\033[{1+int(FOUND)};1H", end="")
        print(f"[ Ethereum | Address: {context[k]['Eth']['Address'][0]} | Balance: {str(context[k]['Eth']['Address'][1][0])} | Tx: {str(context[k]['Eth']['Address'][1][0])}")
    elif next(iter(context[k].keys())) == 'DOGE':
        print(f"\033[{1+int(FOUND)};1H", end="")
        print(f"[ Dogecoin | Address: {context[k]['DOGE']['Address'][0]} | Balance: {str(context[k]['DOGE']['Address'][1][0])} | Tx: {str(context[k]['DOGE']['Address'][1][0])}")
    elif next(iter(context[k].keys())) == 'LTC':
        print(f"\033[{1+int(FOUND)};1H", end="")
        print(f"[ Litecoin | Address: {context[k]['LTC']['Address'][0]} | Balance: {str(context[k]['LTC']['Address'][1][0])} | Tx: {str(context[k]['LTC']['Address'][1][0])}")
    elif next(iter(context[k].keys())) == 'DASH':
        print(f"\033[{1+int(FOUND)};1H", end="")
        print(f"[ Dash | Address: {context[k]['DASH']['Address'][0]} | Balance: {str(context[k]['DASH']['Address'][1][0])} | Tx: {str(context[k]['DASH']['Address'][1][0])}")
    FOUND += 1
    
def print_details(context,details):
    k = next(iter(context.keys()))
    # move cursor to beginning of first line
    print(f"\033[{1+int(FOUND)};1H", end="")
    # overwrite first line with new detail
    print(f"Bitcoin:", end="")
    print(f"\033[{2+int(FOUND)};1H", end="")
    print(f"\t|Compressed Address: {context[k]['BTC']['Compressed Address'][0]} || Balance: {str(context[k]['BTC']['Compressed Address'][1][0])} || Tx: {str(context[k]['BTC']['Compressed Address'][1][1])}", end="")
    print(f"\033[{3+int(FOUND)};1H", end="")
    print(f"\t|UnCompressed Address: {context[k]['BTC']['Uncompressed Address'][0]} || Balance: {str(context[k]['BTC']['Uncompressed Address'][1][0])} || Tx: {str(context[k]['BTC']['Uncompressed Address'][1][1])}", end="")
    print(f"\033[{4+int(FOUND)};1H", end="")
    print(f"\t|P2SH Address: {context[k]['BTC']['P2SH Address'][0]} || Balance: {str(context[k]['BTC']['P2SH Address'][1][0])} || Tx: {str(context[k]['BTC']['P2SH Address'][1][1])}", end="")
    print(f"\033[{5+int(FOUND)};1H", end="")
    print(f"\t|BCH1 Address: {context[k]['BTC']['BCH1 Address'][0]} || Balance: {str(context[k]['BTC']['BCH1 Address'][1][0])} || Tx: {str(context[k]['BTC']['BCH1 Address'][1][1])}", end="")
    # move cursor to beginning of second line
    print(f"\033[{6+int(FOUND)};1H", end="")
    print(f"Ethereum:", end="")
    print(f"\033[{7+int(FOUND)};1H", end="")
    print(f"\t|Address: {context[k]['Eth'][0]} || Balance: {str(context[k]['Eth'][1][0])} || Tx: {str(context[k]['Eth'][1][1])}", end="")
    # overwrite second line with new detail
    print(f"\033[{8+int(FOUND)};1H", end="")
    print(f"DogeCoin:", end="")
    print(f"\033[{9+int(FOUND)};1H", end="")
    print(f"\t|Compressed Address: {context[k]['DOGE']['Compressed Address'][0]} || Balance: {str(context[k]['DOGE']['Compressed Address'][1][0])} || Tx: {str(context[k]['DOGE']['Compressed Address'][1][1])}", end="")
    print(f"\033[{10+int(FOUND)};1H", end="")
    print(f"\t|UnCompressed Address: {context[k]['DOGE']['Uncompressed Address'][0]} || Balance: {str(context[k]['DOGE']['Uncompressed Address'][1][0])} || Tx: {str(context[k]['DOGE']['Uncompressed Address'][1][1])}", end="")

    print(f"\033[{11+int(FOUND)};1H", end="")
    print(f"LiteCoin:", end="")
    print(f"\033[{12+int(FOUND)};1H", end="")
    print(f"\t|Compressed Address: {context[k]['LTC']['Compressed Address'][0]} || Balance: {str(context[k]['LTC']['Compressed Address'][1][0])} || Tx: {str(context[k]['LTC']['Compressed Address'][1][1])}", end="")
    print(f"\033[{13+int(FOUND)};1H", end="")
    print(f"\t|UnCompressed Address: {context[k]['LTC']['Uncompressed Address'][0]} || Balance: {str(context[k]['LTC']['Uncompressed Address'][1][0])} || Tx: {str(context[k]['LTC']['Uncompressed Address'][1][1])}", end="")
    print(f"\033[{14+int(FOUND)};1H", end="")
    print(f"\t|P2SH Address: {context[k]['LTC']['P2SH Address'][0]} || Balance: {str(context[k]['LTC']['P2SH Address'][1][0])} || Tx: {str(context[k]['LTC']['P2SH Address'][1][1])}", end="")
    print(f"\033[{15+int(FOUND)};1H", end="")
    print(f"\t|BCH1 Address: {context[k]['LTC']['BCH1 Address'][0]} || Balance: {str(context[k]['LTC']['BCH1 Address'][1][0])} || Tx: {str(context[k]['LTC']['BCH1 Address'][1][1])}", end="")
    
    # move cursor to beginning of third line
    print(f"\033[{16+int(FOUND)};1H", end="")
    # overwrite third line with new detail
    print(f"Dash:", end="")
    print(f"\033[{17+int(FOUND)};1H", end="")
    print(f"\t|Compressed Address: {context[k]['DASH']['Compressed Address'][0]} || Balance: {str(context[k]['DASH']['Compressed Address'][1][0])} || Tx: {str(context[k]['DASH']['Compressed Address'][1][1])}", end="")
    print(f"\033[{18+int(FOUND)};1H", end="")
    print(f"\t|UnCompressed Address: {context[k]['DASH']['Uncompressed Address'][0]} || Balance: {str(context[k]['DASH']['Uncompressed Address'][1][0])} || Tx: {str(context[k]['DASH']['Uncompressed Address'][1][1])}", end="")
    
    print(f"\033[{19+int(FOUND)};1H", end="")
    print(f"[ Total keys: {details['Tk']} , Found: {details['Fk']} , Error: {details['Ek']} , Speed: {details['Sk']} keys/s", end="")