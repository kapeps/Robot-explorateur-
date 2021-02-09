#ifndef I2C_PROTOCOL
#define I2C_PROTOCOL


#include "driver/i2c.h"
#include "driver/gpio.h"
#include <vector>

#define SDA_PIN GPIO_NUM_21
#define SCL_PIN GPIO_NUM_22
#define I2C_NUM I2C_NUM_0

class I2C_protocol
{
    public:
        I2C_protocol();
        std::vector<uint8_t> scanBus();

    private:
        i2c_config_t _conf;
        i2c_cmd_handle_t _handler;

};

#endif