
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

// len(input_str) must be at least 8 bytes (DES KEY), otherwise => segfault
extern "C" long target_function(uint8_t *input_str) {
    int key_shift_sizes[] = {-1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1};

    int initial_key_permutaion[] = {57, 49, 41, 33, 25, 17, 9,
                                    1, 58, 50, 42, 34, 26, 18,
                                    10, 2, 59, 51, 43, 35, 27,
                                    19, 11, 3, 60, 52, 44, 36,
                                    63, 55, 47, 39, 31, 23, 15,
                                    7, 62, 54, 46, 38, 30, 22,
                                    14, 6, 61, 53, 45, 37, 29,
                                    21, 13, 5, 28, 20, 12, 4};

    int sub_key_permutation[] = {14, 17, 11, 24, 1, 5,
                                 3, 28, 15, 6, 21, 10,
                                 23, 19, 12, 4, 26, 8,
                                 16, 7, 27, 20, 13, 2,
                                 41, 52, 31, 37, 47, 55,
                                 30, 40, 51, 45, 33, 48,
                                 44, 49, 39, 56, 34, 53,
                                 46, 42, 50, 36, 29, 32};
    //KEY_SET https://github.com/binsec/hade/blob/master/experimental_data/src/realWorld/des.h

    uint8_t *main_key = input_str;

    // the for loop produces bitcast i8* to i64* which is not implemented yet
    //DES KEY
    //uint8_t main_key[8];// = {0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70, 0x80};
    /*for (int i = 0; i <8 ; i++) {
    main_key[i] = input_str[i];
  }*/

    typedef struct
    {
        unsigned char k[8];
        unsigned char c[4];
        unsigned char d[4];
    } key_set;

    key_set key_sets[17];

    int i, j;
    int shift_size;
    unsigned char shift_byte, first_shift_bits, second_shift_bits, third_shift_bits, fourth_shift_bits;

    for (i = 0; i < 8; i++)
    {
        key_sets[0].k[i] = 0;
    }

    for (i = 0; i < 56; i++)
    {
        shift_size = initial_key_permutaion[i];
        shift_byte = 0x80 >> ((shift_size - 1) % 8);
        shift_byte &= main_key[(shift_size - 1) / 8];
        shift_byte <<= ((shift_size - 1) % 8);

        key_sets[0].k[i / 8] |= (shift_byte >> i % 8);
    }

    for (i = 0; i < 3; i++)
    {
        key_sets[0].c[i] = key_sets[0].k[i];
    }

    key_sets[0].c[3] = key_sets[0].k[3] & 0xF0;

    for (i = 0; i < 3; i++)
    {
        key_sets[0].d[i] = (key_sets[0].k[i + 3] & 0x0F) << 4;
        key_sets[0].d[i] |= (key_sets[0].k[i + 4] & 0xF0) >> 4;
    }

    key_sets[0].d[3] = (key_sets[0].k[6] & 0x0F) << 4;

    for (i = 1; i < 17; i++)
    {
        for (j = 0; j < 4; j++)
        {
            key_sets[i].c[j] = key_sets[i - 1].c[j];
            key_sets[i].d[j] = key_sets[i - 1].d[j];
        }

        shift_size = key_shift_sizes[i];
        if (shift_size == 1)
        {
            shift_byte = 0x80;
        }
        else
        {
            shift_byte = 0xC0;
        }

        /*
        int if_res = (shift_size == 1);
        shift_byte = 0xC0 - (if_res*0x40); // if shiftsize == 1 then: 0xC0 - 0x40 = 0x80 , else 0xC0
        */

        // Process C
        first_shift_bits = shift_byte & key_sets[i].c[0];
        second_shift_bits = shift_byte & key_sets[i].c[1];
        third_shift_bits = shift_byte & key_sets[i].c[2];
        fourth_shift_bits = shift_byte & key_sets[i].c[3];

        key_sets[i].c[0] <<= shift_size;
        key_sets[i].c[0] |= (second_shift_bits >> (8 - shift_size));

        key_sets[i].c[1] <<= shift_size;
        key_sets[i].c[1] |= (third_shift_bits >> (8 - shift_size));

        key_sets[i].c[2] <<= shift_size;
        key_sets[i].c[2] |= (fourth_shift_bits >> (8 - shift_size));

        key_sets[i].c[3] <<= shift_size;
        key_sets[i].c[3] |= (first_shift_bits >> (4 - shift_size));

        // Process D
        first_shift_bits = shift_byte & key_sets[i].d[0];
        second_shift_bits = shift_byte & key_sets[i].d[1];
        third_shift_bits = shift_byte & key_sets[i].d[2];
        fourth_shift_bits = shift_byte & key_sets[i].d[3];

        key_sets[i].d[0] <<= shift_size;
        key_sets[i].d[0] |= (second_shift_bits >> (8 - shift_size));

        key_sets[i].d[1] <<= shift_size;
        key_sets[i].d[1] |= (third_shift_bits >> (8 - shift_size));

        key_sets[i].d[2] <<= shift_size;
        key_sets[i].d[2] |= (fourth_shift_bits >> (8 - shift_size));

        key_sets[i].d[3] <<= shift_size;
        key_sets[i].d[3] |= (first_shift_bits >> (4 - shift_size));

        for (j = 0; j < 48; j++)
        {
            shift_size = sub_key_permutation[j];
            // OLD
            if (shift_size <= 28)
            {
                shift_byte = 0x80 >> ((shift_size - 1) % 8);
                shift_byte &= key_sets[i].c[(shift_size - 1) / 8];
                shift_byte <<= ((shift_size - 1) % 8);
            }
            else
            {
                shift_byte = 0x80 >> ((shift_size - 29) % 8);
                shift_byte &= key_sets[i].d[(shift_size - 29) / 8];
                shift_byte <<= ((shift_size - 29) % 8);
            }
            /*
            // NEW
            uint8_t if_b = (shift_size > 28);
            uint8_t if_val = if_b * 28;

            shift_byte = 0x80 >> ((shift_size - (1+if_val)) % 8);
            shift_byte &= key_sets[i].c[(shift_size - (1+if_val)) / 8];
            shift_byte <<= ((shift_size - (1+if_val)) % 8);
            */
            key_sets[i].k[j / 8] |= (shift_byte >> j % 8);
        }
    }

    return key_sets[10].d[0] + key_sets[10].d[1] + key_sets[10].c[0] + key_sets[4].k[7];
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
