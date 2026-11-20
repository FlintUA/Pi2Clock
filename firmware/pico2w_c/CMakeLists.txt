cmake_minimum_required(VERSION 3.13)

if (NOT DEFINED PICO_SDK_PATH)
    if (DEFINED ENV{PICO_SDK_PATH})
        set(PICO_SDK_PATH "$ENV{PICO_SDK_PATH}")
    else()
        message(FATAL_ERROR "PICO_SDK_PATH is required (install Raspberry Pi Pico extension)")
    endif()
endif()

include("${PICO_SDK_PATH}/external/pico_sdk_import.cmake")

project(speaking_clock_c C CXX ASM)
unset(CLOCK_FIRMWARE_VERSION CACHE) # Remove the former manually maintained value.
unset(CLOCK_BUILD_ID CACHE)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

# Common clock target; optional radio and decoder profiles are configured below.
add_executable(speaking_clock_c
    main.c
    drivers/ds1302.c
    drivers/lcd1602_i2c.c
    app/countdown.c
    app/timer_controls.c
    app/timer_warning.c
    app/music_catalog.c
    app/music_playlist.c
    app/music_retry.c
    app/music_sleep.c
    app/birthday.c
    app/alarm_engine.c
    app/clock_time.c
    drivers/controls.c
    drivers/dfplayer.c
    drivers/sd_spi.c
    drivers/sd_fat32.c
    audio/queue.c
    audio/router.c
    audio/speech.c
    audio/mp3_probe.c
    audio/pcm_ring.c
    services/settings_store.c
)
target_include_directories(speaking_clock_c PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}
    ${CMAKE_CURRENT_LIST_DIR}/drivers
    ${CMAKE_CURRENT_LIST_DIR}/app
    ${CMAKE_CURRENT_LIST_DIR}/audio
    ${CMAKE_CURRENT_LIST_DIR}/services
)
# Use the full 4 KiB SCRATCH_Y bank for the main stack.
target_compile_definitions(speaking_clock_c PRIVATE PICO_STACK_SIZE=0x1000)
target_link_libraries(speaking_clock_c PRIVATE
    pico_rand
    pico_stdlib
    hardware_i2c
    hardware_spi
    hardware_uart
    hardware_sync
    hardware_flash
    hardware_pwm
    pico_flash
    pico_bootrom
)
pico_enable_stdio_usb(speaking_clock_c 1)
pico_enable_stdio_uart(speaking_clock_c 0)

# The known-good production build keeps this OFF.
option(CLOCK_ENABLE_WIFI "Nonblocking Wi-Fi/NTP and Europe/Berlin time" OFF)
if(CLOCK_ENABLE_WIFI)
    if(NOT PICO_BOARD STREQUAL "pico2_w")
        message(FATAL_ERROR "Network time requires PICO_BOARD=pico2_w")
    endif()
    if(NOT EXISTS "${PICO_EXAMPLES_PATH}/pico_w/wifi/lwipopts_examples_common.h")
        message(FATAL_ERROR "Set PICO_EXAMPLES_PATH for network configuration")
    endif()
    target_sources(speaking_clock_c PRIVATE services/network_time.c)
    target_include_directories(speaking_clock_c PRIVATE "${PICO_EXAMPLES_PATH}/pico_w/wifi")
    target_link_libraries(speaking_clock_c PRIVATE pico_cyw43_arch_lwip_threadsafe_background)
    target_compile_definitions(speaking_clock_c PRIVATE CLOCK_ENABLE_WIFI=1)
endif()
option(CLOCK_ENABLE_PHONE_WEB "Read-only phone status and direct Wi-Fi" OFF)
if(CLOCK_ENABLE_PHONE_WEB)
    if(NOT CLOCK_ENABLE_WIFI)
        message(FATAL_ERROR "Phone web status requires CLOCK_ENABLE_WIFI")
    endif()
    set(_phone_dhcp "${PICO_EXAMPLES_PATH}/pico_w/wifi/access_point/dhcpserver")
    if(NOT EXISTS "${_phone_dhcp}/dhcpserver.c")
        message(FATAL_ERROR "The phone web profile requires the pico-examples DHCP server")
    endif()
    # The page is stored gzip-compressed (about a quarter of its size) and served with
    # Content-Encoding: gzip. CLOCK_WEB_GZIP=OFF reproduces the SDK's uncompressed fsdata.
    option(CLOCK_WEB_GZIP "Store and serve the phone page gzip-compressed" ON)
    find_package(Python3 REQUIRED COMPONENTS Interpreter)
    set(_web_page "${CMAKE_CURRENT_LIST_DIR}/services/phone_web/index.html")
    set(_web_tool "${CMAKE_CURRENT_LIST_DIR}/cmake/web_fsdata.py")
    set(_web_dir "${CMAKE_CURRENT_BINARY_DIR}/generated")
    set(_web_gzip_arg)
    if(CLOCK_WEB_GZIP)
        set(_web_gzip_arg --gzip)
    endif()
    add_custom_command(OUTPUT "${_web_dir}/pico_fsdata.inc"
        DEPENDS "${_web_tool}" "${_web_page}"
        COMMAND ${CMAKE_COMMAND} -E make_directory "${_web_dir}"
        COMMAND "${Python3_EXECUTABLE}" "${_web_tool}" -i "${_web_page}" -o "${_web_dir}/pico_fsdata.inc" ${_web_gzip_arg}
        VERBATIM)
    add_custom_target(clock_phone_web_fsdata DEPENDS "${_web_dir}/pico_fsdata.inc")
    pico_add_library(clock_phone_web_content NOFLAG)
    target_include_directories(clock_phone_web_content INTERFACE "${_web_dir}")
    add_dependencies(speaking_clock_c clock_phone_web_fsdata)
    target_sources(speaking_clock_c PRIVATE services/phone_web.c services/phone_bluetooth.c services/phone_network.c services/phone_wifi.c services/wifi_scan.c services/phone_access.c services/phone_overview.c services/phone_control.c "${_phone_dhcp}/dhcpserver.c")
    target_include_directories(speaking_clock_c PRIVATE "${_phone_dhcp}")
    target_link_libraries(speaking_clock_c PRIVATE pico_lwip_http pico_rand clock_phone_web_content)
    target_compile_definitions(speaking_clock_c PRIVATE CLOCK_ENABLE_PHONE_WEB=1)
endif()
option(CLOCK_ENABLE_A2DP "Experimental BTstack A2DP on Pico 2 W" OFF)
if(CLOCK_ENABLE_A2DP)
    if(NOT PICO_BOARD STREQUAL "pico2_w")
        message(FATAL_ERROR "A2DP requires PICO_BOARD=pico2_w")
    endif()
    if(NOT DEFINED PICO_EXAMPLES_PATH)
        get_filename_component(_pico_home "${PICO_SDK_PATH}/../.." ABSOLUTE)
        set(PICO_EXAMPLES_PATH "${_pico_home}/pico-examples")
    endif()
    if(NOT EXISTS "${PICO_EXAMPLES_PATH}/bluetooth/config/btstack_config_common.h")
        message(FATAL_ERROR "Set PICO_EXAMPLES_PATH to your pico-examples checkout")
    endif()
    set(_a2dp_test "${CMAKE_CURRENT_LIST_DIR}/../../experiments/bluetooth_a2dp_nest/nest_autotest")
    set(_a2dp_orig "${PICO_SDK_PATH}/lib/btstack/example/a2dp_source_demo.c")
    set(_a2dp_generated "${CMAKE_CURRENT_BINARY_DIR}/clock_a2dp_source_generated.c")
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        "${_a2dp_orig}" "${_a2dp_test}/patch_a2dp_source.cmake")
    set(CLOCK_A2DP_TARGET_ADDR "" CACHE STRING "Known A2DP target (experimental; local build only)")
    execute_process(COMMAND "${CMAKE_COMMAND}"
        "-DUPSTREAM_SOURCE=${_a2dp_orig}"
        "-DPATCHED_SOURCE=${_a2dp_generated}"
        "-DAUTO_TARGET_ADDR=${CLOCK_A2DP_TARGET_ADDR}"
        -P "${_a2dp_test}/patch_a2dp_source.cmake"
        RESULT_VARIABLE _patch_result)
    if(NOT _patch_result EQUAL 0)
        message(FATAL_ERROR "Could not prepare A2DP source from installed SDK")
    endif()
    target_sources(speaking_clock_c PRIVATE
        services/bt_catalog.c
        "${_a2dp_generated}"
        "${PICO_SDK_PATH}/lib/btstack/src/btstack_audio_generator.c")
    target_include_directories(speaking_clock_c PRIVATE
        "${_a2dp_test}"
        "${PICO_EXAMPLES_PATH}/bluetooth/config"
        "${PICO_SDK_PATH}/lib/btstack/3rd-party/hxcmod-player"
        "${PICO_SDK_PATH}/lib/btstack/3rd-party/hxcmod-player/mods")
    target_link_libraries(speaking_clock_c PRIVATE
        pico_btstack_cyw43
        pico_btstack_ble
        pico_btstack_classic
        pico_btstack_sbc_encoder)
    if(NOT CLOCK_ENABLE_WIFI)
        target_link_libraries(speaking_clock_c PRIVATE pico_cyw43_arch_none)
    endif()
    target_compile_definitions(speaking_clock_c PRIVATE CLOCK_ENABLE_A2DP=1)
    message(STATUS "Bluetooth A2DP enabled")
endif()

# MP3 decoding is opt-in: keep the previously tested clock image unchanged
# unless the user explicitly requests an experiment. Third-party Helix source
# is checked out separately, not vendored into the clock repository.
option(CLOCK_ENABLE_MP3 "Helix MP3 playback from SPI SD for A2DP" OFF)
set(CLOCK_HELIX_PATH "" CACHE PATH "Path to separate Helix-MP3-Decoder checkout")
if(CLOCK_ENABLE_MP3)
    if(NOT EXISTS "${CLOCK_HELIX_PATH}/src/helix_mp3.h" OR
       NOT EXISTS "${CLOCK_HELIX_PATH}/CMakeLists.txt")
        message(FATAL_ERROR "Set CLOCK_HELIX_PATH to a cloned Helix-MP3-Decoder checkout")
    endif()
    set(BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
    add_subdirectory("${CLOCK_HELIX_PATH}" "${CMAKE_CURRENT_BINARY_DIR}/helix_mp3_build")
    target_link_libraries(speaking_clock_c PRIVATE helix_mp3)
    target_compile_definitions(speaking_clock_c PRIVATE CLOCK_ENABLE_MP3=1)
    message(STATUS "SPI SD MP3 playback enabled")
endif()

# A/B bring-up is opt-in and never changes ordinary firmware layout.
option(CLOCK_ENABLE_OTA_AB "RP2350 A/B boot and authenticated browser update" OFF)
option(CLOCK_OTA_TRIAL "Require ROM explicit acceptance for this image" OFF)
option(CLOCK_OTA_TEST_REJECT_TRIAL "Test image: deliberately exercise ROM rollback" OFF)
set(CLOCK_OTA_SEQUENCE "" CACHE STRING "Ordered bootrom version, 1..65535")
if(CLOCK_ENABLE_OTA_AB)
    if(NOT CLOCK_ENABLE_PHONE_WEB OR NOT PICO_BOARD STREQUAL "pico2_w" OR NOT PICO_PLATFORM STREQUAL "rp2350-arm-s")
        message(FATAL_ERROR "OTA A/B requires the Pico 2 W phone-web profile")
    endif()
    if(NOT CLOCK_OTA_SEQUENCE MATCHES "^[1-9][0-9]*$" OR CLOCK_OTA_SEQUENCE GREATER 65535)
        message(FATAL_ERROR "Set CLOCK_OTA_SEQUENCE=1..65535 explicitly")
    endif()
    if(CLOCK_OTA_TEST_REJECT_TRIAL AND NOT CLOCK_OTA_TRIAL)
        message(FATAL_ERROR "Reject-trial testing requires CLOCK_OTA_TRIAL")
    endif()
    file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/ota_slot_guard.ld" "ASSERT(__flash_binary_end <= 0x10180000, \"OTA application exceeds 1536 KiB slot\");\n")
    target_link_options(speaking_clock_c PRIVATE "LINKER:-T,${CMAKE_CURRENT_BINARY_DIR}/ota_slot_guard.ld")
    target_sources(speaking_clock_c PRIVATE services/ota_layout.c services/ota_boot.c services/ota_upload.c services/ota_image.c services/phone_ota.c)
    target_link_libraries(speaking_clock_c PRIVATE pico_sha256)
    target_compile_definitions(speaking_clock_c PRIVATE CLOCK_ENABLE_OTA_AB=1 CLOCK_OTA_SEQUENCE=${CLOCK_OTA_SEQUENCE})
    if(CLOCK_OTA_TRIAL)
        target_compile_definitions(speaking_clock_c PRIVATE PICO_CRT0_IMAGE_TYPE_TBYB=1)
    endif()
    if(CLOCK_OTA_TEST_REJECT_TRIAL)
        target_compile_definitions(speaking_clock_c PRIVATE CLOCK_OTA_TEST_REJECT_TRIAL=1)
    endif()
    pico_set_binary_version(speaking_clock_c MAJOR 1 MINOR ${CLOCK_OTA_SEQUENCE})
    pico_hash_binary(speaking_clock_c)
endif()

# Resolve identity after all profile options, and refresh before every build.
get_filename_component(CLOCK_SOURCE_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(CLOCK_VERSION_TEMPLATE "${CMAKE_CURRENT_LIST_DIR}/firmware_version.h.in")
set(CLOCK_VERSION_HEADER "${CMAKE_CURRENT_BINARY_DIR}/firmware_version.h")
set(CLOCK_VERSION_ID_FILE "${CMAKE_CURRENT_BINARY_DIR}/speaking_clock_c.build-id.txt")
set(CLOCK_BUILD_PROFILE "")
if(CLOCK_ENABLE_A2DP)
    string(APPEND CLOCK_BUILD_PROFILE "-bt")
endif()
if(CLOCK_ENABLE_MP3)
    string(APPEND CLOCK_BUILD_PROFILE "-mp3")
endif()
if(CLOCK_ENABLE_WIFI)
    string(APPEND CLOCK_BUILD_PROFILE "-wifi")
endif()
if(CLOCK_ENABLE_PHONE_WEB)
    string(APPEND CLOCK_BUILD_PROFILE "-phone")
endif()
if(CLOCK_ENABLE_OTA_AB)
    string(APPEND CLOCK_BUILD_PROFILE "-ota${CLOCK_OTA_SEQUENCE}")
    if(CLOCK_OTA_TRIAL)
        string(APPEND CLOCK_BUILD_PROFILE "-trial")
    endif()
    if(CLOCK_OTA_TEST_REJECT_TRIAL)
        string(APPEND CLOCK_BUILD_PROFILE "-reject")
    endif()
endif()
include(cmake/git_version.cmake)
add_custom_target(clock_version
    COMMAND "${CMAKE_COMMAND}" "-DCLOCK_SOURCE_ROOT=${CLOCK_SOURCE_ROOT}"
        "-DCLOCK_VERSION_TEMPLATE=${CLOCK_VERSION_TEMPLATE}"
        "-DCLOCK_VERSION_HEADER=${CLOCK_VERSION_HEADER}"
        "-DCLOCK_VERSION_ID_FILE=${CLOCK_VERSION_ID_FILE}"
        "-DCLOCK_BUILD_PROFILE=${CLOCK_BUILD_PROFILE}"
        -P "${CMAKE_CURRENT_LIST_DIR}/cmake/git_version.cmake"
    BYPRODUCTS "${CLOCK_VERSION_HEADER}" "${CLOCK_VERSION_ID_FILE}"
    VERBATIM)
add_dependencies(speaking_clock_c clock_version)


pico_add_extra_outputs(speaking_clock_c)
