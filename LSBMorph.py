import shutil
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from numpy import append, where, random, percentile, zeros,logical_not, array
from matplotlib.pyplot import close
import matplotlib.patches as patches
from PIL import Image, ImageTk
import os, time, webbrowser
from astropy.io import fits
from astropy.table import Table, vstack, unique

################################# input ##################################
galaxiesList = ''                         # where do you store galaxies to classify
##########################################################################
user = 1000

secondGalaxiesListOnline = '/run/user/%i/gvfs/sftp:host=10.107.0.229,user=kidslsbs/data02/Hareesh/KiDS/LSB_search/catalogs/Galfit_versions/All_candidates_r_2.fits'%user
secondGalaxiesList = ''                   # where do you store galaxies with 2nd fit
kidsDataOnline = '/run/user/%i/gvfs/sftp:host=10.107.0.229,user=kidslsbs/data02/Hareesh/KiDS/LSB_search'%user
kidsData = ''                             # where do you store images
colorsForPlots = ['viridis', 'red','black']
# some random IDs which look cool
interestingIDs = ['KiDSDR4_J001706.317-334825.57',
                  'KiDSDR4_J000813.589-343441.84',
                  'KiDSDR4_J005225.587-311218.74',
                  'KiDSDR4_J002142.794-323509.57',
                  'KiDSDR4_J005302.514-311157.22',
                  'KiDSDR4_J000815.233-345246.72',
                  'KiDSDR4_J001710.948-342918.25',
                  'KiDSDR4_J003918.218-324602.08',
                  'KiDSDR4_J003258.146-324548.75',
                  'KiDSDR4_J003050.509-301715.66',
                  'KiDSDR4_J003638.246-323426.78',
                  'KiDSDR4_J005231.063-311109.89',
                  'KiDSDR4_J005300.012-311028.58',
                  'KiDSDR4_J225640.861-351345.62',
                  'KiDSDR4_J140056.768-011232.46',
                  'KiDSDR4_J124323.711+012439.06',
                  'KiDSDR4_J113023.156+025029.39',
                  'KiDSDR4_J133250.440-002730.74',
                  'KiDSDR4_J031652.484-353155.40',
                  'KiDSDR4_J104527.395-025755.52']
#### Group of basic/simple function ####
def save_when_close():
    """
    Function for closing
    """
    root.destroy()
def openAladin():
    global ind, indNow
    """
    Function used to open Aladin website with centered galaxy
    """
    ra = kidsTable[indNow]['ra']
    dec = kidsTable[indNow]['dec']
    url = "https://aladin.unistra.fr/AladinLite/?target=%.5f %.5f&fov=0.1"%(ra, dec)
    webbrowser.open(url)
def onEnter(event):
    findNext()
def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"
def saveSmall():
    global newWindowRemake
    newWindowRemake.destroy()
def intput_cat(event):
    """
    Function for opening directories browser
    Used only as a reaction to the event variable
    """
    global kidsData, galaxiesList,person_name, secondGalaxiesList

    if person_name == '':
        # Finding the begining point for the browser
        path_start = os.getcwd()

        # Oppening the browser
        # Result variable is path to the directory
        if event.widget == buttonBrowseFiles:
            filename = tk.filedialog.askdirectory(initialdir=path_start,
                                               title="Select a Directory", )
            if len(filename) != 0:
                entryData.configure(state = 'normal')

                entryData.delete(0, tk.END)
                kidsData = filename
                if len(filename)>30:
                    tt = '../%s'%(filename.split('/')[-1])
                    entryData.insert(tk.END, tt)
                else:
                    entryData.insert(tk.END, filename)

                entryData.configure(state = 'disabled')
        elif event.widget == buttonFindCatalog:
            filename = tk.filedialog.askopenfilename(initialdir=path_start,
                                                  title="Select a Directory", )
            if len(filename) != 0:
                entryCatalog.configure(state = 'normal')

                entryCatalog.delete(0, tk.END)
                galaxiesList = filename
                if len(filename) > 30:
                    tt = '../%s' % (filename.split('/')[-1])
                    entryCatalog.insert(tk.END, tt)
                else:
                    entryCatalog.insert(tk.END, filename)

                entryCatalog.configure(state = 'disabled')
        elif event.widget == buttonFind2ndCatalog:
            filename = tk.filedialog.askopenfilename(initialdir=path_start,
                                                  title="Select a Directory", )
            if len(filename) != 0:
                entryFind2ndCatalog.configure(state = 'normal')

                entryFind2ndCatalog.delete(0, tk.END)
                secondGalaxiesList = filename
                if len(filename) > 30:
                    tt = '../%s' % (filename.split('/')[-1])
                    entryFind2ndCatalog.insert(tk.END, tt)
                else:
                    entryFind2ndCatalog.insert(tk.END, filename)

                entryFind2ndCatalog.configure(state = 'disabled')
    else:
        entry.delete(0, tk.END)
        makeInputButtons()
        person_name = ''
        secondGalaxiesList = ''
        kidsData = ''
    return 'break'
def dataStorage():
    if not checkboxDataStorage_var.get():
        buttonFind2ndCatalog.grid(row=3, column=6, columnspan=2, sticky="ew", padx=5, pady=5)
        entryFind2ndCatalog.grid(row=3, column=8, columnspan=2, sticky="ew", padx=5, pady=5)
        buttonBrowseFiles.grid(row=4, column=6, columnspan=2, sticky="ew", padx=5, pady=5)
        entryData.grid(row=4, column=8, columnspan=2, sticky="ew", padx=5, pady=5)
    else:
        buttonBrowseFiles.grid_forget()
        buttonFind2ndCatalog.grid_forget()
        entryData.grid_forget()
        entryFind2ndCatalog.grid_forget()

#### Used only once at the start ####
def newWindowError(message = ''):
    newWindowError = tk.Toplevel(root)
    newWindowError.title("Error!")
    if message == '':
        war = tk.Label(newWindowError, text='There is some problem!\nI dont see where :(',
                       font=("Arial", 20))
    else:
        war = tk.Label(newWindowError, text='There is some problem!\n%s'%message,
                       font=("Arial", 20))
    #newWindowError.geometry("%ix%i" % (400, 200))
    war.grid(row=0, column=0, columnspan=1, sticky="ew", padx=20, pady=1)
def prepareTable():
    """
    This function prepares or opens the table with results results

    """
    global previousTable, table_path, ind, numberAll, kidsTable, secondGalaxiesList, \
        kidsData, galaxiesList, secondGalaxiesListOnline, kidsDataOnline, secondGalaxiesListData, colorsForPlots
    # get the name
    person_name = entry.get()

    # Check if the entries are complete
    if person_name == '':
        newWindowError('What\'s your name?')
        return
    # Do you have connection to the VPN
    if checkboxDataStorage_var.get():
        #sometimes the user ip can be different, check if it works now
        if os.path.exists(kidsDataOnline + '/r_imgblocks'):
            user = 1000
            while user<1050:
                test = '/run/user/%i/gvfs/sftp:host=10.107.0.229,user=kidslsbs/data02/Hareesh/KiDS/LSB_search' % user
                if os.path.exists(test + '/r_imgblocks'):
                    secondGalaxiesListOnline = '/run/user/%i/gvfs/sftp:host=10.107.0.229,user=kidslsbs/data02/Hareesh/KiDS/LSB_search/catalogs/Galfit_versions/All_candidates_r_2.fits' % user
                    secondGalaxiesList = ''  # where do you store galaxies with 2nd fit
                    kidsDataOnline = '/run/user/%i/gvfs/sftp:host=10.107.0.229,user=kidslsbs/data02/Hareesh/KiDS/LSB_search' % user
                    break
                user +=1


        if (not os.path.exists(kidsDataOnline + '/r_imgblocks')
                or not os.path.exists(secondGalaxiesListOnline)):
            newWindowError('Are you sure you are connected to VPN and the LSB computer?')
            return

        # If VPN is correct, set the variables
        kidsData = kidsDataOnline
        secondGalaxiesList = secondGalaxiesListOnline

    # Check data storage
    if kidsData == "" or not os.path.exists(kidsData + '/r_imgblocks'):
        newWindowError('Where is your directory containing data?\n(The one that we should give you)')
        return
    # Check catalogue path
    if galaxiesList == '' or not os.path.exists(galaxiesList):
        newWindowError('Where is your catalogue?\n(The one that we should give you)')
        return
    # Check 2nd catalogue path
    if secondGalaxiesList == '' or not os.path.exists(secondGalaxiesList):
        newWindowError('Where is your 2nd catalogue?\n(The one that we should give you)')
        return

    # Check if files are valid
    try:
        kidsTable = fits.open(galaxiesList)[1].data
    except Exception as err:
        newWindowError('Wrong path to the galaxy catalogue!\n%s' % err)
        return

    try:
        secondGalaxiesListData = fits.open(secondGalaxiesList)[1].data
    except Exception as err:
        newWindowError('Wrong path to the 2nd galaxy catalogue!\n%s'%err)
        return



    ### Remove unused part ###
    buttonStart.grid_forget()    # start is not needed
    entry_label.grid_forget()    # entry is changed
    checkboxDataStorage.grid_forget()
    buttonFindCatalog.grid_forget()
    entryCatalog.grid_forget()
    buttonDataStorage.grid_forget()
    if not checkboxDataStorage_var.get():
        buttonBrowseFiles.grid_forget()
        buttonFind2ndCatalog.grid_forget()
        entryFind2ndCatalog.grid_forget()
        entryData.grid_forget()
    newentry1_label = tk.Label(top_frame, text="Is it LSB?", font=("Arial", 20))
    newentry1_label.grid(row=0, column=0, columnspan=1, sticky="w", padx=5, pady=5)  # Use 2 parts for the label
    newentry2_label = tk.Label(top_frame, text="Morphology Type", font=("Arial", 20))
    newentry2_label.grid(row=0, column=1, columnspan=1, sticky="w", padx=5, pady=5)  # Use 2 parts for the label
    entry.grid_forget()
    ### Build the bottom part ###
    nameLabel = tk.Label(top_frame, text=person_name, font=("Arial", 20))       # change to not not changable
    nameLabel.grid(row=0, column=3, columnspan=2, sticky="ew", padx=5, pady=5)

    # checkboxes visible
    checkbox11.grid(row=1, column=0, columnspan=1, padx=5, pady=4, sticky="w")
    checkbox12.grid(row=2, column=0, padx=5, pady=4, sticky="w")
    checkbox13.grid(row=3, column=0, padx=5, pady=4, sticky="w")
    checkbox21.grid(row=1, column=1, columnspan=1, padx=5, pady=4, sticky="w")
    checkbox22.grid(row=2, column=1, padx=5, pady=4, sticky="w")
    checkbox23.grid(row=3, column=1, padx=5, pady=4, sticky="w")
    checkbox24.grid(row=4, column=1, padx=5, pady=4, sticky="w")
    checkbox14Redshift.grid(row=4, column=0, padx=5, pady=4, sticky="w")
    buttonAwesome.grid(row=4, column=9, columnspan=1, sticky="ew", padx=5, pady=1)

    # buttons visible
    buttonNext.grid(row=1, column=7, columnspan=1, sticky="ew", padx=5, pady=1)
    buttonPrevious.grid(row=2, column=7, columnspan=1, sticky="ew", padx=5, pady=1)
    buttonSkip.grid(row=3, column=7, columnspan=1, sticky="ew", padx=5, pady=1)
    buttonAladin.grid(row=4, column=7, columnspan=1, sticky="ew", padx=5, pady=1)
    #buttonWeird.grid(row=3, column=9, columnspan=1, sticky="ew", padx=5, pady=1)
    buttonExamples.grid(row=2, column=9, columnspan=1, sticky="ew", padx=5, pady=1)

    # other widgets visible
    comment_label.grid(row=3, column=3, columnspan=2, sticky="ew", padx=5, pady=1)
    comments.grid(row=4, column=3, columnspan=2, sticky="ew", padx=5, pady=1)
    morphByText_Label.grid(row=1, column=3, columnspan=2, sticky="ew", padx=5, pady=1)
    morphByText_Entryl.grid(row=2, column=3, columnspan=2, sticky="ew", padx=5, pady=1)

    # make progress_barr visible
    progress_barr.grid(row=1, column=8, columnspan=1, rowspan = 4, sticky="ns", padx=5, pady=1)
    procentege_label.grid(row=0, column=8, columnspan=1, rowspan = 1, sticky="", padx=5, pady=1)
    # focus on the input
    morphByText_Entryl.focus_set()

    # find the table
    table_path = 'vis_inspect_%s.fits'%person_name
    remoteTable = None

    if kidsData == kidsDataOnline:
        try:
            remoteTable = Table.read(kidsData + '/VisualInspectionResults/' + table_path)
        except: pass

    if os.path.exists(table_path):
        previousTable = Table.read(table_path)
        previousTable = previousTable["ID", "Class", "Morphology", "Comments", 'Sky_Bkg', "Date_of_classification", "AwesomeFlag", "ValidRedshift"]
        if remoteTable != None:
            previousTable = vstack(previousTable, remoteTable)
            previousTable = unique(previousTable, keep='first')
    else:
        if remoteTable != None:
            previousTable = remoteTable
        else:
            previousTable = Table(names=["ID", "Class", "Morphology", "Comments", 'Sky_Bkg', "Date_of_classification", "AwesomeFlag", "ValidRedshift"],
                              dtype=["str", "i8", "i8", "str", "str","str", "i8", "i8"])
        previousTable.write(table_path, overwrite = True)
        if kidsData == kidsDataOnline:
            previousTable.write(kidsData + '/VisualInspectionResults/' + table_path, overwrite = True)



    kidsTable = fits.open(galaxiesList)[1].data
    numberAll = len(kidsTable)
    # get the old IDs
    for gal in previousTable:
        i = where(kidsTable['ID'] == gal['ID'])[0][0]
        ind = append(ind, [i])

    otherInfoPath = 'dataPath_%s.txt'%person_name
    otherInfoPath = open(otherInfoPath, 'w')
    otherInfoPath.write('%s\n%s\n%s\n%s' % (kidsData, galaxiesList, secondGalaxiesList,' '.join(colorsForPlots)))
    otherInfoPath.close()

    # update the progress barr
    procVar.set('%i'%((len(previousTable))/numberAll * 100) + '%')
    progress_barr["value"] = (len(previousTable))/numberAll * 100  # Update the progress bar value
    progress_barr.update()  # Refresh the progress bar
    doneNumber.set('Done ' + str(len(previousTable)) + ' of '+str(numberAll))
    doneLabel.grid(row = 0, column = 7, columnspan = 1, sticky="ew", padx=5, pady=1)


    findNext(firstTime = True)

#### Used only when help needed ####
def helpMe(event):
    global newWindowHelp, tipNumber, canvasForCircles, ccs, hints,dsHints
    tipNumber = 0
    ccs = []
    newWindowHelp = tk.Toplevel(root)
    if event.widget == buttonHelp:
        newWindowHelp.title("Help!")
        war = tk.Label(newWindowHelp, text='Here are some important hints for how to use this tool!', font=("Arial", 20))
        try:
            hints
        except:
            hints = len(os.listdir('Tips'))
            hints = ['Tips/%i.png' % f for f in range(hints - 2)]
            hints = [Image.open(f) for f in hints]
            #hints = [f.crop((0, 0, 1148, 630)) for f in hints]
        nCircles = len(hints)
        tipsHere = hints
    elif event.widget == buttonDataStorage:
        newWindowHelp.title("Data storage connection")
        war = tk.Label(newWindowHelp, text='Here are Ubuntu based hints for connecting to the data storage!', font=("Arial", 20))
        try:
            dsHints
        except:
            dsHints = len(os.listdir('Tips/Connection'))
            dsHints = ['Tips/Connection/%i.png' % f for f in range(dsHints)]
            dsHints = [Image.open(f) for f in dsHints]
            #dsHints = [f.crop((0, 0, 1148, 630)) for f in dsHints]
        tipsHere = dsHints
        nCircles = len(dsHints)
    elif event.widget == buttonExamples:
        newWindowHelp.title("Hard decisions")
        war = tk.Label(newWindowHelp, text='It is not trivial to classify morphologies of galaxies.\nThat\'s why we need you!',
                       font=("Arial", 20))
        try:
            eHints
        except:
            eHints = len(os.listdir('Tips/Examples'))
            eHints = ['Tips/Examples/%i.png' % f for f in range(eHints-1)]
            eHints = [Image.open(f) for f in eHints]
        tipsHere = eHints
        nCircles = len(eHints)
    newWindowHelp.geometry("%ix%i" % (1000, 600))
    war.grid(row=0, column=1, columnspan=1, sticky="ew", padx=20, pady=1)
    newWindowHelp.grid_columnconfigure(1, weight=1, minsize=800)


    b1 = tk.Button(newWindowHelp, text='<', font=("Arial", 20), command=lambda n = -1: showTip(n, nCircles, tipsHere))
    b1.grid(row=1, column=0, columnspan=1, sticky="nsew", padx=5, pady=1)
    b2 = tk.Button(newWindowHelp, text='>', font=("Arial", 20), command=lambda n = +1: showTip(n, nCircles, tipsHere))
    b2.grid(row=1, column=2, columnspan=1, sticky="nsew", padx=5, pady=1)



    canvasForCircles = tk.Canvas(newWindowHelp)
    x0 = 0
    xk = 940
    r = 15
    dx = (xk-x0)/(nCircles+2)
    y0 = 3
    for i in range(nCircles):
        circle = canvasForCircles.create_oval(x0 + (i+1)*dx, y0, x0+ (i+1)*dx+r, y0 + r, outline="grey", width=3)
        ccs.append(circle)
    canvasForCircles.grid(row = 2, column = 1, sticky = 'ew')

    showTip(0, nCircles, tipsHere)
def showTip(n, nmax, tipsHere):
    global tipNumber, newWindowHelp, canvasForCircles, ccs
    if n + tipNumber==nmax:
        tipNumber=len(tipsHere)-1
        return
    elif n + tipNumber<0:
        tipNumber = 0
        return
    else:
        canvasForCircles.itemconfig(ccs[tipNumber], fill = '', outline="grey", width=3)
        tipNumber += n

    imHere = tipsHere[tipNumber]
    fig = Figure(dpi=100)
    ax = fig.add_axes([0, 0, 1,1])
    ax.imshow(imHere)
    ax.set_yticks([], [])
    ax.set_xticks([], [])
    canvas = FigureCanvasTkAgg(fig, master=newWindowHelp)
    canvas.draw()
    canvas.get_tk_widget().grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
    canvasForCircles.itemconfig(ccs[tipNumber], fill = rgb_to_hex(200, 120, 120), outline="black", width=5)
    canvas.mpl_connect("scroll_event", on_scroll)  # Zoom with scroll wheel
    canvas.mpl_connect("button_press_event", on_click)  # Start dragging on click
    canvas.mpl_connect("motion_notify_event", on_motion)  # Drag on motion
    canvas.mpl_connect("button_release_event", on_release)  # Stop dragging on releas
    return
def setColors():
    global newWindowColors, entry_c1,entry_c2,entry_c3, colorsForPlots
    newWindowColors = tk.Toplevel(root)
    newWindowColors.title("Error!")
    war = tk.Label(newWindowColors, text='Set the colors! Names exactly the same as in python\nviridis, plasma, magma, etc\nred, blue, black etc.',
                       font=("Arial", 20))
    war.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=1)

    entry_c1 = tk.Entry(newWindowColors, font=("Arial", 20))
    entry_c1.grid(row=1, column=0, columnspan=1, sticky="ew", padx=5, pady=5)
    entry_c1.delete(0, tk.END)
    entry_c1.insert(tk.END, colorsForPlots[0])
    label_c1 = tk.Label(newWindowColors, text="Cmap for galaxy images", font=("Arial", 20))
    label_c1.grid(row=1, column=1, columnspan=1, sticky="w", padx=5, pady=5)

    entry_c2 = tk.Entry(newWindowColors, font=("Arial", 20))
    entry_c2.grid(row=2, column=0, columnspan=1, sticky="ew", padx=5, pady=5)
    entry_c2.delete(0, tk.END)
    entry_c2.insert(tk.END, colorsForPlots[1])
    label_c2 = tk.Label(newWindowColors, text="Color for galaxy model", font=("Arial", 20))
    label_c2.grid(row=2, column=1, columnspan=1, sticky="w", padx=5, pady=5)

    entry_c3 = tk.Entry(newWindowColors, font=("Arial", 20))
    entry_c3.grid(row=3, column=0, columnspan=1, sticky="ew", padx=5, pady=5)
    entry_c3.delete(0, tk.END)
    entry_c3.insert(tk.END, colorsForPlots[2])
    label_c3 = tk.Label(newWindowColors, text="Color for Redshift point", font=("Arial", 20))
    label_c3.grid(row=3, column=1, columnspan=1, sticky="w", padx=5, pady=5)

    buttonSet = tk.Button(newWindowColors, text = 'Set colors', font=("Arial", 20), command=setForReal)
    buttonSet.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
def setForReal():
    global newWindowColors, entry_c1,entry_c2,entry_c3, colorsForPlots, kidsData, galaxiesList, secondGalaxiesList
    fig = Figure()
    ax = fig.add_axes([0,0,1,1])
    try:
        ax.scatter([1,2],[1,2], c = [1,2], cmap = entry_c1.get())
    except:
        newWindowError('Wrong cmap name!')
        return
    try:
        ax.scatter([1,2],[1,2], c=entry_c2.get())
    except:
        newWindowError('Wrong galaxy model color name!')
        return
    try:
        ax.scatter([1,2],[1,2], c = entry_c3.get())
    except:
        newWindowError('Wrong redshift point color name!')
        return
    close(fig)
    colorsForPlots = [entry_c1.get(), entry_c2.get(), entry_c3.get()]
    otherInfoPath = 'dataPath_%s.txt'%person_name
    otherInfoPath = open(otherInfoPath, 'w')
    otherInfoPath.write('%s\n%s\n%s\n%s' % (kidsData, galaxiesList, secondGalaxiesList,' '.join(colorsForPlots)))
    otherInfoPath.close()
    newWindowColors.destroy()
#### Show different galaxy ####
def findNext(firstTime = False):
    global ind, indNow, kidsTable, attempt1
    """
    This function finds the next galaxy to classify
    """
    # if its the first galaxy get random
    # Check first if the previous one is finished
    if len(ind)>0 and not firstTime:

        # save last results
        # if not valid, make a popup
        notFinished, problemGalaxy = makeEntry(kidsTable[indNow]['ID'])

        if notFinished or problemGalaxy:
            if notFinished:
                newWindow = tk.Toplevel(root)
                newWindow.title("Warning!")
                newWindow.geometry("300x150")
                war = tk.Label(newWindow, text='You did not finish\nthis galaxy!', font=("Arial", 20))
                war.pack(fill=tk.BOTH, expand=1)
            else:
                gal2 = where(secondGalaxiesListData['ID'] == kidsTable[indNow]['ID'])[0][0]
                gal2 = secondGalaxiesListData[gal2]
                make6figures(gal2)
            return

        # reset checkboxes
        resetCheckboxes()
        attempt1 = True


        # if nothing happend, find new random entry
        if ind[-1] == indNow:
            indNow = findNewInd()
            ind = append(ind, [indNow])
        # if you went back, now go forward, for the same galaxy
        else:
            i = where(ind == indNow)[0]
            if len(i) >0:
                indNow = ind[i + 1][0]
                updateOnChange()
            else:
                indNow = findNewInd()
    else:
        # find new random entry
        indNow = findNewInd()
        ind = append(ind, [indNow])

    # prepare images
    make6figures(kidsTable[indNow])

    # go back to active widget
    entry.config(state="normal")  # Make the Entry widget active
    entry.focus_set()  # Set focus to the Entry widget

    # update progress bar
    if (len(ind)-1)/numberAll < 1:
        procVar.set('%i'%((len(ind)-1)/numberAll * 100) + '%')
        progress_barr["value"] = (len(ind)-1)/numberAll * 100  # Update the progress bar value
        doneNumber.set('Done ' + str(len(previousTable)) + ' of '+str(numberAll))
        progress_barr.update()  # Refresh the progress bar
    else:
        newWindow = tk.Toplevel(root)
        newWindow.title("Done")
        newWindow.geometry("300x150")
        war = tk.Label(newWindow, text='You finished!', font=("Arial", 20))
        war.pack(fill=tk.BOTH, expand=1)
def findPrevious(name = ''):
    global ind, indNow, attempt1
    """
    If you want to see the previous anwser
    """
    # if there is no previous, pass
    if len(ind) < 2:
        return
    else:
        # start with finding current one
        i = where(ind == indNow)[0]

        notFinished, problemGalaxy = makeEntry(kidsTable[indNow]['ID'])
        if notFinished:
            ind = ind[0:-1]
        # find previous one
        indNow = ind[i-1][0]
        # remove old entrys
        updateOnChange()
    # show the galaxy
    make6figures(kidsTable[indNow])
def skip(name = ''):
    global ind, indNow, attempt1
    attempt1 = True

    """function used to skip current galaxy"""
    morphByText_Entryl.delete(0, tk.END)
    comments.delete(0, tk.END)
    if len(ind) > 1:
        ind = ind[0:-1]
    elif len(ind) == 1:
        ind = array([]).astype(int)
    else: return

    if name == '':
        ind = append(ind, [random.randint(0, numberAll)])
    else:
        i = where(kidsTable['ID'] == interestingIDs[random.randint(0, len(interestingIDs))])[0]
        if len(i) == 0: return
        ind = append(ind, i)
    resetCheckboxes()
    indNow = ind[-1]
    make6figures(kidsTable[indNow])
def make6figures(gal):
    """
    :param gal: Entry from the input table
    :return:
    """
    global attempt1
    # Get the ID
    name = gal['ID']
    print(name)
    ### Open images ###

    # start with Galfit
    if gal['Nucleus'] == 1:
        var = 'double'
    else:
        var = 'single'

    if attempt1:
        imgblock = fits.open(kidsData + '/r_imgblocks/%s_component/imgblock_%s.fits'%(var, name))
    else:
        imgblock = fits.open(kidsData + '/r_imgblocks/%s_component_unmasked/imgblock_%s.fits'%(var, name))

    # now mask
    try:
        mask = fits.getdata(kidsData + '/masks_r/mask%s.fits'%name)
        mask = imgblock[1].data * logical_not(mask) * one_jansky_arcsec_kids
        vmax = percentile(mask, 99)
    except:
        mask = zeros([200,200])
        vmax = percentile(imgblock[1].data * one_jansky_arcsec_kids, 99)
    # Names of the titles
    axisNames = ['Masked r-Band', 'GalfitModel', 'Residual', 'Raw r-band', 'APLpy', 'Zoomed out']

    # Contrast
    vmax = [vmax, vmax, vmax, percentile(imgblock[1].data * one_jansky_arcsec_kids, 99.7), 0, 0]

    # list of images
    images = [mask,
              imgblock[2].data * one_jansky_arcsec_kids,
              imgblock[3].data * one_jansky_arcsec_kids,
              imgblock[1].data * one_jansky_arcsec_kids,
              Image.open(kidsData + '/color_images/aplpy/' + name + '.png').transpose(Image.FLIP_TOP_BOTTOM),
              Image.open(kidsData + '/color_images/Lupton_RGB_Images/' + name + '.png')]
    ny = 0

    for i in range(6):
        if i == 3: ny+=1
        # Make new figure
        fig = Figure(dpi=100)
        ax = fig.add_axes([0,0,1,yAxis])

        # make image
        if i < 4:
            ax.imshow(images[i], vmax = vmax[i], cmap = colorsForPlots[0])
        else:
            ax.imshow(images[i], vmax = vmax[i])

        ax.set_yticks([], [])
        ax.set_xticks([], [])

        # If its galfit, show the ellipse
        if i <3:

            ellipse = patches.Ellipse(
                (gal['X'], gal['Y']),
                width=(gal['r_r'] * 2 / 0.2),
                height=(gal['r_r'] * 2 / 0.2) * gal['q'],
                angle=gal['PA'] + 90, linewidth=1.5,
                color=colorsForPlots[1], fill=False, linestyle='-', label='Modelled galaxy'
            )

            ax.add_patch(ellipse)
            ax.legend(handles=[ellipse])

        if i == 3:# and gal['Z'] >0:
            #try:
                ax.plot([gal['X'], gal['RedshiftX']], [gal['Y'], gal['RedshiftY']], lw = 2, ls = '--', c = 'k')
                ax.scatter(gal['RedshiftX'], gal['RedshiftY'], c = colorsForPlots[2], marker = 'x', s = 150)
            # except:
            #     ax.plot([gal['X'], redshiftX], [gal['Y'], redshiftY], lw = 2, ls = '--', c = colorsForPlots[2])
            #     ax.scatter(redshiftX, redshiftY, c = 'k', marker = 'x', s = 150)

        # set title
        ax.set_title(axisNames[i])

        # Draw the canvas on the window
        canvas = FigureCanvasTkAgg(fig, master=bottom_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=ny, column=i%3, padx=10, pady=10, sticky="nsew")
        # Bind events to the canvas
        canvas.mpl_connect("scroll_event", on_scroll)  # Zoom with scroll wheel
        canvas.mpl_connect("button_press_event", on_click)  # Start dragging on click
        canvas.mpl_connect("motion_notify_event", on_motion)  # Drag on motion
        canvas.mpl_connect("button_release_event", on_release)  # Stop dragging on releas
def findNewInd():
    global ind, indNow
    if len(ind) == numberAll:
        procVar.set('%i' % ((len(ind)) / numberAll * 100) + '%')
        progress_barr["value"] = (len(ind)) / numberAll * 100  # Update the progress bar value
        doneNumber.set('Done ' + str(len(previousTable)) + ' of ' + str(numberAll))
        progress_barr.update()  # Refresh the progress bar
        return 0
    while True:
        indNow = random.randint(0, numberAll)
        if len(where(ind == indNow)[0]) == 0:
            break
    return indNow

#### Save the results ####
def makeEntry(name):
    """
    :param name: ID of the galaxy
    :return: if entry was done Fasle, else True
    """
    global newWindowRemake, previousTable, kidsData, galaxiesList, attempt1,kidsDataOnline

    # time of the entry
    tNow = time.strftime("%Y/%m/%d-%H:%M")

    # check if the checkboxes are correct
    if (checkbox11_var.get() or checkbox12_var.get() or checkbox13_var.get()) and\
        (checkbox21_var.get() or checkbox22_var.get() or checkbox23_var.get() or checkbox24_var.get()):

        if checkbox11_var.get() and attempt1:
            attempt1 = False
            return False, True
        else:
            # get correct type
            if checkbox11_var.get(): x = -1
            elif checkbox12_var.get(): x = 0
            else: x = 1

            # get correct morphology
            if checkbox21_var.get(): mor = -1
            elif checkbox22_var.get(): mor = 0
            elif checkbox23_var.get(): mor = 1
            else: mor = 2

            if checkboxAwesome_var.get():
                awesomeFlag = 1
            else:
                awesomeFlag = 0

            if checkbox14Redshift_var.get():
                redshiftFlag = 1
            else:
                redshiftFlag = 0

            # check if it was done already
            i = where(previousTable['ID'] == name)[0]
            if len(i)>0:
                previousTable = previousTable[where(previousTable['ID'] != name)[0]]

            # add the row to the table
            if attempt1 == True:
                previousTable.add_row([name, x,mor, comments.get(),'un_masked', tNow, awesomeFlag, redshiftFlag])
            else:
                previousTable.add_row([name, x,mor, comments.get(),'masked', tNow, awesomeFlag, redshiftFlag])


            previousTable.write(table_path, overwrite = True)
            if kidsData == kidsDataOnline:
                previousTable.write(kidsData + '/VisualInspectionResults/' + table_path, overwrite=True)

            # remove old input
            morphByText_Entryl.delete(0, tk.END)
            comments.delete(0, tk.END)
            return False, False
    else:
        return True, True

#### Zoom in/out ####
def on_click(event):
    global drag_start
    """
    This function is used to calculate the position of the mouse during the dragging
    """
    # check if the click was in the axis
    if event.inaxes is not None:
        # size of the canvas
        width, height = event.canvas.get_width_height()

        # position of the click on the canvas
        x = event.x
        y = event.y

        # from 0 to 1
        xClick = x/width
        yClick = y/height/yAxis          # 0.9 from the axis ratio

        drag_start = (xClick,yClick)  # Store the initial click position
def on_motion(event):
    global drag_start
    """
    This function is used to change the position of the image during dragging
    """
    if drag_start is None or event.inaxes is None:
        return  # Ignore if dragging didn't start or cursor is not over an axes

    # size of the canvas
    width, height = event.canvas.get_width_height()
    # position of the click on the canvas
    x = event.x
    y = event.y

    # which axis
    ax = event.inaxes

    # get change of the xlim
    xlim = ax.get_xlim()
    xRange = abs(xlim[1] - xlim[0])
    xClick = x / width
    x0 = xRange*drag_start[0]
    xk = xRange*xClick
    dx = xk-x0

    # get change of the ylim
    ylim = ax.get_ylim()
    yRange = abs(ylim[1] - ylim[0])
    yClick = y / height / yAxis
    y0 = yRange * drag_start[1]
    yk = yRange * yClick
    dy = yk - y0

    # sert new lim
    ax.set_xlim(xlim[0] - dx, xlim[1] - dx)
    ax.set_ylim(ylim[0] + dy, ylim[1] + dy)

    event.canvas.draw()

    # update last position
    xClick = x / width
    yClick = y / height / yAxis

    drag_start = (xClick, yClick)  # Store the initial click position
def on_release(event):
    """
    This function is used when stop dragging
    """
    global drag_start
    drag_start = None  # Reset the drag start position
    event.canvas.draw()  # Ensure the final state is drawn
def on_scroll(event):
    """
    This is used during zoom-in/out
    Get from DeepSeek
    """
    if event.inaxes is None:
        return  # Ignore if the cursor is not over an axes

    scale_factor = 1.1 if event.button == "up" else 0.9  # Zoom in or out
    ax = event.inaxes  # Get the axes where the event occurred

    # Get current x and y limits
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    # Calculate new limits based on the scroll direction
    new_xlim = [
        xlim[0] + (event.xdata - xlim[0]) * (1 - scale_factor),
        xlim[1] + (event.xdata - xlim[1]) * (1 - scale_factor),
    ]
    new_ylim = [
        ylim[0] + (event.ydata - ylim[0]) * (1 - scale_factor),
        ylim[1] + (event.ydata - ylim[1]) * (1 - scale_factor),
    ]

    # Set new limits
    ax.set_xlim(new_xlim)
    ax.set_ylim(new_ylim)

    # Redraw the canvas
    event.canvas.draw()

#### Update variables ####
def update_entry():
    """
    Function for quick updates of the entry values
    """
    txtOld = morphByText_Entryl.get()
    n0 = 0
    try:
        if txtOld[0] == '-':
            if txtOld[1] == '1':
                n0 = 2
                checkbox11_var.set(True)
                checkbox12_var.set(False)
                checkbox13_var.set(False)

        elif txtOld[0] == '0':
            checkbox11_var.set(False)
            checkbox12_var.set(True)
            checkbox13_var.set(False)
        elif txtOld[0] == '1':
            checkbox11_var.set(False)
            checkbox12_var.set(False)
            checkbox13_var.set(True)
        else:
            checkbox11_var.set(False)
            checkbox12_var.set(False)
            checkbox13_var.set(False)
        if n0 == 0:
            n0 = 1
    except:
        checkbox11_var.set(False)
        checkbox12_var.set(False)
        checkbox13_var.set(False)

    if n0 >0:
        try:
            if txtOld[n0] == '-':
                if txtOld[n0+1] == '1':
                    checkbox21_var.set(True)
                    checkbox22_var.set(False)
                    checkbox23_var.set(False)
                    checkbox24_var.set(False)
            elif txtOld[n0] == '0':
                checkbox21_var.set(False)
                checkbox22_var.set(True)
                checkbox23_var.set(False)
                checkbox24_var.set(False)
            elif txtOld[n0] == '1':
                checkbox21_var.set(False)
                checkbox22_var.set(False)
                checkbox23_var.set(True)
                checkbox24_var.set(False)
            elif txtOld[n0] == '2':
                checkbox21_var.set(False)
                checkbox22_var.set(False)
                checkbox23_var.set(False)
                checkbox24_var.set(True)
            else:
                checkbox21_var.set(False)
                checkbox22_var.set(False)
                checkbox23_var.set(False)
                checkbox24_var.set(False)
        except:
            checkbox21_var.set(False)
            checkbox22_var.set(False)
            checkbox23_var.set(False)
            checkbox24_var.set(False)
    else:
        checkbox21_var.set(False)
        checkbox22_var.set(False)
        checkbox23_var.set(False)
        checkbox24_var.set(False)
    top_frame.after(200, update_entry)
def update_entry():
    """
    Function for quick updates of the entry values
    """
    txtOld = morphByText_Entryl.get()
    n0 = 0
    try:
        if txtOld[0] == '-':
            if txtOld[1] == '1':
                n0 = 2
                checkbox11_var.set(True)
                checkbox12_var.set(False)
                checkbox13_var.set(False)

        elif txtOld[0] == '0':
            checkbox11_var.set(False)
            checkbox12_var.set(True)
            checkbox13_var.set(False)
        elif txtOld[0] == '1':
            checkbox11_var.set(False)
            checkbox12_var.set(False)
            checkbox13_var.set(True)
        else:
            checkbox11_var.set(False)
            checkbox12_var.set(False)
            checkbox13_var.set(False)
        if n0 == 0:
            n0 = 1
    except:
        checkbox11_var.set(False)
        checkbox12_var.set(False)
        checkbox13_var.set(False)

    if n0 >0:
        try:
            if txtOld[n0] == '-':
                if txtOld[n0+1] == '1':
                    checkbox21_var.set(True)
                    checkbox22_var.set(False)
                    checkbox23_var.set(False)
                    checkbox24_var.set(False)
            elif txtOld[n0] == '0':
                checkbox21_var.set(False)
                checkbox22_var.set(True)
                checkbox23_var.set(False)
                checkbox24_var.set(False)
            elif txtOld[n0] == '1':
                checkbox21_var.set(False)
                checkbox22_var.set(False)
                checkbox23_var.set(True)
                checkbox24_var.set(False)
            elif txtOld[n0] == '2':
                checkbox21_var.set(False)
                checkbox22_var.set(False)
                checkbox23_var.set(False)
                checkbox24_var.set(True)
            else:
                checkbox21_var.set(False)
                checkbox22_var.set(False)
                checkbox23_var.set(False)
                checkbox24_var.set(False)
        except:
            checkbox21_var.set(False)
            checkbox22_var.set(False)
            checkbox23_var.set(False)
            checkbox24_var.set(False)
    else:
        checkbox21_var.set(False)
        checkbox22_var.set(False)
        checkbox23_var.set(False)
        checkbox24_var.set(False)
    top_frame.after(200, update_entry)
def resetCheckboxes():
    checkbox11_var.set(False)
    checkbox12_var.set(False)
    checkbox13_var.set(False)
    checkbox21_var.set(False)
    checkbox22_var.set(False)
    checkbox23_var.set(False)
    checkbox24_var.set(False)
    checkboxAwesome_var.set(False)
    checkbox14Redshift_var.set(False)
def updateOnlyCheckBoxes(n):
    textNew = ''
    if n == 0:
        checkbox11_var.set(True)
        checkbox12_var.set(False)
        checkbox13_var.set(False)
        textNew += '-1'
        var2 = False
    elif n == 1:
        checkbox11_var.set(False)
        checkbox12_var.set(True)
        checkbox13_var.set(False)
        textNew += '0'
        var2 = False
    elif n == 2:
        checkbox11_var.set(False)
        checkbox12_var.set(False)
        checkbox13_var.set(True)
        textNew += '1'
        var2 = False

    elif n == 3:
        checkbox21_var.set(True)
        checkbox22_var.set(False)
        checkbox23_var.set(False)
        checkbox24_var.set(False)
        textNew += '-1'
        var2 = True
    elif n == 4:
        checkbox21_var.set(False)
        checkbox22_var.set(True)
        checkbox23_var.set(False)
        checkbox24_var.set(False)
        textNew += '0'
        var2 = True
    elif n == 5:
        checkbox21_var.set(False)
        checkbox22_var.set(False)
        checkbox23_var.set(True)
        checkbox24_var.set(False)
        textNew += '1'
        var2 = True
    elif n == 6:
        checkbox21_var.set(False)
        checkbox22_var.set(False)
        checkbox23_var.set(False)
        checkbox24_var.set(True)
        textNew += '2'
        var2 = True
    textOld = morphByText_Entryl.get()
    if var2:
        if len(textOld)>0:
            if textOld[0] == '-':
                textNew = textOld[0:2] + textNew
            else:
                textNew = textOld[0] + textNew
        else:
            textNew = '?' + textNew
    else:
        if len(textOld) > 0:
            if textOld[0] == '-':
                textNew = textNew + textOld[2::]
            else:
                textNew = textNew + textOld[1::]

    morphByText_Entryl.delete(0, tk.END)
    morphByText_Entryl.insert(tk.END, textNew)
def updateOnChange():
    global indNow, ind, attempt1
    morphByText_Entryl.delete(0, tk.END)
    comments.delete(0, tk.END)
    indPrevious = where(previousTable['ID'] == kidsTable[indNow]['ID'])[0]
    if len(indPrevious)>0:
        indPrevious = indPrevious[0]
        preciousResults = previousTable[indPrevious]
    else:
        preciousResults = previousTable[-1]
    try:
        if preciousResults['Comments'] == b'--':
            pass
        else:
            comments.insert(tk.END, preciousResults['Comments'])
    except:
        pass
    awesomeFlag = preciousResults['AwesomeFlag']
    if awesomeFlag == 1:
        checkboxAwesome_var.set(True)
    if awesomeFlag == 0:
        checkboxAwesome_var.set(False)
    if preciousResults['ValidRedshift'] == 1:
        checkbox14Redshift_var.set(True)
    else:
        checkbox14Redshift_var.set(False)
    if preciousResults['Sky_Bkg'] == 'masked':
        attempt1 = True
        preciousResults = str(preciousResults['Class']) + str(preciousResults['Morphology'])
    else:
        attempt1 = False
        preciousResults = str(preciousResults['Class']) + str(preciousResults['Morphology'])
    morphByText_Entryl.insert(tk.END, preciousResults)
def makeInputButtons():
    global checkboxDataStorage_var
    checkboxDataStorage_var.set(True)
    checkboxDataStorage.grid(row=2, column=2, columnspan=3, sticky="ew", padx=5, pady=5)
    entryCatalog.grid(row=2, column=8, columnspan=2, sticky="ew", padx=5, pady=5)
    buttonFindCatalog.config(text='FindCatalog lsbs_r')
    buttonFind2ndCatalog.config(text='FindCatalog r_2')
    buttonDataStorage.grid(row=3, column=2, columnspan=3, sticky="ew", padx=5, pady=5)
    return
################# some important variables for later ############################3
# For click and drag
drag_start = None
# number of all galaxies to classify
# Used for image scalling
one_jansky_arcsec_kids = 10**(0.4 * 23.9) / (0.2**2)
# How much of y axis should image take
yAxis = 0.9
# List of already done images
ind = array([]).astype(int)
#
tipNumber = 0
#
attempt1 = True
# This allows to use the same name as preaviously
files = os.listdir()
person_name = ''
c1 = [190, 220]
c2 = [240, 250]



############### Window related #####################
# Create the main Tkinter window
root = tk.Tk()
root.title("LSBMorph")
root.protocol('WM_DELETE_WINDOW', save_when_close)
root.geometry("%ix%i" % (root.winfo_screenwidth(), root.winfo_screenheight()))



checkboxDataStorage_var = tk.BooleanVar(value=True)
for i in files:
    i1 = i.split('_')
    if i1[0] == 'vis':
        if os.path.exists('dataPath_%s.txt' % i1[-1].split('.')[0]):
            person_name = i1[-1].split('.')[0]

            otherInfoPath = 'dataPath_%s.txt' % person_name
            otherInfoPath = open(otherInfoPath, 'r').readlines()
            kidsData = otherInfoPath[0]
            galaxiesList = otherInfoPath[1]
            secondGalaxiesList = otherInfoPath[2]
            colorsForPlots = otherInfoPath[3].split()
            checkboxDataStorage_var = tk.BooleanVar(value=False)



# Prepare top part, for Checkboxes and Entrys
top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

# Divide the row into 10 parts
for i in range(10):
    top_frame.grid_columnconfigure(i, weight=1)  # Equal weight for all columns

# Prepare bottom part, for Images only
bottom_frame = tk.Frame(root)
bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
for r in range(2):
    bottom_frame.grid_rowconfigure(r, weight=1)
for c in range(3):
    bottom_frame.grid_columnconfigure(c, weight=1)


# What you first at start
entry_label = tk.Label(top_frame, text="Input name", font=("Arial", 20))
entry_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)

entry = tk.Entry(top_frame, font=("Arial", 20))
entry.grid(row=0, column=2, columnspan=3, sticky="ew", padx=5, pady=5)  # Use 6 parts for the Entry widget

entry.delete(0, tk.END)
entry.insert(0, person_name)

buttonStart = tk.Button(top_frame, text = 'Start', font=("Arial", 20), command=prepareTable)
buttonStart.grid(row=0, column=6, columnspan=2, sticky="ew", padx=5, pady=5)

# Data storage

checkboxDataStorage = tk.Checkbutton(top_frame, text="Get data online (NCBJ intranet needed)", variable=checkboxDataStorage_var, font=("Arial", 16),
                            command = dataStorage)

# set dataStorage button
buttonDataStorage = tk.Button(top_frame, text = 'How to connect online?', font=("Arial", 20))
buttonDataStorage.grid(row=0, column=9, columnspan=1, sticky="ew", padx=5, pady=5)
buttonDataStorage.bind('<Button-1>', helpMe)


buttonBrowseFiles = tk.Button(top_frame, text = 'DataPath', font=("Arial", 20))
buttonBrowseFiles.bind('<Button-1>', intput_cat)
entryData = tk.Entry(top_frame, font=("Arial", 12), state="disabled")


entryCatalog = tk.Entry(top_frame, font=("Arial", 12), state="disabled")
buttonFind2ndCatalog = tk.Button(top_frame, text = 'FindCatalog N2', font=("Arial", 20))
buttonFind2ndCatalog.bind('<Button-1>', intput_cat)
entryFind2ndCatalog = tk.Entry(top_frame, font=("Arial", 12), state="disabled")

if person_name == '':
    buttonFindCatalog = tk.Button(top_frame, text = 'FindCatalog N1', font=("Arial", 20))
    makeInputButtons()
else:
    buttonFindCatalog = tk.Button(top_frame, text = 'NewRun', font=("Arial", 20))
buttonFindCatalog.bind('<Button-1>', intput_cat)
buttonFindCatalog.grid(row=2, column=6, columnspan=2, sticky="ew", padx=5, pady=5)

#### The remaining 2 parts will appear empty

# Prepare the checkboxes Variables, Class, Morph and Awesome
checkbox11_var = tk.BooleanVar(value=False)
checkbox12_var = tk.BooleanVar(value=False)
checkbox13_var = tk.BooleanVar(value=False)
checkbox14Redshift_var = tk.BooleanVar(value=False)

checkbox21_var = tk.BooleanVar(value=False)
checkbox22_var = tk.BooleanVar(value=False)
checkbox23_var = tk.BooleanVar(value=False)
checkbox24_var = tk.BooleanVar(value=False)

checkboxAwesome_var = tk.BooleanVar(value=False)

# Prepare the checkboxes
# First column
checkbox11 = tk.Checkbutton(top_frame, text="Failed fitting [-1]", variable=checkbox11_var, font=("Arial", 16),
                            command = lambda n=0: updateOnlyCheckBoxes(n))

checkbox12 = tk.Checkbutton(top_frame, text="Non-LSB [0]", variable=checkbox12_var, font=("Arial", 16),
                            command = lambda n=1: updateOnlyCheckBoxes(n))

checkbox13 = tk.Checkbutton(top_frame, text="LSB [1]", variable=checkbox13_var, font=("Arial", 16),
                            command = lambda n=2: updateOnlyCheckBoxes(n))
checkbox14Redshift = tk.Checkbutton(top_frame, text="Valid redshift", variable=checkbox14Redshift_var, font=("Arial", 16),
                        bg = rgb_to_hex(c1[1], c1[0], c1[0]), activebackground=rgb_to_hex(c2[1], c2[0], c2[0]))
# Second column
checkbox21 = tk.Checkbutton(top_frame, text="Featureless [-1]", variable=checkbox21_var, font=("Arial", 16),
                            command = lambda n=3: updateOnlyCheckBoxes(n))
checkbox22 = tk.Checkbutton(top_frame, text="Not sure [0]", variable=checkbox22_var, font=("Arial", 16),
                            command = lambda n=4: updateOnlyCheckBoxes(n))
checkbox23 = tk.Checkbutton(top_frame, text="LTG (Sp/Irr) [1]", variable=checkbox23_var, font=("Arial", 16),
                            command = lambda n=5: updateOnlyCheckBoxes(n))
checkbox24 = tk.Checkbutton(top_frame, text="ETG (Ell) [2]", variable=checkbox24_var, font=("Arial", 16),
                            command = lambda n=6: updateOnlyCheckBoxes(n))
# Awesome box
buttonAwesome = tk.Checkbutton(top_frame, text = 'Awesome', variable=checkboxAwesome_var, font=("Arial", 20),
                        bg = rgb_to_hex(c1[0], c1[1], c1[0]), activebackground=rgb_to_hex(c2[0], c2[1], c2[0]))
# Prepare the classification within the textbox
morphByText_Label = tk.Label(top_frame, text="Input by typing", font=("Arial", 20))
morphByText_Entryl = tk.Entry(top_frame, font=("Arial", 20))
morphByText_Entryl.bind("<Return>", onEnter)

# Prepare the comments textbox
comment_label = tk.Label(top_frame, text="Comments", font=("Arial", 20))
comments = tk.Entry(top_frame, font=("Arial", 20))
comments.bind("<Return>", onEnter)

# Prepare the progress bar
procVar = tk.StringVar()
procVar.set('')
doneNumber = tk.StringVar()
doneNumber.set('0')
progress_barr = ttk.Progressbar(top_frame, orient = 'vertical', length = 200,mode="determinate")
procentege_label = tk.Label(top_frame, font=("Arial", 20), textvariable = procVar)
doneLabel = tk.Label(top_frame, font=("Arial", 20), textvariable = doneNumber)

# Prepare the buttons for changing galaxy
buttonNext = tk.Button(top_frame, text = 'Next', font=("Arial", 20), command=findNext)
buttonPrevious = tk.Button(top_frame, text = 'Go Back', font=("Arial", 20), command=findPrevious)
buttonSkip = tk.Button(top_frame, text = 'Skip', font=("Arial", 20), command=skip)
buttonAladin = tk.Button(top_frame, text = 'Aladin lite', font=("Arial", 20), command = openAladin)

# Help  button
buttonHelp = tk.Button(top_frame, text = 'Help', font=("Arial", 20))
buttonHelp.grid(row=0, column=9, columnspan=1, sticky="ew", padx=5, pady=5)
buttonHelp.bind('<Button-1>', helpMe)

buttonOptions = tk.Button(top_frame, text = 'Options', font=("Arial", 20), command = setColors)
buttonOptions.grid(row=1, column=9, sticky="ew", padx=5, pady=5)

buttonWeird = tk.Button(top_frame, text = 'Weird', font=("Arial", 20),
                        command=lambda i = interestingIDs[random.randint(0,len(interestingIDs))]:  skip(name = i))
buttonExamples = tk.Button(top_frame, text = 'Exemplary', font=("Arial", 20))
buttonExamples.bind('<Button-1>', helpMe)

if person_name != '':
    entryData.configure(state='normal')

    entryData.delete(0, tk.END)
    if len(kidsData) > 30:
        tt = '../%s' % (kidsData.split('/')[-1])
        entryData.insert(tk.END, tt)
    else:
        entryData.insert(tk.END, kidsData)
    entryData.configure(state='disabled')

    entryCatalog.configure(state='normal')
    entryCatalog.delete(0, tk.END)
    if len(galaxiesList) > 30:
        tt = '../%s' % (galaxiesList.split('/')[-1])
        entryCatalog.insert(tk.END, tt)
    else:
        entryCatalog.insert(tk.END, galaxiesList)
    entryCatalog.configure(state='disabled')

    entryFind2ndCatalog.configure(state='normal')
    entryFind2ndCatalog.delete(0, tk.END)
    if len(secondGalaxiesList) > 30:
        tt = '../%s' % (secondGalaxiesList.split('/')[-1])
        entryFind2ndCatalog.insert(tk.END, tt)
    else:
        entryFind2ndCatalog.insert(tk.END, galaxiesList)
    entryFind2ndCatalog.configure(state='disabled')

# This one connects the checkboxes with entry
update_entry()
# Run the Tkinter event loop
root.mainloop()