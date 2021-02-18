extern "C" {
#include "esp_rest_server_setup.h"
#include "led_blink_task.h"
}

#include "I2C_protocol.h"
#include "i2c_self_test.h"

#include <vector>
#include <string>

extern "C" void app_main(void)
{
    //init_rest_server(); //Initialize server and runs the task
    startBlinkTask();

    i2c_slave_init();
    I2C_protocol my_protocol;
    std::vector<uint8_t> addresses = my_protocol.scanBus(); 
    my_protocol.identify_adresses(&addresses);
}