"""Fixa (ou tira) links no topo da página da bio, na seção "Em destaque", e já publica no GitHub.

  python adicionar.py <link> [--etiqueta "Vídeo novo"] [--titulo "..."]   fixa no topo (o mais novo fica em cima)
  python adicionar.py --listar                                            mostra os destaques
  python adicionar.py --remover <número|link>                             tira um destaque
  --sem-enviar                                                            só grava o links.json, sem commit/push

YouTube (vídeo, Short, youtu.be): pega o título e a capa sozinho, e o link abre no app (duugagno.github.io/yt).
TikTok (link de vídeo): pega o título e a capa pelo oEmbed do TikTok. Outro site: passe --titulo.
Os "Últimos vídeos" do canal não precisam disto: o GitHub atualiza sozinho a cada 30 min."""
import json, os, re, subprocess, sys, urllib.parse, urllib.request

sys.stdout.reconfigure(encoding='utf-8')
AQUI = os.path.dirname(os.path.abspath(__file__))
ARQ = os.path.join(AQUI, 'links.json')
APP = 'https://duugagno.github.io/yt/'


def ler():
    if not os.path.exists(ARQ):
        return {'destaques': []}
    return json.load(open(ARQ, encoding='utf-8'))


def gravar(d):
    with open(ARQ, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write('\n')


def get_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (link-bio)'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))


def youtube(link):
    m = re.search(r'(?:youtu\.be/|[?&]v=|/shorts/|/live/|/embed/)([A-Za-z0-9_-]{11})', link)
    if not m:
        return None
    vid = m.group(1)
    short = '/shorts/' in link
    titulo = ''
    try:
        titulo = get_json('https://www.youtube.com/oembed?format=json&url=' +
                          urllib.parse.quote('https://www.youtube.com/watch?v=' + vid))['title']
    except Exception as e:
        print('aviso: o YouTube não deu o título (vídeo privado, agendado ou processando?):', e)
    return {'titulo': titulo, 'url': APP + ('?s=' if short else '?v=') + vid,
            'imagem': f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg', 'etiqueta': 'Short' if short else 'Vídeo'}


def tiktok(link):
    if 'tiktok.com' not in link:
        return None
    d = {'titulo': '', 'url': link, 'imagem': '', 'etiqueta': 'TikTok'}
    try:
        o = get_json('https://www.tiktok.com/oembed?url=' + urllib.parse.quote(link))
        d['titulo'] = (o.get('title') or '').split('#')[0].strip()
        d['imagem'] = o.get('thumbnail_url') or ''
    except Exception as e:
        print('aviso: o TikTok não deu o título:', e)
    return d


def git(*args):
    return subprocess.run(['git', '-C', AQUI] + list(args), check=True, capture_output=True, text=True).stdout


def enviar(msg):
    git('pull', '--rebase', '--autostash', '-q')   # o GitHub também faz commits (videos.json)
    git('add', 'links.json')
    if not git('status', '--porcelain', 'links.json').strip():
        print('nada mudou')
        return
    git('commit', '-q', '-m', msg)
    git('push', '-q')
    print('publicado; a página atualiza em 1 a 2 minutos: https://duugagno.github.io/getearia/')


def main():
    a = sys.argv[1:]
    sem_enviar = '--sem-enviar' in a
    a = [x for x in a if x != '--sem-enviar']

    def opt(nome):
        if nome in a:
            i = a.index(nome)
            v = a[i + 1] if i + 1 < len(a) else ''
            del a[i:i + 2]
            return v
        return None

    d = ler()
    if not a or a[0] == '--listar':
        for i, x in enumerate(d['destaques'], 1):
            print(f"{i}. [{x.get('etiqueta', '')}] {x.get('titulo', '')}  ->  {x['url']}")
        if not d['destaques']:
            print('(nenhum destaque fixado)')
        return
    if a[0] == '--remover':
        alvo = a[1] if len(a) > 1 else ''
        lista = d['destaques']
        if alvo.isdigit() and 1 <= int(alvo) <= len(lista):
            tirado = lista.pop(int(alvo) - 1)
        else:
            achou = [x for x in lista if alvo and (alvo in x['url'] or x['url'] in alvo)]
            if not achou:
                sys.exit('não achei esse destaque; veja com --listar')
            tirado = achou[0]
            lista.remove(tirado)
        gravar(d)
        print('tirado:', tirado.get('titulo') or tirado['url'])
        if not sem_enviar:
            enviar('Bio: tira ' + (tirado.get('titulo') or tirado['url'])[:60])
        return

    etiqueta, titulo = opt('--etiqueta'), opt('--titulo')
    link = a[0].strip()
    item = youtube(link) or tiktok(link) or {'titulo': '', 'url': link, 'imagem': '', 'etiqueta': 'Link'}
    if titulo:
        item['titulo'] = titulo
    if etiqueta:
        item['etiqueta'] = etiqueta
    if not item['titulo']:
        sys.exit('sem título: passe --titulo "..."')
    d['destaques'] = [x for x in d['destaques'] if x['url'] != item['url']]
    d['destaques'].insert(0, item)
    gravar(d)
    print(f"fixado no topo: [{item['etiqueta']}] {item['titulo']}")
    print('link:', item['url'])
    if len(d['destaques']) > 4:
        print(f"aviso: {len(d['destaques'])} destaques fixados; mais de 4 empurra os vídeos para baixo (tire com --remover)")
    if not sem_enviar:
        enviar('Bio: fixa ' + item['titulo'][:60])


if __name__ == '__main__':
    main()
