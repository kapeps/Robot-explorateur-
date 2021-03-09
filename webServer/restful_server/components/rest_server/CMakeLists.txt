idf_component_register(
                    SRCS "rest_server.cpp" "esp_rest_server_setup.cpp" 
                    INCLUDE_DIRS "include"
                    REQUIRES protocol_examples_common fatfs spiffs nvs_flash mdns esp_http_server json led_blink i2c_protocol)


if(CONFIG_EXAMPLE_WEB_DEPLOY_SF)
    set(WEB_SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/front/web-demo")
    if(EXISTS ${WEB_SRC_DIR}/dist)
        spiffs_create_partition_image(www ${WEB_SRC_DIR}/dist FLASH_IN_PROJECT)
    else()
        message(FATAL_ERROR "${WEB_SRC_DIR}/dist doesn't exit. Please run 'npm run build' in ${WEB_SRC_DIR}")
    endif()
endif()