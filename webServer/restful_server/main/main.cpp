extern "C" {
#include "esp_rest_server_setup.h"
#include "led_blink_task.h"
}
#include "I2C_protocol.h"

#include <vector>
#include <string>

extern "C" void app_main(void)
{
    init_rest_server(); //Initialize server and runs the task
    startBlinkTask();

    I2C_protocol my_protocol;
    std::vector<uint8_t> addresses = my_protocol.scanBus();
    for (std::vector<uint8_t>::iterator it = addresses.begin(); it != addresses.end(); ++it){
        char adress = *it;
        printf(&adress);
    }
}
