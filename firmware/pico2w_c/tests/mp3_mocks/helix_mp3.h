#pragma once
#include <stdint.h>
#include <stddef.h>
typedef struct {int (*seek)(void *,int);size_t (*read)(void *,void *,size_t);void *user_data;} helix_mp3_io_t;
typedef struct {void *dec;const helix_mp3_io_t *io;uint32_t rate;} helix_mp3_t;
int helix_mp3_init(helix_mp3_t *,const helix_mp3_io_t *);
int helix_mp3_deinit(helix_mp3_t *);
uint32_t helix_mp3_get_sample_rate(helix_mp3_t *);
uint32_t helix_mp3_get_bitrate(helix_mp3_t *);
size_t helix_mp3_read_pcm_frames_s16(helix_mp3_t *,int16_t *,size_t);
