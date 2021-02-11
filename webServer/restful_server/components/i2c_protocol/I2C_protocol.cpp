#include "I2C_protocol.h"

#include "esp_log.h"


static const char* TAG = "I2C_protocol";


I2C_protocol::I2C_protocol(){

    _conf.mode = I2C_MODE_MASTER;
    _conf.sda_io_num = SDA_PIN;
    _conf.sda_pullup_en = GPIO_PULLUP_ENABLE;
    _conf.scl_io_num = SCL_PIN;
    _conf.scl_pullup_en = GPIO_PULLUP_ENABLE;
    _conf.master.clk_speed = I2C_MASTER_FREQUENCY;  
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
        ESP_LOGI(TAG, "I2C driver install succes");
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

    for (uint8_t i = 0; i < 128; ++i) {
        i2c_cmd_handle_t cmd = i2c_cmd_link_create();
        i2c_master_start(cmd);
        i2c_master_write_byte(cmd, (i << 1) | I2C_MASTER_WRITE, I2C_MASTER_ACK);
        i2c_master_stop(cmd);
        esp_err_t ret = i2c_master_cmd_begin(I2C_NUM, cmd, 50 / portTICK_RATE_MS);
        i2c_cmd_link_delete(cmd);
        //ESP_LOGI(TAG, "Testing I2C adress %d", i);
        if (ret == ESP_OK) {
            ESP_LOGI(TAG, "Found I2C slave device with address : %d", i);
            adresses.push_back(i);
        }  
    }

    return adresses;
}  

void I2C_protocol::identify_adresses(std::vector<uint8_t> *addresses){

    for(std::vector<uint8_t>::iterator it = addresses->begin(); it != addresses->end(); ++it){
        sendData(command_identify, sizeof(command_identify), *it);
    }
}

void I2C_protocol::sendData(const uint8_t data[], const size_t len, uint8_t address){
    
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (address << 1) | I2C_MASTER_WRITE, I2C_MASTER_ACK);
    i2c_master_write(cmd, data, len, true);
    i2c_master_stop(cmd);
    I2C_protocol::log_I2C_master_cmd_begin_err( i2c_master_cmd_begin(I2C_NUM, cmd, 1000 / portTICK_RATE_MS) );
    i2c_cmd_link_delete(cmd);
}

void I2C_protocol::readData(uint8_t data[], const size_t len, uint8_t address){
    if (len == 0) {
        return;
    }
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (address << 1) | I2C_MASTER_READ, I2C_MASTER_ACK);
    if (len > 1) {
        i2c_master_read(cmd, data, len - 1, I2C_MASTER_ACK);
    }
    i2c_master_read_byte(cmd, data + len - 1, I2C_MASTER_LAST_NACK); //I2C protocols declares that the master needs to end the read with an nack
    i2c_master_stop(cmd);
    I2C_protocol::log_I2C_master_cmd_begin_err( i2c_master_cmd_begin(I2C_NUM, cmd, 1000 / portTICK_RATE_MS) );
    i2c_cmd_link_delete(cmd);
}

void I2C_protocol::log_I2C_master_cmd_begin_err(esp_err_t err){
    if(err == ESP_ERR_INVALID_ARG){
        ESP_LOGE(TAG, "Error sending I2C message : invalid arg");
    }
    else if(err == ESP_FAIL){
        ESP_LOGE(TAG, "Could send I2C message : Sending command error, slave doesn’t ACK the transfer");
    }
    else if(err == ESP_ERR_INVALID_STATE){
        ESP_LOGE(TAG, "Error sending I2C message : I2C driver not installed or not in master mode.");
    }
    else if(err == ESP_ERR_TIMEOUT){
        ESP_LOGE(TAG, "Error sending I2C message : Operation timeout because the bus is busy.");
    }
    else{
        ESP_LOGW(TAG, "Error sending I2C message : Unknown error");
    }
}