import json
import numpy as np
def roiread(name, filetype: str = "OSIRIXJSON", thickness: float = 1):
    '''
        It may be needed to read files from imageJ,
    Osirix and other programs.
    '''
    #filetype = filetype.upper()
    if filetype=="OSIRIXJSON":
        with open(name, 'r') as roi:
            data = roi.read()
            Data = json.loads(data)

        ## this parses OsiriX roi output into float numbers
        ## in x and y coordinate system
        copy = False
        j = 0
        number = ["","",""]
        ContourLength = len(Data["ROI3DPoints"])
        roipoints = np.array([[0.,0.,0.]]*(ContourLength + 1))

        ## litle loop to remove charecters from the midle of the numbers
        ## may just skip it
        ## Should check if .isnumeric() runs faster than True or False loop
        for i in range(0,ContourLength):
            for K in Data["ROI3DPoints"][i]:
                if copy and K != "," and K != "]":
                    number[j] = number[j] + K
                if K == "[":
                    copy = True
                if K == "]":
                    copy = False
                    j = 0
                if K == ",":
                    j += 1

            roipoints[i,0] = float(number[0])
            roipoints[i,1] = float(number[1])
            roipoints[i,2] = float(number[2])
            number = ["","",""]

        ## Repeting the first to point at the end
        ## of the array to create a closed curve
        roipoints[ContourLength] = roipoints[0]
    if filetype=="IMAGEJ" or filetype=="FIJI":
        import roifile as ROI
        roi = ROI.ImagejRoi.fromfile(name)
        xy_array = roi.coordinates()
        z = roi.position*thickness
        z = np.array([z]*xy_array.shape[0])
        array = [[xy_array[:,0][i],xy_array[:,1][i],z[i]] for i in range(xy_array.shape[0])]
        roipoints = np.array(array)
        roipoints = np.append(roipoints,[roipoints[0]],axis=0)
    return roipoints
