import sys
import csv
import argparse
from datetime import datetime

import matplotlib.pylab as plt 


BLANK = ''

def getRawData(csvFn):
    "Use csv module to return data as list of list of strings"
    rows = []
    with open(csvFn, 'r') as f:
        r = csv.reader(f)
        for row in r:
            rows.append(row)
    return rows

def str2float(value, name, row):
    " '140.5' -> 140.5"
    floatValue = None
    if value != '':
        try:
            floatValue = float(value)
        except:
            print("Error converting %s of value '%s' to float in row %d of data" % (name, value, row))
    return floatValue            

def getTimeStampedData(rawData, year):
    """
    Turn raw data (strings) into timestamped floats, where each row of
    raw data looks like:
    ['9/28', '11:30', '121', '108', '67', '70', '', '']
    """         
    sugars = []
    uppers = []
    lowers = []
    bpms = []
    weights = []
    dts = []

    frmt = "%Y/%m/%d %H:%M"
    for i, raw in enumerate(rawData):
        dateStr, timeStr, sugar, upper, lower, bpm, weight, _ = raw
        # if there's no date string, don't trust the rest of the data
        if dateStr == BLANK or timeStr == BLANK:
            continue
        dtStr = "%s/%s %s" % (year, dateStr, timeStr)
        try:
            dt = datetime.strptime(dtStr, frmt)
        except:
            print("ERROR converting '%s' and '%s' to datetime in row %d" % (dateStr, timeStr, i))
            # can't trust the rest of the data
            continue

        dts.append(dt)
        sugars.append(str2float(sugar, 'sugar', i))
        uppers.append(str2float(upper, 'upper', i))
        lowers.append(str2float(lower, 'lower', i))
        bpms.append(str2float(bpm, 'bpm', i))
        weights.append(str2float(weight, 'weight', i))

    return dts, sugars, uppers, lowers, bpms, weights
    
def basicPlot(dts, data, title, ylabel):
    "Create a basic plot of the given timestamped data"
    
    plt.plot(dts, data, '*')
    plt.gcf().autofmt_xdate()
    plt.xlabel("datetime")
    plt.ylabel(ylabel)
    plt.title("%s (Mean=%5.2f)" % (title, meanData(data)))
    plt.savefig("%s.png" % title)
    plt.show()

def meanData(xs):
    "Take the mean of a list of data that might be zero length or contain Nones"
    xss = [x for x in xs if x is not None]
    if len(xss) == 0:
        return 0.0
    else:
        return sum(xss) / float(len(xss))

def binSugars(dts, sugars):
    """
    Take timestamped blood sugar data and bin them by the hour
    of the day, to try and make clear any patters with time of day
    """

    # init data
    hrs = list(range(24))
    num = [0]*24
    data = []
    for i in range(24):
        data.append([])

    # bin data by hour of day
    for dt, sugar in zip(dts, sugars):
        num[dt.hour] += 1
        data[dt.hour].append(sugar)



    meanSugars = [meanData(d) for d in data]

    fig, axs = plt.subplots(2)
    fig.suptitle('Blood Sugar Readings by Hour')
    axs[0].bar(hrs, num) 
    #axs[0].set_xlabel("Hour of Day")
    axs[0].set_ylabel("Number of tests")
    axs[1].bar(hrs, meanSugars)
    axs[1].set_xlabel("Hour of Day")
    axs[1].set_ylabel("Mean Blood Sugar")

    plt.savefig("sugarsByHour.png")

    plt.show()

def plotData(fn, year):

    rawData = getRawData(fn)

    # make sure hdr is as expected
    hdr = rawData[0]
    print("header: ", hdr)
    expHdr = ['Date', 'Time', 'Sugar', 'Upper', 'Lower', 'BPM', 'Weight', 'Notes']
    assert hdr == expHdr

    # first step is to turn strings to timestamps and floats,
    # and we skip the header in front, and the stats at the end
    dts, sugars, uppers, lowers, bpms, weights = getTimeStampedData(rawData[1:-1], year)


    basicPlot(dts, sugars, "sugars vs dt", "sugars")
    basicPlot(dts, uppers, "uppers vs dt", "uppers")
    basicPlot(dts, lowers, "lowers vs dt", "lowers")
    basicPlot(dts, bpms, "bpms vs dt", "heart beats / minute")
    basicPlot(dts, weights, "weight vs dt", "weight (lbs)")

    binSugars(dts, sugars)

def main():
    
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('CSV', metavar='csvFile', type=str,
                    help='a CSV file containing health data')
    parser.add_argument('year', metavar='year', type=int,
                    help='the year for this data')

    args = parser.parse_args()

    print(args, args.CSV)
    plotData(args.CSV, args.year)

if __name__ == '__main__':
    main()