import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET
import os

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

def convert_dd_to_dms(lat, lon): # give in string formats
    lat_dat = dms_from_dd(lat)
    lon_dat = dms_from_dd(lon)

    if lat_dat[0] >= 0:
        if lat_dat[0] < 100:
            lat = f"N0{lat_dat[0]}.{lat_dat[1]}.{lat_dat[2]}.{lat_dat[3]}"
        else:
            lat = f"N{lat_dat[0]}.{lat_dat[1]}.{lat_dat[2]}.{lat_dat[3]}"
    else:
        if lat_dat[0] > -100:
            lat = f"S0{str(lat_dat[0])[1:]}.{lat_dat[1]}.{lat_dat[2]}.{lat_dat[3]}"
        else:
            lat = f"S{str(lat_dat[0])[1:]}.{lat_dat[1]}.{lat_dat[2]}.{lat_dat[3]}"
    if len(lat) != 14:
        for i in range(14 - len(lat)):
            lat += '0'
    if len(lon) != 14:
        for i in range(14 - len(lon)):
            lon += '0'
    return lat, lon

def extract_airport_info(file_path):
    airport_info = []

    tree = ET.parse(file_path)
    root = tree.getroot()
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}

    sct_entries_folder = root.find('.//kml:Folder[kml:name="SCT Entries"]', ns)
    labels_folder = root.find('.//kml:Folder[kml:name="Labels"]', ns)

    if sct_entries_folder is None:
        print("sct not found")

    if labels_folder is None:
        print("Labels not found")

    FIR_SCT_folder = sct_entries_folder.findall('.//kml:Folder[kml:name]', ns)
    for icao_folder in FIR_SCT_folder[1:]:
        icao = icao_folder.find('kml:name', ns).text
        if icao == "Groundlayout":
            continue
        groundlayouts_folder = icao_folder.find('.//kml:Folder[kml:name="Groundlayout"]', ns)
        no_name_folder = groundlayouts_folder.find('.//kml:Folder', ns)
        if no_name_folder is None:
            print("empty no name")
            continue
        for path in no_name_folder.findall('.//kml:Placemark', ns):
            try:
                description = path.find('.//kml:description', ns).text
                coordinates = path.find('.//kml:coordinates', ns).text.strip()
                airport_info.append((icao, description, coordinates))
            except AttributeError:
                print("Found Attribute error in SCT Entries:", icao)

    return airport_info

def extract_region_info(file_path):
    region_info = []
    tree = ET.parse(file_path)
    root = tree.getroot()

    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    regions_folder = root.find('.//kml:Folder[kml:name="Regions"]', ns)

    if regions_folder is None:
        print("Regions not found")

    FIR_regions_folder = regions_folder.findall('.//kml:Folder[kml:name]', ns)
    for icao_folder in FIR_regions_folder[1:]:

        icao = icao_folder.find('kml:name', ns).text
        if icao == "GroundLayout":
            continue
        groundlayouts_folder = icao_folder.find('.//kml:Folder[kml:name="GroundLayout"]', ns)
        if groundlayouts_folder is None:
            continue
        for place in groundlayouts_folder.findall('.//kml:Placemark', ns):
            try:
                description = place.find('.//kml:description', ns).text
                coordinates = place.find('.//kml:coordinates', ns).text
                region_info.append((icao, description, coordinates))
            except AttributeError:
                print("found Attribute Error in Regions:", icao)
                
    return region_info

def extract_label_info(file_path):
    label_info = []
    tree = ET.parse(file_path)
    root = tree.getroot()

    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    Labels_folder = root.find('.//kml:Folder[kml:name="Labels"]', ns)

    if Labels_folder is None:
        print("Labels not found")

    FIR_Labels_folder = Labels_folder.findall('.//kml:Folder[kml:name]', ns)
    for icao_folder in FIR_Labels_folder[1:]:

        icao = icao_folder.find('kml:name', ns).text
        if icao == "GroundLayout":
            continue

        labels_folder = icao_folder.find('.//kml:Folder[kml:name="GroundLayout"]', ns)
        if labels_folder is None:
            continue

        for place in labels_folder.findall('.//kml:Placemark', ns):
            try:
                name = place.find('.//kml:name', ns).text
                lon = place.find('.//kml:coordinates', ns).text
                label_info.append((icao, name, lon))
            except AttributeError:
                print("Found Freetext Attribute error for:", icao)
    return label_info

def process_files(kml_path, sct_path, ese_path):
    airport_info = extract_airport_info(kml_path)
    region_info = extract_region_info(kml_path)
    labels_info = extract_label_info(kml_path)
    
    GEOstr = str()
    REGstr = str()
    FREstr = str()
    
    with open('output_sct.txt', 'w', encoding='utf-8') as f:
        write_str = '[GEO]\n'
        prev = ''
        for icao, description, coordinates in airport_info:
            if icao != prev:
                write_str += '\n;--------------GEO---------------\n\n'
                prev = icao
                write_str += icao + ' GroundLayout '
            coordinate = coordinates.split(' ')
            lat, lon = convert_dd_to_dms(coordinate[0].split(',')[1], coordinate[0].split(',')[0])
            for i in coordinate[1:]:
                lat1, lon1 = convert_dd_to_dms(i.split(',')[1], i.split(',')[0])
                write_str += lat + ' ' + lon + ' ' + lat1 + ' ' + lon1 + ' COLOR_' + description + '\n'
                lat = lat1
                lon = lon1
        GEOstr = write_str
        f.write(write_str)
        
    with open('output_reg.txt', 'w', encoding='utf-8') as f:
        write_str = '[REGIONS]\n'
        prev = ''
        for icao, description, coordinates in region_info:
            if icao != prev:
                write_str += '\n;--------------regions---------------\n'
                prev = icao
            write_str += '\nREGIONNAME ' + icao + ' GroundLayout\nCOLOR_' + description + '      '
            for i in coordinates.strip().split(' '):
                j = i.split(',')
                lat, lon = convert_dd_to_dms(i.split(',')[1], i.split(',')[0])
                write_str += lat + ' ' + lon + '\n   '
        REGstr = write_str
        f.write(write_str)

    with open('output_lab.txt', 'w', encoding='utf-8') as f:
        write_str = '[FREETEXT]\n'
        prev = ''
        for icao, name, coordinate in labels_info:
            lat, lon = convert_dd_to_dms(coordinate.split(',')[1], coordinate.split(',')[0])
            if icao != prev:
                write_str += '\n;--------------freetext---------------\n'
                prev = icao
            write_str += lat + ':' + lon + ':' + icao + ':' + name + '\n'
        FREstr = write_str
        f.write(write_str)
        
    messagebox.showinfo("Process Completed", "Files have been processed and outputs are generated.")

def select_kml_file():
    kml_file_path.set(filedialog.askopenfilename(filetypes=[("KML files", "*.kml")]))
    
def select_sct_file():
    sct_file_path.set(filedialog.askopenfilename(filetypes=[("SCT files", "*.sct")]))
    
def select_ese_file():
    ese_file_path.set(filedialog.askopenfilename(filetypes=[("ESE files", "*.ese")]))

def run_script():
    kml_path = kml_file_path.get()
    sct_path = sct_file_path.get()
    ese_path = ese_file_path.get()
    
    if not kml_path or not sct_path or not ese_path:
        messagebox.showwarning("Missing files", "Please select all required files.")
        return
    
    process_files(kml_path, sct_path, ese_path)

app = tk.Tk()
app.title("KML to SCT/REG/FREETEXT Converter")

kml_file_path = tk.StringVar()
sct_file_path = tk.StringVar()
ese_file_path = tk.StringVar()

tk.Label(app, text="KML File").grid(row=0, column=0, padx=10, pady=10)
tk.Entry(app, textvariable=kml_file_path, width=50).grid(row=0, column=1, padx=10, pady=10)
tk.Button(app, text="Browse", command=select_kml_file).grid(row=0, column=2, padx=10, pady=10)

tk.Label(app, text="SCT File").grid(row=1, column=0, padx=10, pady=10)
tk.Entry(app, textvariable=sct_file_path, width=50).grid(row=1, column=1, padx=10, pady=10)
tk.Button(app, text="Browse", command=select_sct_file).grid(row=1, column=2, padx=10, pady=10)

tk.Label(app, text="ESE File").grid(row=2, column=0, padx=10, pady=10)
tk.Entry(app, textvariable=ese_file_path, width=50).grid(row=2, column=1, padx=10, pady=10)
tk.Button(app, text="Browse", command=select_ese_file).grid(row=2, column=2, padx=10, pady=10)

tk.Button(app, text="Run", command=run_script).grid(row=3, column=0, columnspan=3, pady=20)

app.mainloop()
