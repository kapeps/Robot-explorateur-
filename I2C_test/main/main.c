/* Hello World Example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_spi_flash.h"
#include "driver/i2c.h"
#include "driver/gpio.h"

static const char *MAINTAG = "esp_I2C_main";

void app_main(void)
{
    printf("Hello world!\n");

    //ESP32’s internal pull-ups are in the range of tens of kOhm, which is, in most cases, insufficient for use as I2C pull-ups. Users are advised to use external pull-ups with values described in the I2C specification.
    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = GPIO_NUM_21,         // select GPIO specific to your project
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_io_num = GPIO_NUM_22,         // select GPIO specific to your project
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = 100000,  // 100000Hz
        // .clk_flags = 0,          /*!< Optional, you can use I2C_SCLK_SRC_FLAG_* flags to choose i2c source clock here. */
    };

    if(i2c_param_config(I2C_NUM_0, &conf) != ESP_OK){
            printf("Could not config");
    }

    if( i2c_driver_install(I2C_NUM_0, I2C_MODE_MASTER, 0, 0, 0) != ESP_OK){
            printf("Could not install");
    }

    
    uint8_t adress = 8;
    uint8_t data[] = { 'H', 'e', 'l', 'l', 'o', ' ', 'a', 'r', 'd', 'u', 'i', 'n', 'o' , '\n'} ;

    i2c_cmd_handle_t my_handler = i2c_cmd_link_create();
    i2c_master_start(my_handler);
    i2c_master_write_byte(my_handler, (adress << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write(my_handler, &data, sizeof(data), true);
    i2c_master_stop(my_handler);

    i2c_master_cmd_begin(I2C_NUM_0, my_handler, 0);
}