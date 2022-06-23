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
//SRC: https://gist.github.com/rverton/a44fc8ca67ab9ec32089
#define N 256   // 2^8
#define SWAP(a, b) (((a) ^= (b)), ((b) ^= (a)), ((a) ^= (b)))

extern "C" long target_function(uint8_t *key, uint8_t *plaintext)
{
  uint32_t p_len = 5;
  uint8_t ciphertext[p_len];

  uint8_t S[N];

  //KSA
  int j = 0;

  for(int i = 0; i < N; i++)
      S[i] = i;

  for(int i = 0; i < N; i++) {
      j = (j + S[i] + key[i % p_len]) % N;

      SWAP(S[i], S[j]);
  }

  //PRGA
  int i = 0;
  j = 0;

  for(size_t n = 0, len = p_len/*strlen(plaintext)*/; n < len; n++) {
      i = (i + 1) % N;
      j = (j + S[i]) % N;

      SWAP(S[i], S[j]);
      int rnd = S[(S[i] + S[j]) % N];

      ciphertext[n] = rnd ^ plaintext[n];
  }

  int res = 0;
  for (i=0; i < p_len; i++) {
    res+=ciphertext[i];
  }
  return res;
}

int main(int argc, char *argv[]) {
  uint8_t* arg1 = (uint8_t*)argv[1];
  uint8_t* arg2 = (uint8_t*)argv[2];
  double duration_sum = 0;
  long result = 0;
  for (int i = 0; i < 10000; ++i) {
    auto t1 = std::chrono::high_resolution_clock::now();
    result = target_function(arg1, arg2);
    auto t2 = std::chrono::high_resolution_clock::now();
    duration_sum += std::chrono::duration<double, std::micro>( t2 - t1 ).count();
  }
  printf("Output: %lu\nTime: %lfms\n", (uint64_t)result, (duration_sum / 10000));
  return 0;
}
