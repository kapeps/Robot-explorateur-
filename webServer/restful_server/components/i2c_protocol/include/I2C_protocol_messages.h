#ifndef I2C_PROTOCOL_MESSAGES_H
#define I2C_PROTOCOL_MESSAGES_H

#define DATA_LENGTH 512                  /*!< Data buffer length of test buffer */
#define DELAY_TIME_BETWEEN_ITEMS_MS 1000 /*!< delay time between different test items */

static const uint8_t id_drivetrain[] = {'d','i','v','e','t','r','a','i','n','\n'};


//Command sent to a slave to request his id
static const uint8_t command_identify[] = {'i','d','r','e','q','u','e','s','t','\n'};



#endif //I2C_PROTOCOL_MESSAGES_H