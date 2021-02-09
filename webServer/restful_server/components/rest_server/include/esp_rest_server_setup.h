#ifndef ESP_REST_SERVER_SETUP
#define ESP_REST_SERVER_SETUP



#include "sdkconfig.h"
#include "driver/gpio.h"
#include "esp_vfs_semihost.h"
#include "esp_vfs_fat.h"
#include "esp_spiffs.h"
#include "sdmmc_cmd.h"
#include "nvs_flash.h"
#include "esp_netif.h"
#include "esp_event.h"
#include "esp_log.h"
#include "mdns.h"
#include "lwip/apps/netbiosns.h"
#include "protocol_examples_common.h"
#if CONFIG_EXAMPLE_WEB_DEPLOY_SD
#include "driver/sdmmc_host.h"
#endif

#include "rest_server.h"

#define MDNS_INSTANCE "esp home web server"


esp_err_t start_rest_server(const char *base_path);
static void initialise_mdns(void);
esp_err_t init_fs(void);
void init_rest_server();

#endif //ESP_REST_SERVER_SETUP