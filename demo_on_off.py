import sys
import time

from APC_SMART_UPS import APC as apc

debug = False
# debug = True

print('\n\n')
print('#'*80)
print('APC Smart-UPS interface demo')
print('#'*80)


ups = apc('COM5')
print('open serial port', ups.serial_open())
print('set ups to smart mode', ups.set_ups_to_smart_mode(debug))    

print('turn ups on', ups.turn_ups_on(True))
# print('turn ups off', ups.turn_off_ups(True))

print('return to simple mode', ups.return_to_simple_mode(debug))
print('#'*80)    