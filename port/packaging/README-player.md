# The Last of Us Remastered — port para PC / PC port

Por HayatoG · YouTube: [@hayatog-dev](https://www.youtube.com/@hayatog-dev) · Discord: [discord.gg/UMkdMYZh9g](https://discord.gg/UMkdMYZh9g) · Código: [github.com/HayatoG/tlou_pc](https://github.com/HayatoG/tlou_pc)

**Nenhum arquivo do jogo vem neste pacote.** Você precisa da sua própria cópia de The Last of Us Remastered para PS4. / **No game files are included.** You need your own copy of The Last of Us Remastered for PS4.

Versão de desenvolvimento: **o jogo ainda não inicia.** / Development build: **the game does not boot yet.**

---

## Português

### Arquivos do jogo necessários

Tudo vem do **seu** PS4 (GoldHEN + Itemzflow). Nada disso vai no download. Use **The Last of Us Remastered CUSA00552 (EUA), jogo base 1.00 com o update 1.11**, montado numa pasta só, com o jogo base e o update por cima. São ~56 GB.

| Arquivo | Vem de | Para quê |
|---|---|---|
| `eboot.bin` | update 1.11 | o código do jogo (tem que ser o do 1.11) |
| `sce_module/libc.prx`, `sce_module/libSceFios2.prx` | update 1.11 | bibliotecas do próprio jogo |
| `patch.psarc` | update 1.11 | o conteúdo do update |
| `build/ps4/` | jogo base | o conteúdo do jogo (níveis, sons, vídeos) |
| `data.psarc` | jogo base | dados iniciais |
| `sce_sys/` (`param.sfo`, `icon0.png`, `pic1.png`) | jogo base (+ `param.sfo` do update) | metadados e a arte do launcher |
| `sce_discmap.plt`, `sce_discmap_patch.plt` | base + update | mapa de arquivos |

**Do firmware do console:** nada. A pasta `system_lib/` fica vazia.

**Como montar a pasta:**
1. No Itemzflow, faça o dump do jogo (`CUSA00552`) e do update (`CUSA00552-patch`) para um pendrive exFAT.
2. No PC, copie a pasta do jogo base e depois copie o conteúdo do update **por cima**, substituindo os arquivos.
3. O `param.sfo` da versão 1.11 fica no PS4 em `/system_data/priv/appmeta/CUSA00552/param.sfo`: copie para o `sce_sys/` da pasta montada.
4. **Não use o FTP do GoldHEN para o jogo base:** `build/ps4/main/mp-levels.psarc` passa de 4 GB e o FTP corta arquivos desse tamanho. Use o pendrive.

**PC:** Windows 10 (1903+)/11 64 bits ou Linux x86-64 (glibc 2.39+), placa de vídeo com Vulkan 1.3 (6 GB de VRAM recomendados).

### Como jogar

1. Extraia o pacote numa pasta qualquer (no Windows, fora do .zip).
2. Abra **The Last of Us Remastered** (`The Last of Us Remastered.exe` no Windows). No Windows, se aparecer "O Windows protegeu o computador", clique em *Mais informações* e depois em *Executar assim mesmo*. O programa não é assinado digitalmente.
3. Em **Pasta do jogo**, escolha a pasta que tem o `eboot.bin`. Escolha o idioma e clique em **Jogar**.

No Linux, `./install_desktop.sh` adiciona o jogo ao menu de aplicativos.

### Durante o jogo
- **F10**: contador de FPS · **Insert** (ou R3 + L2): menu do port
- Controles de PS4/PS5, Xbox e 8BitDo via SDL3, por USB ou Bluetooth.

### Problemas
- **Não abre ou fecha sozinho**: é o esperado nesta fase. Mande o `out/last_run.log` no [Discord](https://discord.gg/UMkdMYZh9g) ou numa [issue](https://github.com/HayatoG/tlou_pc/issues) se quiser ajudar.

---

## English

### Required game files

Everything comes from **your own** PS4 (GoldHEN + Itemzflow). None of it is in the download. Use **The Last of Us Remastered CUSA00552 (US), base game 1.00 with update 1.11**, merged into one folder, with the base game and the update on top. About 56 GB.

| File | From | Purpose |
|---|---|---|
| `eboot.bin` | update 1.11 | the game code (must be the 1.11 one) |
| `sce_module/libc.prx`, `sce_module/libSceFios2.prx` | update 1.11 | the game's own libraries |
| `patch.psarc` | update 1.11 | the update's content |
| `build/ps4/` | base game | the game content (levels, sound, movies) |
| `data.psarc` | base game | startup data |
| `sce_sys/` (`param.sfo`, `icon0.png`, `pic1.png`) | base game (+ the update's `param.sfo`) | metadata and the launcher art |
| `sce_discmap.plt`, `sce_discmap_patch.plt` | base + update | file map |

**From the console firmware:** nothing. The `system_lib/` folder stays empty.

**How to build the folder:**
1. In Itemzflow, dump the game (`CUSA00552`) and the update (`CUSA00552-patch`) to an exFAT USB drive.
2. On the PC, copy the base game folder, then copy the update's contents **over it**, replacing files.
3. The 1.11 `param.sfo` is at `/system_data/priv/appmeta/CUSA00552/param.sfo` on the PS4: copy it into the merged folder's `sce_sys/`.
4. **Don't use GoldHEN's FTP for the base game:** `build/ps4/main/mp-levels.psarc` is over 4 GB and the FTP truncates files that size. Use the USB drive.

**PC:** 64-bit Windows 10 (1903+)/11 or x86-64 Linux (glibc 2.39+), a graphics card with Vulkan 1.3 (6 GB of VRAM recommended).

### How to play

1. Extract the package anywhere (on Windows, outside the .zip).
2. Open **The Last of Us Remastered** (`The Last of Us Remastered.exe` on Windows). On Windows, if "Windows protected your PC" appears, click *More info*, then *Run anyway*. The program is not digitally signed.
3. Under **Game folder**, choose the folder that has `eboot.bin`. Pick the language and click **Play**.

On Linux, `./install_desktop.sh` adds the game to the applications menu.

### While playing
- **F10**: FPS counter · **Insert** (or R3 + L2): the port's menu
- PS4/PS5, Xbox and 8BitDo controllers via SDL3, over USB or Bluetooth.

### Problems
- **Does not start or closes by itself**: expected at this stage. Send `out/last_run.log` on [Discord](https://discord.gg/UMkdMYZh9g) or in an [issue](https://github.com/HayatoG/tlou_pc/issues) if you want to help.

---

This project is not affiliated with Sony Interactive Entertainment or Sucker Punch Productions. TLOU is a trademark of Sony Interactive Entertainment. / Este projeto não tem vínculo com a Sony Interactive Entertainment ou a Sucker Punch Productions.
