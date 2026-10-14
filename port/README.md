# port/ — loader, runtime e núcleo de vídeo do The Last Guardian para PC

Este diretório tem o código que roda o `eboot.bin` original do TLG (PS4, CUSA03627 v1.03) no PC:

- `scripts/`: preparação e link do eboot com os módulos do jogo e do console (`prepare.py`, `link_modules.py`);
- `src/`: loader (`probe.c`) e runtime que reimplementa as bibliotecas do PS4 (`runtime_*.c`, `runtime_tlg.c`);
- `gpu/`: tradução de GPU para Vulkan (núcleo do shadPS4, mais o overlay/menu em `gpu/shim/`);
- `launcher/`: launcher gráfico (`tlg_launcher.py`) e núcleo de execução (`tlg_run.py`).

Documentação, status e instruções de uso estão no [README principal](../README.md).
A origem do código (gow3_pc → bloodborne_pc, shadPS4) e a licença (GPL-2.0-or-later) estão em
[UPSTREAM.md](UPSTREAM.md) e [LICENSE](LICENSE).
