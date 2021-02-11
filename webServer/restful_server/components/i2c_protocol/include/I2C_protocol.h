#ifndef I2C_PROTOCOL
#define I2C_PROTOCOL


#include "driver/i2c.h"
#include "driver/gpio.h"
#include <vector>
#include <map>


#include "I2C_protocol_messages.h"

#define SDA_PIN GPIO_NUM_21
#define SCL_PIN GPIO_NUM_22
#define I2C_NUM I2C_NUM_0
#define I2C_MASTER_FREQUENCY 10000 //Hz


enum Slave_devices {Drivetrain};


class I2C_protocol
{
    public:
        I2C_protocol();
        std::vector<uint8_t> scanBus();
        void identify_adresses(std::vector<uint8_t> *addresses);

    private:
        i2c_config_t _conf;
        std::map<Slave_devices, uint8_t> slave_address;

        static void sendData(const uint8_t data[], const size_t len, uint8_t address);
        static void readData(uint8_t data[], const size_t len, uint8_t address);
        static void log_I2C_master_cmd_begin_err(esp_err_t ret);


};

#endif