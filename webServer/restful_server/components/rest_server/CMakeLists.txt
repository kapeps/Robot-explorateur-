idf_component_register(
                    SRCS "esp_rest_server_setup.c" "rest_server.c" 
                    INCLUDE_DIRS "include"
                    REQUIRES protocol_examples_common fatfs spiffs nvs_flash mdns esp_http_server json led_blink)


