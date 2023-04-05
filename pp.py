from math import *
import PySimpleGUI as sg

#Maximum input value for the scoll GUI items - arbitrarily high
MAX = 100000


def genLine(length, extrudeRate, moveRate, axis, header, startPos):
    """Generates a GCODE to produce a line of set length, speed, and extrusion rate
    Arguments: line length in mm - length
               extrusion rate in mm/s - extrudeRate
               movement speed in mm/s - moveRate
               line axis (X or Y) - axis
               (header and startpos passed to be used in saving)
    Returns:   Nothing, but saves a calculated GCODE file"""
    newHeader = header[:]
    newHeader += ["G0 F" + str(moveRate*60)]
    time = length/moveRate
    extrudeRate = extrudeRate * time #convert mm/s to mm

    if (axis == 'X'):
        index = 1
    else:
        index = 2

    endPos = axis + str(float(startPos[index][1:-1]) + length) #concats and saves final end position
    newHeader += ["G1 " + endPos + " E" + str(extrudeRate)] #adds end position with extrusion rate
    saveFile('Line_Test.gcode', newHeader)
    print("Complete!")

def genCircle(radius, extrudeRate, moveRate, header, startPos):
    """Generates a GCODE to produce a circle of set radius, speed, and extrusion rate
    Arguments: circle radius in mm - radius
               extrusion rate in mm/s - extrudeRate
               movement speed in mm/s - moveRate
               line axis (X or Y) - axis
    Returns:   Nothing, but saves a calculated GCODE file"""
    newHeader = header[:]
    newHeader += ["G0 F" + str(moveRate*60)]
    time = (radius*2*pi)/moveRate
    extrudeAmt = extrudeRate * time #convert mm/s to mm
    newHeader += ["G2 " + startPos[1] + startPos[2] + "E" + str(extrudeAmt) + " R" + str(radius)]
    saveFile('Circle_Test.gcode', newHeader)
    print("Complete!")

def genGradient(numDivisions, length, initVal, endVal, constVal, header, axis, chosenVar, startPos):
    """Generates a GCODE to produce a line of set length - keeping either speed, flow rate, or volume constant 
        based on user selection, and varying the other value (speed or flow rate) from an initial to end state
        over a set number of divisions.
    Arguments: line length in mm - length
               number of variable steps - numDivisions
               the inital value of the modified variable - initVal
               the final value of the modified variable - endVal
               the value of the constant variable - constVal
               the variable to be held constant - chosenVar
               line axis (X or Y) - axis
    Returns:   Nothing, but saves a calculated GCODE file"""
    newHeader = header[:]
    if (axis == 'X'):
        index = 1
    else:
        index = 2

    if (chosenVar == 'Constant speed'):
        newHeader += ["G0 F" + str(constVal*60)]
        time = length/constVal
        flowDivision = (endVal - initVal)/(numDivisions - 1)
        posDivision = length / (numDivisions - 1)
        for i in range(numDivisions):
            endPos = axis + str(float(startPos[index][1:-1]) + (posDivision * i))
            newHeader += ["G1 " + endPos + " E" + str((initVal + (flowDivision * i)) * time)]
    elif (chosenVar == 'Constant flow rate'): #volume decreases to match speed
        speedDivision = (endVal - initVal)/(numDivisions - 1)
        posDivision = length / (numDivisions - 1)
        for i in range(numDivisions):
            endPos = axis + str(float(startPos[index][1:-1]) + (posDivision * i))
            speed = initVal + (speedDivision * i)
            time = posDivision / speed
            extrudeRate = constVal * time
            newHeader += ["G0 F" + str((speed * 60))]
            newHeader += ["G1 " + endPos + " E" + str(extrudeRate)]
    elif (chosenVar == 'Constant volume'): #volume constant to speed
        speedDivision = (endVal - initVal)/(numDivisions - 1)
        posDivision = length / (numDivisions - 1)
        totalTime = 0
        for i in range(numDivisions):
            totalTime += (posDivision / (initVal + (speedDivision * i)))
        extrudeRate = constVal * totalTime
        for i in range(numDivisions):
            endPos = axis + str(float(startPos[index][1:-1]) + (posDivision * i))
            speed = initVal + (speedDivision * i)
            newHeader += ["G0 F" + str((speed * 60))]
            newHeader += ["G1 " + endPos + " E" + str(extrudeRate)]
    saveFile('Gradient_Test.gcode', newHeader)
    print('Complete!')



def saveFile (filename, content):
    """Takes a filename and list of lines and writes them to a text file, saving it as a gcode
    Arguments: The name of the output file - filename
               the content of the file, each element being a line - content
    Returns:   Nothing, but writes the list content to a file"""

    code = open(filename, 'w')
    for line in content:
        code.write(line)
        code.write('\n')
    code.close()

#__________________________________________________________________________________________________#
#ERROR DETECTION
#Use try/except statments to make sure user inputs stored in the values dictionary match requirements

def circleError(values):
    """Tests the user inputs relating to circle generation in the values dictionary, throws an
       appropriate error if they dont match expectations"""
    try:
        float (values['RADIUS'])
    except ValueError:
        sg.popup("Radius value must be a number")
        return False

    try:
        float(values['C_EXTRUDE_RATE'])
    except ValueError:
        sg.popup("Extrusion rate must be a number")
        return False

    try:
        float(values["C_MOVE_RATE"])
    except:
        sg.popup("Movement rate must be a number")
        return False
    return True

def lineError(values):
    """Tests the user inputs relating to line generation in the values dictionary, throws an
       appropriate error if they dont match expectations"""
    try:
        float (values['L_LENGTH'])
    except ValueError:
        sg.popup("Line length must be a number")
        return False

    try:
        float(values['L_EXTRUDE_RATE'])
    except ValueError:
        sg.popup("Extrusion rate must be a number")
        return False

    try:
        float(values["L_MOVE_RATE"])
    except:
        sg.popup("Movement rate must be a number")
        return False
    return True

def gradError(values):
    """Tests the user inputs relating to gradient line generation in the values dictionary, throws an
       appropriate error if they dont match expectations"""
    try:
        int(values['G_STEPS'])
    except ValueError:
        sg.popup("Number of steps must be an integer")
        return False

    try:
        float (values['G_LENGTH'])
    except ValueError:
        sg.popup("Line length must be a number")
        return False

    try:
        float(values['INIT'])
    except ValueError:
        sg.popup("Initial value must be a number")
        return False
    
    try:
        float(values['FINAL'])
    except:
        sg.popup("Final value must be a number")
        return False

    try:
        float(values['CONST'])
    except:
        sg.popup("Constant value must be a number")
        return False
    return True

#GUI generation - it's messy but matches PySimpleGUI's needs


def make_window():
    ''' Makes a window of determined layout and elements. 
        This just creates the window elements, layout, and variables.'''

    sg.theme('DarkGrey15')
    line_layout = [ #This list create the line subpage
        [sg.Text('Generate a line test')],
        [sg.Text('Start position'), sg.Text('X:'), sg.Spin([i for i in range(1,MAX)],initial_value=110, k='L_X'),
                                    sg.Text('Y:'), sg.Spin([i for i in range(1,MAX)],initial_value=110, k='L_Y'),
                                    sg.Text('Z:'), sg.Spin([i for i in range(1,MAX)],initial_value=2, k='L_Z')],
        [sg.Text('Line length (mm)'), sg.Input(key='L_LENGTH')],
        [sg.Text('Extrusion rate (mm/s)'), sg.Input(key = 'L_EXTRUDE_RATE')],
        [sg.Text('Movement rate (mm/s)'), sg.Input(key = 'L_MOVE_RATE')],
        [sg.Text('Movement axis'), sg.Radio('X axis', "RADIO1", default=True, size=(10,1), k='X1'), sg.Radio('Y axis', "RADIO1", size=(10,1), k='Y1')],
        [sg.Button('Generate', key = "genline"), sg.Button('Close', key = 'L_CLOSE')]
        ]

    circle_layout = [
        [sg.Text('Generate a circle test')],
        [sg.Text('Start position'), sg.Text('X:'), sg.Spin([i for i in range(1,MAX)],initial_value=110, k='C_X'),
                                    sg.Text('Y:'), sg.Spin([i for i in range(1,MAX)],initial_value=110, k='C_Y'),
                                    sg.Text('Z:'), sg.Spin([i for i in range(1,MAX)],initial_value=2, k='C_Z')],
        [sg.Text('Circle radius (mm)'), sg.Input(key='RADIUS')],
        [sg.Text('Extrusion rate (mm/s)'), sg.Input(key = 'C_EXTRUDE_RATE')],
        [sg.Text('Movement rate (mm/s)'), sg.Input(key = 'C_MOVE_RATE')],
        [sg.Button('Generate', key = "gencircle"), sg.Button('Close', key = 'C_CLOSE')]
    ]

    gradient_layout = [
        [sg.Text('Generate a gradiated line test')],
        [sg.Text('Start position'), sg.Text('X:'), sg.Spin([i for i in range(1,MAX)],initial_value=110, k='G_X'),
                                    sg.Text('Y:'), sg.Spin([i for i in range(1,MAX)],initial_value=110, k='G_Y'),
                                    sg.Text('Z:'), sg.Spin([i for i in range(1,MAX)],initial_value=2, k='G_Z')],
        [sg.Text('Line length (mm)'), sg.Input(key='G_LENGTH')],
        [sg.Text('Total number of gradient steps'), sg.Input(key = 'G_STEPS')],
        [sg.Text('Test style'), sg.Combo(values=('Constant speed', 'Constant flow rate', 'Constant volume'), default_value='Constant speed', readonly=True, k='STYLE')],
        [sg.Text('Constant value (mm/s)'), sg.Input(key = 'CONST')],
        [sg.Text('Initial value (mm/s)'), sg.Input(key = 'INIT')],
        [sg.Text('Final value (mm/s)'), sg.Input(key = 'FINAL')],
        [sg.Text('Movement axis'), sg.Radio('X axis', "RADIO2", default=True, size=(10,1), k='X2'), sg.Radio('Y axis', "RADIO2", size=(10,1), k='Y2')],
        [sg.Button('Generate', key = "gengrad"), sg.Button('Close', key = 'G_CLOSE')]
    ]

    about_layout = [
        [sg.Text('About each test:')],
        [sg.Button('Line test', key = 'LINE'), sg.Button('Circle test', key = "CIRC"), sg.Button('Gradiated test', key = "GRAD")],
        [sg.Text('Created for the Santanalab 3D bioprinter project')],
        [sg.Text("Made with love by Alex Martin (HMC '25) <3")],
        [sg.Button('Close', key = 'A_CLOSE')]
    ]

    layout = [[sg.Text('SantanaLab Parameterization Platform', size=(38, 1), justification='center', font=("Helvetica", 16), relief=sg.RELIEF_RIDGE, k='-TEXT HEADING-')]] 
    layout += [[sg.TabGroup([[sg.Tab('Line test', line_layout), sg.Tab('Circle test', circle_layout), sg.Tab('Gradiated test', gradient_layout), sg.Tab('About', about_layout)]])]] #combine subpages in tabs
    window = sg.Window("Santanalab P.P.", layout)
    return window

def main():
    ''' Creates and runs the parameterization GUI'''
    window = make_window() #creates the window

    while True: #Detects user inputs. If a generate button is pressed, it loads the values into the corresponding function to generate a gcode
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'L_CLOSE' or event == 'C_CLOSE' or event == 'G_CLOSE' or event == 'A_CLOSE':
            break
        if event == 'genline':
            if(lineError(values)):
                startPos = ["G0 ", "X" + str(values['L_X']) + ' ', "Y" + str(values['L_Y']) + ' ', "Z" + str(values['L_Z'])]
                header = ["G21", "G90", "M83", "", "G28","G0 F1000", ''.join(startPos),"T0", 'G4 S2', " "]
                if (values['X1'] == True):
                    axis = "X"
                else:
                    axis = "Y"
                genLine(float(values['L_LENGTH']), -float(values['L_EXTRUDE_RATE']), float(values["L_MOVE_RATE"]), axis, header, startPos)
                sg.popup("File generated!", keep_on_top=True)

        if event == 'gencircle':
            if (circleError(values)):
                startPos = ["G0 ", "X" + str(values['C_X']) + ' ', "Y" + str(values['C_Y']) + ' ', "Z" + str(values['C_Z'])]
                header = ["G21", "G90", "M83", "", "G28","G0 F1000",''.join(startPos),"T0", 'G4 S2', " "]
                genCircle(float(values['RADIUS']), -float(values['C_EXTRUDE_RATE']), float(values["C_MOVE_RATE"]), header, startPos)
                sg.popup("File generated!", keep_on_top=True)

        if event == 'gengrad':
            if(gradError(values)):
                startPos = ["G0 ", "X" + str(values['G_X']) + ' ', "Y" + str(values['G_Y']) + ' ', "Z" + str(values['G_Z'])]
                header = ["G21", "G90", "M83", "", "G28","G0 F1000",''.join(startPos),"T0", 'G4 S2', " "]
                if (values['X1'] == True):
                    axis = "X"
                else:
                    axis = "Y"
                genGradient(int(values['G_STEPS']), float(values['G_LENGTH']), float(values['INIT']), float(values['FINAL']), float(values['CONST']), header, axis, values['STYLE'], startPos)
                sg.popup("File generated!", keep_on_top=True)

        if event == "LINE":
            sg.popup('Produces a line of user set length, flow rate, and movement rate.',
                        'Axis determines the positive direction of movement from the starting point.',
                        'Serves as a basic test for combined movement and extrusion.',
                        keep_on_top=True)
        if event == "CIRC":
            sg.popup('Produces a circle of user set radius, flow rate, and movement.',
                        'Enables the testing of more complex shape-specific movements.',
                        keep_on_top = True)
        if event == "GRAD":
            sg.popup('Produces a line of set length, where either flow rate or movement rate increments over an input number of intervals.',
                        'The constant value can be either flow rate or movement rate, with the initial and final values being the non-constant variable.',
                        'Constant volume also has a varied speed, but extrudes a constant volume over each segment - determined by the set flow rate.', 
                        keep_on_top = True)
        
    window.close()

main()