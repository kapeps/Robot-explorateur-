#ifndef I2C_SELFTEST
#define I2C_SELFTEST

#include "I2C_protocol.h"
#include "driver/gpio.h"
#include "driver/i2c.h"

#define I2C_SLAVE_SCL_IO GPIO_NUM_18                 /*!< gpio number for i2c slave clock */
#define I2C_SLAVE_SDA_IO GPIO_NUM_19                 /*!< gpio number for i2c slave data */
#define I2C_SLAVE_NUM I2C_NUM_1                     /*!< I2C port number for slave dev */
#define I2C_SLAVE_TX_BUF_LEN (2 * DATA_LENGTH)      /*!< I2C slave tx buffer size */
#define I2C_SLAVE_RX_BUF_LEN (2 * DATA_LENGTH)      /*!< I2C slave rx buffer size */
#define ESP_SLAVE_ADDR 0x24

esp_err_t i2c_slave_init()
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
        return err;
    }
    return i2c_driver_install(I2C_SLAVE_NUM, conf_slave.mode, I2C_SLAVE_RX_BUF_LEN, I2C_SLAVE_TX_BUF_LEN, 0);
}

#endif