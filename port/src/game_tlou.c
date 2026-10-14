/* SPDX-License-Identifier: GPL-2.0-or-later
 *
 * The Last of Us Remastered (tlou_pc, CUSA00552 1.11): hook table for the core
 * (src/runtime_game.h). Every import the game needs is answered by the core itself
 * (runtime_fiber.c, runtime_offline.c and the rest), so there are no game resolvers yet.
 */
#include "runtime_game.h"

static const char *const titles[] = {"CUSA00552", NULL};
const RuntimeGame runtime_game = {
    .slug = "tlou",
    .name = "The Last of Us Remastered",
    .title_ids = titles,
    .env_prefix = "TLOU_",
    .profile = "profile.ini",
};
