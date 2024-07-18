
/*
 * Copyright (c) 2016 Thomas Pornin <pornin@bolet.org>
 *
 * Permission is hereby granted, free of charge, to any person obtaining
 * a copy of this software and associated documentation files (the
 * "Software"), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish,
 * distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so, subject to
 * the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 * BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
 * ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#ifndef LIBTOMMATH_BEAR_H
#define LIBTOMMATH_BEAR_H

/* ==================================================================== */
/*
 * Constant-time primitives. These functions manipulate 32-bit values in
 * order to provide constant-time comparisons and multiplexers.
 *
 * Boolean values (the "ctl" bits) MUST have value 0 or 1.
 *
 * Implementation notes:
 * =====================
 *
 * The uintN_t types are unsigned and with width exactly N bits; the C
 * standard guarantees that computations are performed modulo 2^N, and
 * there can be no overflow. Negation (unary '-') works on unsigned types
 * as well.
 *
 * The intN_t types are guaranteed to have width exactly N bits, with no
 * padding bit, and using two's complement representation. Casting
 * intN_t to uintN_t really is conversion modulo 2^N. Beware that intN_t
 * types, being signed, trigger implementation-defined behaviour on
 * overflow (including raising some signal): with GCC, while modular
 * arithmetics are usually applied, the optimizer may assume that
 * overflows don't occur (unless the -fwrapv command-line option is
 * added); Clang has the additional -ftrapv option to explicitly trap on
 * integer overflow or underflow.
 */

#include <stdint.h>
#include <stddef.h>
#include <limits.h>

#include "tommath_private.h"

/*
 * Negate a boolean.
 */
static inline mp_digit
NOT(mp_digit ctl)
{
    return ctl ^ 1;
}

/*
 * Multiplexer: returns x if ctl == 1, y if ctl == 0.
 */
static inline mp_digit
MUX(mp_digit ctl, mp_digit x, mp_digit y)
{
    return y ^ (-ctl & (x ^ y));
}

/*
 * Equality check: returns 1 if x == y, 0 otherwise.
 */
static inline mp_digit
EQ(mp_digit x, mp_digit y)
{
    mp_digit q;

    q = x ^ y;
    return NOT((q | -q) >> (MP_DIGIT_SIZE - 1));
}

/*
 * Inequality check: returns 1 if x != y, 0 otherwise.
 */
static inline mp_digit
NEQ(mp_digit x, mp_digit y)
{
    mp_digit q;

    q = x ^ y;
    return (q | -q) >> (MP_DIGIT_SIZE - 1);
}

/*
 * Comparison: returns 1 if x > y, 0 otherwise.
 */
static inline mp_digit
GT(mp_digit x, mp_digit y)
{
    /*
     * If both x < 2^(ds-1) and x < 2^(ds-1), then y-x will have its high
     * bit set if x > y, cleared otherwise.
     *
     * If either x >= 2^(ds-1) or y >= 2^(ds-1) (but not both), then the
     * result is the high bit of x.
     *
     * If both x >= 2^(ds-1) and y >= 2^(ds-1), then we can virtually
     * subtract 2^(ds-1) from both, and we are back to the first case.
     * Since (y-2^(ds-1))-(x-2^(ds-1)) = y-x, the subtraction is already
     * fine.
     */
    mp_digit z;

    z = y - x;
    return (z ^ ((x ^ y) & (x ^ z))) >> (MP_DIGIT_SIZE - 1);
}

/*
 * Other comparisons (greater-or-equal, lower-than, lower-or-equal).
 */
#define GE(x, y)   NOT(GT(y, x))
#define LT(x, y)   GT(y, x)
#define LE(x, y)   NOT(GT(x, y))

/*
 * General comparison: returned value is -1, 0 or 1, depending on
 * whether x is lower than, equal to, or greater than y.
 */
static inline mp_sdigit
CMP(mp_digit x, mp_digit y)
{
    return (mp_sdigit)GT(x, y) | -(mp_sdigit)GT(y, x);
}

/*
 * Returns 1 if x == 0, 0 otherwise. Take care that the operand is signed.
 */
//TODO Fix this.
static inline uint32_t
EQ0(int32_t x)
{
    uint32_t q;

    q = (uint32_t)x;
    return ~(q | -q) >> 31;
}

/*
 * Returns 1 if x > 0, 0 otherwise. Take care that the operand is signed.
 */
//TODO Fix this.
static inline uint32_t
GT0(int32_t x)
{
    /*
     * High bit of -x is 0 if x == 0, but 1 if x > 0.
     */
    uint32_t q;

    q = (uint32_t)x;
    return (~q & -q) >> 31;
}

/*
 * Returns 1 if x >= 0, 0 otherwise. Take care that the operand is signed.
 */
//TODO Fix this.
static inline uint32_t
GE0(int32_t x)
{
    return ~(uint32_t)x >> 31;
}

/*
 * Returns 1 if x < 0, 0 otherwise. Take care that the operand is signed.
 */
//TODO Fix this.
static inline uint32_t
LT0(int32_t x)
{
    return (uint32_t)x >> 31;
}

/*
 * Returns 1 if x <= 0, 0 otherwise. Take care that the operand is signed.
 */
//TODO Fix this.
static inline uint32_t
LE0(int32_t x)
{
    uint32_t q;

    /*
     * ~-x has its high bit set if and only if -x is nonnegative (as
     * a signed int), i.e. x is in the -(2^31-1) to 0 range. We must
     * do an OR with x itself to account for x = -2^31.
     */
    q = (uint32_t)x;
    return (q | ~-q) >> 31;
}


/*
 * Compute the bit length of a mp_digit. Returned value is between 0
 * and MP_DIGIT_SIZE (inclusive).
 */
static inline mp_digit
BIT_LENGTH(mp_digit x)
{
    mp_digit k, c;

    k = NEQ(x, 0);
#if defined(MP_64BIT)
    c = GT(x, 0xFFFFFFFF); x = MUX(c, x >> 32, x); k += c << 5;
    c = GT(x, 0x0000FFFF); x = MUX(c, x >> 16, x); k += c << 4;
#elif defined(MP_32BIT)
    c = GT(x, 0x0000FFFF); x = MUX(c, x >> 16, x); k += c << 4;
#endif
    c = GT(x, 0x000000FF); x = MUX(c, x >>  8, x); k += c << 3;
    c = GT(x, 0x0000000F); x = MUX(c, x >>  4, x); k += c << 2;
    c = GT(x, 0x00000003); x = MUX(c, x >>  2, x); k += c << 1;
    k += GT(x, 0x00000001);
    return k;
}

/*
 * Compute the minimum of x and y.
 */
static inline mp_digit
MIN(mp_digit x, mp_digit y)
{
    return MUX(GT(x, y), y, x);
}

/*
 * Compute the maximum of x and y.
 */
static inline mp_digit
MAX(mp_digit x, mp_digit y)
{
    return MUX(GT(x, y), x, y);
}

/*
 * Multiply two 32-bit integers, with a 64-bit result. This default
 * implementation assumes that the basic multiplication operator
 * yields constant-time code.
 */
#define MUL(x, y)   ((uint64_t)(x) * (uint64_t)(y))

/*
 * Multiply two 31-bit integers, with a 62-bit result. This default
 * implementation assumes that the basic multiplication operator
 * yields constant-time code.
 * The MUL31_lo() macro returns only the low 31 bits of the product.
 */
#define MUL31(x, y)     ((uint64_t)(x) * (uint64_t)(y))
#define MUL31_lo(x, y)  (((uint32_t)(x) * (uint32_t)(y)) & (uint32_t)0x7FFFFFFF)

/*
 * Multiply two words together; the sum of the lengths of the two
 * operands must not exceed 31 (for instance, one operand may use 16
 * bits if the other fits on 15).
 */
#define MUL15(x, y)   ((uint32_t)(x) * (uint32_t)(y))

/*
 * Arithmetic right shift (sign bit is copied). What happens when
 * right-shifting a negative value is _implementation-defined_, so it
 * does not trigger undefined behaviour, but it is still up to each
 * compiler to define (and document) what it does. Most/all compilers
 * will do an arithmetic shift, the sign bit being used to fill the
 * holes; this is a native operation on the underlying CPU, and it would
 * make little sense for the compiler to do otherwise. GCC explicitly
 * documents that it follows that convention.
 */
#define ARSH(x, n)   ((*(int32_t *)&(x)) >> (n))


#endif //LIBTOMMATH_BEAR_H
