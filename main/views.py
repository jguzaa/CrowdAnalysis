from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from main.models import CrowdDensity
from .forms import NewUserForm
from django.core.files.storage import FileSystemStorage
from .forms import FootageForm
from .models import Footage
from plotly.offline import plot
import plotly.graph_objs as go

from .tasks import create_db_csv


import pandas as pd
import matplotlib.pyplot as plt
import os
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import operator

success = ''

# Create your views here.

# Business logic here

# render homepage
def homepage(request):
    return render(request= request,
                  template_name="main/home.html",
                  context={"users": CrowdDensity.objects.all})

#graph page for graph showing
def graph(request):

    data = plotgraph()
    x_data = data['predict_time']
    y_data = data['predict_num']

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_data,
        y=y_data,
        line=dict(color='green')
    ))
    fig.update_layout(
        title="Forecast data of number of people vs time",
        xaxis_title="time",
        yaxis_title="ppl no."
    )
    predict_plot_div = plot(fig, output_type='div')

    # do for loop for collected data plotting
    collected = data['collected']
    dates = []
    collected_plot_divs = []

    for date in collected:
        time = collected[date]['time']
        num = (collected[date])['num']

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=time,
            y=num,
            line=dict(color='blue')
        ))
        fig.update_layout(
            title=date,
            xaxis_title="time",
            yaxis_title="ppl no."
        )

        this_plot_div = plot(fig, output_type='div')
        collected_plot_divs.append(this_plot_div)

    return render(request, "main/graph.html", context={'more': data['more_cus'],
                                                       'less': data['less_cus'],
                                                       'predict_plot_div': predict_plot_div,
                                                       'collected_plot_divs': collected_plot_divs
                                                       })


# render register page as well as its function
def register(request):
    # handle the post request
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username') # normalize the name to consistent format
            messages.success(request,  f"New account created: {username}")
            login(request, user)
            messages.info(request, f"You are now logged in as: {username}")
            # if user finished registering, redirect to another page
            return redirect("main:homepage")
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")

            # re-render the form
            return render(request=request,
                          template_name="main/register.html",
                          context={"form": form})

    #re render the user form
    form = NewUserForm
    return render(request, "main/register.html", context={"form": form})

# render logout request
def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("main:homepage")

# render login page as well as its function
def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data = request.POST)

        # check if the form is valid
        if form.is_valid():
            # get hold of the text field
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # authenticate the user
            user = authenticate(username = username, password = password)
            # check if the user is authenticated
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as: {username}")
                return redirect("main:homepage")
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")

    form = AuthenticationForm()
    return render(request, "main/login.html", {"form": form})



def video_list(request, success=None):

    # input trigger command
    #if(success != ''):
    success = create_db_csv.delay()

    videos = Footage.objects.all()
    return render(request, 'main/video_list.html', {
        'videos': videos,
        'status' : success
    })

def upload_video(request):
    if request.method == "POST":
        form = FootageForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()

            return redirect('main:video_list')
    else:
        form = FootageForm()
    return render(request, 'main/upload_video.html', {
        'form': form
    })

def plotgraph():
    projectDir = os.path.dirname(os.path.realpath(__file__))

    # set up time for column name
    col_name = []
    for h in range(24):
        for m in range(60):
            if (m % 10 == 0):
                if (m == 0):
                    col_name.append(str(h) + ':00')
                else:
                    col_name.append(str(h) + ':' + str(m))

    # set business start hour and end hour
    start_h = 17
    end_h = 22

    starth_index = col_name.index(str(start_h) + ':00')
    endh_index = col_name.index(str(end_h) + ':00')
    endh_index += 1

    # import csv file
    df = pd.read_csv(r'' + projectDir + '/csv/db.csv')
    daysName = df['Date'].tolist()

    # delete date column
    df = df.drop(columns=['Date'])

    # create the list of the day which data collected
    days = pd.DataFrame(list(range(1, df.shape[0] + 1)), columns=['day'])
    # df = df.set_index('Date')

    # train the system which X is the day and Y is the number of ppl in each period
    X_train, X_test, y_train, y_test = train_test_split(days, df, test_size=0.2, random_state=5)

    # model instantiation
    lm = LinearRegression()

    # fitting model for each time period then add to predict list
    predict_list = []
    trending_list = []
    score_list = []

    for period in col_name:
        lm.fit(X_train, y_train[period])
        predict_val = lm.predict([[df.shape[0] + 1]])
        if predict_val >= 0:
            predict_list.append(predict_val[0])
        else:
            predict_list.append(0)
        trending_list.append(lm.coef_[0])
        score_list.append(lm.score(X_test, y_test[period]))

    # print(score_list)

    # Looking for beta value which shows the trend of number in future
    index_max, value_max = max(enumerate(trending_list), key=operator.itemgetter(1))
    index_min, value_min = min(enumerate(trending_list), key=operator.itemgetter(1))

    # Match with the period of time
    #print("The period which most tend to have more customer ", col_name[index_max])
    #print("The period which most tend to lost customer ", col_name[index_min])

    # creat data dictionary to return
    return_data = {}
    return_data['more_cus'] = col_name[index_max]
    return_data['less_cus'] = col_name[index_min]

    # get the prediction data
    return_data['predict_time'] = col_name[starth_index:endh_index]
    return_data['predict_num'] = predict_list[starth_index:endh_index]

    # do the loop to get collected data
    collected_data = {}
    for i in range(df.shape[0]):
        collected_data[daysName[df.shape[0] - 1 - i]] = {'time' : col_name[starth_index:endh_index], 'num':df.iloc[i - 1][starth_index:endh_index]}

    return_data['collected'] = collected_data
    return return_data



    #return [col_name[starth_index:endh_index],predict_list[starth_index:endh_index]]

    # start plot graph
    # fig, axs = plt.subplots(df.shape[0] + 1, sharex=True, sharey=True, gridspec_kw={'hspace': 1})
    # fig.suptitle('amount of people vs time for each day')
    # axs[0].title.set_text("Prediction")
    # axs[0].plot(col_name[starth_index:endh_index], predict_list[starth_index:endh_index])
    # for i in range(1, df.shape[0] + 1):
    #     axs[i].title.set_text(daysName[i - 1])
    #     axs[i].plot(col_name[starth_index:endh_index], df.iloc[i - 1][starth_index:endh_index])
    #
    # for ax in axs.flat:
    #     ax.set(xlabel='time', ylabel='no. ppl')
    #     ax.label_outer()
    #
    # plt.show()
