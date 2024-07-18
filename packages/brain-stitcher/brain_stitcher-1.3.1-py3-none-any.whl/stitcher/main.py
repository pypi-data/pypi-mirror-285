'''
    A colections of points Point() are correlated in a manner that creates
    a perimeter Perimeter(). Every perimeter should be nice, i.e.:
        1) Not self-intersecting;
        2) No overlaping points;
        3) Have a prefered orientation.
    If we can garantee this properties, than we proceed to stitch a colection
    of perimeters in a surface Surface().
'''

import json
import os
import time

import numpy as np
import reconstruction as rct

from file_reader import roiread

def island_init(file_dir,f):
    arq = roiread(f"{file_dir}/{f}",filetype,thickness)
    I = rct.Perimeter(arq,full_init=False)
    I.fix_intersection() #use only with manual segmentation
    return I


cwd = os.getcwd()
path = ''
with open(f'{path}/main.json', 'r') as settings:
    data = settings.read()
    Data = json.loads(data)
    FileDir = Data["FileDir"]
    OutputDir = Data["OutputDir"]


##Only estimates by Analytical Approximation
estimation_only = False
##Forcing to recache files
force_cache = False

try:
    os.makedirs(OutputDir)
except:
    pass

opt_par_list = ["Name","FileType","Thickness","Super Resolusition","Start"]
name = "NONAME"
filetype = "OSIRIXJSON"
thickness = 1
new_res = 0
start_points = {}
report = {}
for opt in opt_par_list:
    if not opt in Data.keys():
        continue
    if opt=="Name":
        name = Data[opt]
    if opt=="FileType":
        filetype = Data[opt]
    if opt=="Thickness":
        thickness = float(Data[opt])
    if opt=="Super Resolusition":
        new_res = Data[opt]
    if opt=="Start":
        start_points = Data[opt][0]

Bruno_dict = {"Stitches3D":[{}]}

print("Loading files\n\n")
print(FileDir)

for block in Data["Stitches3D"]:
    for section in block:
        S = rct.Surface()
        for file in block[section]:
            try:
                if isinstance(file,list):
                    I = 0
                    for f in file:
                        I_s = island_init(FileDir,f)
                        if I == 0:
                            I = I_s
                        else:
                            I.islands_ensemble(I_s)
                else:
                    I = island_init(FileDir,file)
                I.remove_overlap(delta=0.0)
                I.fix_intersection()
                I.area_vec()
                I.compute_length()
                S.add_island(I)

            except Exception:
                if isinstance(file,list):
                    print(f"Failed to load pack:{file}, single:{f}")
                else:
                    print(f"Failed to load:{file}")
                    
        if not estimation_only:
            print("\nBuilding surface: ",section)
            Bruno_dict["Stitches3D"][0][section]=[S.vol_est,S.area_est]
            ##Starting points conditions
            if section in start_points.keys():
                start_pass = start_points[section]
            else:
                start_pass = {}

            S._intersection_range = 15000 #how far back the intersection is to be considered
            S.fix_limit = 150   #how many faces Stitcher tries to fix self-intersection
                                #with a given starting point
            S.intersection_limit = 20 #how many starting points before ignoring self-intersection
            
            try:
                close_list = Data["CloseSurface"][0][str(section)]
            except:
                close_list = []


            S.build_surface(close_list,start_pass)
            report.setdefault("intersection",[])
            report.setdefault("control",{})
            if S.self_intersection:
                report["intersection"].append(section)

            chosen_params_S = {
            'intersection_range':S._intersection_range,
            'fix_limit':S.fix_limit,
            'intersection_limit':S.intersection_limit
            }
            report['control'][f'{section}'] = chosen_params_S
            with open(f'{OutputDir}/{name}_{section}.obj', "w") as out_file:
                out_file.write(S.surfaceV)
                out_file.write(S.surfaceE)
            # Extra lids that might be needed
            # So rare that dont even need to be optmized
            # Leave as is
            try:
                C_extra = Data["CloseExtra"][0][str(section)]
            except:
                C_extra = []
            S_extra = rct.Surface()
            for file_colection in C_extra:
                    get = file_colection[0]
                    for file_index in file_colection[1]:
                        contours = Data["Stitches3D"][0][str(section)][get][file_index]
                        Local_I = island_init(FileDir,contours)
                        Local_I.remove_overlap(delta=0.0)
                        S_extra.close_extra(Local_I)
                        list_extras = os.listdir(f"{OutputDir}")
                        list_extras = [f for f in list_extras if f"Extra_{name}_{section}" in f]
                        extra_unique_name = len(list_extras)
                        with open(f'{OutputDir}/Extra_{name}_{section}_{extra_unique_name}.obj', "w") as out_file:
                            out_file.write(S_extra.surfaceV_extra)
                            out_file.write(S_extra.surfaceE_extra)
            
        else:
            S.estimate_geometric_values()
            print(f"Lateral Area estimation: {S.area_est:.2f}\nSlab Volume estimation: {S.vol_est:.2f}".replace(".",","))

if report:
    desktop = os.path.expanduser("~/Desktop").replace("\\","/")
    sub = FileDir.split("/")[-1]
    if not os.path.isdir(f'{desktop}/reports'):
        os.mkdir(f'{desktop}/reports')
    if not os.path.isfile(f'{desktop}/reports/{sub}.json'):
        with open(f'{desktop}/reports/{sub}.json', "w") as out_file:
            pass
    with open(f'{desktop}/reports/{sub}.json', "r+") as out_file:
        current = out_file.read()
        if current:
            current = json.loads(current)
        else:
            current = {}
        current['intersection'] = current.setdefault("intersection",[])+report['intersection']
        current['intersection'] = list(set(current['intersection']))
        current.setdefault('control',{})
        for rc in report['control']:
            current['control'][rc] = report['control'][rc]
        current.setdefault('analytical',{})
        for rc in Bruno_dict["Stitches3D"][0]:
            current['analytical'][rc] = Bruno_dict["Stitches3D"][0][rc]
        out_text = json.dumps(current)
        out_text = out_text.replace("[","[\n")
        out_text = out_text.replace(",",",\n")
        out_file.seek(0)
        out_file.write(out_text)
        out_file.truncate()

time.process_time()
