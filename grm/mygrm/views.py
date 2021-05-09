
# Create your views here.
import base64

from io import StringIO, BytesIO

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from garminconnect import Garmin, GarminConnectConnectionError, GarminConnectAuthenticationError, \
    GarminConnectTooManyRequestsError
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
from matplotlib import pylab
from pylab import *
import PIL, PIL.Image



def index_view(request):
    return render(request, 'mygrm/index.html')

def show_data(request):
    print("####", "kekse: ", request.POST)
    user = request.POST['user']
    password = request.POST['password']
    try:
        client = Garmin(user, password )
        client.login()
    except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
    ) as err:
        print("Error occurred during Garmin Connect Client init: %s" % err)
        return render(request, 'mygrm/showdata.html', {
            'user': user,
            'password': password,
            'error_message': "Login Did Not Work ! " + "%s" %err,
        })
    except Exception:  # pylint: disable=broad-except
        print("Unknown error occurred during Garmin Connect Client init")

    print("####client: ", client.get_full_name())

    try:
        activities = client.get_activities(0, 5000)  # 0=start, 1=limit
    except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
    ) as err:
        print("Error occurred during client.get_activities(): %s" % err)
        return render(request, 'mygrm/showdata.html', {
            'user': user,
            'password': password,
            'error_message': "client.get_activities() Did Not Work ! " + "%s" %err,
    })
    except Exception:  # pylint: disable=broad-except
        print("Unknown error occurred during Garmin Connect Client get activities")

    df = DataFrame(activities)
    df1 = df[
        ['activityId', 'activityName', 'startTimeLocal', 'activityType', 'distance', 'movingDuration', 'elevationGain',
         'elevationLoss', 'averageSpeed', 'calories', 'averageHR', 'maxHR']]

    for index, row in df1.iterrows():
        print("index: ", index, " row: ", row[3]['typeKey'])
        type_key = row[3]['typeKey']
        print("type: ", type_key)

        if ((row[3]['typeKey']) != 'running'):
            print("delete row with index : ", index)
            df1.drop(index, inplace=True)
        else:
            print("trying to set : ", index)
            df1.replace = 'running'

    df1["startTimeLocal"] = df1["startTimeLocal"].astype("datetime64")

    dfplt = df1[['startTimeLocal', 'distance']]
    dfplt['distance'] = dfplt['distance'] / 1000
    print(dfplt.head())
    dfplt["startTimeLocal"] = dfplt["startTimeLocal"].astype("datetime64")



    # Set descriptions:
    plt.title("Gelaufene Kilometer pro Monat (Quelle Garmin)")
    plt.ylabel('km', fontsize=5)
    plt.xlabel('Monat', fontsize=5)

    plt.rcParams['figure.figsize'] = [40, 20]
    groupedDF = dfplt['distance'].groupby([dfplt["startTimeLocal"].dt.year, dfplt["startTimeLocal"].dt.month]).sum()
    print(groupedDF)
    # colors=
    # df.loc[df['set_of_numbers'] <= 4, 'equal_or_lower_than_4?'] = 'True'
    colors = []
    i = 0
    for index, value in groupedDF.items():
        print("Index : ", index, "Value : ", value)
        if (value >= 100):
            colors.insert(i, 'g')
        elif (value > 75):
            colors.insert(i, 'lime')
        elif (value > 50):
            colors.insert(i, 'cyan')
        elif (value > 25):
            colors.insert(i, 'orange')
        else:
            colors.insert(i, 'r')
        i = i + 1

    print(type(colors))
    print(colors)

    dfplt['distance'].groupby([dfplt["startTimeLocal"].dt.year, dfplt["startTimeLocal"].dt.month]).sum().plot(
        kind="bar", color=colors, fontsize='3')
    # df1.groupby(pd.Grouper(key='startTimeLocal', freq='1M')).count().plot(kind="bar")

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    buf.close()


#    return HttpResponse(buffer.getvalue(), mimetype="image/png")

    return render(request, 'mygrm/showdata.html', {
            'user': user,
            'password': password,
            'image_base64': image_base64,
        })