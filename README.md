# Link da bio do Azor - Getearia

Página: https://getearia.github.io/ (repositório público `Getearia/getearia.github.io`, da organização Getearia, para o endereço não mostrar o usuário pessoal do GitHub).

O que ela mostra:
- os botões do YouTube e do TikTok, que abrem os apps;
- os links fixados à mão (`links.json`);
- o vídeo novo, os Shorts recentes e mais vídeos do canal (`videos.json`).

O `videos.json` se atualiza sozinho: a cada 30 min, o GitHub lê o feed do canal (`atualizar.py`, rodado pelo `.github/workflows/publicar.yml`) e republica a página quando aparece vídeo novo.

Os links de vídeo passam pela página https://getearia.github.io/yt/, que abre o app do YouTube em vez do navegador do Instagram.

## Fixar um link no topo
```
python adicionar.py <link do YouTube ou do TikTok> [--etiqueta "Vídeo novo"] [--titulo "..."]
python adicionar.py --listar
python adicionar.py --remover 1
```
Ele grava o `links.json`, faz o commit e o push. A página muda em 1 a 2 minutos.

## Página que abre o app do YouTube
`yt/index.html` (https://getearia.github.io/yt/?v=ID, ?s=ID, ?c=@canal). É a mesma página do antigo `duugagno/yt`, que continua no ar só para os links de story já postados.
