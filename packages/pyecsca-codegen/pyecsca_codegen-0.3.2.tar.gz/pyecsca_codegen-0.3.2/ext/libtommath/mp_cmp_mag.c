#include "tommath_private.h"
#include "bear.h"
#ifdef MP_CMP_MAG_C
/* LibTomMath, multiple-precision integer library -- Tom St Denis */
/* SPDX-License-Identifier: Unlicense */

/* compare magnitude of two ints (unsigned) */
mp_ord mp_cmp_mag(const mp_int *a, const mp_int *b)
{
    int n;
    mp_ord res = MP_EQ;

    if (a->used != b->used) {
        return a->used > b->used ? MP_GT : MP_LT;
    }

    for (n = a->used; n --> 0;) {
        res = MUX(EQ(a->dp[n], b->dp[n]) | NEQ(res, MP_EQ), res, CMP(a->dp[n], b->dp[n]));
    }

    return res;
}
#endif