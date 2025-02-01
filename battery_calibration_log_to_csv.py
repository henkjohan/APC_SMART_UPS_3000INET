import sys
import time
from datetime import date
from datetime import datetime

from APC_SMART_UPS import APC as apc

debug = False
# debug = True

do_cal = False
# do_cal = True

print('\n\n')
print('#'*80)
print('APC Smart-UPS interface demo')
print('#'*80)

ups = apc('COM5')

if ups.serial_open():
    ups.set_ups_to_smart_mode(debug)
else:
    sys.exit(0)


filename = 'ups_log_'
filename += str(date.today()) + '_'
filename += str(str(datetime.now().time()).split('.')[0]).replace(':','-')
filename += '.csv'

header = ''
header += 'counter,'
header += 'date,'
header += 'time,'
header += 'line voltage,'
header += 'output voltage,'
header += 'ups and utility frequency,'
header += 'load power,'
header += 'battery capacity,'
header += 'battery voltage,'
header += 'ups internal temperature,'
header += 'ups internal status,'
f = open(filename, 'w')
f.write(header + '\n')
f.close()


counter = 0

while True:
    dataline = ''
    dataline += str(counter) + ','
    dataline += str(date.today()) + ','
    dataline += str(datetime.now().time()).split('.')[0] + ','
    dataline += str(ups.line_voltage(debug)) + ','
    dataline += str(ups.output_voltage(debug)) + ','
    dataline += str(ups.ups_and_utility_operating_frequency(debug)) + ','
    dataline += str(ups.load_power(debug)) + ','
    dataline += str(ups.battery_capacity(debug)) + ','
    dataline += str(ups.battery_voltage(debug)) + ','
    dataline += str(ups.ups_internal_temperature(debug)) + ','
    dataline += str(ups.ups_status(debug)) + ','

    f = open(filename, 'a')
    f.write(dataline + '\n')
    f.close()

    print(dataline)

    if (counter == 2) and (do_cal == True):
        ups.run_time_calibration(True)
    
    counter += 1
    time.sleep(1)

