#include "esp_rest_server_setup.h"
#include "led_blink_task.h"

void app_main(void)
{
    init_rest_server(); //Initialize server and runs the task
    startBlinkTask();
}
