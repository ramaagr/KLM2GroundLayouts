# This Script has been made by Ramanuj Agarwal for the sake of ease of building and updating
# Ground Layouts for Euroscope , an Application used in the VATSIM Network.



import xml.etree.ElementTree as ET

print("Running KLM2GroundLayouts V1.0.1 - Developed and Owned by Ramanuj Agarwal")

def dms_from_dd(decimal_degrees_str):
    decimal_degrees = float(decimal_degrees_str)
    degrees = int(decimal_degrees)
    remaining_minutes = (abs(decimal_degrees - degrees) * 60)
    minutes = int(remaining_minutes)
    remaining_seconds = (remaining_minutes - minutes) * 60
    seconds = int(remaining_seconds)
    fractions_of_seconds = int((remaining_seconds - seconds) * 1000)
    
    # Ensure fractions_of_seconds is in 3 digits
    fractions_of_seconds_str = str(fractions_of_seconds).zfill(3)
    
    minutes = str(minutes).zfill(2)
    seconds = str(seconds).zfill(2)

    return degrees, minutes, seconds, fractions_of_seconds_str

def convert_dd_to_dms(lat,lon): # give in string formats
    lat_dat=dms_from_dd(lat)
    lon_dat=dms_from_dd(lon)

    if lat_dat[0]>=0:
        if lat_dat[0]<100:
            lat=f"N0{lat_dat[0]}.{lat_dat[1]}.{lat_dat[2]}.{lat_dat[3]}"
        else:
            lat=f"N{lat_dat[0]}.{lat_dat[1]}.{lat_dat[2]}.{lat_dat[3]}"
    else:
        if lat_dat[0]>-100:
            lat=f"S0{str(lat_dat[0])[1:]}.{lat_dat[1]}.{lat_dat[2]}.{lat_dat[3]}"
        else:
            lat=f"S{str(lat_dat[0])[1:]}.{lat_dat[1]}.{lat_dat[2]}.{lat_dat[3]}"

    if lon_dat[0]>=0:
        if lon_dat[0]<100:
            lon=f"E0{lon_dat[0]}.{lon_dat[1]}.{lon_dat[2]}.{lon_dat[3]}"
        else:
            lon=f"E{lon_dat[0]}.{lon_dat[1]}.{lon_dat[2]}.{lon_dat[3]}"
    else:
        if lon_dat[0]>-100:
            lon=f"W0{str(lon_dat[0])[1:]}.{lon_dat[1]}.{lon_dat[2]}.{lon_dat[3]}"
        else:
            lon=f"W{str(lon_dat[0])[1:]}.{lon_dat[1]}.{lon_dat[2]}.{lon_dat[3]}"
    if len(lat)!=14:
        for i in range(14-len(lat)):
            lat+='0'
    if len(lon)!=14:
        for i in range(14-len(lon)):
            lon+='0'
    return lat,lon

def extract_airport_info(file_path):
    airport_info = []

    tree = ET.parse(file_path)
    root = tree.getroot()
    # Define namespace for KML
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}

    # Find the SCT Entries folder
    sct_entries_folder = root.find('.//kml:Folder[kml:name="SCT Entries"]', ns)
    labels_folder = root.find('.//kml:Folder[kml:name="Labels"]',ns)

    if sct_entries_folder is None:
        print("sct not found")

    if labels_folder is None:
        print("Labels not found")

    # Iterate through ICAO named folders'
    FIR_SCT_folder=sct_entries_folder.findall('.//kml:Folder[kml:name]',ns)
    for icao_folder in FIR_SCT_folder[1:]:
        # Extract ICAO code
        icao = icao_folder.find('kml:name', ns).text
        if icao=="Groundlayout":
            continue
        # Find the groundlayouts folder
        # print(icao)
        groundlayouts_folder = icao_folder.find('.//kml:Folder[kml:name="Groundlayout"]', ns)
        
        # Find the folder with no name inside groundlayouts
        no_name_folder = groundlayouts_folder.find('.//kml:Folder', ns)
        if no_name_folder is None:
            print("empty no name")
            continue
        # Iterate through paths
        for path in no_name_folder.findall('.//kml:Placemark', ns):
           # print(path.find('.//kml:name',ns).text)
            try:
                description = path.find('.//kml:description', ns).text
                coordinates = path.find('.//kml:coordinates', ns).text.strip()
                airport_info.append((icao, description,coordinates))
            except AttributeError:
                print("Found Attribute error in SCT Entries:",icao)

    return airport_info

def extract_region_info(file_path):
    region_info = []
    tree = ET.parse(file_path)
    root = tree.getroot()

    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    regions_folder = root.find('.//kml:Folder[kml:name="Regions"]',ns)

    if regions_folder is None:
        print("Regions not found")

    FIR_regions_folder = regions_folder.findall('.//kml:Folder[kml:name]',ns)
    for icao_folder in FIR_regions_folder[1:]:

        icao = icao_folder.find('kml:name',ns).text
        if icao=="GroundLayout":
            continue
        #print(icao)
        groundlayouts_folder = icao_folder.find('.//kml:Folder[kml:name="GroundLayout"]',ns)
        if groundlayouts_folder is None:
            continue
        for place in groundlayouts_folder.findall('.//kml:Placemark', ns):
            try:
                description = place.find('.//kml:description', ns).text
                coordinates = place.find('.//kml:coordinates', ns).text
                region_info.append((icao, description, coordinates))
            except AttributeError:
                print("found Attribute Error in Regions:",icao)
                
    return region_info

def extract_label_info(file_path):
    label_info = []
    tree = ET.parse(file_path)
    root = tree.getroot()

    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    Labels_folder = root.find('.//kml:Folder[kml:name="Labels"]',ns)

    if Labels_folder is None:
        print("Labels not found")


    FIR_Labels_folder = Labels_folder.findall('.//kml:Folder[kml:name]',ns)
    for icao_folder in FIR_Labels_folder[1:]:

        icao = icao_folder.find('kml:name', ns).text
        if icao=="GroundLayout":
            continue

        labels_folder = icao_folder.find('.//kml:Folder[kml:name="GroundLayout"]',ns)
        if labels_folder is None:
            continue

        for place in labels_folder.findall('.//kml:Placemark', ns):
            try:
                name = place.find('.//kml:name',ns).text
                lon = place.find('.//kml:coordinates',ns).text
                #lat = place.find('.//kml:latitude',ns).text
                label_info.append((icao, name, lon))
            except AttributeError:
                print("Found Freetext Attribute error for:",icao)
    return label_info

file_path = input('enter klm path:')
airport_info = extract_airport_info(file_path)
region_info = extract_region_info(file_path)
labels_info = extract_label_info(file_path)
GEOstr=str()
REGstr=str()
FREstr=str()
with open('output_sct.txt','w',encoding='utf-8') as f:
    write_str='[GEO]\n'
    
    prev=''
    
    for icao,description,coordinates in airport_info:
        if icao!=prev:
            write_str+='\n;--------------GEO---------------\n\n'
            prev=icao
            write_str+=icao+' GroundLayout '
        coordinate=coordinates.split(' ')
        lat,lon=convert_dd_to_dms(coordinate[0].split(',')[1],coordinate[0].split(',')[0])
        for i in coordinate[1:]:
            lat1,lon1=convert_dd_to_dms(i.split(',')[1],i.split(',')[0])
            write_str+=lat+' '+lon+' '+lat1+' '+lon1+' COLOR_'+description+'\n'
            lat=lat1
            lon=lon1
    GEOstr = write_str
    f.write(write_str)
        
with open('output_reg.txt','w',encoding='utf-8') as f:
    write_str='[REGIONS]\n'

    prev=''
    
    for icao,description,coordinates in region_info:
        if icao!=prev:
            write_str+='\n;--------------regions---------------\n'
            prev=icao
        write_str+='\nREGIONNAME '+icao+' GroundLayout\nCOLOR_'+description+'      '
        for i in coordinates.strip().split(' '):
            j = i.split(',')
            lat,lon=convert_dd_to_dms(i.split(',')[1],i.split(',')[0])
            write_str+=lat+' '+lon+'\n   '
    REGstr = write_str
    f.write(write_str)

with open('output_lab.txt','w',encoding='utf-8') as f:
    write_str='[FREETEXT]\n'
    prev=''
    for icao,name,coordinate in labels_info:
        lat, lon = convert_dd_to_dms(coordinate.split(',')[1], coordinate.split(',')[0])
        if icao!=prev:
            write_str+='\n;--------------freetext---------------\n'
            prev=icao
        write_str+=lat+':'+lon+':'+icao+':'+name+'\n'
    FREstr = write_str
    f.write(write_str)
    
print("FINISHED :)")

print("1 for pasting output to SCT and ESE FILE")

a=input()

if a!="1":
    exit()
    
else:
    sct_src=input("enter the location of SCT file:")
    ese_src=input("enter the location of ESE file:")
    new_sct=str()
    new_ese=str()
    print("PLS WAIT FOR A MINUTE :)")
    with open(sct_src,'r') as f:
        a=f.read().split('\n')
        skip=0
        for i in range(len(a)):
            if a[i]=='':
                if skip==1:
                    continue
                else:
                    new_sct+='\n'
                    continue
            elif a[i][0]=='[':
                skip=0
                print("Found ",a[i]," in SCT")
                if a[i]=="[GEO]":
                    new_sct+=GEOstr+'\n'
                    skip=1
                    print("OVERWRITING GEO")
                    continue
                elif a[i]=="[regions]" or a[i] == "[REGIONS]":
                    new_sct+=REGstr+'\n'
                    skip=1
                    print("OVERWRITING REGIONS")
                    continue
                else:
                    new_sct+=a[i]+'\n'
                    continue
            if skip==0:
                new_sct+=a[i]+'\n'
                continue
    with open(sct_src,'w') as f:
        f.write(new_sct)
        print("succesfully written SCT")
    with open(ese_src,'r') as f:
        a=f.read().split('\n')
        skip=0
        for i in range(len(a)):
            if a[i]=='':
                if skip==1:
                    continue
                else:
                    new_ese+='\n'
                    continue
            elif a[i][0]=='[':
                skip=0
                print("FOUND ",a[i]," in ESE")
                if a[i]=="[FREETEXT]":
                    new_ese+=FREstr+'\n'
                    skip=1
                    print("OVERWRITING FREETEXT")
                    continue
                else:
                    new_ese+=a[i]+'\n'
                    continue
            if skip==0:
                new_ese+=a[i]+'\n'
                continue
    with open(ese_src,'w') as f:
        f.write(new_ese)
print("done")

