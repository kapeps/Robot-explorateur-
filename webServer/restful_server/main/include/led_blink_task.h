#ifndef LED_BLINK_TASK_H
#define LED_BLINK_TASK_H

#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "sdkconfig.h"


#define LED_PIN GPIO_NUM_2

void blinkTask( void * pvParameters);
void startBlinkTask();

int onTime;
int offTime;;


#endif //LED_BLINK_TASK