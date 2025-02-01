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

# if ups.test_lights_and_beeper(debug) != 0:
#     print('ups failed lights and beeper test')


# if ups.battery_test(debug) != 0:
#     print('ups failed to perform battery test')

# if ups.battery_test_result(debug) != 0:
    # print('battery result not OK, maybe not available')

# print('number of battery packs', ups.number_of_battery_packs(debug))

# print('last transfer cause', ups.transfer_cause(debug))

# print('firmware version', ups.firmware_version(debug))

# print('ups nominal battery voltage rating', ups.ups_nominal_battery_voltage_rating(debug))

# print('battery capacity', ups.battery_capacity(debug))

# print('line quality', ups.acceptable_line_quality(debug))

# print('ups status', ups.ups_status(debug))




# print('turn ups on', ups.turn_ups_on(True))
# print('turn ups off', ups.turn_off_ups(True))

# print('run time calibration', ups.run_time_calibration(True))


print('battery voltage', ups.battery_voltage(debug))
print('battery capacity', ups.battery_capacity(debug))
print('load power', ups.load_power(debug))
print('ups internal temperature', ups.ups_internal_temperature(debug))
# # print('ups and utility frequency', ups.ups_and_utility_operating_frequency(debug))
print('line voltage', ups.line_voltage(debug))
# # print('maximum line voltage', ups.maximum_line_voltage(debug))
# # print('minimum line voltage', ups.minimum_line_voltage(debug))
print('output voltage', ups.output_voltage(debug))

print('ups status', ups.ups_status(debug))


print('return to simple mode', ups.return_to_simple_mode(debug))


print('#'*80)    