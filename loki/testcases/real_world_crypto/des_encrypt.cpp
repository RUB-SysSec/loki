
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

#define ENCRYPTION_MODE 1

/* constant key schedule arrays */
const int key_shift_sizes_glob[] = {-1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1};

const int initial_key_permutation_glob[] = {57, 49, 41, 33, 25, 17, 9,
                                  1, 58, 50, 42, 34, 26, 18,
                                  10, 2, 59, 51, 43, 35, 27,
                                  19, 11, 3, 60, 52, 44, 36,
                                  63, 55, 47, 39, 31, 23, 15,
                                  7, 62, 54, 46, 38, 30, 22,
                                  14, 6, 61, 53, 45, 37, 29,
                                  21, 13, 5, 28, 20, 12, 4};

const int sub_key_permutation_glob[] = {14, 17, 11, 24, 1, 5,
                               3, 28, 15, 6, 21, 10,
                               23, 19, 12, 4, 26, 8,
                               16, 7, 27, 20, 13, 2,
                               41, 52, 31, 37, 47, 55,
                               30, 40, 51, 45, 33, 48,
                               44, 49, 39, 56, 34, 53,
                               46, 42, 50, 36, 29, 32};

/* constant encryption arrays */ 
const int initial_message_permutation_glob[] = {58, 50, 42, 34, 26, 18, 10, 2,
                                       60, 52, 44, 36, 28, 20, 12, 4,
                                       62, 54, 46, 38, 30, 22, 14, 6,
                                       64, 56, 48, 40, 32, 24, 16, 8,
                                       57, 49, 41, 33, 25, 17, 9, 1,
                                       59, 51, 43, 35, 27, 19, 11, 3,
                                       61, 53, 45, 37, 29, 21, 13, 5,
                                       63, 55, 47, 39, 31, 23, 15, 7};

const int message_expansion_glob[] = {32, 1, 2, 3, 4, 5,
                             4, 5, 6, 7, 8, 9,
                             8, 9, 10, 11, 12, 13,
                             12, 13, 14, 15, 16, 17,
                             16, 17, 18, 19, 20, 21,
                             20, 21, 22, 23, 24, 25,
                             24, 25, 26, 27, 28, 29,
                             28, 29, 30, 31, 32, 1};

const int S1_glob[] = {14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7,
              0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8,
              4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0,
              15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13};

const int S2_glob[] = {15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10,
              3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5,
              0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15,
              13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9};

const int S3_glob[] = {10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8,
              13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1,
              13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7,
              1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12};

const int S4_glob[] = {7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15,
              13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9,
              10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4,
              3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14};

const int S5_glob[] = {2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9,
              14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6,
              4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14,
              11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3};

const int S6_glob[] = {12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11,
              10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8,
              9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6,
              4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13};

const int S7_glob[] = {4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1,
              13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6,
              1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2,
              6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12};

const int S8_glob[] = {13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7,
              1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2,
              7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8,
              2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11};

const int right_sub_message_permutation_glob[] = {16, 7, 20, 21,
                                         29, 12, 28, 17,
                                         1, 15, 23, 26,
                                         5, 18, 31, 10,
                                         2, 8, 24, 14,
                                         32, 27, 3, 9,
                                         19, 13, 30, 6,
                                         22, 11, 4, 25};

const int final_message_permutation_glob[] = {40, 8, 48, 16, 56, 24, 64, 32,
                                     39, 7, 47, 15, 55, 23, 63, 31,
                                     38, 6, 46, 14, 54, 22, 62, 30,
                                     37, 5, 45, 13, 53, 21, 61, 29,
                                     36, 4, 44, 12, 52, 20, 60, 28,
                                     35, 3, 43, 11, 51, 19, 59, 27,
                                     34, 2, 42, 10, 50, 18, 58, 26,
                                     33, 1, 41, 9, 49, 17, 57, 25};

typedef struct
{
  unsigned char k[8] = {};
  unsigned char c[4] = {};
  unsigned char d[4] = {};
} key_set;

// Important: encrypt mode only!
// len(input_str) must be at least 8 bytes (msg to encrypt), otherwise => segfault
extern "C" long target_function(uint8_t *input_str, uint8_t *key_input)
{

  int initial_message_permutation[64];
  int message_expansion[48];
  int S1[64];
  int S2[64];
  int S3[64];
  int S4[64];
  int S5[64];
  int S6[64];
  int S7[64];
  int S8[64];
  int right_sub_message_permutation[32];
  int final_message_permutation[64];
  // key_set key_sets[17];

  for (uint32_t i = 0; i < 64; ++i)
  {
    initial_message_permutation[i] = initial_message_permutation_glob[i];
  }

  for (uint32_t i = 0; i < 48; ++i)
  {
    message_expansion[i] = message_expansion_glob[i];
  }

  for (uint32_t i = 0; i < 64; ++i)
  {
    S1[i] = S1_glob[i];
    S2[i] = S2_glob[i];
    S3[i] = S3_glob[i];
    S4[i] = S4_glob[i];
    S5[i] = S5_glob[i];
    S6[i] = S6_glob[i];
    S7[i] = S7_glob[i];
    S8[i] = S8_glob[i];
  }

  for (uint32_t i = 0; i < 32; ++i)
  {
    right_sub_message_permutation[i] = right_sub_message_permutation_glob[i];
  }

  for (uint32_t i = 0; i < 64; ++i)
  {
    final_message_permutation[i] = final_message_permutation_glob[i];
  }

  /* Initialize key schedule constant arrays: */
  int key_shift_sizes[17];
  int initial_key_permutation[56];
  int sub_key_permutation[48];

  for (int i = 0; i < 17; i++)
  {
    key_shift_sizes[i] = key_shift_sizes_glob[i];
  } 

  for (int i = 0; i < 56; i++)
  {
    initial_key_permutation[i] = initial_key_permutation_glob[i];
  } 

  for (int i = 0; i < 48; i++)
  {
    sub_key_permutation[i] = sub_key_permutation_glob[i];
  } 
  
  uint8_t *main_key = key_input;


  // key_set key_sets[17] = {}; // we can't handle that struct's padding/alignment
  uint8_t key_sets_k[17][8] = {{0}, {0}, {0}, {0}, {0}, {0}, {0}, {0}};
  uint8_t key_sets_c[17][4] = {{0}, {0}, {0}, {0}};
  uint8_t key_sets_d[17][4] = {{0}, {0}, {0}, {0}};

  int i, j;
  int shift_size;
  unsigned char shift_byte, first_shift_bits, second_shift_bits, third_shift_bits, fourth_shift_bits;

  for (i = 0; i < 8; i++)
  {
      key_sets_k[0][i] = 0;
  }

  for (i = 0; i < 56; i++)
  {
      shift_size = initial_key_permutation[i];
      shift_byte = 0x80 >> ((shift_size - 1) % 8);
      shift_byte &= main_key[(shift_size - 1) / 8];
      shift_byte <<= ((shift_size - 1) % 8);

      key_sets_k[0][i / 8] |= (shift_byte >> i % 8);
  }

  for (i = 0; i < 3; i++)
  {
      key_sets_c[0][i] = key_sets_k[0][i];
  }

  key_sets_c[0][3] = key_sets_k[0][3] & 0xF0;

  for (i = 0; i < 3; i++)
  {
      key_sets_d[0][i] = (key_sets_k[0][i + 3] & 0x0F) << 4;
      key_sets_d[0][i] |= (key_sets_k[0][i + 4] & 0xF0) >> 4;
  }

  key_sets_d[0][3] = (key_sets_k[0][6] & 0x0F) << 4;

  for (i = 1; i < 17; i++)
  {
      for (j = 0; j < 4; j++)
      {
          key_sets_c[i][j] = key_sets_c[i - 1][j];
          key_sets_d[i][j] = key_sets_d[i - 1][j];
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

      /* IF delete:
      int if_res = (shift_size == 1);
      shift_byte = 0xC0 - (if_res*0x40); // if shiftsize == 1 then: 0xC0 - 0x40 = 0x80 , else 0xC0
      */

      // Process C
      first_shift_bits = shift_byte & key_sets_c[i][0];
      second_shift_bits = shift_byte & key_sets_c[i][1];
      third_shift_bits = shift_byte & key_sets_c[i][2];
      fourth_shift_bits = shift_byte & key_sets_c[i][3];

      key_sets_c[i][0] <<= shift_size;
      key_sets_c[i][0] |= (second_shift_bits >> (8 - shift_size));

      key_sets_c[i][1] <<= shift_size;
      key_sets_c[i][1] |= (third_shift_bits >> (8 - shift_size));

      key_sets_c[i][2] <<= shift_size;
      key_sets_c[i][2] |= (fourth_shift_bits >> (8 - shift_size));

      key_sets_c[i][3] <<= shift_size;
      key_sets_c[i][3] |= (first_shift_bits >> (4 - shift_size));

      // Process D
      first_shift_bits = shift_byte & key_sets_d[i][0];
      second_shift_bits = shift_byte & key_sets_d[i][1];
      third_shift_bits = shift_byte & key_sets_d[i][2];
      fourth_shift_bits = shift_byte & key_sets_d[i][3];

      key_sets_d[i][0] <<= shift_size;
      key_sets_d[i][0] |= (second_shift_bits >> (8 - shift_size));

      key_sets_d[i][1] <<= shift_size;
      key_sets_d[i][1] |= (third_shift_bits >> (8 - shift_size));

      key_sets_d[i][2] <<= shift_size;
      key_sets_d[i][2] |= (fourth_shift_bits >> (8 - shift_size));

      key_sets_d[i][3] <<= shift_size;
      key_sets_d[i][3] |= (first_shift_bits >> (4 - shift_size));

      for (j = 0; j < 48; j++)
      {
          shift_size = sub_key_permutation[j];
          // OLD
          if (shift_size <= 28)
          {
              shift_byte = 0x80 >> ((shift_size - 1) % 8);
              shift_byte &= key_sets_c[i][(shift_size - 1) / 8];
              shift_byte <<= ((shift_size - 1) % 8);
          }
          else
          {
              shift_byte = 0x80 >> ((shift_size - 29) % 8);
              shift_byte &= key_sets_d[i][(shift_size - 29) / 8];
              shift_byte <<= ((shift_size - 29) % 8);
          }
          // NEW
          /* IF delete
          uint8_t if_b = (shift_size > 28);
          uint8_t if_val = if_b * 28;

          shift_byte = 0x80 >> ((shift_size - (1+if_val)) % 8);
          shift_byte &= key_sets[i].c[(shift_size - (1+if_val)) / 8];
          shift_byte <<= ((shift_size - (1+if_val)) % 8);
          */

          key_sets_k[i][j / 8] |= (shift_byte >> j % 8);
      }
  }

  uint8_t *message_piece = input_str; /*{ 0x41,
                           0x41,
                           0x41,
                           0x41,
                           0x41,
                           0x41,
                           0x41,
                           0x41 }; //AAAAAAAA*/

  // uint32_t mode = ENCRYPTION_MODE;
  uint8_t processed_piece[8]; // output / encrypted block
  int k;
  unsigned char initial_permutation[8];
  
  //memset(initial_permutation, 0, 8);
  //memset(processed_piece, 0, 8);
  for (i = 0; i < 8; i++) {
    initial_permutation[i] = 0;
    processed_piece[i] = 0;
  }

  for (i = 0; i < 64; i++)
  {
    shift_size = initial_message_permutation[i];
    shift_byte = 0x80 >> ((shift_size - 1) % 8);
    shift_byte &= message_piece[(shift_size - 1) / 8];
    shift_byte <<= ((shift_size - 1) % 8);

    initial_permutation[i / 8] |= (shift_byte >> i % 8);
  }

  unsigned char l[4], r[4];
  for (i = 0; i < 4; i++)
  {
    l[i] = initial_permutation[i];
    r[i] = initial_permutation[i + 4];
  }

  unsigned char ln[4], rn[4], er[6], ser[4];

  int key_index;
  for (k = 1; k <= 14; k++)
  {
    //memcpy(ln, r, 4);
    for (int m = 0; m < 4; m++)
      ln[m] = r[m];

    //memset(er, 0, 6);
    for (int m = 0; m < 6; m++)
          er[m] = 0;

    for (i = 0; i < 48; i++)
    {
      shift_size = message_expansion[i];
      shift_byte = 0x80 >> ((shift_size - 1) % 8);
      shift_byte &= r[(shift_size - 1) / 8];
      shift_byte <<= ((shift_size - 1) % 8);

      er[i / 8] |= (shift_byte >> i % 8);
    }

    /*if (mode == DECRYPTION_MODE)
    {
      key_index = 17 - k;
    }
    else
    {*/
    key_index = k;
    //}

    for (i = 0; i < 6; i++)
    {
      er[i] ^= key_sets_k[key_index][i];
    }

    unsigned char row, column;

    for (i = 0; i < 4; i++)
    {
      ser[i] = 0;
    }

    // 0000 0000 0000 0000 0000 0000
    // rccc crrc cccr rccc crrc cccr

    // Byte 1
    row = 0;
    row |= ((er[0] & 0x80) >> 6);
    row |= ((er[0] & 0x04) >> 2);

    column = 0;
    column |= ((er[0] & 0x78) >> 3);

    ser[0] |= ((unsigned char)S1[row * 16 + column] << 4);

    row = 0;
    row |= (er[0] & 0x02);
    row |= ((er[1] & 0x10) >> 4);

    column = 0;
    column |= ((er[0] & 0x01) << 3);
    column |= ((er[1] & 0xE0) >> 5);

    ser[0] |= (unsigned char)S2[row * 16 + column];

    // Byte 2
    row = 0;
    row |= ((er[1] & 0x08) >> 2);
    row |= ((er[2] & 0x40) >> 6);

    column = 0;
    column |= ((er[1] & 0x07) << 1);
    column |= ((er[2] & 0x80) >> 7);

    ser[1] |= ((unsigned char)S3[row * 16 + column] << 4);

    row = 0;
    row |= ((er[2] & 0x20) >> 4);
    row |= (er[2] & 0x01);

    column = 0;
    column |= ((er[2] & 0x1E) >> 1);

    ser[1] |= (unsigned char)S4[row * 16 + column];

    // Byte 3
    row = 0;
    row |= ((er[3] & 0x80) >> 6);
    row |= ((er[3] & 0x04) >> 2);

    column = 0;
    column |= ((er[3] & 0x78) >> 3);

    ser[2] |= ((unsigned char)S5[row * 16 + column] << 4);

    row = 0;
    row |= (er[3] & 0x02);
    row |= ((er[4] & 0x10) >> 4);

    column = 0;
    column |= ((er[3] & 0x01) << 3);
    column |= ((er[4] & 0xE0) >> 5);

    ser[2] |= (unsigned char)S6[row * 16 + column];

    // Byte 4
    row = 0;
    row |= ((er[4] & 0x08) >> 2);
    row |= ((er[5] & 0x40) >> 6);

    column = 0;
    column |= ((er[4] & 0x07) << 1);
    column |= ((er[5] & 0x80) >> 7);

    ser[3] |= ((unsigned char)S7[row * 16 + column] << 4);

    row = 0;
    row |= ((er[5] & 0x20) >> 4);
    row |= (er[5] & 0x01);

    column = 0;
    column |= ((er[5] & 0x1E) >> 1);

    ser[3] |= (unsigned char)S8[row * 16 + column];

    for (i = 0; i < 4; i++)
    {
      rn[i] = 0;
    }

    for (i = 0; i < 32; i++)
    {
      shift_size = right_sub_message_permutation[i];
      shift_byte = 0x80 >> ((shift_size - 1) % 8); 
      shift_byte &= ser[(shift_size - 1) / 8];
      shift_byte <<= ((shift_size - 1) % 8);

      rn[i / 8] |= (shift_byte >> i % 8);
    }

    for (i = 0; i < 4; i++)
    {
      rn[i] ^= l[i];
    }

    for (i = 0; i < 4; i++)
    {
      l[i] = ln[i];
      r[i] = rn[i];
    }
  }

  unsigned char pre_end_permutation[8];
  for (i = 0; i < 4; i++)
  {
    pre_end_permutation[i] = r[i];
    pre_end_permutation[4 + i] = l[i];
  }

  for (i = 0; i < 64; i++)
  {
    shift_size = final_message_permutation[i];
    shift_byte = 0x80 >> ((shift_size - 1) % 8);
    shift_byte &= pre_end_permutation[(shift_size - 1) / 8];
    shift_byte <<= ((shift_size - 1) % 8);

    processed_piece[i / 8] |= (shift_byte >> i % 8);
  }
  //}
  int result = 0;
  for (int i = 0; i < 8; i++)
  {
    result += processed_piece[i];
  }
  return result;
}

int main(int argc, char *argv[]) {
  if (argc < 3) {
    printf("Expected %d parameters\n", 2);
    return -1;
  }
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
