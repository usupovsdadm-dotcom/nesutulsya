# -*- coding: utf-8 -*-
"""Общие куски разметки: шапка, мобильное меню, подвал, нижняя панель, cookie, lightbox."""
BASE = 'https://usupovsdadm-dotcom.github.io/nesutulsya/'
OLD = 'https://xn----itbtfwbfhb5g8a.xn--p1ai'
PHONE = '+7 926 691-18-05'
TEL = 'tel:+79266911805'
VK = 'https://vk.com/nesutulsyamsk'

VK_SVG = '<svg viewBox="0 0 24 24"><path d="M12.8 17.5C6.6 17.5 3.1 13.3 3 6.3h3.1c.1 5.1 2.3 7.3 4.1 7.7V6.3h2.9v4.4c1.8-.2 3.6-2.2 4.3-4.4h2.9c-.5 2.7-2.5 4.7-3.9 5.5 1.4.7 3.7 2.4 4.5 5.7h-3.2c-.7-2.2-2.4-3.9-4.6-4.1v4.1h-.3z"/></svg>'

def nav_items(P, home):
    h = '' if home else P  # на главной якоря без префикса
    return [
        ('home', 'Главная', P if P else './'),
        ('shop', 'Услуги', P + 'shop/'),
        ('founder', 'Основатель', P + 'founder/'),
        ('team', 'Команда', h + '#team'),
        ('friends', 'Нам доверяют', P + 'friends/'),
        ('orto', 'Стельки', P + 'orto/'),
        ('store', 'Мерч', P + 'store/'),
        ('contacts', 'Контакты', h + '#contacts'),
    ]

def _links(P, home, active):
    out = []
    for key, label, href in nav_items(P, home):
        cur = ' aria-current="page"' if key == active else ''
        out.append(f'<a href="{href}"{cur}>{label}</a>')
    return ''.join(out)

def header(P, active, zapis_href, home=False):
    logo_href = '#top' if home else (P if P else './')
    return f'''<header class="hdr" id="hdr">
  <a class="hdr__logo" href="{logo_href}" aria-label="НеСутулься — на главную"><img src="{P}assets/img/logo.webp" alt="НеСутулься" width="900" height="197"></a>
  <nav class="hdr__nav" aria-label="Разделы сайта">
    {_links(P, home, active)}
  </nav>
  <div class="hdr__right">
    <span class="status" data-status><i></i><span>10:00–21:00 МСК</span></span>
    <a class="hdr__phone" href="{TEL}">{PHONE}</a>
    <a class="btn btn--sm btn--lime magnetic" href="{zapis_href}">Записаться</a>
    <button class="burger" id="burger" aria-label="Меню" aria-expanded="false" aria-controls="mnav"><span></span><span></span><span></span></button>
  </div>
</header>

<div class="mnav" id="mnav" aria-hidden="true">
  <nav aria-label="Меню">
    {_links(P, home, active)}<a href="{zapis_href}">Запись · 5&nbsp;000&nbsp;₽</a>
  </nav>
  <div class="mnav__foot"><a href="{TEL}">{PHONE}</a><span data-status class="status"><i></i><span>10:00–21:00 МСК</span></span></div>
</div>'''

def footer(P, home=False):
    h = '' if home else P
    return f'''<footer class="ftr">
  <div class="ftr__top">
    <img class="ftr__logo" src="{P}assets/img/logo.webp" alt="НеСутулься" width="900" height="197" loading="lazy">
    <nav class="ftr__nav" aria-label="Карта сайта">
      <div><b>О нас</b><a href="{P if P else './'}">Главная</a><a href="{P}founder/">Основатель</a><a href="{h}#team">Команда</a><a href="{P}friends/">Нам доверяют</a><a href="{h}#contacts">Контакты</a></div>
      <div><b>Услуги</b><a href="{P}shop/">Услуги и цены</a><a href="{P}shop/#online">Онлайн</a><a href="{P}orto/">Стельки</a><a href="{P}shop/#cert">Подарочный сертификат</a><a href="{P}store/">Мерч</a></div>
      <div><b>Пациентам</b><a href="{P}patients/">Отправить исследования</a><a href="{P}application/">Приложение</a><a href="{h}#faq">Вопросы</a><a href="https://music.yandex.ru/album/21096211/track/100491307" target="_blank" rel="noopener">Подкаст</a></div>
      <div><b>Медиа</b><a href="{VK}" target="_blank" rel="noopener">VK</a><a href="https://vkvideo.ru/@club231053786" target="_blank" rel="noopener">VK Видео</a><a href="https://rutube.ru/channel/27963576/" target="_blank" rel="noopener">Rutube</a><a href="https://max.ru/id772086427984_biz" target="_blank" rel="noopener">MAX</a></div>
    </nav>
  </div>
  <div class="ftr__bottom">
    <p>ИП Тумарец Кирилл Михайлович · ОГРНИП 319774600434803 · ИНН 772086427984</p>
    <p class="ftr__legal"><a href="{P}privacy/">Политика обработки персональных данных</a><a href="{P}cookie/">Политика cookie</a><a href="{P}ps/">Пользовательское соглашение</a><a href="{P}oferta/">Публичная оферта</a></p>
  </div>
</footer>

<nav class="mbar" aria-label="Быстрые действия">
  <a href="{TEL}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1z"/></svg>Позвонить</a>
  <a href="{{ZAPIS}}" class="mbar__main">Записаться</a>
  <a href="{VK}" target="_blank" rel="noopener">{VK_SVG.replace('<svg ', '<svg aria-hidden="true" ')}Написать</a>
</nav>

<div class="cookie" id="cookie" role="dialog" aria-label="Использование cookies" hidden>
  <b>Использование cookies</b>
  <p>Используя наш сайт, вы даёте согласие на обработку <a href="{P}cookie/">файлов cookie</a> и <a href="{P}privacy/">пользовательских данных</a>. Если вы не хотите, чтобы ваши данные обрабатывались, пожалуйста, покиньте сайт.</p>
  <div class="cookie__btns"><button class="btn btn--ghost" type="button" data-cookie="no">Отказаться</button><button class="btn btn--lime" type="button" data-cookie="yes"><span>Согласиться</span></button></div>
</div>

<div class="lightbox" id="lightbox" hidden><button class="lightbox__x" aria-label="Закрыть">×</button><img alt=""></div>'''

def fx(P):
    """Курсор-баллончик и прогресс-бар (как на главной)."""
    return '''<canvas id="sprayCursor" class="spray-canvas" aria-hidden="true"></canvas>
<div class="can-cursor" id="canCursor" aria-hidden="true"><svg viewBox="0 0 40 64"><rect x="9" y="16" width="22" height="44" rx="5" fill="#bdf06b" stroke="#0d0d0d" stroke-width="2"/><rect x="13" y="8" width="14" height="10" rx="2" fill="#f2f2ec" stroke="#0d0d0d" stroke-width="2"/><rect x="17" y="2" width="6" height="7" rx="1" fill="#ff2d8a" stroke="#0d0d0d" stroke-width="2"/><path d="M9 34h22" stroke="#0d0d0d" stroke-width="2"/><text x="20" y="50" font-size="9" text-anchor="middle" font-family="Unbounded,sans-serif" font-weight="800" fill="#0d0d0d">НС</text></svg></div>
<div class="progress" aria-hidden="true"><i id="progressBar"></i></div>'''

def head(P, slug, title, desc, og_title=None):
    url = BASE + (slug + '/' if slug else '')
    og_title = og_title or title
    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0d0d0d">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="ru_RU">
<meta property="og:site_name" content="НеСутулься">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}assets/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{P}assets/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="{P}assets/favicon-32.png">
<link rel="apple-touch-icon" href="{P}assets/apple-touch-icon.png">
<link rel="preload" href="{P}assets/fonts/wetpaint.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{P}assets/fonts/unbounded.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{P}assets/fonts/manrope.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{P}css/style.css?v=6">
</head>'''

SCRIB = '<svg class="scrib" viewBox="0 0 300 24" preserveAspectRatio="none" aria-hidden="true"><path d="M3 15 C 40 4, 80 22, 120 12 S 200 4, 240 14 S 285 18, 297 9" pathLength="1"/></svg>'

def sec_head(title, sub=None, glitch=False, tag='h2'):
    g = ' glitch' if glitch else ''
    s = f'<p class="sec-sub reveal">{sub}</p>' if sub else ''
    return f'<div class="sec-head"><{tag} class="spray-title{g}" data-text="{title}">{title}</{tag}>{SCRIB}{s}</div>'

import random
def tear(fill, bottom=False, seed=1):
    r = random.Random(seed); pts = []; x = 0
    while x < 1440:
        pts.append(f'L{x} {r.uniform(8,34):.1f}'); x += r.randint(10, 38)
    pts.append(f'L1440 {r.uniform(8,34):.1f}')
    d = 'M0 60 ' + ' '.join(pts) + ' L1440 60 Z'
    if bottom:
        return f'<svg class="tear tear--b" viewBox="0 0 1440 60" preserveAspectRatio="none" aria-hidden="true"><path d="{d}" fill="{fill}"/></svg>'
    return f'<svg class="tear" viewBox="0 0 1440 60" preserveAspectRatio="none" aria-hidden="true" style="transform:scaleY(-1)"><path d="{d}" fill="{fill}"/></svg>'

CTAPE = 'ОСТОРОЖНО: ОСАНКА ✦ НЕ СУТУЛЬСЯ ✦ НАЙДЁМ ПРИЧИНУ ✦ ИСПРАВИМ ✦ ' * 3
def tape_band(text=CTAPE, cls='ctape--y ctape--rev'):
    return f'<div class="tape-band"><div class="ctape {cls}" aria-hidden="true"><div class="ctape__track"><span>{text}</span><span>{text}</span></div></div></div>'
