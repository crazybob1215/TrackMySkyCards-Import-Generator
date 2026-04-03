import csv
import json
import os

import pandas as pd
import requests
from colorama import Fore


def Get_hex_from_reg(reg: str):
    # This function tries to convert the aircraft registration to the Mode-S hex ID
    print(Fore.WHITE + "ICAO is unknown, converting registration to Mode-S hex...")
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
    try:
        details = response.json()
    except json.JSONDecodeError:
        icao = "n/a"
        return icao
    else:
        try:
            return details['ICAOTypeCode']
        except KeyError:
            icao = "n/a"
            return icao
    finally:
        response.close()

def convert_from_reg(reg: str):
    print(Fore.WHITE + "Trying to get the ICAO type for "+reg+" from hexdb...")
    # This function tries to convert the aircraft registration to the ICAO via hexdb's free api
    url = f'https://hexdb.io/reg-hex?reg={reg}'
    response = requests.get(url)
    hex = response.text
    response.close()
    
    if hex == "n/a":
        print(Fore.RED + reg+" couldn't be converted via hexdb. It will need to be checked manually.\n")
        icao = "n/a"
    else:
        url = f'https://hexdb.io/api/v1/aircraft/{hex}'
        response = requests.get(url)
        try:
            details = response.json()
        except json.JSONDecodeError:
            icao = "n/a"
        else:
            try:
                icao = details['ICAOTypeCode']
            except KeyError:
                icao = "n/a"
        finally:
            response.close()
    if icao == "n/a":
        print(Fore.RED + reg+" couldn't be converted via hexdb. It will need to be checked manually.\n")
    return icao

def skystats_smasher(reg: str, caughtDB, mainRegFile):
    # This function runs if the hexdb conversion fails to return either the Mode-S hex ID or the ICAO type code.
    # This depends on the user generating a "registrations.csv" export from the skystats.win site.
    try:
        skystatsFile = working_path+'\\registrations.csv'
        skystatsRegs = pd.read_csv(skystatsFile, keep_default_na=False)
    except FileNotFoundError:
        print(Fore.RED + "No SkyStats export found!")
        icao = convert_from_reg(reg) # this is going to either return a good ICAO or an "n/a"
    else:
        print(Fore.WHITE + "Checking against SkyStats export...")
        try:
            # try to find the reg in the skystats registrations export
            icao = skystatsRegs.loc[(skystatsRegs['Registration'] == reg), 'Aircraft ID'].iloc[0]
        except IndexError:
            # the registration wasn't found. This means the user either didn't pull a fresh export from skystats, or they placed it in the wrong location. Or skystats changed the naming of the file...
            print(Fore.RED + reg+" doesn't exist in the SkyStats export. Did you pull a fresh copy and place it in the right location?")
        
        if icao == "":
            print(Fore.YELLOW + "SkyStats doesn't know what "+reg+" is.")
            icao = convert_from_reg(reg) # this is going to either return a good ICAO or an "n/a"
    finally:
        # no matter what is returned, update the record in caught_registrations
        caughtDB.loc[(caught['registration'] == reg), 'icao'] = icao
        with open(mainRegFile, 'w', newline='') as file:
                caughtDB.to_csv(file, index=False)
        #caughtDB.to_csv(mainRegFile, index=False)
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
        with open(mainRegFile, 'a+', newline='') as file:
            csvwriter = csv.writer(file)
            csvwriter.writerow(header)
            print(Fore.GREEN + "Success!\n")

    # build a list of types and how many times they've been caught
    types = {}
    for reg in regs:
        reg = reg['reg']
        #reg = "F-PDHZ"
        if reg == "SKY-CARDS":
            continue
        print(Fore.YELLOW + "Checking registration code: "+reg)
        # check if the registration has already been caught by the player previously
        try:
            icao = caught.loc[(caught['registration'] == reg), 'icao'].iloc[0]
        except IndexError:
            newRow = pd.DataFrame({'registration':[reg], 'hex':["n/a"], 'icao':["n/a"]})
            with open(mainRegFile, 'a+', newline='') as file:
                newRow.to_csv(file, index=False, header=False)
            caught = pd.read_csv(mainRegFile, keep_default_na=False)
            icao = ""

        if icao == "n/a":
            print(Fore.YELLOW + reg+" has been checked previously, but the ICAO type is not known.")
            icao = skystats_smasher(reg, caught, mainRegFile)
        elif icao == "":
            print(Fore.YELLOW + reg+" has not been checked yet.")
            icao = skystats_smasher(reg, caught, mainRegFile)
        
        if icao != "n/a":
            print(Fore.GREEN + reg+" is a(n) "+icao+"\n")
            if icao in types:
                types[icao]["Registrations Caught"] += 1
            else:
                types[icao] = {"Registrations Caught":1, "Glow Count":0, "Tier":"paper"}

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
