#include "I2C_protocol.h"

#include "esp_log.h"

static const char* TAG = "I2C_protocol";

I2C_protocol::I2C_protocol(){

    _conf.mode = I2C_MODE_MASTER;
    _conf.sda_io_num = SDA_PIN;
    _conf.sda_pullup_en = GPIO_PULLUP_ENABLE;
    _conf.scl_io_num = SCL_PIN;
    _conf.scl_pullup_en = GPIO_PULLUP_ENABLE;
    _conf.master.clk_speed = 100000;  // 100000Hz
    // _conf.clk_flags = 0;          /*!< Optional, you can use I2C_SCLK_SRC_FLAG_* flags to choose i2c source clock here. */
    

    esp_err_t err = i2c_param_config(I2C_NUM, &_conf);
    if(err == ESP_OK){
        ESP_LOGI(TAG, "I2C configuration succes");
    }
    else if(err == ESP_ERR_INVALID_ARG){
        ESP_LOGE(TAG, "Could not configure I2C, invalid arg");
    }
    else{
        ESP_LOGW(TAG, "Unknow I2C configuration error");
    }
    
    err = i2c_driver_install(I2C_NUM, I2C_MODE_MASTER, 0, 0, 0);
    if(err == ESP_OK){
        ESP_LOGI(TAG, "I2C install succes");
    }
    else if(err == ESP_ERR_INVALID_ARG){
        ESP_LOGE(TAG, "Could not install I2C, invalid arg");
    }
    else if(err == ESP_FAIL){
        ESP_LOGE(TAG, "Could not install I2C, driver install error");
    }
    else{
        ESP_LOGW(TAG, "Unknow I2C install error");
    }
}

std::vector<uint8_t> I2C_protocol::scanBus(){
    std::vector<uint8_t> adresses;

    uint8_t adress;
    for (int i = 0; i < 128; i += 16) {
        for (int j = 0; j < 16; j++) {
            adress = i + j;
            i2c_cmd_handle_t cmd = i2c_cmd_link_create();
            i2c_master_start(cmd);
            i2c_master_write_byte(cmd, (adress << 1) | I2C_MASTER_WRITE, true);
            i2c_master_stop(cmd);
            esp_err_t ret = i2c_master_cmd_begin(I2C_NUM, cmd, 50 / portTICK_RATE_MS);
            i2c_cmd_link_delete(cmd);
            ESP_LOGI(TAG, "Testing I2C adress %d", adress);
            if (ret == ESP_OK) {
                ESP_LOGI(TAG, "Found I2C slave device at %d", adress);
                adresses.push_back(adress);
            }
        }
    }

    return adresses;

}