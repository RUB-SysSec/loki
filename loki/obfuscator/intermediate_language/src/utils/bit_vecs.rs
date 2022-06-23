pub fn is_bit_set(pos: u8, x: u32) -> bool {
    match x & (1 << pos) {
        0 => false,
        _ => true,
    }
}

pub fn slice_val(v: u64, start: u8, end: u8) -> u64 {
    let shift = (end - start + 1).min(63);
    let mask = (1 << shift) - 1;
    mask & (v >> start)
}

pub fn concat_val(x: u64, y: u64, size: usize) -> u64 {
    (x << size) | y
}

pub fn u32_to_bit_vec(instruction_bytes: u32) -> Vec<u8> {
    let mut ret = Vec::with_capacity(32);
    for index in 0..32 {
        if is_bit_set(index, instruction_bytes) {
            ret.push(1);
        } else {
            ret.push(0);
        }
    }
    ret
}

pub fn sign_extend(x: u64, size_x: usize, size: usize) -> u64 {
    let mask = 1 << (size_x - 1);
    mask_to_size((x ^ mask).wrapping_sub(mask), size)
}

pub fn mask_to_size(x: u64, size: usize) -> u64 {
    if size >= 64 {
        return x;
    }

    x & ((1 << size) - 1)
}

pub fn get_minus_one(size: usize) -> u64 {
    match size {
        64 => u64::max_value().into(),
        _ => (1 << size) - 1,
    }
}

pub fn is_negative(x: u64, size: usize) -> bool {
    (x >> (size - 1)) != 0
}

pub fn to_negative(x: u64, size: usize) -> u64 {
    assert!(size <= 32);
    if !is_negative(x, size) {
        return mask_to_size(x, size) - x;
    }
    x
}

pub fn saturating_cast(x: u64) -> u32 {
    match x > u32::max_value().into() {
        true => u32::max_value(),
        false => x as u32,
    }
}

pub fn shl(x: u64, y: u64, size: u64) -> u64 {
    match size {
        8 => x.checked_shl(saturating_cast(y)).unwrap_or(0) as u64,
        16 => x.checked_shl(saturating_cast(y)).unwrap_or(0) as u64,
        32 => x.checked_shl(saturating_cast(y)).unwrap_or(0) as u64,
        64 => x.checked_shl(saturating_cast(y)).unwrap_or(0),
        _ => unreachable!(),
    }
}

pub fn shr(x: u64, y: u64, size: u64) -> u64 {
    match size {
        8 => x.checked_shr(saturating_cast(y)).unwrap_or(0) as u64,
        16 => x.checked_shr(saturating_cast(y)).unwrap_or(0) as u64,
        32 => x.checked_shr(saturating_cast(y)).unwrap_or(0) as u64,
        64 => x.checked_shr(saturating_cast(y)).unwrap_or(0),
        _ => unreachable!(),
    }
}

pub fn ashr(x: u64, mut y: u64, size: u64) -> u64 {
    if y >= size {
        y = size - 1;
    }

    match size {
        8 => ((x as i8) >> (y as i8)) as u8 as u64,
        16 => ((x as i16) >> (y as i16)) as u16 as u64,
        32 => ((x as i32) >> (y as i32)) as u32 as u64,
        64 => ((x as i64) >> (y as i64)) as u64,
        _ => unreachable!(),
    }
}

pub fn sdiv(x: u64, y: u64, size: u64) -> u64 {
    match size {
        8 => {
            match y {
                0 if (x as i8) < 0 => return 1,
                0 => return 0xff,
                _ => {}
            };
            ((x as i8).wrapping_div(y as i8) as u8) as u64
        }
        16 => {
            match y {
                0 if (x as i16) < 0 => return 1,
                0 => return 0xffff,
                _ => {}
            };
            ((x as i16).wrapping_div(y as i16) as u16) as u64
        }
        32 => {
            match y {
                0 if (x as i32) < 0 => return 1,
                0 => return 0xffffffff,
                _ => {}
            };
            ((x as i32).wrapping_div(y as i32) as u32) as u64
        }
        64 => {
            match y {
                0 if (x as i64) < 0 => return 1,
                0 => return 0xffffffffffffffff,
                _ => {}
            };
            (x as i64).wrapping_div(y as i64) as u64
        }
        _ => unreachable!(),
    }
}

pub fn srem(x: u64, y: u64, size: u64) -> u64 {
    if y == 0 {
        return x;
    }

    match size {
        8 => ((x as i8).wrapping_rem(y as i8) as u8) as u64,
        16 => ((x as i16).wrapping_rem(y as i16) as u16) as u64,
        32 => ((x as i32).wrapping_rem(y as i32) as u32) as u64,
        64 => (x as i64).wrapping_rem(y as i64) as u64,
        _ => unreachable!(),
    }
}

pub fn slt(x: u64, y: u64, size: u64) -> u64 {
    match size {
        8 => {
            if (x as i8) < (y as i8) {
                1
            } else {
                0
            }
        }
        16 => {
            if (x as i16) < (y as i16) {
                1
            } else {
                0
            }
        }
        32 => {
            if (x as i32) < (y as i32) {
                1
            } else {
                0
            }
        }
        64 => {
            if (x as i64) < (y as i64) {
                1
            } else {
                0
            }
        }
        _ => unreachable!(),
    }
}

pub fn sle(x: u64, y: u64, size: u64) -> u64 {
    match size {
        8 => {
            if (x as i8) <= (y as i8) {
                1
            } else {
                0
            }
        }
        16 => {
            if (x as i16) <= (y as i16) {
                1
            } else {
                0
            }
        }
        32 => {
            if (x as i32) <= (y as i32) {
                1
            } else {
                0
            }
        }
        64 => {
            if (x as i64) <= (y as i64) {
                1
            } else {
                0
            }
        }
        _ => unreachable!(),
    }
}
