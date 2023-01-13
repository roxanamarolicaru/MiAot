#!/bin/sh
echo Initialization of the catalog...
osascript -e 'tell app "Terminal" to do script "cd Documents/GitHub/miaot/catalog/ && python ./main_catalog.py ./settings_miaot.json"' 
sleep 5 
echo Initialization of devices...
osascript -e 'tell app "Terminal" to do script "cd Documents/GitHub/miaot/devices/ && python ./main_devices.py ./conf/settings_device_bowl_food.json"'  
osascript -e 'tell app "Terminal" to do script "cd Documents/GitHub/miaot/devices/ && python ./main_devices.py ./conf/settings_device_bowl_water.json"'  
osascript -e 'tell app "Terminal" to do script "cd Documents/GitHub/miaot/devices/ && python ./main_devices.py ./conf/settings_device_kennel.json"'   
osascript -e 'tell app "Terminal" to do script "cd Documents/GitHub/miaot/devices/ && python ./main_devices.py ./conf/settings_device_food_pool.json"'   
osascript -e 'tell app "Terminal" to do script "cd Documents/GitHub/miaot/devices/ && python ./main_devices.py ./conf/settings_device_water_tank.json"' 
echo Initialization of collar...
osascript -e 'tell app "Terminal" to do script "cd Documents/GitHub/miaot/collar/ && sudo python ./main_collar.py ./settings_device_collar.json"' 
sleep 5
echo Initialization of thingspeak...
osascript -e 'tell app "Terminal" to do script "cd Documents/GitHub/miaot/thingspeak_adaptor/ && python ./main_thingspeak_adaptor.py ./settings_thingspeak.json"' 
echo Initialization of controllers...
osascript -e 'tell app "Terminal" to do script "cd Documents/GitHub/miaot/controllers/ && python ./main_environment_controller.py ./conf/settings_device_bowl_water_controller.json"' 
osascript -e 'tell app "Terminal" to do script "cd Documents/GitHub/miaot/controllers/ && python ./main_timer_controller.py ./conf/settings_device_bowl_food_controller_timer.json"' 
osascript -e 'tell app "Terminal" to do script "cd Documents/GitHub/miaot/controllers/ && python ./main_timer_controller.py ./conf/settings_device_kennel_controller_timer.json"' 
echo Initialization finished