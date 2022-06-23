
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>
#include <climits>
#include <chrono>
// #define DEBUG

using namespace std;

struct Context;
using Handler = void (*)(Context &);

extern "C" {
void __attribute__((noinline)) vm_setup(Context &, uint64_t);
void __attribute__((noinline)) vm_exit(Context &);

void __attribute__((noinline)) vm_alu1_rrr(Context &);
void __attribute__((noinline)) vm_alu2_rrr(Context &);
void __attribute__((noinline)) vm_alu3_rrr(Context &);
void __attribute__((noinline)) vm_alu4_rrr(Context &);
void __attribute__((noinline)) vm_alu5_rrr(Context &);
void __attribute__((noinline)) vm_alu6_rrr(Context &);
void __attribute__((noinline)) vm_alu7_rrr(Context &);
void __attribute__((noinline)) vm_alu8_rrr(Context &);
void __attribute__((noinline)) vm_alu9_rrr(Context &);
void __attribute__((noinline)) vm_alu10_rrr(Context &);
void __attribute__((noinline)) vm_alu11_rrr(Context &);
void __attribute__((noinline)) vm_alu12_rrr(Context &);
void __attribute__((noinline)) vm_alu13_rrr(Context &);
void __attribute__((noinline)) vm_alu14_rrr(Context &);
void __attribute__((noinline)) vm_alu15_rrr(Context &);
void __attribute__((noinline)) vm_alu16_rrr(Context &);
void __attribute__((noinline)) vm_alu17_rrr(Context &);
void __attribute__((noinline)) vm_alu18_rrr(Context &);
void __attribute__((noinline)) vm_alu19_rrr(Context &);
void __attribute__((noinline)) vm_alu20_rrr(Context &);
void __attribute__((noinline)) vm_alu21_rrr(Context &);
void __attribute__((noinline)) vm_alu22_rrr(Context &);
void __attribute__((noinline)) vm_alu23_rrr(Context &);
void __attribute__((noinline)) vm_alu24_rrr(Context &);
void __attribute__((noinline)) vm_alu25_rrr(Context &);
void __attribute__((noinline)) vm_alu26_rrr(Context &);
void __attribute__((noinline)) vm_alu27_rrr(Context &);
void __attribute__((noinline)) vm_alu28_rrr(Context &);
void __attribute__((noinline)) vm_alu29_rrr(Context &);
void __attribute__((noinline)) vm_alu30_rrr(Context &);
void __attribute__((noinline)) vm_alu31_rrr(Context &);
void __attribute__((noinline)) vm_alu32_rrr(Context &);
void __attribute__((noinline)) vm_alu33_rrr(Context &);
void __attribute__((noinline)) vm_alu34_rrr(Context &);
void __attribute__((noinline)) vm_alu35_rrr(Context &);
void __attribute__((noinline)) vm_alu36_rrr(Context &);
void __attribute__((noinline)) vm_alu37_rrr(Context &);
void __attribute__((noinline)) vm_alu38_rrr(Context &);
void __attribute__((noinline)) vm_alu39_rrr(Context &);
void __attribute__((noinline)) vm_alu40_rrr(Context &);
void __attribute__((noinline)) vm_alu41_rrr(Context &);
void __attribute__((noinline)) vm_alu42_rrr(Context &);
void __attribute__((noinline)) vm_alu43_rrr(Context &);
void __attribute__((noinline)) vm_alu44_rrr(Context &);
void __attribute__((noinline)) vm_alu45_rrr(Context &);
void __attribute__((noinline)) vm_alu46_rrr(Context &);
void __attribute__((noinline)) vm_alu47_rrr(Context &);
void __attribute__((noinline)) vm_alu48_rrr(Context &);
void __attribute__((noinline)) vm_alu49_rrr(Context &);
void __attribute__((noinline)) vm_alu50_rrr(Context &);
void __attribute__((noinline)) vm_alu51_rrr(Context &);
void __attribute__((noinline)) vm_alu52_rrr(Context &);
void __attribute__((noinline)) vm_alu53_rrr(Context &);
void __attribute__((noinline)) vm_alu54_rrr(Context &);
void __attribute__((noinline)) vm_alu55_rrr(Context &);
void __attribute__((noinline)) vm_alu56_rrr(Context &);
void __attribute__((noinline)) vm_alu57_rrr(Context &);
void __attribute__((noinline)) vm_alu58_rrr(Context &);
void __attribute__((noinline)) vm_alu59_rrr(Context &);
void __attribute__((noinline)) vm_alu60_rrr(Context &);
void __attribute__((noinline)) vm_alu61_rrr(Context &);
void __attribute__((noinline)) vm_alu62_rrr(Context &);
void __attribute__((noinline)) vm_alu63_rrr(Context &);
void __attribute__((noinline)) vm_alu64_rrr(Context &);
void __attribute__((noinline)) vm_alu65_rrr(Context &);
void __attribute__((noinline)) vm_alu66_rrr(Context &);
void __attribute__((noinline)) vm_alu67_rrr(Context &);
void __attribute__((noinline)) vm_alu68_rrr(Context &);
void __attribute__((noinline)) vm_alu69_rrr(Context &);
void __attribute__((noinline)) vm_alu70_rrr(Context &);
void __attribute__((noinline)) vm_alu71_rrr(Context &);
void __attribute__((noinline)) vm_alu72_rrr(Context &);
void __attribute__((noinline)) vm_alu73_rrr(Context &);
void __attribute__((noinline)) vm_alu74_rrr(Context &);
void __attribute__((noinline)) vm_alu75_rrr(Context &);
void __attribute__((noinline)) vm_alu76_rrr(Context &);
void __attribute__((noinline)) vm_alu77_rrr(Context &);
void __attribute__((noinline)) vm_alu78_rrr(Context &);
void __attribute__((noinline)) vm_alu79_rrr(Context &);
void __attribute__((noinline)) vm_alu80_rrr(Context &);
void __attribute__((noinline)) vm_alu81_rrr(Context &);
void __attribute__((noinline)) vm_alu82_rrr(Context &);
void __attribute__((noinline)) vm_alu83_rrr(Context &);
void __attribute__((noinline)) vm_alu84_rrr(Context &);
void __attribute__((noinline)) vm_alu85_rrr(Context &);
void __attribute__((noinline)) vm_alu86_rrr(Context &);
void __attribute__((noinline)) vm_alu87_rrr(Context &);
void __attribute__((noinline)) vm_alu88_rrr(Context &);
void __attribute__((noinline)) vm_alu89_rrr(Context &);
void __attribute__((noinline)) vm_alu90_rrr(Context &);
void __attribute__((noinline)) vm_alu91_rrr(Context &);
void __attribute__((noinline)) vm_alu92_rrr(Context &);
void __attribute__((noinline)) vm_alu93_rrr(Context &);
void __attribute__((noinline)) vm_alu94_rrr(Context &);
void __attribute__((noinline)) vm_alu95_rrr(Context &);
void __attribute__((noinline)) vm_alu96_rrr(Context &);
void __attribute__((noinline)) vm_alu97_rrr(Context &);
void __attribute__((noinline)) vm_alu98_rrr(Context &);
void __attribute__((noinline)) vm_alu99_rrr(Context &);
void __attribute__((noinline)) vm_alu100_rrr(Context &);
void __attribute__((noinline)) vm_alu101_rrr(Context &);
void __attribute__((noinline)) vm_alu102_rrr(Context &);
void __attribute__((noinline)) vm_alu103_rrr(Context &);
void __attribute__((noinline)) vm_alu104_rrr(Context &);
void __attribute__((noinline)) vm_alu105_rrr(Context &);
void __attribute__((noinline)) vm_alu106_rrr(Context &);
void __attribute__((noinline)) vm_alu107_rrr(Context &);
void __attribute__((noinline)) vm_alu108_rrr(Context &);
void __attribute__((noinline)) vm_alu109_rrr(Context &);
void __attribute__((noinline)) vm_alu110_rrr(Context &);
void __attribute__((noinline)) vm_alu111_rrr(Context &);
void __attribute__((noinline)) vm_alu112_rrr(Context &);
void __attribute__((noinline)) vm_alu113_rrr(Context &);
void __attribute__((noinline)) vm_alu114_rrr(Context &);
void __attribute__((noinline)) vm_alu115_rrr(Context &);
void __attribute__((noinline)) vm_alu116_rrr(Context &);
void __attribute__((noinline)) vm_alu117_rrr(Context &);
void __attribute__((noinline)) vm_alu118_rrr(Context &);
void __attribute__((noinline)) vm_alu119_rrr(Context &);
void __attribute__((noinline)) vm_alu120_rrr(Context &);
void __attribute__((noinline)) vm_alu121_rrr(Context &);
void __attribute__((noinline)) vm_alu122_rrr(Context &);
void __attribute__((noinline)) vm_alu123_rrr(Context &);
void __attribute__((noinline)) vm_alu124_rrr(Context &);
void __attribute__((noinline)) vm_alu125_rrr(Context &);
void __attribute__((noinline)) vm_alu126_rrr(Context &);
void __attribute__((noinline)) vm_alu127_rrr(Context &);
void __attribute__((noinline)) vm_alu128_rrr(Context &);
void __attribute__((noinline)) vm_alu129_rrr(Context &);
void __attribute__((noinline)) vm_alu130_rrr(Context &);
void __attribute__((noinline)) vm_alu131_rrr(Context &);
void __attribute__((noinline)) vm_alu132_rrr(Context &);
void __attribute__((noinline)) vm_alu133_rrr(Context &);
void __attribute__((noinline)) vm_alu134_rrr(Context &);
void __attribute__((noinline)) vm_alu135_rrr(Context &);
void __attribute__((noinline)) vm_alu136_rrr(Context &);
void __attribute__((noinline)) vm_alu137_rrr(Context &);
void __attribute__((noinline)) vm_alu138_rrr(Context &);
void __attribute__((noinline)) vm_alu139_rrr(Context &);
void __attribute__((noinline)) vm_alu140_rrr(Context &);
void __attribute__((noinline)) vm_alu141_rrr(Context &);
void __attribute__((noinline)) vm_alu142_rrr(Context &);
void __attribute__((noinline)) vm_alu143_rrr(Context &);
void __attribute__((noinline)) vm_alu144_rrr(Context &);
void __attribute__((noinline)) vm_alu145_rrr(Context &);
void __attribute__((noinline)) vm_alu146_rrr(Context &);
void __attribute__((noinline)) vm_alu147_rrr(Context &);
void __attribute__((noinline)) vm_alu148_rrr(Context &);
void __attribute__((noinline)) vm_alu149_rrr(Context &);
void __attribute__((noinline)) vm_alu150_rrr(Context &);
void __attribute__((noinline)) vm_alu151_rrr(Context &);
void __attribute__((noinline)) vm_alu152_rrr(Context &);
void __attribute__((noinline)) vm_alu153_rrr(Context &);
void __attribute__((noinline)) vm_alu154_rrr(Context &);
void __attribute__((noinline)) vm_alu155_rrr(Context &);
void __attribute__((noinline)) vm_alu156_rrr(Context &);
void __attribute__((noinline)) vm_alu157_rrr(Context &);
void __attribute__((noinline)) vm_alu158_rrr(Context &);
void __attribute__((noinline)) vm_alu159_rrr(Context &);
void __attribute__((noinline)) vm_alu160_rrr(Context &);
void __attribute__((noinline)) vm_alu161_rrr(Context &);
void __attribute__((noinline)) vm_alu162_rrr(Context &);
void __attribute__((noinline)) vm_alu163_rrr(Context &);
void __attribute__((noinline)) vm_alu164_rrr(Context &);
void __attribute__((noinline)) vm_alu165_rrr(Context &);
void __attribute__((noinline)) vm_alu166_rrr(Context &);
void __attribute__((noinline)) vm_alu167_rrr(Context &);
void __attribute__((noinline)) vm_alu168_rrr(Context &);
void __attribute__((noinline)) vm_alu169_rrr(Context &);
void __attribute__((noinline)) vm_alu170_rrr(Context &);
void __attribute__((noinline)) vm_alu171_rrr(Context &);
void __attribute__((noinline)) vm_alu172_rrr(Context &);
void __attribute__((noinline)) vm_alu173_rrr(Context &);
void __attribute__((noinline)) vm_alu174_rrr(Context &);
void __attribute__((noinline)) vm_alu175_rrr(Context &);
void __attribute__((noinline)) vm_alu176_rrr(Context &);
void __attribute__((noinline)) vm_alu177_rrr(Context &);
void __attribute__((noinline)) vm_alu178_rrr(Context &);
void __attribute__((noinline)) vm_alu179_rrr(Context &);
void __attribute__((noinline)) vm_alu180_rrr(Context &);
void __attribute__((noinline)) vm_alu181_rrr(Context &);
void __attribute__((noinline)) vm_alu182_rrr(Context &);
void __attribute__((noinline)) vm_alu183_rrr(Context &);
void __attribute__((noinline)) vm_alu184_rrr(Context &);
void __attribute__((noinline)) vm_alu185_rrr(Context &);
void __attribute__((noinline)) vm_alu186_rrr(Context &);
void __attribute__((noinline)) vm_alu187_rrr(Context &);
void __attribute__((noinline)) vm_alu188_rrr(Context &);
void __attribute__((noinline)) vm_alu189_rrr(Context &);
void __attribute__((noinline)) vm_alu190_rrr(Context &);
void __attribute__((noinline)) vm_alu191_rrr(Context &);
void __attribute__((noinline)) vm_alu192_rrr(Context &);
void __attribute__((noinline)) vm_alu193_rrr(Context &);
void __attribute__((noinline)) vm_alu194_rrr(Context &);
void __attribute__((noinline)) vm_alu195_rrr(Context &);
void __attribute__((noinline)) vm_alu196_rrr(Context &);
void __attribute__((noinline)) vm_alu197_rrr(Context &);
void __attribute__((noinline)) vm_alu198_rrr(Context &);
void __attribute__((noinline)) vm_alu199_rrr(Context &);
void __attribute__((noinline)) vm_alu200_rrr(Context &);
void __attribute__((noinline)) vm_alu201_rrr(Context &);
void __attribute__((noinline)) vm_alu202_rrr(Context &);
void __attribute__((noinline)) vm_alu203_rrr(Context &);
void __attribute__((noinline)) vm_alu204_rrr(Context &);
void __attribute__((noinline)) vm_alu205_rrr(Context &);
void __attribute__((noinline)) vm_alu206_rrr(Context &);
void __attribute__((noinline)) vm_alu207_rrr(Context &);
void __attribute__((noinline)) vm_alu208_rrr(Context &);
void __attribute__((noinline)) vm_alu209_rrr(Context &);
void __attribute__((noinline)) vm_alu210_rrr(Context &);
void __attribute__((noinline)) vm_alu211_rrr(Context &);
void __attribute__((noinline)) vm_alu212_rrr(Context &);
void __attribute__((noinline)) vm_alu213_rrr(Context &);
void __attribute__((noinline)) vm_alu214_rrr(Context &);
void __attribute__((noinline)) vm_alu215_rrr(Context &);
void __attribute__((noinline)) vm_alu216_rrr(Context &);
void __attribute__((noinline)) vm_alu217_rrr(Context &);
void __attribute__((noinline)) vm_alu218_rrr(Context &);
void __attribute__((noinline)) vm_alu219_rrr(Context &);
void __attribute__((noinline)) vm_alu220_rrr(Context &);
void __attribute__((noinline)) vm_alu221_rrr(Context &);
void __attribute__((noinline)) vm_alu222_rrr(Context &);
void __attribute__((noinline)) vm_alu223_rrr(Context &);
void __attribute__((noinline)) vm_alu224_rrr(Context &);
void __attribute__((noinline)) vm_alu225_rrr(Context &);
void __attribute__((noinline)) vm_alu226_rrr(Context &);
void __attribute__((noinline)) vm_alu227_rrr(Context &);
void __attribute__((noinline)) vm_alu228_rrr(Context &);
void __attribute__((noinline)) vm_alu229_rrr(Context &);
void __attribute__((noinline)) vm_alu230_rrr(Context &);
void __attribute__((noinline)) vm_alu231_rrr(Context &);
void __attribute__((noinline)) vm_alu232_rrr(Context &);
void __attribute__((noinline)) vm_alu233_rrr(Context &);
void __attribute__((noinline)) vm_alu234_rrr(Context &);
void __attribute__((noinline)) vm_alu235_rrr(Context &);
void __attribute__((noinline)) vm_alu236_rrr(Context &);
void __attribute__((noinline)) vm_alu237_rrr(Context &);
void __attribute__((noinline)) vm_alu238_rrr(Context &);
void __attribute__((noinline)) vm_alu239_rrr(Context &);
void __attribute__((noinline)) vm_alu240_rrr(Context &);
void __attribute__((noinline)) vm_alu241_rrr(Context &);
void __attribute__((noinline)) vm_alu242_rrr(Context &);
void __attribute__((noinline)) vm_alu243_rrr(Context &);
void __attribute__((noinline)) vm_alu244_rrr(Context &);
void __attribute__((noinline)) vm_alu245_rrr(Context &);
void __attribute__((noinline)) vm_alu246_rrr(Context &);
void __attribute__((noinline)) vm_alu247_rrr(Context &);
void __attribute__((noinline)) vm_alu248_rrr(Context &);
void __attribute__((noinline)) vm_alu249_rrr(Context &);
void __attribute__((noinline)) vm_alu250_rrr(Context &);
void __attribute__((noinline)) vm_alu251_rrr(Context &);
void __attribute__((noinline)) vm_alu252_rrr(Context &);
void __attribute__((noinline)) vm_alu253_rrr(Context &);
void __attribute__((noinline)) vm_alu254_rrr(Context &);
void __attribute__((noinline)) vm_alu255_rrr(Context &);
void __attribute__((noinline)) vm_alu256_rrr(Context &);
void __attribute__((noinline)) vm_alu257_rrr(Context &);
void __attribute__((noinline)) vm_alu258_rrr(Context &);
void __attribute__((noinline)) vm_alu259_rrr(Context &);
void __attribute__((noinline)) vm_alu260_rrr(Context &);
void __attribute__((noinline)) vm_alu261_rrr(Context &);
void __attribute__((noinline)) vm_alu262_rrr(Context &);
void __attribute__((noinline)) vm_alu263_rrr(Context &);
void __attribute__((noinline)) vm_alu264_rrr(Context &);
void __attribute__((noinline)) vm_alu265_rrr(Context &);
void __attribute__((noinline)) vm_alu266_rrr(Context &);
void __attribute__((noinline)) vm_alu267_rrr(Context &);
void __attribute__((noinline)) vm_alu268_rrr(Context &);
void __attribute__((noinline)) vm_alu269_rrr(Context &);
void __attribute__((noinline)) vm_alu270_rrr(Context &);
void __attribute__((noinline)) vm_alu271_rrr(Context &);
void __attribute__((noinline)) vm_alu272_rrr(Context &);
void __attribute__((noinline)) vm_alu273_rrr(Context &);
void __attribute__((noinline)) vm_alu274_rrr(Context &);
void __attribute__((noinline)) vm_alu275_rrr(Context &);
void __attribute__((noinline)) vm_alu276_rrr(Context &);
void __attribute__((noinline)) vm_alu277_rrr(Context &);
void __attribute__((noinline)) vm_alu278_rrr(Context &);
void __attribute__((noinline)) vm_alu279_rrr(Context &);
void __attribute__((noinline)) vm_alu280_rrr(Context &);
void __attribute__((noinline)) vm_alu281_rrr(Context &);
void __attribute__((noinline)) vm_alu282_rrr(Context &);
void __attribute__((noinline)) vm_alu283_rrr(Context &);
void __attribute__((noinline)) vm_alu284_rrr(Context &);
void __attribute__((noinline)) vm_alu285_rrr(Context &);
void __attribute__((noinline)) vm_alu286_rrr(Context &);
void __attribute__((noinline)) vm_alu287_rrr(Context &);
void __attribute__((noinline)) vm_alu288_rrr(Context &);
void __attribute__((noinline)) vm_alu289_rrr(Context &);
void __attribute__((noinline)) vm_alu290_rrr(Context &);
void __attribute__((noinline)) vm_alu291_rrr(Context &);
void __attribute__((noinline)) vm_alu292_rrr(Context &);
void __attribute__((noinline)) vm_alu293_rrr(Context &);
void __attribute__((noinline)) vm_alu294_rrr(Context &);
void __attribute__((noinline)) vm_alu295_rrr(Context &);
void __attribute__((noinline)) vm_alu296_rrr(Context &);
void __attribute__((noinline)) vm_alu297_rrr(Context &);
void __attribute__((noinline)) vm_alu298_rrr(Context &);
void __attribute__((noinline)) vm_alu299_rrr(Context &);
void __attribute__((noinline)) vm_alu300_rrr(Context &);
void __attribute__((noinline)) vm_alu301_rrr(Context &);
void __attribute__((noinline)) vm_alu302_rrr(Context &);
void __attribute__((noinline)) vm_alu303_rrr(Context &);
void __attribute__((noinline)) vm_alu304_rrr(Context &);
void __attribute__((noinline)) vm_alu305_rrr(Context &);
void __attribute__((noinline)) vm_alu306_rrr(Context &);
void __attribute__((noinline)) vm_alu307_rrr(Context &);
void __attribute__((noinline)) vm_alu308_rrr(Context &);
void __attribute__((noinline)) vm_alu309_rrr(Context &);
void __attribute__((noinline)) vm_alu310_rrr(Context &);
void __attribute__((noinline)) vm_alu311_rrr(Context &);
void __attribute__((noinline)) vm_alu312_rrr(Context &);
void __attribute__((noinline)) vm_alu313_rrr(Context &);
void __attribute__((noinline)) vm_alu314_rrr(Context &);
void __attribute__((noinline)) vm_alu315_rrr(Context &);
void __attribute__((noinline)) vm_alu316_rrr(Context &);
void __attribute__((noinline)) vm_alu317_rrr(Context &);
void __attribute__((noinline)) vm_alu318_rrr(Context &);
void __attribute__((noinline)) vm_alu319_rrr(Context &);
void __attribute__((noinline)) vm_alu320_rrr(Context &);
void __attribute__((noinline)) vm_alu321_rrr(Context &);
void __attribute__((noinline)) vm_alu322_rrr(Context &);
void __attribute__((noinline)) vm_alu323_rrr(Context &);
void __attribute__((noinline)) vm_alu324_rrr(Context &);
void __attribute__((noinline)) vm_alu325_rrr(Context &);
void __attribute__((noinline)) vm_alu326_rrr(Context &);
void __attribute__((noinline)) vm_alu327_rrr(Context &);
void __attribute__((noinline)) vm_alu328_rrr(Context &);
void __attribute__((noinline)) vm_alu329_rrr(Context &);
void __attribute__((noinline)) vm_alu330_rrr(Context &);
void __attribute__((noinline)) vm_alu331_rrr(Context &);
void __attribute__((noinline)) vm_alu332_rrr(Context &);
void __attribute__((noinline)) vm_alu333_rrr(Context &);
void __attribute__((noinline)) vm_alu334_rrr(Context &);
void __attribute__((noinline)) vm_alu335_rrr(Context &);
void __attribute__((noinline)) vm_alu336_rrr(Context &);
void __attribute__((noinline)) vm_alu337_rrr(Context &);
void __attribute__((noinline)) vm_alu338_rrr(Context &);
void __attribute__((noinline)) vm_alu339_rrr(Context &);
void __attribute__((noinline)) vm_alu340_rrr(Context &);
void __attribute__((noinline)) vm_alu341_rrr(Context &);
void __attribute__((noinline)) vm_alu342_rrr(Context &);
void __attribute__((noinline)) vm_alu343_rrr(Context &);
void __attribute__((noinline)) vm_alu344_rrr(Context &);
void __attribute__((noinline)) vm_alu345_rrr(Context &);
void __attribute__((noinline)) vm_alu346_rrr(Context &);
void __attribute__((noinline)) vm_alu347_rrr(Context &);
void __attribute__((noinline)) vm_alu348_rrr(Context &);
void __attribute__((noinline)) vm_alu349_rrr(Context &);
void __attribute__((noinline)) vm_alu350_rrr(Context &);
void __attribute__((noinline)) vm_alu351_rrr(Context &);
void __attribute__((noinline)) vm_alu352_rrr(Context &);
void __attribute__((noinline)) vm_alu353_rrr(Context &);
void __attribute__((noinline)) vm_alu354_rrr(Context &);
void __attribute__((noinline)) vm_alu355_rrr(Context &);
void __attribute__((noinline)) vm_alu356_rrr(Context &);
void __attribute__((noinline)) vm_alu357_rrr(Context &);
void __attribute__((noinline)) vm_alu358_rrr(Context &);
void __attribute__((noinline)) vm_alu359_rrr(Context &);
void __attribute__((noinline)) vm_alu360_rrr(Context &);
void __attribute__((noinline)) vm_alu361_rrr(Context &);
void __attribute__((noinline)) vm_alu362_rrr(Context &);
void __attribute__((noinline)) vm_alu363_rrr(Context &);
void __attribute__((noinline)) vm_alu364_rrr(Context &);
void __attribute__((noinline)) vm_alu365_rrr(Context &);
void __attribute__((noinline)) vm_alu366_rrr(Context &);
void __attribute__((noinline)) vm_alu367_rrr(Context &);
void __attribute__((noinline)) vm_alu368_rrr(Context &);
void __attribute__((noinline)) vm_alu369_rrr(Context &);
void __attribute__((noinline)) vm_alu370_rrr(Context &);
void __attribute__((noinline)) vm_alu371_rrr(Context &);
void __attribute__((noinline)) vm_alu372_rrr(Context &);
void __attribute__((noinline)) vm_alu373_rrr(Context &);
void __attribute__((noinline)) vm_alu374_rrr(Context &);
void __attribute__((noinline)) vm_alu375_rrr(Context &);
void __attribute__((noinline)) vm_alu376_rrr(Context &);
void __attribute__((noinline)) vm_alu377_rrr(Context &);
void __attribute__((noinline)) vm_alu378_rrr(Context &);
void __attribute__((noinline)) vm_alu379_rrr(Context &);
void __attribute__((noinline)) vm_alu380_rrr(Context &);
void __attribute__((noinline)) vm_alu381_rrr(Context &);
void __attribute__((noinline)) vm_alu382_rrr(Context &);
void __attribute__((noinline)) vm_alu383_rrr(Context &);
void __attribute__((noinline)) vm_alu384_rrr(Context &);
void __attribute__((noinline)) vm_alu385_rrr(Context &);
void __attribute__((noinline)) vm_alu386_rrr(Context &);
void __attribute__((noinline)) vm_alu387_rrr(Context &);
void __attribute__((noinline)) vm_alu388_rrr(Context &);
void __attribute__((noinline)) vm_alu389_rrr(Context &);
void __attribute__((noinline)) vm_alu390_rrr(Context &);
void __attribute__((noinline)) vm_alu391_rrr(Context &);
void __attribute__((noinline)) vm_alu392_rrr(Context &);
void __attribute__((noinline)) vm_alu393_rrr(Context &);
void __attribute__((noinline)) vm_alu394_rrr(Context &);
void __attribute__((noinline)) vm_alu395_rrr(Context &);
void __attribute__((noinline)) vm_alu396_rrr(Context &);
void __attribute__((noinline)) vm_alu397_rrr(Context &);
void __attribute__((noinline)) vm_alu398_rrr(Context &);
void __attribute__((noinline)) vm_alu399_rrr(Context &);
void __attribute__((noinline)) vm_alu400_rrr(Context &);
void __attribute__((noinline)) vm_alu401_rrr(Context &);
void __attribute__((noinline)) vm_alu402_rrr(Context &);
void __attribute__((noinline)) vm_alu403_rrr(Context &);
void __attribute__((noinline)) vm_alu404_rrr(Context &);
void __attribute__((noinline)) vm_alu405_rrr(Context &);
void __attribute__((noinline)) vm_alu406_rrr(Context &);
void __attribute__((noinline)) vm_alu407_rrr(Context &);
void __attribute__((noinline)) vm_alu408_rrr(Context &);
void __attribute__((noinline)) vm_alu409_rrr(Context &);
void __attribute__((noinline)) vm_alu410_rrr(Context &);
void __attribute__((noinline)) vm_alu411_rrr(Context &);
void __attribute__((noinline)) vm_alu412_rrr(Context &);
void __attribute__((noinline)) vm_alu413_rrr(Context &);
void __attribute__((noinline)) vm_alu414_rrr(Context &);
void __attribute__((noinline)) vm_alu415_rrr(Context &);
void __attribute__((noinline)) vm_alu416_rrr(Context &);
void __attribute__((noinline)) vm_alu417_rrr(Context &);
void __attribute__((noinline)) vm_alu418_rrr(Context &);
void __attribute__((noinline)) vm_alu419_rrr(Context &);
void __attribute__((noinline)) vm_alu420_rrr(Context &);
void __attribute__((noinline)) vm_alu421_rrr(Context &);
void __attribute__((noinline)) vm_alu422_rrr(Context &);
void __attribute__((noinline)) vm_alu423_rrr(Context &);
void __attribute__((noinline)) vm_alu424_rrr(Context &);
void __attribute__((noinline)) vm_alu425_rrr(Context &);
void __attribute__((noinline)) vm_alu426_rrr(Context &);
void __attribute__((noinline)) vm_alu427_rrr(Context &);
void __attribute__((noinline)) vm_alu428_rrr(Context &);
void __attribute__((noinline)) vm_alu429_rrr(Context &);
void __attribute__((noinline)) vm_alu430_rrr(Context &);
void __attribute__((noinline)) vm_alu431_rrr(Context &);
void __attribute__((noinline)) vm_alu432_rrr(Context &);
void __attribute__((noinline)) vm_alu433_rrr(Context &);
void __attribute__((noinline)) vm_alu434_rrr(Context &);
void __attribute__((noinline)) vm_alu435_rrr(Context &);
void __attribute__((noinline)) vm_alu436_rrr(Context &);
void __attribute__((noinline)) vm_alu437_rrr(Context &);
void __attribute__((noinline)) vm_alu438_rrr(Context &);
void __attribute__((noinline)) vm_alu439_rrr(Context &);
void __attribute__((noinline)) vm_alu440_rrr(Context &);
void __attribute__((noinline)) vm_alu441_rrr(Context &);
void __attribute__((noinline)) vm_alu442_rrr(Context &);
void __attribute__((noinline)) vm_alu443_rrr(Context &);
void __attribute__((noinline)) vm_alu444_rrr(Context &);
void __attribute__((noinline)) vm_alu445_rrr(Context &);
void __attribute__((noinline)) vm_alu446_rrr(Context &);
void __attribute__((noinline)) vm_alu447_rrr(Context &);
void __attribute__((noinline)) vm_alu448_rrr(Context &);
void __attribute__((noinline)) vm_alu449_rrr(Context &);
void __attribute__((noinline)) vm_alu450_rrr(Context &);
void __attribute__((noinline)) vm_alu451_rrr(Context &);
void __attribute__((noinline)) vm_alu452_rrr(Context &);
void __attribute__((noinline)) vm_alu453_rrr(Context &);
void __attribute__((noinline)) vm_alu454_rrr(Context &);
void __attribute__((noinline)) vm_alu455_rrr(Context &);
void __attribute__((noinline)) vm_alu456_rrr(Context &);
void __attribute__((noinline)) vm_alu457_rrr(Context &);
void __attribute__((noinline)) vm_alu458_rrr(Context &);
void __attribute__((noinline)) vm_alu459_rrr(Context &);
void __attribute__((noinline)) vm_alu460_rrr(Context &);
void __attribute__((noinline)) vm_alu461_rrr(Context &);
void __attribute__((noinline)) vm_alu462_rrr(Context &);
void __attribute__((noinline)) vm_alu463_rrr(Context &);
void __attribute__((noinline)) vm_alu464_rrr(Context &);
void __attribute__((noinline)) vm_alu465_rrr(Context &);
void __attribute__((noinline)) vm_alu466_rrr(Context &);
void __attribute__((noinline)) vm_alu467_rrr(Context &);
void __attribute__((noinline)) vm_alu468_rrr(Context &);
void __attribute__((noinline)) vm_alu469_rrr(Context &);
void __attribute__((noinline)) vm_alu470_rrr(Context &);
void __attribute__((noinline)) vm_alu471_rrr(Context &);
void __attribute__((noinline)) vm_alu472_rrr(Context &);
void __attribute__((noinline)) vm_alu473_rrr(Context &);
void __attribute__((noinline)) vm_alu474_rrr(Context &);
void __attribute__((noinline)) vm_alu475_rrr(Context &);
void __attribute__((noinline)) vm_alu476_rrr(Context &);
void __attribute__((noinline)) vm_alu477_rrr(Context &);
void __attribute__((noinline)) vm_alu478_rrr(Context &);
void __attribute__((noinline)) vm_alu479_rrr(Context &);
void __attribute__((noinline)) vm_alu480_rrr(Context &);
void __attribute__((noinline)) vm_alu481_rrr(Context &);
void __attribute__((noinline)) vm_alu482_rrr(Context &);
void __attribute__((noinline)) vm_alu483_rrr(Context &);
void __attribute__((noinline)) vm_alu484_rrr(Context &);
void __attribute__((noinline)) vm_alu485_rrr(Context &);
void __attribute__((noinline)) vm_alu486_rrr(Context &);
void __attribute__((noinline)) vm_alu487_rrr(Context &);
void __attribute__((noinline)) vm_alu488_rrr(Context &);
void __attribute__((noinline)) vm_alu489_rrr(Context &);
void __attribute__((noinline)) vm_alu490_rrr(Context &);
void __attribute__((noinline)) vm_alu491_rrr(Context &);
void __attribute__((noinline)) vm_alu492_rrr(Context &);
void __attribute__((noinline)) vm_alu493_rrr(Context &);
void __attribute__((noinline)) vm_alu494_rrr(Context &);
void __attribute__((noinline)) vm_alu495_rrr(Context &);
void __attribute__((noinline)) vm_alu496_rrr(Context &);
void __attribute__((noinline)) vm_alu497_rrr(Context &);
void __attribute__((noinline)) vm_alu498_rrr(Context &);
void __attribute__((noinline)) vm_alu499_rrr(Context &);
void __attribute__((noinline)) vm_alu500_rrr(Context &);
void __attribute__((noinline)) vm_alu501_rrr(Context &);
void __attribute__((noinline)) vm_alu502_rrr(Context &);
void __attribute__((noinline)) vm_alu503_rrr(Context &);
void __attribute__((noinline)) vm_alu504_rrr(Context &);
void __attribute__((noinline)) vm_alu505_rrr(Context &);
void __attribute__((noinline)) vm_alu506_rrr(Context &);
void __attribute__((noinline)) vm_alu507_rrr(Context &);
void __attribute__((noinline)) vm_alu508_rrr(Context &);
void __attribute__((noinline)) vm_alu509_rrr(Context &);
void __attribute__((noinline)) vm_alu510_rrr(Context &);
void __attribute__((noinline)) vm_alu511_rrr(Context &);
}

constexpr size_t kRegCount = 65536;

constexpr size_t kOffsetOutput = 0;
constexpr size_t kOffsetIp = 1;

struct Context {
  uint64_t regs[kRegCount];
  void reset() { std::memset(regs, 0, kRegCount); }
};

extern "C" {
Handler handler_table[] = {
    &vm_exit,         &vm_alu1_rrr,     &vm_alu2_rrr,     &vm_alu3_rrr,
    &vm_alu4_rrr,     &vm_alu5_rrr,     &vm_alu6_rrr,     &vm_alu7_rrr,
    &vm_alu8_rrr,     &vm_alu9_rrr,     &vm_alu10_rrr,    &vm_alu11_rrr,
    &vm_alu12_rrr,    &vm_alu13_rrr,    &vm_alu14_rrr,    &vm_alu15_rrr,
    &vm_alu16_rrr,    &vm_alu17_rrr,    &vm_alu18_rrr,    &vm_alu19_rrr,
    &vm_alu20_rrr,    &vm_alu21_rrr,    &vm_alu22_rrr,    &vm_alu23_rrr,
    &vm_alu24_rrr,    &vm_alu25_rrr,    &vm_alu26_rrr,    &vm_alu27_rrr,
    &vm_alu28_rrr,    &vm_alu29_rrr,    &vm_alu30_rrr,    &vm_alu31_rrr,
    &vm_alu32_rrr,    &vm_alu33_rrr,    &vm_alu34_rrr,    &vm_alu35_rrr,
    &vm_alu36_rrr,    &vm_alu37_rrr,    &vm_alu38_rrr,    &vm_alu39_rrr,
    &vm_alu40_rrr,    &vm_alu41_rrr,    &vm_alu42_rrr,    &vm_alu43_rrr,
    &vm_alu44_rrr,    &vm_alu45_rrr,    &vm_alu46_rrr,    &vm_alu47_rrr,
    &vm_alu48_rrr,    &vm_alu49_rrr,    &vm_alu50_rrr,    &vm_alu51_rrr,
    &vm_alu52_rrr,    &vm_alu53_rrr,    &vm_alu54_rrr,    &vm_alu55_rrr,
    &vm_alu56_rrr,    &vm_alu57_rrr,    &vm_alu58_rrr,    &vm_alu59_rrr,
    &vm_alu60_rrr,    &vm_alu61_rrr,    &vm_alu62_rrr,    &vm_alu63_rrr,
    &vm_alu64_rrr,    &vm_alu65_rrr,    &vm_alu66_rrr,    &vm_alu67_rrr,
    &vm_alu68_rrr,    &vm_alu69_rrr,    &vm_alu70_rrr,    &vm_alu71_rrr,
    &vm_alu72_rrr,    &vm_alu73_rrr,    &vm_alu74_rrr,    &vm_alu75_rrr,
    &vm_alu76_rrr,    &vm_alu77_rrr,    &vm_alu78_rrr,    &vm_alu79_rrr,
    &vm_alu80_rrr,    &vm_alu81_rrr,    &vm_alu82_rrr,    &vm_alu83_rrr,
    &vm_alu84_rrr,    &vm_alu85_rrr,    &vm_alu86_rrr,    &vm_alu87_rrr,
    &vm_alu88_rrr,    &vm_alu89_rrr,    &vm_alu90_rrr,    &vm_alu91_rrr,
    &vm_alu92_rrr,    &vm_alu93_rrr,    &vm_alu94_rrr,    &vm_alu95_rrr,
    &vm_alu96_rrr,    &vm_alu97_rrr,    &vm_alu98_rrr,    &vm_alu99_rrr,
    &vm_alu100_rrr,   &vm_alu101_rrr,   &vm_alu102_rrr,   &vm_alu103_rrr,
    &vm_alu104_rrr,   &vm_alu105_rrr,   &vm_alu106_rrr,   &vm_alu107_rrr,
    &vm_alu108_rrr,   &vm_alu109_rrr,   &vm_alu110_rrr,   &vm_alu111_rrr,
    &vm_alu112_rrr,   &vm_alu113_rrr,   &vm_alu114_rrr,   &vm_alu115_rrr,
    &vm_alu116_rrr,   &vm_alu117_rrr,   &vm_alu118_rrr,   &vm_alu119_rrr,
    &vm_alu120_rrr,   &vm_alu121_rrr,   &vm_alu122_rrr,   &vm_alu123_rrr,
    &vm_alu124_rrr,   &vm_alu125_rrr,   &vm_alu126_rrr,   &vm_alu127_rrr,
    &vm_alu128_rrr,   &vm_alu129_rrr,   &vm_alu130_rrr,   &vm_alu131_rrr,
    &vm_alu132_rrr,   &vm_alu133_rrr,   &vm_alu134_rrr,   &vm_alu135_rrr,
    &vm_alu136_rrr,   &vm_alu137_rrr,   &vm_alu138_rrr,   &vm_alu139_rrr,
    &vm_alu140_rrr,   &vm_alu141_rrr,   &vm_alu142_rrr,   &vm_alu143_rrr,
    &vm_alu144_rrr,   &vm_alu145_rrr,   &vm_alu146_rrr,   &vm_alu147_rrr,
    &vm_alu148_rrr,   &vm_alu149_rrr,   &vm_alu150_rrr,   &vm_alu151_rrr,
    &vm_alu152_rrr,   &vm_alu153_rrr,   &vm_alu154_rrr,   &vm_alu155_rrr,
    &vm_alu156_rrr,   &vm_alu157_rrr,   &vm_alu158_rrr,   &vm_alu159_rrr,
    &vm_alu160_rrr,   &vm_alu161_rrr,   &vm_alu162_rrr,   &vm_alu163_rrr,
    &vm_alu164_rrr,   &vm_alu165_rrr,   &vm_alu166_rrr,   &vm_alu167_rrr,
    &vm_alu168_rrr,   &vm_alu169_rrr,   &vm_alu170_rrr,   &vm_alu171_rrr,
    &vm_alu172_rrr,   &vm_alu173_rrr,   &vm_alu174_rrr,   &vm_alu175_rrr,
    &vm_alu176_rrr,   &vm_alu177_rrr,   &vm_alu178_rrr,   &vm_alu179_rrr,
    &vm_alu180_rrr,   &vm_alu181_rrr,   &vm_alu182_rrr,   &vm_alu183_rrr,
    &vm_alu184_rrr,   &vm_alu185_rrr,   &vm_alu186_rrr,   &vm_alu187_rrr,
    &vm_alu188_rrr,   &vm_alu189_rrr,   &vm_alu190_rrr,   &vm_alu191_rrr,
    &vm_alu192_rrr,   &vm_alu193_rrr,   &vm_alu194_rrr,   &vm_alu195_rrr,
    &vm_alu196_rrr,   &vm_alu197_rrr,   &vm_alu198_rrr,   &vm_alu199_rrr,
    &vm_alu200_rrr,   &vm_alu201_rrr,   &vm_alu202_rrr,   &vm_alu203_rrr,
    &vm_alu204_rrr,   &vm_alu205_rrr,   &vm_alu206_rrr,   &vm_alu207_rrr,
    &vm_alu208_rrr,   &vm_alu209_rrr,   &vm_alu210_rrr,   &vm_alu211_rrr,
    &vm_alu212_rrr,   &vm_alu213_rrr,   &vm_alu214_rrr,   &vm_alu215_rrr,
    &vm_alu216_rrr,   &vm_alu217_rrr,   &vm_alu218_rrr,   &vm_alu219_rrr,
    &vm_alu220_rrr,   &vm_alu221_rrr,   &vm_alu222_rrr,   &vm_alu223_rrr,
    &vm_alu224_rrr,   &vm_alu225_rrr,   &vm_alu226_rrr,   &vm_alu227_rrr,
    &vm_alu228_rrr,   &vm_alu229_rrr,   &vm_alu230_rrr,   &vm_alu231_rrr,
    &vm_alu232_rrr,   &vm_alu233_rrr,   &vm_alu234_rrr,   &vm_alu235_rrr,
    &vm_alu236_rrr,   &vm_alu237_rrr,   &vm_alu238_rrr,   &vm_alu239_rrr,
    &vm_alu240_rrr,   &vm_alu241_rrr,   &vm_alu242_rrr,   &vm_alu243_rrr,
    &vm_alu244_rrr,   &vm_alu245_rrr,   &vm_alu246_rrr,   &vm_alu247_rrr,
    &vm_alu248_rrr,   &vm_alu249_rrr,   &vm_alu250_rrr,   &vm_alu251_rrr,
    &vm_alu252_rrr,   &vm_alu253_rrr,   &vm_alu254_rrr,   &vm_alu255_rrr,
    &vm_alu256_rrr,   &vm_alu257_rrr,   &vm_alu258_rrr,   &vm_alu259_rrr,
    &vm_alu260_rrr,   &vm_alu261_rrr,   &vm_alu262_rrr,   &vm_alu263_rrr,
    &vm_alu264_rrr,   &vm_alu265_rrr,   &vm_alu266_rrr,   &vm_alu267_rrr,
    &vm_alu268_rrr,   &vm_alu269_rrr,   &vm_alu270_rrr,   &vm_alu271_rrr,
    &vm_alu272_rrr,   &vm_alu273_rrr,   &vm_alu274_rrr,   &vm_alu275_rrr,
    &vm_alu276_rrr,   &vm_alu277_rrr,   &vm_alu278_rrr,   &vm_alu279_rrr,
    &vm_alu280_rrr,   &vm_alu281_rrr,   &vm_alu282_rrr,   &vm_alu283_rrr,
    &vm_alu284_rrr,   &vm_alu285_rrr,   &vm_alu286_rrr,   &vm_alu287_rrr,
    &vm_alu288_rrr,   &vm_alu289_rrr,   &vm_alu290_rrr,   &vm_alu291_rrr,
    &vm_alu292_rrr,   &vm_alu293_rrr,   &vm_alu294_rrr,   &vm_alu295_rrr,
    &vm_alu296_rrr,   &vm_alu297_rrr,   &vm_alu298_rrr,   &vm_alu299_rrr,
    &vm_alu300_rrr,   &vm_alu301_rrr,   &vm_alu302_rrr,   &vm_alu303_rrr,
    &vm_alu304_rrr,   &vm_alu305_rrr,   &vm_alu306_rrr,   &vm_alu307_rrr,
    &vm_alu308_rrr,   &vm_alu309_rrr,   &vm_alu310_rrr,   &vm_alu311_rrr,
    &vm_alu312_rrr,   &vm_alu313_rrr,   &vm_alu314_rrr,   &vm_alu315_rrr,
    &vm_alu316_rrr,   &vm_alu317_rrr,   &vm_alu318_rrr,   &vm_alu319_rrr,
    &vm_alu320_rrr,   &vm_alu321_rrr,   &vm_alu322_rrr,   &vm_alu323_rrr,
    &vm_alu324_rrr,   &vm_alu325_rrr,   &vm_alu326_rrr,   &vm_alu327_rrr,
    &vm_alu328_rrr,   &vm_alu329_rrr,   &vm_alu330_rrr,   &vm_alu331_rrr,
    &vm_alu332_rrr,   &vm_alu333_rrr,   &vm_alu334_rrr,   &vm_alu335_rrr,
    &vm_alu336_rrr,   &vm_alu337_rrr,   &vm_alu338_rrr,   &vm_alu339_rrr,
    &vm_alu340_rrr,   &vm_alu341_rrr,   &vm_alu342_rrr,   &vm_alu343_rrr,
    &vm_alu344_rrr,   &vm_alu345_rrr,   &vm_alu346_rrr,   &vm_alu347_rrr,
    &vm_alu348_rrr,   &vm_alu349_rrr,   &vm_alu350_rrr,   &vm_alu351_rrr,
    &vm_alu352_rrr,   &vm_alu353_rrr,   &vm_alu354_rrr,   &vm_alu355_rrr,
    &vm_alu356_rrr,   &vm_alu357_rrr,   &vm_alu358_rrr,   &vm_alu359_rrr,
    &vm_alu360_rrr,   &vm_alu361_rrr,   &vm_alu362_rrr,   &vm_alu363_rrr,
    &vm_alu364_rrr,   &vm_alu365_rrr,   &vm_alu366_rrr,   &vm_alu367_rrr,
    &vm_alu368_rrr,   &vm_alu369_rrr,   &vm_alu370_rrr,   &vm_alu371_rrr,
    &vm_alu372_rrr,   &vm_alu373_rrr,   &vm_alu374_rrr,   &vm_alu375_rrr,
    &vm_alu376_rrr,   &vm_alu377_rrr,   &vm_alu378_rrr,   &vm_alu379_rrr,
    &vm_alu380_rrr,   &vm_alu381_rrr,   &vm_alu382_rrr,   &vm_alu383_rrr,
    &vm_alu384_rrr,   &vm_alu385_rrr,   &vm_alu386_rrr,   &vm_alu387_rrr,
    &vm_alu388_rrr,   &vm_alu389_rrr,   &vm_alu390_rrr,   &vm_alu391_rrr,
    &vm_alu392_rrr,   &vm_alu393_rrr,   &vm_alu394_rrr,   &vm_alu395_rrr,
    &vm_alu396_rrr,   &vm_alu397_rrr,   &vm_alu398_rrr,   &vm_alu399_rrr,
    &vm_alu400_rrr,   &vm_alu401_rrr,   &vm_alu402_rrr,   &vm_alu403_rrr,
    &vm_alu404_rrr,   &vm_alu405_rrr,   &vm_alu406_rrr,   &vm_alu407_rrr,
    &vm_alu408_rrr,   &vm_alu409_rrr,   &vm_alu410_rrr,   &vm_alu411_rrr,
    &vm_alu412_rrr,   &vm_alu413_rrr,   &vm_alu414_rrr,   &vm_alu415_rrr,
    &vm_alu416_rrr,   &vm_alu417_rrr,   &vm_alu418_rrr,   &vm_alu419_rrr,
    &vm_alu420_rrr,   &vm_alu421_rrr,   &vm_alu422_rrr,   &vm_alu423_rrr,
    &vm_alu424_rrr,   &vm_alu425_rrr,   &vm_alu426_rrr,   &vm_alu427_rrr,
    &vm_alu428_rrr,   &vm_alu429_rrr,   &vm_alu430_rrr,   &vm_alu431_rrr,
    &vm_alu432_rrr,   &vm_alu433_rrr,   &vm_alu434_rrr,   &vm_alu435_rrr,
    &vm_alu436_rrr,   &vm_alu437_rrr,   &vm_alu438_rrr,   &vm_alu439_rrr,
    &vm_alu440_rrr,   &vm_alu441_rrr,   &vm_alu442_rrr,   &vm_alu443_rrr,
    &vm_alu444_rrr,   &vm_alu445_rrr,   &vm_alu446_rrr,   &vm_alu447_rrr,
    &vm_alu448_rrr,   &vm_alu449_rrr,   &vm_alu450_rrr,   &vm_alu451_rrr,
    &vm_alu452_rrr,   &vm_alu453_rrr,   &vm_alu454_rrr,   &vm_alu455_rrr,
    &vm_alu456_rrr,   &vm_alu457_rrr,   &vm_alu458_rrr,   &vm_alu459_rrr,
    &vm_alu460_rrr,   &vm_alu461_rrr,   &vm_alu462_rrr,   &vm_alu463_rrr,
    &vm_alu464_rrr,   &vm_alu465_rrr,   &vm_alu466_rrr,   &vm_alu467_rrr,
    &vm_alu468_rrr,   &vm_alu469_rrr,   &vm_alu470_rrr,   &vm_alu471_rrr,
    &vm_alu472_rrr,   &vm_alu473_rrr,   &vm_alu474_rrr,   &vm_alu475_rrr,
    &vm_alu476_rrr,   &vm_alu477_rrr,   &vm_alu478_rrr,   &vm_alu479_rrr,
    &vm_alu480_rrr,   &vm_alu481_rrr,   &vm_alu482_rrr,   &vm_alu483_rrr,
    &vm_alu484_rrr,   &vm_alu485_rrr,   &vm_alu486_rrr,   &vm_alu487_rrr,
    &vm_alu488_rrr,   &vm_alu489_rrr,   &vm_alu490_rrr,   &vm_alu491_rrr,
    &vm_alu492_rrr,   &vm_alu493_rrr,   &vm_alu494_rrr,   &vm_alu495_rrr,
    &vm_alu496_rrr,   &vm_alu497_rrr,   &vm_alu498_rrr,   &vm_alu499_rrr,
    &vm_alu500_rrr,   &vm_alu501_rrr,   &vm_alu502_rrr,   &vm_alu503_rrr,
    &vm_alu504_rrr,   &vm_alu505_rrr,   &vm_alu506_rrr,   &vm_alu507_rrr,
    &vm_alu508_rrr,   &vm_alu509_rrr,   &vm_alu510_rrr,   &vm_alu511_rrr,
    };

Context context;

// Dummy values, to be relaced by the generator.
uint32_t argument_indices[] = {
    1,
    2,
    3,
    4,
};

volatile size_t argument_count =
    sizeof(argument_indices) / sizeof(*argument_indices);
}

#define BC_WORD                                                                \
  *reinterpret_cast<uint16_t *>(&bytecode[IP]);                                \
  IP += sizeof(uint16_t);

#define BC_QWORD                                                               \
  *reinterpret_cast<uint64_t *>(&bytecode[IP]);                                \
  IP += sizeof(uint64_t);

uint8_t bytecode[] = {};

#define R0 context.regs[reg_r0]
#define R1 context.regs[reg_r1]
#define R2 context.regs[reg_r2]
#define R3 context.regs[reg_r3]
#define IP context.regs[kOffsetIp]

#ifdef DEFINE
#define ENC_RRRIK                                                              \
  uint16_t reg_r0 = BC_WORD;                                                   \
  uint16_t reg_r1 = BC_WORD;                                                   \
  uint16_t reg_r2 = BC_WORD;                                                   \
  uint64_t imm64 = BC_QWORD;                                                   \
  uint64_t key64 = BC_QWORD;                                                   \
  printf("  RRRK: 0x%x, 0x%x, 0x%x (imm64: 0x%lx, key: 0x%lx)\n", reg_r0,      \
         reg_r1, reg_r2, imm64, key64);
#else
#define ENC_RRRIK                                                              \
  uint16_t reg_r0 = BC_WORD;                                                   \
  uint16_t reg_r1 = BC_WORD;                                                   \
  uint16_t reg_r2 = BC_WORD;                                                   \
  uint64_t imm64 = BC_QWORD;                                                   \
  uint64_t key64 = BC_QWORD;
#endif
#define ENC_RRRRK                                                              \
  uint16_t reg_r0 = BC_WORD;                                                   \
  uint16_t reg_r1 = BC_WORD;                                                   \
  uint16_t reg_r2 = BC_WORD;                                                   \
  uint16_t reg_r3 = BC_WORD;                                                   \
  uint64_t key64 = BC_QWORD;                                                   \
  printf("  RRRRK: %x, %x, %x, %x (key: %lx)\n", reg_r0, reg_r1, reg_r2,       \
         reg_r3, key64);

#define ENC_RRIK                                                               \
  uint16_t reg_r0 = BC_WORD;                                                   \
  uint16_t reg_r1 = BC_WORD;                                                   \
  uint64_t imm64 = BC_QWORD;                                                   \
  uint64_t key64 = BC_QWORD;                                                   \
  printf("  RRIK: %x, %x, %lx (key: %lx)\n", reg_r0, reg_r1, imm64, key64);

#ifdef DEBUG
#define VM_NEXT                                                                \
  do {                                                                         \
    uint16_t next = BC_WORD;                                                   \
    printf("OPCODE: %x\n", next);                                              \
    handler_table[next](context);                                              \
  } while (0)
#else
#define VM_NEXT                                                                \
  do {                                                                         \
    uint16_t next = BC_WORD;                                                   \
    handler_table[next](context);                                              \
  } while (0)
#endif

__attribute__((noinline)) void vm_setup(uint64_t vm_argv[], Context &context,
                                        uint64_t initial_ip) {
  context.reset();
  context.regs[kOffsetIp] = initial_ip;

  #ifdef DEBUG
  printf("argument_count: %lu\n", argument_count);
  #endif
  for (uint32_t index = 0; index < argument_count; index++) {
    context.regs[argument_indices[index]] = vm_argv[index];
    #ifdef DEBUG
    printf("%d: reg %u takes input 0x%lx\n", index, argument_indices[index],
           vm_argv[index]);
    #endif
  }
  #ifdef DEBUG
  printf("Initial ip: %lx\n-----------------------------------\n",
         context.regs[kOffsetIp]);
  #endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu1_rrr(Context &context) {
  #ifdef DEBUG
  printf("DEBUG: Memory access handler called\n");
  #endif
  ENC_RRRIK;
  if (key64 == 2) { /* alloca operation */
    #ifdef DEBUG
    printf("        R0 = alloca(%lx)\n", imm64);
    #endif
    R0 = (uint64_t)alloca(imm64);
    #ifdef DEBUG
    printf("        R0 = 0x%lx ; (ptr to allocated memory)\n", R0);
    #endif
  } else if (key64 == 1) { /* store operation */
    if (imm64 == 64) {
      #ifdef DEBUG
      printf("        STORE(addr: 0x%lx, val: 0x%lx, size: 64)\n", R1, R2);
      #endif
      *(uint64_t*) R1 = R2;
    } else if (imm64 == 32) {
      #ifdef DEBUG
      printf("        STORE(addr: 0x%lx, val: 0x%lx, size: 32)\n", R1, R2);
      #endif
      *((uint32_t*) R1) = (uint32_t)R2;
    } else if (imm64 == 16) {
      #ifdef DEBUG
      printf("        STORE(addr: 0x%lx, val: 0x%lx, size: 16)\n", R1, R2);
      #endif
      *((uint16_t*) R1) = (uint16_t)R2;
    } else if (imm64 == 8) {
      #ifdef DEBUG
      printf("        STORE(addr: 0x%lx, val: 0x%lx, size: 8)\n", R1, R2);
      #endif
      *(uint8_t*)R1 = (uint8_t)R2;
    } else {
      /* This should never happen unless Rust code failed to set size properly */
      printf("\nUNREACHABLE STORE: imm64 indicating size is set to %lu (must be multiple of 8 up to 64). Exiting..\n", imm64);
      exit(1);
    }
    R0 = R2; /* we must set R0 -> load value we just stored */
  } else if (key64 == 0) { /* load operation */
    if (imm64 == 64) {
      #ifdef DEBUG
      printf("        R0 = qword ptr [0x%lx]\n", R1);
      #endif
      R0 = *((uint64_t*) R1);
    } else if (imm64 == 32) {
      #ifdef DEBUG
      printf("        R0 = dword ptr [0x%lx]\n", R1);
      #endif
      R0 = *((uint32_t*) R1);
    } else if (imm64 == 16) {
      #ifdef DEBUG
      printf("        R0 = word ptr [0x%lx]\n", R1);
      #endif
      R0 = *((uint16_t*) R1);
    } else if (imm64 == 8) {
      #ifdef DEBUG
      printf("        R0 = byte ptr [0x%lx]\n", R1);
      #endif
      R0 = *((uint8_t*) R1);
    } else {
      /* This should never happen unless Rust code failed to set size properly */
      printf("\nUNREACHABLE LOAD: imm64 indicating size is set to %lu (must be multiple of 8 up to 64). Exiting..\n", imm64);
      exit(1);
    }
    #ifdef DEBUG
    printf("        R0 = 0x%lx (loaded value)\n", R0);
    #endif
  } else { /* unreachable */
      /* This should never happen unless Rust code failed to set size properly */
      printf("\nUNREACHABLE: No valid memory operation detected: imm64 = 0x%lx, key = 0x%lx. Exiting..\n", imm64, key64);
      exit(1);
  }
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu2_rrr(Context &context) {
  ENC_RRRIK;
  R0 = R1 - R2;
#ifdef DEBUG
  printf("        %lx = %lx - %lx\n", R0, R1, R2);
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu3_rrr(Context &context) {
  ENC_RRRIK;
  R0 = R1 || R2;
#ifdef DEBUG
  printf("        %lx = %lx OR %lx\n", R0, R1, R2);
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu4_rrr(Context &context) {
  ENC_RRRIK;
  R0 = R1 && R2;
#ifdef DEBUG
  printf("        %lx = %lx AND %lx\n", R0, R1, R2);
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu5_rrr(Context &context) {
  ENC_RRRIK;
  R0 = R1 ^ R2;
#ifdef DEBUG
  printf("        %lx = %lx XOR %lx\n", R0, R1, R2);
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu6_rrr(Context &context) {
  ENC_RRRIK;
  R0 = !(R1 && R2);
#ifdef DEBUG
  printf("        %lx = %lx NAND %lx\n", R0, R1, R2);
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu7_rrr(Context &context) {
  ENC_RRRIK;
  R0 = !(R1 || R2);
#ifdef DEBUG
  printf("        %lx = %lx NOR %lx\n", R0, R1, R2);
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu8_rrr(Context &context) {
  ENC_RRRIK;
  R0 = !R1;
#ifdef DEBUG
  printf("        %lx = NOT %lx\n", R0, R1);
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu9_rrr(Context &context) {
  ENC_RRRIK;
  R0 = -R1;
#ifdef DEBUG
  printf("        %lx = - %lx\n", R0, R1);
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu10_rrr(Context &context) {
  ENC_RRRIK;
// TODO
#ifdef DEBUG
  printf("NOT IMPLEMENTED: ashr\n");
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu11_rrr(Context &context) {
  ENC_RRRIK;
  R0 = R1 >> R2;
#ifdef DEBUG
  printf("        %lx = %lx >> %lx\n", R0, R1, R2);
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu12_rrr(Context &context) {
  ENC_RRRIK;
  R0 = R1 << R2;
#ifdef DEBUG
  printf("        %lx = %lx << %lx\n", R0, R1, R2);
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu13_rrr(Context &context) {
  ENC_RRRIK;
  R0 = R1 * R2;
#ifdef DEBUG
  printf("        %lx = %lx * %lx\n", R0, R1, R2);
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu14_rrr(Context &context) {
  ENC_RRRIK;
  R0 = R1 / R2;
#ifdef DEBUG
  printf("        %lx = %lx / %lx\n", R0, R1, R2);
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu15_rrr(Context &context) {
  ENC_RRRIK;
// TODO
#ifdef DEBUG
  printf("NOT IMPLEMENTED: sdiv\n");
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu16_rrr(Context &context) {
  ENC_RRRIK;
  R0 = R1 % R2;
#ifdef DEBUG
  printf("        %lx = %lx MOD %lx\n", R0, R1, R2);
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu17_rrr(Context &context) {
  ENC_RRRIK;
// TODO
#ifdef DEBUG
  printf("NOT IMPLEMENTED: srem\n");
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu18_rrr(Context &context) {
  ENC_RRRIK;
  R0 = (R1 < R2);
#ifdef DEBUG
  printf("        %lx = (%lx < %lx)\n", R0, R1, R2);
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu19_rrr(Context &context) {
  ENC_RRRIK;
// TODO
#ifdef DEBUG
  printf("NOT IMPLEMENTED: slt\n");
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu20_rrr(Context &context) {
  ENC_RRRIK;
  R0 = (R1 <= R2);
#ifdef DEBUG
  printf("        %lx = (%lx <= %lx)\n", R0, R1, R2);
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu21_rrr(Context &context) {
  ENC_RRRIK;
// TODO
#ifdef DEBUG
  printf("NOT IMPLEMENTED: sle\n");
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu22_rrr(Context &context) {
  ENC_RRRIK;
  R0 = (R1 == R2);
#ifdef DEBUG
  printf("        %lx = (%lx == %lx)\n", R0, R1, R2);
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu23_rrr(Context &context) {
  ENC_RRRIK;
// TODO
#ifdef DEBUG
  printf("NOT IMPLEMENTED: ite\n");
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu24_rrr(Context &context) {
  ENC_RRRIK;
// TODO
#ifdef DEBUG
  printf("NOT IMPLEMENTED: zero_extend\n");
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu25_rrr(Context &context) {
  ENC_RRRIK;
// TODO
#ifdef DEBUG
  printf("NOT IMPLEMENTED: sign_extend\n");
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu26_rrr(Context &context) {
  ENC_RRRIK;
// TODO
#ifdef DEBUG
  printf("NOT IMPLEMENTED: load\n");
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu27_rrr(Context &context) {
  ENC_RRRIK;
// TODO
#ifdef DEBUG
  printf("NOT IMPLEMENTED: store\n");
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu28_rrr(Context &context) {
  ENC_RRRIK;
// TODO
#ifdef DEBUG
  printf("NOT IMPLEMENTED: alloc\n");
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu29_rrr(Context &context) {
  ENC_RRRIK;
  R0 = R1;
#ifdef DEBUG
  printf("        %lx = %lx (mov reg)\n", R0, R1);
#endif
  VM_NEXT;
}

void __attribute__((noinline)) vm_alu30_rrr(Context &context) {
  ENC_RRRIK;
  R0 = imm64;
#ifdef DEBUG
  printf("        %lx = %lx (mov imm)\n", R0, imm64);
#endif
  VM_NEXT;
}
void __attribute__((noinline)) vm_alu31_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu32_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu33_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu34_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu35_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu36_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu37_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu38_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu39_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu40_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu41_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu42_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu43_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu44_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu45_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu46_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu47_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu48_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu49_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu50_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu51_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu52_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu53_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu54_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu55_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu56_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu57_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu58_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu59_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu60_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu61_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu62_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu63_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu64_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu65_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu66_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu67_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu68_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu69_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu70_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu71_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu72_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu73_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu74_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu75_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu76_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu77_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu78_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu79_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu80_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu81_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu82_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu83_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu84_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu85_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu86_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu87_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu88_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu89_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu90_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu91_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu92_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu93_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu94_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu95_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu96_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu97_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu98_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu99_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu100_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu101_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu102_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu103_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu104_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu105_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu106_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu107_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu108_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu109_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu110_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu111_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu112_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu113_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu114_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu115_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu116_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu117_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu118_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu119_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu120_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu121_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu122_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu123_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu124_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu125_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu126_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu127_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu128_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu129_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu130_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu131_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu132_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu133_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu134_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu135_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu136_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu137_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu138_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu139_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu140_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu141_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu142_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu143_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu144_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu145_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu146_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu147_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu148_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu149_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu150_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu151_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu152_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu153_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu154_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu155_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu156_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu157_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu158_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu159_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu160_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu161_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu162_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu163_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu164_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu165_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu166_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu167_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu168_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu169_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu170_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu171_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu172_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu173_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu174_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu175_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu176_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu177_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu178_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu179_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu180_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu181_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu182_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu183_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu184_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu185_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu186_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu187_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu188_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu189_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu190_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu191_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu192_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu193_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu194_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu195_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu196_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu197_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu198_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu199_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu200_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu201_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu202_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu203_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu204_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu205_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu206_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu207_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu208_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu209_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu210_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu211_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu212_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu213_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu214_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu215_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu216_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu217_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu218_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu219_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu220_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu221_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu222_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu223_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu224_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu225_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu226_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu227_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu228_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu229_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu230_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu231_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu232_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu233_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu234_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu235_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu236_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu237_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu238_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu239_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu240_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu241_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu242_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu243_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu244_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu245_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu246_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu247_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu248_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu249_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu250_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu251_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu252_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu253_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu254_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu255_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu256_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu257_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu258_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu259_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu260_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu261_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu262_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu263_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu264_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu265_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu266_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu267_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu268_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu269_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu270_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu271_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu272_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu273_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu274_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu275_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu276_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu277_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu278_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu279_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu280_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu281_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu282_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu283_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu284_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu285_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu286_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu287_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu288_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu289_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu290_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu291_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu292_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu293_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu294_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu295_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu296_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu297_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu298_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu299_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu300_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu301_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu302_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu303_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu304_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu305_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu306_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu307_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu308_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu309_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu310_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu311_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu312_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu313_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu314_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu315_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu316_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu317_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu318_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu319_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu320_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu321_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu322_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu323_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu324_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu325_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu326_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu327_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu328_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu329_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu330_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu331_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu332_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu333_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu334_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu335_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu336_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu337_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu338_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu339_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu340_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu341_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu342_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu343_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu344_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu345_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu346_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu347_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu348_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu349_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu350_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu351_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu352_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu353_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu354_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu355_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu356_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu357_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu358_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu359_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu360_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu361_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu362_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu363_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu364_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu365_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu366_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu367_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu368_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu369_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu370_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu371_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu372_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu373_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu374_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu375_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu376_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu377_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu378_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu379_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu380_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu381_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu382_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu383_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu384_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu385_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu386_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu387_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu388_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu389_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu390_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu391_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu392_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu393_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu394_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu395_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu396_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu397_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu398_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu399_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu400_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu401_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu402_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu403_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu404_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu405_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu406_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu407_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu408_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu409_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu410_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu411_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu412_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu413_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu414_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu415_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu416_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu417_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu418_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu419_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu420_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu421_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu422_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu423_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu424_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu425_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu426_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu427_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu428_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu429_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu430_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu431_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu432_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu433_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu434_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu435_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu436_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu437_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu438_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu439_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu440_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu441_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu442_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu443_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu444_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu445_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu446_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu447_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu448_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu449_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu450_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu451_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu452_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu453_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu454_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu455_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu456_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu457_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu458_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu459_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu460_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu461_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu462_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu463_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu464_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu465_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu466_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu467_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu468_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu469_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu470_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu471_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu472_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu473_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu474_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu475_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu476_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu477_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu478_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu479_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu480_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu481_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu482_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu483_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu484_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu485_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu486_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu487_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu488_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu489_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu490_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu491_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu492_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu493_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu494_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu495_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu496_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu497_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu498_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu499_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu500_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu501_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu502_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu503_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu504_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu505_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu506_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu507_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu508_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu509_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu510_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void __attribute__((noinline)) vm_alu511_rrr(Context &context) {ENC_RRRIK; R0 = R1 + R2; VM_NEXT;}

void vm_exit(Context &) {
#ifdef DEBUG
  printf("-----------------------------------\nReached vm_exit.\n");
#endif
}

uint64_t parse_input(char const *s, int base = 10) {
    if (s[0] == 's') {
      return (uint64_t)(s+1);
    }
    char *end;
    long  res;
    errno = 0;
    res = strtoul(s, &end, base);
    if (errno == ERANGE && res == LONG_MAX) {
      printf("Argument %s caused overflow\n", s);
      exit(1);
    }
    if (errno == ERANGE && res == LONG_MIN) {
      printf("Argument %s caused underflow\n", s);
      exit(1);
    }
    if (*s == '\0' || *end != '\0') {
      printf("Argument %s cannot be converted - will be interpreted as string\n", s);
      return (uint64_t)s;
    }
    return (uint64_t)res;
}

int main(int argc, char *argv[]) {
  if (argc < 1 + argument_count) {
    printf("Expected %lu parameters\n", argument_count);
    return -1;
  }

  /* Prepare arguments for VM */
  uint64_t vm_argv[argument_count];
  for (int i = 0; i < argument_count; ++i) {
    /* Convert number_strings to number */
    vm_argv[i] = parse_input(argv[i+1]);
    printf("arg %d: 0x%lx\n", i, vm_argv[i]);
  }
  double duration_sum = 0;
  int result = 0;
  for (int i = 0; i < 10000; ++i) {
    auto t1 = std::chrono::high_resolution_clock::now();
    vm_setup(vm_argv, context, 0);
    auto t2 = std::chrono::high_resolution_clock::now();
    duration_sum += std::chrono::duration<double, std::micro>( t2 - t1 ).count();
  }
  printf("Output: %lu\n", context.regs[kOffsetOutput]);
  printf("Time: %lf\n", (duration_sum / 10000));
  printf("Done.\n");
  return 0;
}
