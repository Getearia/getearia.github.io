"""Lê o feed público do canal no YouTube e grava os últimos vídeos em videos.json (só a biblioteca padrão do Python).
Roda sozinho no GitHub (a cada 30 min, .github/workflows/publicar.yml) e também roda aqui: python atualizar.py"""
import json, os, re, sys, urllib.request
from datetime import datetime, timezone

CANAL = 'UCSUV-9GGbmqeAnMdV78K_3A'   # @getearia
FEED = 'https://www.youtube.com/feeds/videos.xml?channel_id=' + CANAL
AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, 'videos.json')


def ler_feed():
    req = urllib.request.Request(FEED, headers={'User-Agent': 'Mozilla/5.0 (link-bio)'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8')


def desescapar(t):
    return (t.replace('&quot;', '"').replace('&#39;', "'").replace('&apos;', "'").replace('&lt;', '<').replace('&gt;', '>')
            .replace('&amp;', '&'))


def main():
    xml = ler_feed()
    videos = []
    for e in re.findall(r'<entry>(.*?)</entry>', xml, re.S):
        vid = re.search(r'<yt:videoId>(.*?)</yt:videoId>', e)
        tit = re.search(r'<title>(.*?)</title>', e, re.S)
        pub = re.search(r'<published>(.*?)</published>', e)
        link = re.search(r'<link rel="alternate" href="(.*?)"', e)
        if not (vid and tit):
            continue
        videos.append({'id': vid.group(1), 'titulo': desescapar(tit.group(1).strip()),
                       'tipo': 'short' if link and '/shorts/' in link.group(1) else 'video',
                       'publicado': pub.group(1) if pub else ''})
    if not videos:
        sys.exit('o feed veio vazio; videos.json ficou como estava')
    antigo = None
    if os.path.exists(SAIDA):
        try:
            antigo = json.load(open(SAIDA, encoding='utf-8')).get('videos')
        except ValueError:
            pass
    # O feed só traz os 15 envios mais recentes; com vários Shorts por dia, os longos sairiam da lista em poucos dias.
    # Por isso os longos que já estavam no videos.json ficam (até 20), mesmo depois de saírem do feed.
    ids = {v['id'] for v in videos}
    guardados = [v for v in (antigo or []) if v.get('tipo') == 'video' and v.get('id') not in ids]
    longos = sorted([v for v in videos if v['tipo'] == 'video'] + guardados, key=lambda v: v.get('publicado', ''), reverse=True)[:20]
    videos = sorted([v for v in videos if v['tipo'] == 'short'] + longos, key=lambda v: v.get('publicado', ''), reverse=True)
    if antigo == videos:
        print('sem vídeo novo')
        return
    dados = {'atualizado': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'videos': videos}
    with open(SAIDA, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print(f'{len(videos)} vídeos gravados ({sum(v["tipo"] == "short" for v in videos)} Shorts)')


if __name__ == '__main__':
    main()
