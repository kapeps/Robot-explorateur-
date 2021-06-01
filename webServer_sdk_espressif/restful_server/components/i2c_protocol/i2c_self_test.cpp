#include "i2c_self_test.h"

#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"


static const char* TAG = "i2c_self_test";

static void i2c_slave_task( void * pvParameters ){
    int size;
    uint8_t *data = (uint8_t *)malloc(DATA_LENGTH);
    while(true){

        //vTaskDelay(2000 / portTICK_PERIOD_MS);
        size = i2c_slave_read_buffer(I2C_SLAVE_NUM, data, I2C_SLAVE_RX_BUF_LEN, 1000 / portTICK_RATE_MS);
        if(size > 0){
            ESP_LOGI(TAG, "Received message : ");
            ESP_LOG_BUFFER_CHAR_LEVEL(TAG, data, size, ESP_LOG_INFO);
            /* for(int i = 0; i < size; i++){
                 printf("%c", data[i]);
            }
            printf("\n"); */
        }
    }

}


void i2c_slave_init()
{
    i2c_config_t conf_slave;
    conf_slave.sda_io_num = I2C_SLAVE_SDA_IO;
    conf_slave.sda_pullup_en = GPIO_PULLUP_ENABLE;
    conf_slave.scl_io_num = I2C_SLAVE_SCL_IO;
    conf_slave.scl_pullup_en = GPIO_PULLUP_ENABLE;
    conf_slave.mode = I2C_MODE_SLAVE;
    conf_slave.slave.addr_10bit_en = 0;
    conf_slave.slave.slave_addr = ESP_SLAVE_ADDR;
    
    esp_err_t err = i2c_param_config(I2C_SLAVE_NUM, &conf_slave);
    if (err != ESP_OK) {
        return ;
    }
    i2c_driver_install(I2C_SLAVE_NUM, conf_slave.mode, I2C_SLAVE_RX_BUF_LEN, I2C_SLAVE_TX_BUF_LEN, 0);
    xTaskCreate(i2c_slave_task, "i2c slave task", 1024 * 2, (void *)0, 10, NULL);
}

