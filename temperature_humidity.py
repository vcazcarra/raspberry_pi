import Adafruit_DHT
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('/home/pi/emails_from_python/')
from lib_emails import send_email_attached_file

#constants for the sensor
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
TIME_FOR_CSV = 60*60*24 # In seconds
TIME_FOR_READING = 30 # In seconds
output_path = '/home/pi/temperature_humidity/'
tic_csv = time.time()

#lists for the csv
humidity_csv = []
temperature_cs = []
asci_time_csv = []
x_axis_plot = []

#email to send the figure
receiver_email = "--------"

while True:
   
    if time.time()-tic_csv < TIME_FOR_CSV:
         
        #Read temperature and humidity
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)       

        if humidity is not None and temperature is not None:
            #Round values
            humidity = np.round(humidity,2)-6
            temperature = np.round(temperature,2)
            
            #Check that the values in inside a "valid" range to avoid wrong readings
            if humidity > 0 and humidity < 100 and temperature > 0 and temperature < 30:                
                #save the current values
                humidity_csv.append(humidity)
                temperature_cs.append(temperature)
            else:
                #save the last correct values to avoid outlayers in the plot
                humidity_csv.append(humidity_csv[-1])
                temperature_cs.append(temperature_cs[-1])
                
            #print values
            print(time.asctime(),"Temp = {0:0.1f}*C  Humidity = {1:0.1f}%".format(temperature, humidity))
            asci_time_csv.append(time.asctime())
            #genrate a vector for the xaxis of the plot
            struct_time = time.localtime()
            x_axis_plot.append(str(struct_time.tm_mon).zfill(2)+str(struct_time.tm_mday)+str(struct_time.tm_hour)+str(struct_time.tm_min).zfill(2)+str(struct_time.tm_sec).zfill(2))
            
        else:
            print("Failed to retrieve data from humidity sensor")
            
        #Wait some time before reading again        
        time.sleep(TIME_FOR_READING)
    else:
        #generate a pandadata frame
        out_csv = pd.DataFrame({
            'date':np.asarray(asci_time_csv),
            'humidity':np.asarray(humidity_csv),
            'temperature':np.asarray(temperature_cs)
            })
         

        # get name for the file from the day
        struct_time = time.localtime()
        name_file = str(struct_time.tm_year)+str(struct_time.tm_mon).zfill(2)+str(struct_time.tm_mday).zfill(2)#+'_'+str(struct_time.tm_hour)+'_'+str(struct_time.tm_min).zfill(2)
        #save the csv file
        out_csv.to_csv(output_path+'csv/humidity_temperature_'+name_file+'.csv',index=False)
        
        ###plot temperature and humidity
        fig, ax1 = plt.subplots(figsize=(20,4))
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Humidity [%]', color='blue')
        ax1.plot(range(len(humidity_csv)), np.asarray(humidity_csv),color='blue')
        ax1.set_ylim([40,90])
        x_ticks_values = np.linspace(0,len(humidity_csv),len(humidity_csv))
        x_tick_label = np.asarray(asci_time_csv)
        x_ticks_pos = np.linspace(0,len(humidity_csv)-1,24,dtype='int')
        plt.xticks(x_ticks_values[x_ticks_pos], x_tick_label[x_ticks_pos], rotation='vertical')
        ax1.tick_params(axis='y', labelcolor='blue')
        plt.grid()
        ax2 = ax1.twinx()  
        ax2.set_ylabel('Temperature [*C]', color='red')  
        ax2.plot(range(len(temperature_cs)), np.asarray(temperature_cs),color='red')
        ax2.tick_params(axis='y', labelcolor='red')
        ax2.set_ylim([15,25])
        plt.margins(0.2)
        plt.subplots_adjust(bottom=0.25)
        title_name = 'Max / Min Humidity: '+ str(np.round(np.max(np.asarray(humidity_csv)),2)) + '  /  ' + str(np.round(np.min(np.asarray(humidity_csv)),2)) + ' [%] ' + '               Max / Min Temperature: '+ str(np.round(np.max(np.asarray(temperature_cs)),2)) + ' / '+ str(np.round(np.min(np.asarray(temperature_cs)),2)) + ' [*C] '
        plt.title(title_name)
        plt.savefig(output_path+'png/humidity_temperature_'+name_file+'.png',bbox_inches='tight')
              

        #send email 
        subject = 'Humidity temperature '+name_file
        body = 'Humidity temperature '+name_file 
        filename = output_path+'png/humidity_temperature_'+name_file+'.png'
        send_email_attached_file(receiver_email,subject,body,filename)
        
        #Reset timer to save the next csv file
        tic_csv = time.time()
        #lists for the csv
        humidity_csv = []
        temperature_cs = []
        asci_time_csv = []
        
        
        
