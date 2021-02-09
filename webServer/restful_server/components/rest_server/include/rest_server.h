#ifndef REST_SERVER
#define REST_SERVER

#include <string.h>
#include <fcntl.h>
#include "esp_http_server.h"
#include "esp_system.h"
#include "esp_log.h"
#include "esp_vfs.h"
#include "cJSON.h"


#define FILE_PATH_MAX (ESP_VFS_PATH_MAX + 128)
#define SCRATCH_BUFSIZE (10240)

typedef struct rest_server_context {
    char base_path[ESP_VFS_PATH_MAX + 1];
    char scratch[SCRATCH_BUFSIZE];
} rest_server_context_t;

#define CHECK_FILE_EXTENSION(filename, ext) (strcasecmp(&filename[strlen(filename) - strlen(ext)], ext) == 0)

/* Set HTTP response content type according to file extension */
static esp_err_t set_content_type_from_file(httpd_req_t *req, const char *filepath);

/* Send HTTP response with the contents of the requested file */
static esp_err_t rest_common_get_handler(httpd_req_t *req);

/* Simple handler for light brightness control */
static esp_err_t light_brightness_post_handler(httpd_req_t *req);

static esp_err_t led_post_handler(httpd_req_t *req);

/* Simple handler for getting system handler */
static esp_err_t system_info_get_handler(httpd_req_t *req);

/* Simple handler for getting temperature data */
static esp_err_t temperature_data_get_handler(httpd_req_t *req);

esp_err_t start_rest_server(const char *base_path);

#endif //REST_SERVER