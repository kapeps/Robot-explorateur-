#ifndef I2C_SELFTEST
#define I2C_SELFTEST

#include "I2C_protocol.h"
#include "driver/gpio.h"
#include "driver/i2c.h"

#define DATA_LENGTH 512                  /*!< Data buffer length of test buffer */
#define DELAY_TIME_BETWEEN_ITEMS_MS 1000 /*!< delay time between different test items */


#define I2C_SLAVE_SCL_IO GPIO_NUM_18                 /*!< gpio number for i2c slave clock */
#define I2C_SLAVE_SDA_IO GPIO_NUM_19                 /*!< gpio number for i2c slave data */
#define I2C_SLAVE_NUM I2C_NUM_1                     /*!< I2C port number for slave dev */
#define I2C_SLAVE_TX_BUF_LEN (2 * DATA_LENGTH)      /*!< I2C slave tx buffer size */
#define I2C_SLAVE_RX_BUF_LEN (2 * DATA_LENGTH)      /*!< I2C slave rx buffer size */
#define ESP_SLAVE_ADDR 0x24


//Initalizes the I2C_SLAVE_NUM I2C driver to be a slave and launches the task
void i2c_slave_init();


#endif