# TrackMySkyCards-Import-Generator
This tool uses the export file created by the [skycards-export tool](https://github.com/mfkp/skycards-export) to create an import file for the [TrackMySkyCards](https://trackmyskycards.vercel.app/) site.

## Pre-requisites
- You will need Python 3 for this tool
- The "skycards_user.json" created by the skycards-export tool is required for this tool

## Workflow
I suggest you create a folder on your computer to store the required scripts and their outputs. While this isn't a hard requirement, you will need to have all of the scripts and their outputs in the same location for this tool to function. I suggest creating a folder so that way you aren't hunting for all of it when you want to run the tool.

1. Download the skycards-export tool from the [skycards-export](https://github.com/mfkp/skycards-export) repository, place it in your folder, then run the skycards-export tool. You should have a "skycards_user.json" file in the same folder. Optionally, get your "registrations.csv" from the [SkyStats](https://skystats.win) website. This will help resolve some of the unconvertable registrations without needing to check hexdb. See the [SkyStats Registrations Export](#skystats-registrations-export) section for the full process.
2. Download the "skycards_converter.py" and place it in the same folder as the skycards export. I've also included a Windows batch script "skycards_converter.cmd" to simplify running the tool. Just place it in the same location and it will run the python tool when double clicked. Otherwise, feel free to run the python script however you like.
  1. To save some time and avoid annoying the people running [hexdb.io](https://hexdb.io/), I would suggest that you also download the "caught_registrations.csv" from this repository. It is a list of all the registrations that I have checked against hexdb, SkyStats, or manually searched on the wider web. The converter checks this list first before trying to get the info from hexdb, so it will keep from making redundant API calls to hexdb. If you don't download my copy, this tool will create a blank copy for you and save any registrations you check for later reference.
3. As long as no unexpected errors are encountered, the tool will create a "TrackMySkyCards_Import.csv" in the same folder. Import this file following the instructions in the [TrackMySkyCards](#trackmyskycards-import) section.

If you encounter any errors, see the [Troubleshooting](#troubleshooting) section for potential solutions.

***DISCLAIMER**: I cannot gaurantee that the data in "caught_registrations.csv" is perfectly accurate. The free resources that exist and are available with the information needed for this tool are sometimes not perfectly up-to-date or may have slightly different information from what SkyCards thinks is right. For example, SkyCards treats some aircraft sub-types the same as their parent type. Be aware that some manual review will likely be needed to get the best results. I have already done this for a number of registrations, which is included in the "caught_registrations.csv" found in this repository.*

## How the tool works
1. The tool pulls all of the registrations from your "skycards_user.json" file and attempts to convert each registration to the aircraft type. First, it tries to use the "caught_registrations.csv", then the "registrations.csv", then finally it uses the hexdb API if the registration -> ICAO type couldn't be completed through the first two methods. The registrations are saved to "caught_registrations.csv" with their Mode-S hex ID and ICAO type code as they are identified. If the Mode-S hex ID or ICAO type code can't be found, they are set to "n/a". The script will also report in the terminal when a registration can't be converted. In those cases, I've found that google/duckduckgo/your search engine of choice is your friend. Searching "airplane registration $registrationID" may yield results from airplane spotter websites, official registry databases, or other sources. I usually take anything I find from those sources and compare against the "Airpedia" in SkyCards to confirm the match is correct and get the ICAO type that SkyCards uses. Once you get the ICAO type code, you can manually update the registration's entry in "caught_registrations.csv", and it will be counted the next time the script is run.
2. The tool then evaluates all the "cards" entries in the "skycards_user.json" file to get: the aircraft types that you have caught, the "glow count" for that type, and the card tier. The number of times you caught each type is tracked in step 1 and included in this step. The four pieces of info for each type are then saved in the "TrackMySkyCards_Import.csv".

## SkyStats Registrations Export
1. Follow the instructions for the skycards-export tool to get your "skycards_user.json" file.
2. Go to SkyStats and import your "skycards_user.json" using the box outlined in the following image:![image](https://github.com/crazybob1215/TrackMySkyCards-Import-Generator/blob/main/images/skystats_import_1.png)
3. Between your stats and the cards, click the "Registrations" tab:![image](https://github.com/crazybob1215/TrackMySkyCards-Import-Generator/blob/main/images/skystats_import_2.png)
4. Scroll down till you can see the "Export Registrations CSV" button at the bottom right. Click the button, then after the file is downloaded move it to the folder where you have the "skycards_converter.py" tool.![image](https://github.com/crazybob1215/TrackMySkyCards-Import-Generator/blob/main/images/skystats_import_3.png)

## TrackMySkyCards Import
1. From your TrackMySkyCards dashboard, click the "Account" tab at the bottom right:![image](https://github.com/crazybob1215/TrackMySkyCards-Import-Generator/blob/main/images/trackmyskycards_import_1.png)
2. Click the "Choose CSV/TSV file" button, then navigate to your skycards converter folder and select the "TrackMySkyCards_Import.csv" file:![image](https://github.com/crazybob1215/TrackMySkyCards-Import-Generator/blob/main/images/trackmyskycards_import_2.png)
3. The button should change to say "Choose a different file" and show "Selected file: TrackMySkyCards_Import.csv" directly under it, as well as "Parsed ### rows. Ready to import" at the bottom left.![image](https://github.com/crazybob1215/TrackMySkyCards-Import-Generator/blob/main/images/trackmyskycards_import_3.png)
4. Click "Import CSV", then wait for the file to be processed. When completed, a status box will appear at the top right of the page noting how many rows were successfully imported and, if any failed, a count of how many rows failed.![image](https://github.com/crazybob1215/TrackMySkyCards-Import-Generator/blob/main/images/trackmyskycards_import_4.png)

## Troubleshooting
### TrackMySkyCards # rows failed to import
This is likely due to your import file either containing an aircraft type (ICAO type code) that does not exist in TrackMySkyCards, or your "caught" count for an aircraft type is more than the number of that aircraft that exists (or how many TrackMySkyCards thinks exist). The best way to resolve this is to use the "Export your data" function in TrackMySkyCards and then compare that export against the import file to find either the missing type(s) or mismatched count(s).

### More to come?
Have you run into an issue not listed here? Let me know, and I'll see what I can figure out to fix it!
