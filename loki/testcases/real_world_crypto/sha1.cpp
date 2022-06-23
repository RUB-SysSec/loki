
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <chrono>
#include <string>

struct Foo
{
  int a, b, c;
};

extern Foo foo;

/*
    orig Source: https://github.com/jasinb/sha1/blob/master/sha1.c

    SHA1 Algorithm to encrypt 55byte blocks
*/
#define ROTL32(value, bits) (((value) << (bits)) | ((value) >> (32 - (bits))))

// typedef struct
// {
//   uint8_t block[64];
//   uint32_t h[5];
//   uint64_t bytes;
//   uint32_t cur;
// } sha1_ctx;

static const uint32_t g_k[4] =
{
  0x5A827999,
  0x6ED9EBA1,
  0x8F1BBCDC,
  0xCA62C1D6
};

extern "C" long target_function(uint8_t *data)
{
  uint32_t k[4];

  for(uint32_t i = 0; i < 4; i++) {
    k[i] = g_k[i];
  }

  // 55 is max here!
  size_t data_len = 55;

  // sha1_ctx ctx;

  uint8_t ctx_block[64];
  uint32_t ctx_h[5];
  uint64_t ctx_bytes; 
  uint32_t ctx_cur;

  // Init sh1 ctx
  ctx_h[0] = 0x67452301;
  ctx_h[1] = 0xefcdab89;
  ctx_h[2] = 0x98badcfe;
  ctx_h[3] = 0x10325476;
  ctx_h[4] = 0xc3d2e1f0;
  ctx_bytes = data_len;
  ctx_cur = 0;

  // ln 128 in orig sha1.c: prevent additional call to processBlock by keeping size < 56
  for (size_t i = 0; i < data_len; i++) {
    ctx_block[i] = data[i];
    ctx_cur++;
  }

  //printf("blocksize : %u\n", ctx_cur);

  ctx_block[ctx_cur++] = 0x80;

  uint64_t bits = ctx_bytes * 8;

  ctx_block[56] = (uint8_t)(bits >> 56 & 0xff);
  ctx_block[57] = (uint8_t)(bits >> 48 & 0xff);
  ctx_block[58] = (uint8_t)(bits >> 40 & 0xff);
  ctx_block[59] = (uint8_t)(bits >> 32 & 0xff);
  ctx_block[60] = (uint8_t)(bits >> 24 & 0xff);
  ctx_block[61] = (uint8_t)(bits >> 16 & 0xff);
  ctx_block[62] = (uint8_t)(bits >> 8  & 0xff);
  ctx_block[63] = (uint8_t)(bits >> 0  & 0xff);

  /*for (int i = 0; i < 64; i++) {
    if(i%16==0 && i != 0) printf("\n");
    printf("%x, ", ctx_block[i]);
  }
  printf("\n");*/

  uint32_t w[16];
  uint32_t a = ctx_h[0];
  uint32_t b = ctx_h[1];
  uint32_t c = ctx_h[2];
  uint32_t d = ctx_h[3];
  uint32_t e = ctx_h[4];
  int t;

  for (t = 0; t < 16; t++) {
    uint8_t *te = (uint8_t*)(&(ctx_block[t*4]));
    w[t] = ( te[0] << 24) | (te[1] << 16) | (te[2] << 8) | te[3];
    //printf("%x Byte: %x\n", te, w[t]);
  }
  for (t = 0; t < 80; t++)
  {
    int s = t & 0xf;
    uint32_t temp;
    if (t >= 16)
      w[s] = ROTL32(w[(s + 13) & 0xf] ^ w[(s + 8) & 0xf] ^ w[(s + 2) & 0xf] ^ w[s], 1);

    uint32_t f = 0;

    if (t < 80)
      f =  b ^ c ^ d;
    if (t < 60)
      f = (b & c) | (b & d) | (c & d);
    if (t < 40)
      f = b ^ c ^ d;
    if (t < 20)
      f = (b & c) | ((~b) & d);

    temp = ROTL32(a, 5) + f + e + w[s] + k[t/20];

    e = d; d = c; c = ROTL32(b, 30); b = a; a = temp;

    //printf("ws: %x f %x temp: %x a %x b %x c %x \n", w[s],f, temp, a, b, c);
  }

  ctx_h[0] += a;
  ctx_h[1] += b;
  ctx_h[2] += c;
  ctx_h[3] += d;
  ctx_h[4] += e;

  long sum = 0;

  for (uint8_t i = 0; i < 5; i++) {
    sum += (long)ctx_h[i];
  }

  return sum;
}

int main(int argc, char *argv[]) {
  if (argc < 2) {
    printf("Expected %d parameters\n", 1);
    return -1;
  }
  uint8_t* arg1 = (uint8_t*)argv[1];
  double duration_sum = 0;
  long result = 0;
  for (int i = 0; i < 10000; ++i) {
    auto t1 = std::chrono::high_resolution_clock::now();
    result = target_function(arg1);
    auto t2 = std::chrono::high_resolution_clock::now();
    duration_sum += std::chrono::duration<double, std::micro>( t2 - t1 ).count();
  }
  printf("Output: %lu\nTime: %lfms\n", (uint64_t)result, (duration_sum / 10000));
  return 0;
}
