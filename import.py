#!/usr/bin/python3

import sys
import csv
import requests
import time
import click

@click.command()
@click.option('--url','-u', help='KEA API url [required]')
@click.option('--fin','-f',help='KEA CSV lease4 file [required]')
@click.option('--verbose','-v', count=True, help='increase command output (max 2)')

def main(url,verbose,fin):
   if not url or not fin:
      sys.exit("Invalid usage: "+sys.argv[0]+" --help for more info")
   raw_lease = 0
   good_lease = 0
   csvsource = fin
   with open(csvsource) as csvfile:
      info = csv.reader(csvfile, delimiter=',', quotechar='|')
      csv_headings = next(info)
      for row in info:
         raw_lease += 1
         if verbose == 3:
           print(f"lease timestamp: {int(row[4])}, time now: {int(time.time())}")
         if int(row[4]) > int(time.time()):
            good_lease +=1
            ip = row[0]
            hw = row[1]
            expire = int(row[4])
            subnet_id = int(row[5])
            if not check_lease(url,ip,hw,subnet_id,expire):
               if verbose == 2:
                  print("{"+ip+", "+hw+"} Lease exists.")
               elif verbose == 1:
                  print (".",end='',flush=True)
            myjson = {'command': 'lease4-add', 'service': ['dhcp4'],'arguments': { 'subnet-id': subnet_id, 'ip-address': ip, 'hw-address': hw,'expire': expire}}
            r = requests.post(url, json=myjson)
            if verbose == 3:
              print(myjson)
            if verbose == 2:
               print("{"+ip+", "+hw+"} status code: "+str(r.status_code) +", result: "+r.json()[0]['text'])
            if (r.status_code == 200) and int(r.json()[0]["result"]) == 0:
               if verbose == 1:
                  print ("0",end='',flush=True)
            else:
               if verbose == 1:
                  print (".",end='',flush=True)
   print ("\nLeases scanned: "+str(raw_lease))
   print ("Leases imported: "+str(good_lease))

def check_lease(url,ip,hw,subnet_id,expire):
   myjson = {'command': 'lease4-get', 'service': ['dhcp4'],'arguments': { 'subnet-id': subnet_id, 'hw-address': hw, 'ip-address' : ip ,"expire": expire}}
   r = requests.post(url, json=myjson)
   return (r.json()[0]['result'])


if __name__ == '__main__':
   main()
