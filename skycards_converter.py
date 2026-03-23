import csv
import json
import os

import pandas as pd
import requests
from colorama import Fore


def Get_hex_from_reg(reg: str):
    # This function tries to convert the aircraft registration to the Mode-S hex ID
    print(Fore.WHITE + "New registration, converting to hex...")
    url = f'https://hexdb.io/reg-hex?reg={reg}'
    response = requests.get(url)
    details = response.text
    response.close()
    return details

def Get_info_from_hex(hex: str):
    # This function should only run if the Get_hex_from_reg function worked. This one takes the Mode-S hex ID and converts it to the ICAO aircraft type.
    print(Fore.WHITE + "Hex conversion success, getting ICAO...")
    url = f'https://hexdb.io/api/v1/aircraft/{hex}'
    response = requests.get(url)
    details = response.json()
    response.close()
    return details['ICAOTypeCode']

def skystats_smasher(reg: str, caughtDB):
    # This function runs if the hexdb conversion fails to return either the Mode-S hex ID or the ICAO type code.
    # This depends on the user generating a "registrations.csv" export from the skystats.win site.
    try:
        skystatsFile = working_path+'\\registrations.csv'
        skystatsRegs = pd.read_csv(skystatsFile, keep_default_na=False)
    except FileNotFoundError:
        print(Fore.RED + "No SkyStats export found. ICAO type will need to be found manually!\n")
        icao = "n/a"
        return icao
    else:
        print(Fore.WHITE + "Checking against SkyStats export...")
        index = 0
        icao = ""
        for skystatsReg in skystatsRegs['Registration']:
            if reg == skystatsReg:
                icao = skystatsRegs['Aircraft ID'][index]
                if icao == "":
                    print(Fore.RED + "SkyStats doesn't know what "+reg+" is... womp womp\n")
                    icao = "n/a"
                    break 
                print(Fore.GREEN + "Found "+reg+" is a(n) "+icao+"!\n")
                # Update the user's db with the found ICAO type
                caughtDB.loc[(caught['registration'] == reg).idxmax(), 'icao'] = icao
                caughtDB.to_csv(mainRegFile, index=False)
                break
            else:
                index += 1
        return icao


if __name__ == '__main__':
    # Get the working path for this script
    working_path = os.path.dirname(os.path.realpath(__file__))

    # load the skycards export json file and read in the cards & unique registrations caught by the player
    # the export also includes the airports unlocked by the player, but I don't currently have any use for that
    try:
        file =  open(working_path+'\\skycards_user.json')
        skycards_export = (json.load(file))
    except FileNotFoundError:
        print(Fore.RED + "No SkyCards export found!")
    else:
        cards = skycards_export['cards']
        regs = skycards_export['uniqueRegs']
    
    # load the "database" of previously reviewed registrations
    # if it doesn't exist, create a blank copy with the header
    try:
        mainRegFile = working_path+'\\caught_registrations.csv'
        caught = pd.read_csv(mainRegFile, keep_default_na=False)
    except FileNotFoundError:
        print(Fore.RED + "Personal registrations db doesn't exist. Creating a blank copy to build on...\n")
        header = ("registration","hex","icao")
        with open(mainRegFile, 'a+', newline='') as orf:
            csvwriter = csv.writer(orf)
            csvwriter.writerow(header)
            print(Fore.GREEN + "Success!\n")

    # build a list of types and how many times they've been caught
    types = {}
    for reg in regs:
        if reg['reg'] == "SKY-CARDS":
            continue
        print(Fore.YELLOW + "Checking registration code: "+reg['reg'])
        # check if the registration has already been caught by the player previously
        index = 0
        icao = ""
        for existingReg in caught['registration']:
            doNotAdd = False
            if reg['reg'] == existingReg:
                icao = caught['icao'][index]
                doNotAdd = True
                if icao == "n/a":
                    print(Fore.YELLOW + reg['reg']+" has been checked previously, but the ICAO type is not known.")
                    icao = skystats_smasher(reg['reg'], caught)
                else:
                    print(Fore.WHITE + existingReg+" has already been checked previously.\n")
                break
            else:
                index += 1
        
        if icao == "":
            # This runs when the reg doesn't exist in "caught_registrations.csv"
            hex = Get_hex_from_reg(reg['reg'])
            if hex != "n/a":
                icao = Get_info_from_hex(hex)
                if icao == "n/a":
                    print(Fore.RED + "Couldn't get the ICAO type code.")
                    icao = skystats_smasher(reg['reg'], caught)
                else:
                    print(Fore.GREEN + reg['reg']+" is a(n) "+icao+"\n")
            else:
                print(Fore.RED + "Couldn't get the Mode-S hex code.")
                icao = skystats_smasher(reg['reg'], caught)
        if icao != "n/a":
            if icao in types:
                types[icao]["Registrations Caught"] += 1
            else:
                types[icao] = {"Registrations Caught":1, "Glow Count":0, "Tier":"paper"}
        if doNotAdd == False:
            newRow = (reg['reg'],hex,icao)
            with open(mainRegFile, 'a+', newline='') as orf:
                csvwriter = csv.writer(orf)
                csvwriter.writerow(newRow)

    # Get info from the SkyCards cards, like glow count and tier
    for card in cards:
        try:
            types[card['modelId']]["Glow Count"] = card["glowCount"]
            types[card['modelId']]["Tier"] = card["tier"]
        except:
            types[card['modelId']] = {"Registrations Caught":1, "Glow Count":0, "Tier":"paper"}

    # Write the gathered info to a csv for import to TrackMySkyCards
    fields = ['ICAO','Registrations Caught','Glow Count','Tier']
    with open('TrackMySkyCards_Import.csv', 'w', newline='') as csvfile:
        csvwriter = csv.DictWriter(csvfile, fields)
        csvwriter.writeheader()
        for icao in types:
            csvwriter.writerow({'ICAO':icao,'Registrations Caught':types[icao]['Registrations Caught'],'Glow Count':types[icao]['Glow Count'],'Tier':types[icao]['Tier']})

    print(Fore.GREEN + "Review complete!")