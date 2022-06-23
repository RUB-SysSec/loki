#include <cstdint>
#include <cstdio>
#include <cstring>
#include <chrono>
#include <string>
struct Foo {
  int a, b, c;
};
extern Foo foo;
extern "C" long target_function(unsigned long r0, unsigned long r1) {
  unsigned long n = 1;
  unsigned long count = 0;
  unsigned long result = 0;
  for(count=0; count <= n; count++)    /* for loop terminates if count>n */
  {
    result += r0 + r1;
  }
  return result;
}
int main(int argc, char *argv[]) {
  unsigned long arg1 = std::stoull(argv[1]);
  unsigned long arg2 = std::stoull(argv[2]);
  if (argc < 3) {
    return -1;
  }
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
