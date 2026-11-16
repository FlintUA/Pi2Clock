#include "ota_image.h"
#include <string.h>
static uint32_t word(const uint8_t *p) {uint32_t v;memcpy(&v,p,4);return v;}
bool ota_image_block(const uint8_t *b,uint32_t bytes,uint32_t sequence,uint32_t *next) {
    if(bytes<28 || word(b)!=0xffffded3u)return false;
    bool type=false,version=false,hash=false;uint32_t i=4;
    while(i+4<=bytes && i<384u) {
        uint32_t item=word(b+i),tag=item&255u;
        if(tag==255u) {
            if((item>>8)!=(i-4u)/4u || i+12u>bytes || word(b+i+8)!=0xab123579u)return false;
            *next=word(b+i+4);return type && version && (bytes<=32u || hash);
        }
        uint32_t count=(item>>8)&255u;
        if(!count || i+count*4u>bytes || (tag&128u))return false;
        if(tag==0x42u) {if(type || item!=0x90210142u)return false;type=true;}
        if(tag==0x48u) {if(version || count!=2u || word(b+i+4)!=(0x10000u|sequence))return false;version=true;}
        if(tag==0x4bu)hash=count==9u;
        if(tag==0x0au)return false;
        i+=count*4u;
    }
    return false;
}
