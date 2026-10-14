/* SPDX-License-Identifier: GPL-2.0-or-later
 *
 * The Last of Us Remastered (tlou_pc, CUSA00552 1.11): hook table for the core
 * (src/runtime_game.h). Every import the game needs is answered by the core itself
 * (runtime_fiber.c, runtime_offline.c and the rest), so there are no game resolvers yet.
 */
#include <stdio.h>
#include <string.h>
#include "runtime_game.h"

/* ndgi-orbis-device.cpp WaitOnContextDone halts the game when a frame's GPU work takes over
 * 2 s (float at image offset 0x1177810, read only there, 1.11). On PC the first use of a shader
 * compiles it, which can exceed that once; the limit becomes 60 s. */
#define FRAME_TIMEOUT_OFFSET 0x1177810u
static int patch_image(const RuntimeGameImage *image) {
    float old = 2.0f, limit = 60.0f;
    if (image->size < FRAME_TIMEOUT_OFFSET + 4 || memcmp(image->base + FRAME_TIMEOUT_OFFSET, &old, 4)) {
        printf("TLOU: frame timeout not found (not the 1.11 eboot?): left as is\n");
        return 0;
    }
    memcpy(image->base + FRAME_TIMEOUT_OFFSET, &limit, 4);
    return 1;
}

static const char *const titles[] = {"CUSA00552", NULL};
const RuntimeGame runtime_game = {
    .slug = "tlou",
    .name = "The Last of Us Remastered",
    .title_ids = titles,
    .env_prefix = "TLOU_",
    .profile = "profile.ini",
    .patch_image = patch_image,
};
