from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from .Data_Generation import weather
import os
import pandas as pd
import numpy as np
import pkg_resources
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from datetime import datetime, timedelta
import seaborn as sns
from matplotlib.ticker import MaxNLocator

#Get_token_ready
def authorize():
    creds = None
    credentials_path = pkg_resources.resource_filename(__name__, 'credentials.json')
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes=['https://www.googleapis.com/auth/drive'])
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/drive'],
                redirect_uri='http://localhost:8501/'
            )
            creds = flow.run_local_server(port=8501)
        # with open('token.json', 'w') as token:
        #     token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)
    print('Welcome to RSEI, you have successfully accessed.')
    print('Data processing might take 30-50s, please wait')
    return service

class TemperaturePlotter:
    def __init__(self, city, time_span):
        self.city = city
        self.time_span = time_span
        self.wea=None
    def wae_query(self, service):
        wea = weather()
        wea.connect(service)
        wea.get_input(city_name=self.city, span=self.time_span)
        wea.get_geocode()
        wea.get_threshold()
        wea.get_file_name()
        wea.get_drive_data()
        wea.get_extreme_wea()
        wea.get_heatwave()
        self.wea=wea

    def plot_temperature_distribution(self):
        feature = "Dry Bulb Temperature"
        fig, ax = plt.subplots(1, 1, figsize=(6.5, 3), dpi=300, constrained_layout=True)
        timindex = self.wea.All_df[:8760].index
        for i in range(10):
            select = self.wea.All_df[8760 * i:8760 * (i + 1)]
            ax.plot_date(timindex, select[feature], linestyle='-', linewidth=1, markersize=0.1, color='gray')
        ax.plot_date(timindex, self.wea.TMY_df[feature], linestyle='-', linewidth=0.6,
                     markersize=0.08, color='#F2A71B', label="Typical Meteorological Year")
        ax.plot_date(timindex, select[feature], linestyle='-', linewidth=1, markersize=0.1, color='gray',
                     label="10 Years Temperature Distribution")
        ax.plot_date(timindex, self.wea.EWY_df[feature], linestyle='-', linewidth=1.2,
                     markersize=0.08, color='red', label="Extreme Warm Year")
        ax.plot_date(timindex, self.wea.ECY_df[feature], linestyle='-', linewidth=1.2,
                     markersize=0.08, color='blue', label="Extreme Cold Year")
        leg = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.26), ncol=2, fontsize=11, frameon=False)
        for i in leg.legend_handles:
            i.set_linewidth(1)
        ax.set_ylabel('Temperature[°C]', fontsize=16, fontweight='bold')
        ax.tick_params(axis='both', which='minor', labelsize=11)
        ax.tick_params(axis='both', which='major', labelsize=11)
        ax.xaxis.set_major_locator(dates.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(dates.DateFormatter('%b'))
        ax.margins(x=0)
        plt.show()

class Outage:
    def __init__(self):
        self.Outage=None

    def outage_query(self, service):
        wea = weather()
        wea.connect(service)
        wea.get_outage_data()
        self.wea=wea


def weather_query(city, time_span, sce):
    """

    :param city: I have integrated this function with Google Geo Coding API, so it should be capable to query any location inside U.S., and give you the nearest city
    :param time_span: 'Mid-term' and 'Long-term' only
    :param sce: TMY, EWY, ECY and All (Typical meteorological year, Extreme warm year, Extreme cold year, and all raw data)
    :return: epw file and pandas dataframe
    """
    plotter = TemperaturePlotter(city=city, time_span=time_span)
    plotter.wae_query(service=authorize())
    plotter.plot_temperature_distribution()
    if sce != 'All':
        _epw = plotter.wea.outputepw(sce)
    else:
        _epw = plotter.wea.raw_io
    _df = plotter.wea.data_dict['{}_df'.format(sce)]

    return _epw.getvalue(), _df, plotter.wea.heat_wave_events

def outage_query(sample_size, time_window):
    Outage_event = Outage()
    Outage_event.outage_query(service=authorize())
    power_outage_data = Outage_event.wea.outagedf
    power_outage_data["Start_time"] = pd.to_datetime(power_outage_data["Start"], format='%m/%d/%Y %H:%M')
    power_outage_data["Duration_Minutes"].fillna(0, inplace=True)
    Mon = power_outage_data["Start_time"].dt.month.to_numpy()
    Day = power_outage_data["Start_time"].dt.day.to_numpy()
    Hour = power_outage_data["Start_time"].dt.hour.to_numpy()
    Dur = np.array(power_outage_data["Duration_Minutes"])

    def outage_generator(sample_size, time_window):
        timewindow = time_window
        MCMC = {}
        iter = sample_size
        np.random.seed(2814)
        for i in range(iter):
            agg = {}
            Outage = np.ones(96 * timewindow)
            Mon_MCMC = np.random.choice(Mon, size=1)[0]
            first_d_month = datetime(2023, Mon_MCMC, 1, 0, 0, 0)
            first_d_next_month = datetime(first_d_month.year, first_d_month.month + 1, 1, 0,
                                          0) if first_d_month.month != 12 else datetime(first_d_month.year + 1, 1, 1, 0,
                                                                                        0)
            num_day_month = (first_d_next_month - timedelta(minutes=1)).day
            Day_MCMC = np.clip(np.random.choice(Day, size=1)[0], 1, num_day_month)
            Hour_MCMC = np.random.choice(Hour, size=1)[0]
            Dur_MCMC = np.random.choice(Dur, size=1)[0]
            if Dur_MCMC >= 4320:
                Dur_MCMC = 4320
            Outage[Hour_MCMC * 4: Hour_MCMC * 4 + max(1, int(Dur_MCMC / 15))] = 0

            # Find end day as well
            Start_datetime = datetime(2023, Mon_MCMC, Day_MCMC, Hour_MCMC)
            Sim_start = Start_datetime
            Sim_end = Start_datetime + timedelta(minutes=Dur_MCMC)
            if Sim_end.year - Sim_start.year > 0:
                Mon_MCMC = 1
                Day_MCMC = 1
                Hour_MCMC = Hour_MCMC
                Dur_MCMC = Dur_MCMC
            else:
                None

            Start_datetime = datetime(2023, Mon_MCMC, Day_MCMC, Hour_MCMC)
            Sim_end = Start_datetime + timedelta(minutes=Dur_MCMC) + timedelta(days=1)

            outage_start = "2023-{}-{}".format(Mon_MCMC, Day_MCMC)
            agg["Mon_MCMC"] = Mon_MCMC
            agg["Day_MCMC"] = Day_MCMC
            agg["Hour_MCMC"] = Hour_MCMC
            agg["Dur_MCMC"] = Dur_MCMC
            agg["time[h]"] = np.repeat(np.arange(0, 24 * timewindow), 4)
            agg["outage_start"] = outage_start
            agg["outage_end"] = '2023-{}-{}'.format(Sim_end.month, Sim_end.day)
            agg["Outage"] = Outage
            start_time = pd.to_datetime(agg["outage_start"])
            end_time = pd.to_datetime(agg["outage_end"])
            agg["len"] = int((end_time - start_time).total_seconds() / 3600 * 4)
            MCMC[i] = agg

        return MCMC
    MCMC = outage_generator(sample_size, time_window)

    MCMCdf = pd.DataFrame.from_dict(MCMC).T

    def MCMC_show(raw, feature, datastr):
        if datastr == 'Mon':
            xlabel = 'Month of a year'
            bin = 12
        if datastr == 'Day':
            xlabel = 'Day of a month'
            bin = 31
        if datastr == 'Hour':
            xlabel = 'Hour of a day'
            bin = 24
        if datastr == 'Dur':
            xlabel = 'Duration(Min)'
            bin = 50

        # The first plot show 1 sample example, and 2nd plot show MCMC comparison
        if len(MCMCdf[feature].values) > 1:
            fig, axes = plt.subplots(2, 1, figsize=(2, 2), dpi=300, sharex=True, constrained_layout=True)
            if datastr == 'Dur':
                sns.histplot(raw, kde=True, stat='probability', color='blue', bins=bin, label='Raw Distribution',
                             ax=axes[0])
            else:
                sns.histplot(raw, kde=True, stat='probability', color='blue', bins=bin, label='Raw Distribution',
                             discrete=True, ax=axes[0])

            # sns.histplot(raw, kde=True, stat='probability', color='blue', bins=bin, label='Raw Distribution', discrete=True, ax=axes[0])
            sns.histplot(data=MCMCdf, x=feature, kde=True, stat='probability', color='red', bins=bin,
                         label='MCMC Sampling', discrete=True, ax=axes[1])
            axes[0].set_ylabel('Probability', fontsize=8, fontweight='bold')
            axes[1].set_ylabel('Probability', fontsize=8, fontweight='bold')
            axes[0].tick_params(axis='both', which='both', labelsize=7)
            axes[1].tick_params(axis='both', which='both', labelsize=7)
            axes[0].margins(x=0)
            axes[1].margins(x=0)
            axes[1].set_xlabel(xlabel, fontsize=8, fontweight='bold')
            axes[0].set_xlabel(None)
            axes[0].xaxis.set_major_locator(MaxNLocator(integer=True))
            axes[1].xaxis.set_major_locator(MaxNLocator(integer=True))
            axes[1].legend([], [], frameon=False)
            axes[0].legend([], [], frameon=False)

            plt.close(fig)
            folder_path = "../Plots"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            figurename = '{}_with_sample_size{}.png'.format(xlabel, len(MCMCdf[feature].values))
            figuresave = os.path.join(folder_path, figurename)
            fig.savefig(figuresave)
        else:
            fig, ax = plt.subplots(1, 1, figsize=(2, 1.8), dpi=300, sharex=True, constrained_layout=True)
            if datastr == 'Dur':
                sns.histplot(raw, kde=True, stat='probability', color='blue', label='Raw Distribution', ax=ax)
                ax.set_xlim(0, 5000)
                ax.set_xticks(np.arange(0, 5000 + 1, 1000))
                ax.tick_params(axis='both', which='both', labelsize=7)
            else:
                sns.histplot(raw, kde=True, stat='probability', color='blue', bins=bin, label='Raw Distribution',
                             discrete=True, ax=ax)
                ax.tick_params(axis='both', which='both', labelsize=7)
                ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            ax.axvline(x=MCMCdf[feature].values, color='red', linewidth=2, label='MCMC Sampling')
            ax.set_ylabel('Probability', fontsize=8, fontweight='bold')
            ax.set_ylabel('Probability', fontsize=8, fontweight='bold')
            ax.margins(x=0)
            ax.set_xlabel(xlabel, fontsize=8, fontweight='bold')
            ax.legend(loc='center', bbox_to_anchor=(0.5, 1.15), ncol=1, fontsize=8, frameon=False)
            plt.show()
    MCMC_show(raw=Mon, feature="Mon_MCMC", datastr='Mon')
    MCMC_show(raw=Day, feature="Day_MCMC", datastr='Day')
    MCMC_show(raw=Hour, feature="Hour_MCMC", datastr='Hour')
    MCMC_show(raw=Dur,  feature="Dur_MCMC", datastr='Dur')



def find_heat_wave_events(df):
    """
    Detailed method: "https://www.sciencedirect.com/science/article/pii/S2405880716300309"
    :param df:
    :return:
    """
    All_df=df
    daily_mean_temp  = All_df["Dry Bulb Temperature"].resample('1D').mean().dropna()
    # Calculate percentiles
    Spic = np.percentile(daily_mean_temp , 99.5)
    Sdeb = np.percentile(daily_mean_temp , 97.5)
    Sint = np.percentile(daily_mean_temp , 95)
    # Initialize variables
    heat_wave = False
    heat_wave_start = None
    heat_waves = []

    # Iterate over the daily mean temperatures to detect heat waves
    for i in range(len(daily_mean_temp)):
        temp = daily_mean_temp.iloc[i]

        if temp >= Spic:
            # Backtrack to find the start day of the heat wave
            heat_wave_start = None
            for j in range(i, -1, -1):
                if daily_mean_temp.iloc[j] >= Sdeb:
                    heat_wave_start = j
                else:
                    break
            if heat_wave_start is not None:
                heat_wave = True

        if heat_wave:
            if temp < Sdeb:
                consecutive_cool_days = 0
                for j in range(i, min(i + 3, len(daily_mean_temp))):
                    if daily_mean_temp.iloc[j] < Sdeb:
                        consecutive_cool_days += 1
                    else:
                        break
                if consecutive_cool_days >= 3 or temp < Sint:
                    heat_wave = False
                    heat_waves.append((heat_wave_start, i))
                    heat_wave_start = None

    # Add the last heat wave if it ends at the end of the dataset
    if heat_wave:
        heat_waves.append((heat_wave_start, len(daily_mean_temp) - 1))

    # Collect data
    All_df['heat_wave'] = False
    heat_wave_events = []
    for start, end in heat_waves:
        start_date = daily_mean_temp.index[start]
        end_date = daily_mean_temp.index[end]
        duration = (end_date - start_date).days + 1
        max_temp = daily_mean_temp[start:end + 1].max()
        heat_wave_df = All_df.loc[start_date:end_date]
        All_df.loc[start_date:end_date, 'heat_wave'] = True
        heat_wave_events.append({
            'start_date': start_date,
            'end_date': end_date,
            'duration_days': duration,
            'max_temperature': max_temp,
            'dataframe': heat_wave_df
        })
        print(f"Heat wave from {start_date} to {end_date}")
        print(f"Duration: {duration} days")
        print(f"Max Temperature: {max_temp:.2f}°C")
        print('---')

    return All_df, heat_wave_events

