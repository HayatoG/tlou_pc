# Arquivos do jogo necessários / Required game files

[Português](#arquivos-do-jogo-necessários) · [English](#required-game-files)

## Arquivos do jogo necessários

Tudo vem do **seu** PS4 (GoldHEN + Itemzflow). Nada disso vai no download. Use **The Last of Us Remastered CUSA00552 (EUA), jogo base 1.00 com o update 1.11**, montado numa pasta só, com o jogo base e o update por cima. São ~56 GB (55 GB do jogo base + 0,7 GB do update).

| Arquivo | Vem de | Para quê |
|---|---|---|
| `eboot.bin` | update 1.11 | o código do jogo (tem que ser o do 1.11) |
| `sce_module/libc.prx`, `sce_module/libSceFios2.prx` | update 1.11 | bibliotecas do próprio jogo |
| `patch.psarc` | update 1.11 | o conteúdo do update |
| `build/ps4/` | jogo base | o conteúdo do jogo (níveis, sons, vídeos) |
| `data.psarc` | jogo base | dados iniciais |
| `sce_sys/` (`param.sfo`, `icon0.png`, `pic1.png`) | jogo base (+ `param.sfo` do update) | metadados e a arte do launcher |
| `sce_discmap.plt`, `sce_discmap_patch.plt` | base + update | mapa de arquivos |

**Do firmware do console:** nada. A pasta `system_lib/` do pacote fica vazia.

**Como montar a pasta:**
1. No Itemzflow, faça o dump do jogo (`CUSA00552`) e do update (`CUSA00552-patch`) para um pendrive **exFAT**.
2. No PC, copie a pasta do jogo base e depois copie o conteúdo do update **por cima**, substituindo os arquivos. Também dá para usar `scripts/make_game_view.py <base> <update> <saída>`, que monta a pasta com links, sem ocupar espaço.
3. O `param.sfo` da versão 1.11 fica no PS4 em `/system_data/priv/appmeta/CUSA00552/param.sfo`: copie para o `sce_sys/` da pasta montada.
4. **Não use o FTP do GoldHEN para o jogo base:** `build/ps4/main/mp-levels.psarc` passa de 4 GB, e o FTP corta arquivos desse tamanho. Use o pendrive. Para o update, o FTP serve (`/mnt/sandbox/pfsmnt/CUSA00552-patch0`, com o jogo aberto).

## Required game files

Everything comes from **your own** PS4 (GoldHEN + Itemzflow). None of it is in the download. Use **The Last of Us Remastered CUSA00552 (US), base game 1.00 with update 1.11**, merged into one folder, with the base game and the update on top. About 56 GB (55 GB base game + 0.7 GB update).

| File | From | Purpose |
|---|---|---|
| `eboot.bin` | update 1.11 | the game code (must be the 1.11 one) |
| `sce_module/libc.prx`, `sce_module/libSceFios2.prx` | update 1.11 | the game's own libraries |
| `patch.psarc` | update 1.11 | the update's content |
| `build/ps4/` | base game | the game content (levels, sound, movies) |
| `data.psarc` | base game | startup data |
| `sce_sys/` (`param.sfo`, `icon0.png`, `pic1.png`) | base game (+ the update's `param.sfo`) | metadata and the launcher art |
| `sce_discmap.plt`, `sce_discmap_patch.plt` | base + update | file map |

**From the console firmware:** nothing. The package's `system_lib/` folder stays empty.

**How to build the folder:**
1. In Itemzflow, dump the game (`CUSA00552`) and the update (`CUSA00552-patch`) to an **exFAT** USB drive.
2. On the PC, copy the base game folder, then copy the update's contents **over it**, replacing files. Or use `scripts/make_game_view.py <base> <update> <out>`, which builds the folder with links and uses no extra space.
3. The 1.11 `param.sfo` is at `/system_data/priv/appmeta/CUSA00552/param.sfo` on the PS4: copy it into the merged folder's `sce_sys/`.
4. **Don't use GoldHEN's FTP for the base game:** `build/ps4/main/mp-levels.psarc` is over 4 GB, and the FTP truncates files that size. Use the USB drive. For the update, the FTP works (`/mnt/sandbox/pfsmnt/CUSA00552-patch0`, with the game running).
