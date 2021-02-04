#include "led_blink_task.h"


void blinkTask( void * pvParameters )
{
    onTime = 1000;
    offTime = 1000;
    gpio_reset_pin(LED_PIN);
    /* Set the GPIO as a push/pull output */
    gpio_set_direction(LED_PIN, GPIO_MODE_OUTPUT);

    for( ;; )
    {
        /* Blink off (output low) */
        gpio_set_level(LED_PIN, 0);
        vTaskDelay(offTime / portTICK_PERIOD_MS);
        /* Blink on (output high) */
        gpio_set_level(LED_PIN, 1);
        vTaskDelay(onTime / portTICK_PERIOD_MS);
    }
}

void startBlinkTask(){
    xTaskCreate(blinkTask, "Blink Task", 2000, NULL, tskIDLE_PRIORITY, NULL );
}

