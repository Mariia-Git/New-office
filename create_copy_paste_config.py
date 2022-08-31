from ast import match_case
from fileinput import filename
import re

conf_type = 'HP_Dnepr', 'HP_other', 'cisco', 'Выход'
conf_max = len(conf_type) - 1

def validate_ip(ip_address):
    try:
        match = re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", ip_address)
  
        if not bool(match):
            return False

        bytes = ip_address.split(".")
  
        for ip_byte in bytes:
            if int(ip_byte) < 0 or int(ip_byte) > 255:
                return False
        return True
    except:
        return False

def validate_ip_with_mask(ip_with_mask):
    try:
        addresses = ip_with_mask.split("/")
    
        if not validate_ip(addresses[0]):
            return False
    
        if validate_ip(addresses[1]):
            return True
        elif bool(re.match(r"[0-9]{1,2}", addresses[1])) and \
            (int(addresses[1]) > 0 or int(addresses[1]) <= 32 ):
            return True
        else:
            return False
    except:
        return False

def create_hp_conf(scr_n):
    print(f'\nВы выбрали вариант "{conf_type[scr_n]}"')
    ports_valid = 1
    hostname = 'hostname'
    default_gateway = '10.10.10.10'
    ip_addr = '10.10.10.254/24'
    input_loop = True
    while input_loop:
        temp = input(f'Введите имя хоста [{hostname}]: ')
        hostname = temp if len(temp) else hostname
        temp = input(f'Введите Ip address default gateway [{default_gateway}]: ')
        default_gateway = temp if len(temp) else default_gateway
        temp = input(f'Введите IP address и mask устройства [{ip_addr}]]: ')
        ip_addr = temp if len(temp) else ip_addr
        ports_in = input('Введите количество портов (24,26,28,50) ')
        try:
            ports_n = int(ports_in)
            match ports_n:
                case 24:
                    ports_t = 'tagged 21-24'
                    ports_u = 'untagged 1-20'
                    ports_unif_u = 'untagged 21'
                    ports_unif_t = 'tagged 22-24'
                    ports_df = 'no untagged 1-24'
                    ports_l = 'loop-protect 1-20'
                    ports_valid = 1
                case 26:
                    ports_t = 'tagged 23-26'
                    ports_u = 'untagged 1-22'
                    ports_unif_u = 'untagged 23'
                    ports_unif_t = 'tagged 24-26'
                    ports_df = 'no untagged 1-26'
                    ports_l = 'loop-protect 1-22'
                    ports_valid = 1
                case 28:
                    ports_t = 'tagged 25-28'
                    ports_u = 'untagged 1-24'
                    ports_unif_u = 'untagged 25'
                    ports_unif_t = 'tagged 26-28'
                    ports_df = 'no untagged 1-28'
                    ports_l = 'loop-protect 1-24'
                    ports_valid = 1
                case 50:
                    ports_t = 'tagged 49-52'
                    ports_u = 'untagged 1-48'
                    ports_unif_u = 'untagged 49'
                    ports_unif_t = 'tagged 50-52'
                    ports_df = 'no untagged 1-52'
                    ports_l = 'loop-protect 1-48'
                    ports_valid = 1
                case _:
                    ports_t = 'tagged 21-24'
                    ports_u = 'untagged 1-20'
                    ports_unif_u = 'untagged 21'
                    ports_unif_t = 'tagged 22-24'
                    ports_df = 'no untagged 1-24'
                    ports_l = 'loop-protect 1-20'
                    ports_valid = 0
        except:
            ports_t = 'tagged 21-24'
            ports_u = 'untagged 1-20'
            ports_unif_u = 'untagged 21'
            ports_unif_t = 'tagged 22-24'
            ports_df = 'no untagged 1-24'
            ports_l = 'loop-protect 1-20'
            ports_valid = 0

        print(f'\nВведено:')
        print(f'{hostname=}', end = ' ')
        print('(OK)' if len(hostname) > 0 and len(hostname) < 65 else '(слишком длиное имя)') # надобы проверить не только длину
        print(f'{default_gateway=}', end = ' ')
        print('(OK)' if validate_ip(default_gateway) else '(неправильно введен шлюз)')
        print(f'{ip_addr=}', end=' ')
        print('(OK)' if validate_ip_with_mask(ip_addr) else '(неправильно введен адрес)')
        print(f'{ports_n=}', end=' ')
        print(f'(OK)' if ports_valid else f'(ошибка, будет как 24)')
        print('\n')

        try:
            print('1 Повторить ввод')
            print('2 Принять и продолжить')
            temp = input('Сделайте выбор или нажмите любую клавишу для выхода в главное меню: ')
            temp = int(temp)
            match temp:
                case 1:
                    print('\n')
                    #input_loop = True  - и так тру
                case 2:
                    print('\n')
                    input_loop = False
                case _:
                    return True
        except:
            print('Сбой. Выходим в главное меню.')
            return True
    try:
        #if validate_ip_with_mask(ip_addr):
        name_of_config_file = f'{conf_type[scr_n]}_{hostname}_{ip_addr.split("/")[0] if validate_ip_with_mask(ip_addr) else "iphz"}_{ ports_in if ports_valid else "hz24"}.txt'
        print('Генерация конфига.')
        if scr_n == 0:
            config_str = f'''#+++++++++++++ {conf_type[scr_n]}-Configure { ports_in if ports_valid else "hz24"} ports +++++++++++++

config
hostname "{hostname}"
timesync sntp
sntp unicast
sntp server priority 1 10.0.241.1
time timezone 120
ip default-gateway {default_gateway}
snmp-server community "public" unrestricted
vlan 1310
   name "sw-manage"
   {ports_t}
   ip address {ip_addr}
   exit
vlan 733
   name "VIDEO"
   {ports_t}
   no ip address
   exit
vlan 718
   name "SKD-local"
   {ports_t}
   exit
vlan 714
   name "ubnt_manage"
   {ports_t}
   no ip address
   exit
vlan 200
   name "wifi-p"
   {ports_t}
   no ip address
   exit
vlan 1
   name "DEFAULT_VLAN"
   {ports_df}
   no ip address
   exit 
password manage user backup
bbiwy984
bbiwy984
password operator user admin
ForexPWD349
ForexPWD349
no tftp server
{ports_l}
loop-protect mode vlan
loop-protect disable-timer 60
crypto key generate ssh
ip ssh
ip ssh filetransfer
wr mem
'''
        elif scr_n == 1:
            config_str = f'''#+++++++++++++ {conf_type[scr_n]}-Configure { ports_in if ports_valid else "hz24"} ports +++++++++++++

config
hostname "{hostname}"
timesync sntp
sntp unicast
sntp server priority 1 192.168.1.1
time timezone 120
ip default-gateway {default_gateway}
snmp-server community "public" unrestricted
vlan 10
   name "FRX-10"
   {ports_u}
   {ports_t}
   ip address {ip_addr}
   exit
vlan 20
   name "FRX_20"
   {ports_t}
   exit
vlan 30
   name "unifi-manage"
   {ports_unif_u}
   {ports_unif_t}
   exit
vlan 40
   name "wifi-p"
   {ports_t}
   no ip address
   exit
vlan 1
   name "DEFAULT_VLAN"
   {ports_df}
   no ip address
   exit 
password manage user backup
bbiwy984
bbiwy984
password operator user admin
ForexPWD349
ForexPWD349
no tftp server
{ports_l}
loop-protect mode vlan
loop-protect disable-timer 60
crypto key generate ssh
ip ssh
ip ssh filetransfer
wr mem
'''
        else:
            config_str = f'''#+++++++++++++ HP-Dnepr-Configure { ports_in if ports_valid else "hz24"} ports +++++++++++++
            HZ что сюда писать,
            видимо что-то пошло не так.
            '''
        print(f'Запись файла {name_of_config_file}')
        config_file = open(name_of_config_file, 'w')
        config_file.write(config_str)
        config_file.close()
    except:
        print(f'\nСбой записи файла\n')
        return True
    print(f'Файл записан\n')

def create_cisco_conf(scr_n):
    print(f'\nВы выбрали вариант "{conf_type[scr_n]}"')
    print('Пока не реализовано')
    print(f'\n')


while True:
    for i, m in enumerate(conf_type):
        print(f'{i}: {m}')
    try:
        scr_n = int(input('Выберите вариант конфига или выход со скрипта: '))
    except:
        print('\nНет такого варианта. Попробуйте еще раз.')
        continue
    if scr_n in (0,1):
        create_hp_conf(scr_n)
    elif scr_n == 2: 
        create_cisco_conf(scr_n)
    elif scr_n == conf_max:
        print('\nПокедава!\n')
        break
    else:
        print('\nНет такого варианта. Попробуйте еще раз.')
       
