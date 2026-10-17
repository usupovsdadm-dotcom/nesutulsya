# -*- coding: utf-8 -*-
"""Сборка внутренних страниц «НеСутулься».
Запуск из корня репозитория:  python3 tools/build.py
Генерирует <slug>/index.html для каждой страницы и обновляет шапку/подвал в index.html
(между маркерами <!-- @hdr --> … <!-- /@hdr --> и <!-- @ftr --> … <!-- /@ftr -->), а также sitemap.xml.
Тексты, цены и фото — с текущего сайта не-сутулься.рф."""
import os, re, json, html as H
from partials import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = '../'

def page(slug, active, title, desc, body, zapis_href=None, og_title=None):
    zapis_href = zapis_href or (P + '#zapis')
    ftr = footer(P).replace('{ZAPIS}', zapis_href)
    doc = f'''{head(P, slug, title, desc, og_title)}
<body>
<a class="skip" href="#main">К содержимому</a>
{fx(P)}

<!-- @hdr -->
{header(P, active, zapis_href)}
<!-- /@hdr -->

<main id="main">
{body}
</main>

<!-- @ftr -->
{ftr}
<!-- /@ftr -->

<script src="{P}js/main.js?v=5" defer></script>
</body>
</html>
'''
    d = os.path.join(ROOT, slug); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf8').write(doc)
    print('built', slug + '/index.html')

def phero(title, sub=None, crumbs=None, label=None, art=None, cta=None, glitch=False, long=False):
    cr = f'<nav class="crumbs reveal" aria-label="Хлебные крошки"><a href="{P}">Главная</a><span aria-hidden="true">/</span><span aria-current="page">{crumbs}</span></nav>' if crumbs else ''
    lb = f'<p class="label-tape reveal">{label}</p>' if label else ''
    sb = f'<p class="phero__sub reveal">{sub}</p>' if sub else ''
    ct = f'<div class="phero__cta reveal">{cta}</div>' if cta else ''
    g = (' glitch' if glitch else '') + (' spray-title--long' if long else '')
    copy = f'<div class="phero__copy">{cr}{lb}<h1 class="spray-title{g}" data-text="{title}">{title}</h1>{SCRIB}{sb}{ct}</div>'
    if art:
        inner = f'<div class="phero__inner phero__inner--split">{copy}<div class="phero__art reveal">{art}</div></div>'
    else:
        inner = f'<div class="phero__inner">{copy}</div>'
    return f'''<section class="phero sec-head" id="top" style="text-align:left;max-width:none;margin:0">
  <div class="phero__wall" data-speed="0.2" aria-hidden="true"></div>
  <div class="splat splat--1" data-speed="-0.12" aria-hidden="true"></div>
  {inner}
</section>'''

AGREE = f'<label class="agree"><input type="checkbox" name="agree" required><span>Согласен на обработку персональных данных по <a href="{P}privacy/">Политике</a> и с условиями <a href="{P}oferta/">Оферты</a></span></label>'
OSMOTR = '<label class="agree" data-osmotr-box hidden><input type="checkbox" name="osmotr"><span>Подтверждаю, что мной уже пройден осмотр *</span></label>'

def lead_form(title, btn, select_html='', osmotr=False, alt=True):
    return f'''<form class="form lead reveal" id="leadForm" novalidate>
      <span class="tape tape--tl" aria-hidden="true"></span><span class="tape tape--br" aria-hidden="true"></span>
      <h3 class="form__t">{title}</h3>
      {select_html}
      <label class="field"><span>Имя *</span><input name="name" type="text" autocomplete="name" required maxlength="60" placeholder="Как к тебе обращаться"></label>
      <label class="field"><span>Телефон *</span><input name="phone" type="tel" autocomplete="tel" inputmode="tel" required placeholder="+7 (___) ___-__-__"></label>
      {OSMOTR if osmotr else ''}
      {AGREE}
      <input type="text" name="website" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
      <button class="btn btn--black btn--xl btn--block magnetic" type="submit"><span>{btn}</span></button>
      <p class="form__err" role="alert" hidden></p>
      <p class="form__alt">Или сразу: <a href="{TEL}">{PHONE}</a> · <a href="{VK}" target="_blank" rel="noopener">VK</a></p>
      <div class="form__ok" hidden>
        <div class="form__okmark" aria-hidden="true">✓</div>
        <h3>Заявка у нас!</h3>
        <p>Перезвоним в рабочее время — 10:00–21:00 по Москве. Не хочешь ждать — набери сам:</p>
        <a class="btn btn--black btn--block" href="{TEL}">{PHONE}</a>
      </div>
    </form>'''

def rub(n):
    return f'{n:,}'.replace(',', '&nbsp;') + '&nbsp;₽'

# ---------------------------------------------------------------- УСЛУГИ (/shop)
CONS_MORE = ('Комплексы упражнений разрабатываются индивидуально под каждого пациента для самостоятельной работы в домашних условиях.',
             '*С собой лучше взять все имеющиеся заключения, исследования (МРТ). Если этого нет, то специалист на осмотре скажет, какие именно исследования понадобятся. Форма одежды свободная. Для комфорта можно взять шорты и футболку по желанию.')
CONS_LEAD = 'На осмотре специалист подробно разбирает вашу проблему, собирает полный анамнез, оценивает картину в целом, выстраивая план работы в заведении и так же в домашних условиях. После осмотра (если состояние позволяет) уже дается начальный этап индивидуальной программы на дом.'
SESS_LEAD = 'Сессия (60 минут) включает в себя различные техники и инструменты, подобранные после осмотра с учетом этапа восстановления и реакции организма.'
SESS_MORE = ('Сессия проводится индивидуально, совмещает в себе проработку на кушетке и работу в зале. После сессии присылается обязательно отчет по состоянию для корректировки плана работы и домашнего комплекса. Комплексы упражнений разрабатываются индивидуально под каждого для самостоятельной работы в домашних условиях с поддержкой специалиста в чате. Обратная связь обязательна для эффективной работы.',
             '*Форма одежды спортивная (чтобы было удобно работать с вашим телом на кушетке и комфортно заниматься в зале).')
BLOCK_MORE = ('Ежедневная отчетность и обратная связь. Комплексы упражнений разрабатываются индивидуально под каждого для самостоятельной работы в домашних условиях с поддержкой специалиста в чате. Администраторы выстроят удобный и гибкий график вместе с вами.',
              '*Форма одежды спортивная.')
def block_lead(n, w):
    return f'Блок из {w} сессий. Посещение по назначенному графику от специалиста в зависимости от вашей проблемы и реакции организма.'

# (id, заголовок группы, [услуги]); услуга: dict(t, price, img, ava, where, lead, more, osm)
SHOP = [
 ('cons', 'Консультации', [
   dict(t='Консультация специалиста Тумарца К.М.', price=5000, ava='team/tumarec.webp', where='В заведении / Онлайн', lead=CONS_LEAD, more=CONS_MORE),
   dict(t='Консультация специалиста Суслова А.Д.', price=4000, ava='team/suslov.webp', where='В заведении / Онлайн', lead=CONS_LEAD, more=CONS_MORE),
 ]),
 ('sess', 'Сессии', [
   dict(t='Разовая сессия', price=8000, img='shop/session.webp', lead=SESS_LEAD, more=SESS_MORE, osm=True),
   dict(t='Блок 6 сессий', price=45900, img='shop/h6.webp', lead='Блок из шести сессий. Посещение по назначенному графику от специалиста в зависимости от вашей проблемы и реакции организма.', more=BLOCK_MORE, osm=True),
   dict(t='Блок 12 сессий', price=88800, img='shop/h12.webp', lead='Блок из двенадцати сессий. Посещение по назначенному графику от специалиста в зависимости от вашей проблемы и реакции организма.', more=BLOCK_MORE, osm=True),
   dict(t='Блок 24 сессии', price=168000, img='shop/h24.webp', lead='Блок из двадцати четырех сессий. Посещение по назначенному графику от специалиста в зависимости от вашей проблемы и реакции организма.', more=BLOCK_MORE, osm=True),
 ]),
 ('vyezd', 'Выезд', [
   dict(t='Выезд. Разовая сессия', price=8000, img='shop/session.webp', lead=SESS_LEAD, more=SESS_MORE, osm=True),
   dict(t='Выезд. Блок 6 сессий', price=45900, img='shop/h6.webp', lead='Блок из шести сессий. Посещение по назначенному графику от специалиста в зависимости от вашей проблемы и реакции организма.', more=BLOCK_MORE, osm=True),
   dict(t='Выезд. Блок 12 сессий', price=88800, img='shop/h12.webp', lead='Блок из двенадцати сессий. Посещение по назначенному графику от специалиста в зависимости от вашей проблемы и реакции организма.', more=BLOCK_MORE, osm=True),
 ]),
 ('zal', 'Зал', [
   dict(t='Разовое индивидуальное занятие с инструктором', price=5000, lead='Индивидуальное занятие с инструктором.', osm=True),
   dict(t='Блок 10 индивидуальных занятий с инструктором', price=40000, osm=True),
 ]),
 ('stelki', 'Стельки', [
   dict(t='Индивидуальные стельки', price=9500, img='orto/insole.webp', lead='В стоимость входит два этапа посещения: 1.&nbsp;Изготовление стелек. 2.&nbsp;Коррекция через назначенное время.', link=('Подробнее о стельках', 'orto/')),
   dict(t='Коррекция стелек', price=3500),
 ]),
 ('online', 'Онлайн', [
   dict(t='Онлайн. Разовая сессия', price=5000, osm=True),
   dict(t='Онлайн. Блок 6 сессий', price=27000, osm=True),
   dict(t='Онлайн. Блок 12 сессий', price=48000, osm=True),
 ]),
 ('fitness', 'Фитнес', [
   dict(t='Фитнес онлайн. Разовое занятие', price=5000, osm=True),
   dict(t='Фитнес онлайн. Блок 10 занятий', price=40000, osm=True),
 ]),
 ('massage', 'Массаж', [
   dict(t='Массаж 30 минут', price=2500, img='shop/massage30.webp'),
   dict(t='Массаж 60 минут', price=4500),
   dict(t='Массаж 90 минут', price=6500),
 ]),
]

def svc_card(s, i):
    img = ''
    if s.get('ava'):
        img = f'<div class="svc__img svc__img--ava"><img src="{P}assets/img/{s["ava"]}" alt="{s["t"]}" width="420" height="420" loading="lazy" decoding="async"></div>'
    elif s.get('img'):
        img = f'<div class="svc__img"><img src="{P}assets/img/{s["img"]}" alt="{s["t"]}" loading="lazy" decoding="async"></div>'
    where = f'<span class="svc__where">{s["where"]}</span>' if s.get('where') else ''
    lead = f'<p class="svc__p">{s["lead"]}</p>' if s.get('lead') else ''
    more = ''
    if s.get('more'):
        more = '<details class="pcard__more"><summary>Подробнее</summary>' + ''.join(f'<p>{m}</p>' for m in s['more']) + '</details>'
    badge = '<span class="svc__badge">только после осмотра</span>' if s.get('osm') else ''
    link = f'<p class="svc__note"><a href="{P}{s["link"][1]}">{s["link"][0]} →</a></p>' if s.get('link') else ''
    val = f'{s["t"]} — {s["price"]:,} ₽'.replace(',', ' ')
    return f'''<article class="svc tilt reveal" style="--d:{(i%3)*70}ms">
  {img}<h3 class="svc__t">{s["t"]}</h3>{where}{badge}{lead}{more}{link}
  <div class="svc__foot"><span class="svc__price">{rub(s["price"])}</span><a class="btn btn--black magnetic" href="#zapis" data-service="{H.escape(val)}"><span>Записаться</span></a></div>
</article>'''

def build_shop():
    chips = ''.join(f'<a href="#{gid}">{t if gid!="cons" else "Консультация"}</a>' for gid, t, _ in SHOP) + '<a href="#cert">Сертификат</a>'
    groups = ''
    for gid, t, items in SHOP:
        groups += f'<section class="svc-group" id="{gid}"><h2 class="svc-group__t">{t}</h2><div class="svc-grid">' + ''.join(svc_card(s, i) for i, s in enumerate(items)) + '</div></section>\n'
    opts = '<option value="">Первичный приём / консультация — подберём на звонке</option>'
    for gid, t, items in SHOP:
        opts += f'<optgroup label="{t}">'
        for s in items:
            val = f'{s["t"]} — {s["price"]:,} ₽'.replace(',', ' ')
            osm = ' data-osmotr="1"' if s.get('osm') else ''
            opts += f'<option value="{H.escape(val)}"{osm}>{H.escape(val)}</option>'
        opts += '</optgroup>'
    opts += '<option value="Подарочный сертификат">Подарочный сертификат</option>'
    select = f'<label class="field"><span>Услуга</span><select name="service">{opts}</select></label>'
    body = phero('УСЛУГИ', 'Полный спектр услуг для восстановления подвижности вашего организма.', crumbs='Услуги', label='Услуги и цены · Москва и онлайн', art=f'<img src="{P}assets/img/shop/osmotr.webp" alt="Реабилитация: осмотр" width="600" height="600" style="max-width:420px;margin:0 auto;filter:drop-shadow(0 30px 40px rgba(0,0,0,.7));rotate:4deg">',
                 cta=f'<a class="btn btn--lime btn--xl magnetic" href="#zapis"><span>Записаться</span></a><a class="btn btn--ghost btn--xl magnetic" href="{TEL}"><span>Позвонить</span></a>')
    body += f'''
<section class="sec sec--dark" style="padding-top:50px">
  <nav class="chips" aria-label="Разделы услуг">{chips}</nav>
  {groups}
  <section class="cert reveal" id="cert">
    <div class="cert__img"><img src="{P}assets/img/shop/certificate.webp" alt="Подарочный сертификат «НеСутулься»" width="540" height="960" loading="lazy" decoding="async"></div>
    <div>
      <h2>ПОДАРОЧНЫЙ СЕРТИФИКАТ</h2>
      <p><b>Уверены, вы знаете, кому это точно надо!</b></p>
      <p>Лучший подарок — сертификат на конкретную услугу или пополни карточку на любую сумму.</p>
      <a class="btn btn--lime btn--xl magnetic" href="#zapis" data-service="Подарочный сертификат"><span>Заказать сертификат</span></a>
    </div>
  </section>
  {tear('#bdf06b', bottom=True, seed=21)}
</section>

<section class="zapis zapis--page" id="zapis">
  <div class="zapis__paint" aria-hidden="true"></div>
  <div class="zapis__inner">
    <div class="zapis__info">
      <h2 class="spray-title spray-title--dark" data-text="ЗАПИСЬ">ЗАПИСЬ</h2>
      <ul class="checks reveal">
        <li>Выбери услугу — администратор перезвонит и подберёт время</li>
        <li>Сессии, блоки, зал, онлайн и фитнес — только после первичного осмотра</li>
        <li>Оплата блока — по договору, можно разделить на несколько платежей</li>
      </ul>
      <div class="zapis__notes reveal">
        <p><b>Первичный приём — {rub(5000)}</b> (ведущий специалист) или <b>{rub(4000)}</b> (специалист).</p>
        <p>Полный прейскурант — в <a href="{P}oferta/#price">публичной оферте</a>.</p>
      </div>
    </div>
    {lead_form('Записаться', 'Отправить заявку', select, osmotr=True)}
  </div>
</section>'''
    page('shop', 'shop', 'Услуги и цены — реабилитация «НеСутулься», Москва',
         'Цены на услуги «НеСутулься»: консультация от 4 000 ₽, сессии и блоки 6/12/24, выезд, зал, онлайн, фитнес, массаж, индивидуальные стельки, подарочный сертификат.',
         body, zapis_href='#zapis')

# ---------------------------------------------------------------- СТЕЛЬКИ (/orto)
def build_orto():
    bens = ['Уменьшают нагрузку', 'Повышают устойчивость', 'Уменьшают усталость ног', 'Эстетический вид ног', 'Улучшают кровообращение', 'Распределяют нагрузку']
    rots = ['-1.5deg', '1deg', '-0.5deg', '1.5deg', '-1deg', '0.8deg']
    bh = '<div class="bens">' + ''.join(f'<div class="ben reveal" style="--r:{r};--d:{i*60}ms">{b}</div>' for i, (b, r) in enumerate(zip(bens, rots))) + '</div>'
    art = f'<img src="{P}assets/img/orto/insole.webp" alt="Индивидуальная стелька RootFoot" width="1000" height="625" style="filter:drop-shadow(0 30px 40px rgba(0,0,0,.7));rotate:-6deg">'
    body = phero('СТЕЛЬКИ', None, crumbs='Стельки', label='Индивидуальные стельки RootFoot', art=art,
                 cta=f'<a class="btn btn--lime btn--xl magnetic" href="#zapis"><span>Записаться на изготовление</span></a><a class="btn btn--ghost btn--xl magnetic" href="{P}shop/#stelki"><span>Цены</span></a>')
    body = body.replace('</h1>' + SCRIB, '</h1>' + SCRIB + '<p class="phero__sub reveal" style="font:800 clamp(20px,2.4vw,32px)/1.2 Unbounded,sans-serif;text-transform:uppercase;color:var(--ink)">Индивидуальные стельки</p>' + bh, 1)
    docs = [('doc1', 'Документ соответствия 1'), ('doc2', 'Документ соответствия 2'), ('doc3', 'Документ соответствия 3'), ('doc4', 'Сертификат соответствия')]
    rr = ['-4deg', '3deg', '-2deg', '4deg']
    dh = ''.join(f'<button class="polaroid" style="--r:{r}" data-full="{P}assets/img/orto/{d}.webp" aria-label="Открыть: {t}"><img src="{P}assets/img/orto/{d}-t.webp" alt="{t}" width="360" height="500" loading="lazy" decoding="async"><span>{t}</span></button>' for (d, t), r in zip(docs, rr))
    body += f'''
<section class="sec sec--brick" id="memoryform">
  {sec_head('MEMORYFORM', 'Технология, материал и принцип работы стелек RootFoot.')}
  <div class="mf-banner reveal"><img src="{P}assets/img/orto/memoryform.webp" alt="MemoryForm" width="1080" height="327" loading="lazy" decoding="async"></div>
  <div class="cards3">
    <article class="icard tilt reveal" style="--d:0ms"><h3>Технология</h3><p>Технология MemoryForm мягко и постоянно адаптируются под изменения ваших ног. Стелька постоянно меняется, поддерживая или расслабляя только те участки стопы, где это действительно нужно.</p></article>
    <article class="icard icard--accent tilt reveal" style="--d:80ms"><h3>Материал</h3><p>Термочувствительный материал, который мы используем, гибкий и прочный: он выдерживает целый год активных занятий спортом и ежедневного использования.</p></article>
    <article class="icard tilt reveal" style="--d:160ms"><h3>Принцип работы</h3><p>Стельки RootFoot устраняют ударные нагрузки и снимают перенапряжение всего двигательного аппарата. Эти характеристики делают занятия спортом безопасными для здоровья.</p><p>Изначально RootFoot создавались для большого спорта и высоких нагрузок: бега, лыж и сноуборда, многих других видов спорта.</p></article>
  </div>
</section>

<section class="sec sec--dark" id="price">
  {sec_head('ЦЕНЫ')}
  <div class="prices">
    <div class="prow reveal"><div><b>Индивидуальные стельки</b><small>В стоимость входит два этапа посещения: 1. Изготовление стелек. 2. Коррекция через назначенное время.</small></div><span>{rub(9500)}</span></div>
    <div class="prow reveal"><div><b>Коррекция стелек</b></div><span>{rub(3500)}</span></div>
  </div>
  {tear('#bdf06b', bottom=True, seed=31)}
</section>

<section class="zapis" id="zapis">
  <div class="zapis__paint" aria-hidden="true"></div>
  <div class="zapis__inner">
    <div class="zapis__info">
      <h2 class="spray-title spray-title--dark spray-title--long" data-text="ЗАПИШИТЕСЬ НА ИЗГОТОВЛЕНИЕ">ЗАПИШИТЕСЬ НА ИЗГОТОВЛЕНИЕ</h2>
      <div class="pricetag reveal"><span>прямо сейчас</span></div>
      <ul class="checks reveal"><li>Изготовление стелек</li><li>Коррекция через назначенное время</li></ul>
    </div>
    {lead_form('Записаться на изготовление', 'Отправить заявку', '<input type="hidden" name="service" value="Индивидуальные стельки — 9 500 ₽">')}
  </div>
</section>

<section class="sec sec--concrete" id="docs">
  {tear('#bdf06b', seed=32)}
  {sec_head('ДОКУМЕНТЫ СООТВЕТСТВИЯ', 'Нажми на документ, чтобы открыть его крупно.')}
  <div class="docs docs--big" aria-label="Документы соответствия">{dh}</div>
</section>'''
    page('orto', 'orto', 'Индивидуальные стельки RootFoot MemoryForm — «НеСутулься», Москва',
         'Индивидуальные стельки RootFoot по технологии MemoryForm: уменьшают нагрузку, повышают устойчивость и распределяют нагрузку. Изготовление и коррекция — 9 500 ₽.',
         body, zapis_href='#zapis')

# ---------------------------------------------------------------- ОСНОВАТЕЛЬ (/founder)
def build_founder():
    art = f'<figure class="photo-frame" style="margin:0"><img src="{P}assets/img/founder-photo.webp" alt="Кирилл Михайлович Тумарец" width="805" height="1100" fetchpriority="high"></figure>'
    body = phero('КИРИЛЛ ТУМАРЕЦ', None, crumbs='Основатель', label='Основатель · ведущий реабилитолог', art=art, glitch=True, long=True)
    body = body.replace('</h1>' + SCRIB, '</h1>' + SCRIB + '<p class="fhero__name reveal">Кирилл Михайлович</p><blockquote class="fquote reveal">Если вы находитесь на данном сайте, вы однозначно в поиске хорошего специалиста, который поможет разобраться и исправить возникшие проблемы с опорно-двигательным аппаратом. Совместно с моей командой квалифицированных и опытных специалистов, проверенных временем, мы работаем для решения ваших проблем и улучшения качества жизни.</blockquote>', 1)
    docs = [('dip_mag', 'Диплом магистра МГАФК', '-5deg'), ('dip_bak', 'Диплом бакалавра МГАФК', '3deg'), ('dip_med', 'Диплом медицинского брата', '-2deg'), ('dip_rent', 'Сертификат: рентгенология', '4deg'), ('dip_pk', 'Повышение квалификации: рентгенология', '-3deg')]
    dh = ''.join(f'<button class="polaroid" style="--r:{r}" data-full="{P}assets/img/docs/{d}.webp" aria-label="Открыть: {t}"><img src="{P}assets/img/docs/{d}-t.webp" alt="{t}" width="420" height="310" loading="lazy" decoding="async"><span>{t}</span></button>' for d, t, r in docs)
    body += f'''
<section class="sec sec--concrete" id="about">
  {sec_head('ДАВАЙТЕ ЗНАКОМИТЬСЯ БЛИЖЕ')}
  <p class="lead-text reveal" style="text-align:center">Моя деятельность началась в фитнес-индустрии, где я начал работать персональным тренером в залах и вести клиентов онлайн. Это было и моё личное увлечение, которым я занимался в свободное время.</p>
  <div class="tl" style="margin-top:46px">
    <article class="icard tilt reveal" style="--r:-1deg;--d:0ms"><h3>Работа в реанимации</h3><p>Бесценный опыт для специалиста, чья деятельность связана со здоровьем и функциональностью человека. Чего только не увидишь и через какие различные ситуации не пройдёшь, каждый день борьба за жизнь и нормализацию состояния здесь и сейчас.</p></article>
    <article class="icard icard--accent tilt reveal" style="--r:1deg;--d:80ms"><h3>Медицинское обеспечение МВД</h3><p>Пришло время развиваться далее и хотелось посмотреть и изучить медицину с другой стороны. Нужен был опыт и понимание с полным погружением в лучевую диагностику.</p></article>
    <article class="icard tilt reveal" style="--r:-.6deg;--d:160ms"><h3>Реабилитация</h3><p>Получив разносторонний опыт и хорошую практику, начал работать непосредственно по второму профильному образованию — реабилитолог, параллельно всё время повышая квалификацию, дополняя знания различными выездами и государственными курсами.</p></article>
  </div>
</section>

<section class="sec sec--brick" id="center">
  <div class="fsplit">
    <div class="reveal">
      <h2>Реабилитационный центр «неСутулься»</h2>
      <p>В 2018 году, объединив свой опыт в медицинской сфере, подходы в работе реабилитационных центров, нюансы по реабилитации, протоколы восстановления различных клиник и некоторых стран, я сформировал своё видение и концепцию работы заведения.</p>
      <p>Везде мне не хватало индивидуальности, погружения в проблему полноценно и, самое важное, комплексно, чтобы это шло одним блоком. Поскольку я вырос в самой обычной семье, как и многие, немаловажным фактором был финансовый вопрос. Нужно было просчитать и сформировать цену, чтобы было по минимуму дополнительных продаж (только в случае необходимого продления посещения в особых случаях послеоперационного периода), в стоимость чтобы входила действительно работа со всем опорно-двигательным аппаратом.</p>
      <p>Чтобы специалист качественно, обширно и с полным погружением выполнял работу ОТ и ДО, не задумываясь, что это уже другой неоплаченный блок, который можно продать, лишая пациента грамотного и своевременного восстановления. Хотелось дать пациентам действительно высокий уровень реабилитации и показать, что комплексный подход и профессиональный уровень есть и в России.</p>
    </div>
    <div class="phone-shot reveal"><img src="{P}assets/img/founder/reviews-phone.webp" alt="Отзывы пациентов о мастерской «НеСутулься»" width="615" height="1093" loading="lazy" decoding="async"></div>
  </div>
</section>

<section class="sec sec--dark" id="docs">
  {sec_head('ОБРАЗОВАНИЕ', 'Дипломы и сертификаты — нажми, чтобы открыть.')}
  <div class="docs" aria-label="Документы об образовании" style="margin-top:0">{dh}</div>
</section>

<section class="sec sec--concrete" id="podcast">
  {tear('#0f0f0f', seed=41)}
  <div class="slogan">
    <h2 class="slogan__t reveal">Не можешь изменить — создай своё и&nbsp;возглавь!</h2>
    <a class="pod reveal" href="https://music.yandex.ru/album/21096211/track/100491307" target="_blank" rel="noopener">
      <img src="{P}assets/img/founder/podcast.webp" alt="Подкаст «Что нужно человеку для счастья?»" width="600" height="1098" loading="lazy" decoding="async">
      <div><b>Слушайте подкаст «Что нужно человеку для счастья?»</b><span>по ссылке на Яндекс Музыке ▶</span></div>
    </a>
    <h3 class="h3-tag reveal" style="margin-top:60px">Подписывайтесь на наши медиа</h3>
    <div class="socials socials--big reveal">
      <a href="https://rutube.ru/channel/27963576/" target="_blank" rel="noopener" aria-label="Rutube"><b>R</b></a>
      <a href="https://vkvideo.ru/@club231053786" target="_blank" rel="noopener" aria-label="VK Видео"><svg viewBox="0 0 24 24"><path d="M8 5.5v13l11-6.5z"/></svg></a>
      <a href="{VK}" target="_blank" rel="noopener" aria-label="VK">{VK_SVG}</a>
      <a href="https://max.ru/id772086427984_biz" target="_blank" rel="noopener" aria-label="MAX"><b>MAX</b></a>
    </div>
  </div>
  <div class="more-link"><a class="btn btn--lime btn--xl magnetic" href="{P}#zapis"><span>Записаться на приём — {rub(5000)}</span></a></div>
</section>'''
    page('founder', 'founder', 'Кирилл Тумарец — основатель «НеСутулься», ведущий реабилитолог',
         'Кирилл Михайлович Тумарец — основатель реабилитационного центра «НеСутулься»: путь от фитнеса и реанимации до своей мастерской, образование, подкаст.',
         body)
# ---------------------------------------------------------------- НАМ ДОВЕРЯЮТ (/friends)
def build_friends():
    idx = open(os.path.join(ROOT, 'index.html'), encoding='utf8').read()
    wall = re.search(r'<div class="wall" id="wall">(.*?)</div>\s*<p class="wall__hint"', idx, re.S).group(1)
    wall = wall.replace('src="assets/', f'src="{P}assets/').replace('loading="lazy" ', '')
    body = phero('НАМ ДОВЕРЯЮТ', 'Спортсмены, артисты и друзья мастерской — на нашей стене.', crumbs='Нам доверяют', label='14 друзей мастерской')
    body += f'''
<section class="sec sec--brick friends" style="padding-top:70px">
  <div class="wall wall--grid">{wall}</div>
  <div class="more-link"><a class="btn btn--lime btn--xl magnetic" href="{P}#zapis"><span>Хочу так же — записаться</span></a></div>
</section>'''
    page('friends', 'friends', 'Нам доверяют — спортсмены и друзья мастерской «НеСутулься»',
         'Сёрферы, сноубордисты, актёры и предприниматели, которые восстанавливаются в «НеСутулься»: Феликиди, Белякова, Ленчевский, Сапрыкин и другие.',
         body)

# ---------------------------------------------------------------- ПАЦИЕНТАМ (/patients)
def shot(name, alt, w, h):
    return f'<figure class="shot" style="width:min({w}px,100%)"><img src="{P}assets/img/patients/{name}.webp" alt="{alt}" width="{w}" height="{h}" loading="lazy" decoding="async"></figure>'

def build_patients():
    art = f'<img src="{P}assets/img/patients/icon.webp" alt="" width="196" height="196" style="width:180px;margin:0 auto;border-radius:30px;box-shadow:0 0 60px rgba(255,225,77,.3)">'
    body = phero('РЕЗУЛЬТАТЫ ИССЛЕДОВАНИЙ', 'Как отправить результаты исследования (КТ, МРТ, рентген) врачу.', crumbs='Результаты исследований', label='Отправить результаты исследования', art=art, long=True)
    body += f'''
<section class="sec sec--concrete" id="why">
  <div class="wrap wrap--narrow">
    {sec_head('КАК ОТПРАВИТЬ?', 'Как отправить результаты исследования врачу?')}
    <div class="hstep reveal">
      <p>Современное развитие коммуникационных и цифровых технологий даёт широкие возможности для обмена информацией.</p>
      <p>Результаты мультиспиральной компьютерной томографии (МСКТ, КТ) и магнитно-резонансной томографии (МРТ), цифровой рентгенографии имеют важное значение для диагностики.</p>
      <p>Необходимо отметить, что данные исследования не всегда являются исчерпывающими для установления правильного диагноза. Неверная трактовка без оценки клинической картины, осмотра пациента и истории заболевания часто приводит к ложным заключениям.</p>
      <p>Вместе с тем предварительная оценка результатов данных исследований позволяет больше внимания уделить клинической картине и свести к минимуму технические сложности. Например, чтение результатов исследований, записанных на диск, требует от 5 до 30 минут. Возможны ошибки при записи или повреждение диска, что в дальнейшем может потребовать повторного визита.</p>
    </div>
  </div>
</section>

<section class="sec sec--dark" id="steps">
  <div class="howto">
    <article class="hstep reveal"><span class="hstep__n">Шаг 0 · подготовка</span><h3>Скопируйте данные с диска</h3>
      <p>Для отправки данных исследований необходима вся информация, содержащаяся на диске. Наиболее важны <b>файл DICOMDIR</b> и <b>папка DICOM</b>.</p>
      <p>Для открытия диска в системе Windows необходимо нажать правую кнопку мыши на иконке дисковода и выбрать «Открыть» («Автозапуск» выбирать НЕ НАДО). Затем скопировать файл DICOMDIR и папку DICOM на компьютер.</p>
      <p>Чтобы отправить информацию, можно использовать несколько способов:</p>
    </article>
    <article class="hstep reveal" id="v1"><span class="hstep__n">Вариант 1</span><h3>Архив и письмо</h3>
      <p>Папку DICOM сжать (добавить в архив ZIP, RAR) и прикрепить к отправляемому письму.</p>
    </article>
    <article class="hstep reveal" id="v2"><span class="hstep__n">Вариант 2</span><h3>Яндекс Диск в браузере</h3>
      <p>Создать учётную запись на Яндекс Диске и перетянуть папку с файлами прямо в окно браузера (Google Chrome, Safari, Internet Explorer, Opera, Firefox).</p>
      <p>Затем вы можете отправить ссылку на результаты исследований врачу:</p>
      {shot('disk-folder', 'Папка с результатами исследований на Яндекс Диске', 1000, 567)}
      <p>Выберите нужную папку одним щелчком мыши. Появится окно с кнопкой «Поделиться»:</p>
      {shot('share-btn', 'Кнопка «Поделиться»', 288, 126)}<br>
      {shot('share-link', 'Окно со ссылкой на папку', 458, 850)}
      <p>Скопировать ссылку на папку и отправить её по электронной почте:</p>
      <p><a class="mail" href="mailto:footsurg@mail.ru">footsurg@mail.ru</a></p>
    </article>
    <article class="hstep reveal" id="v3"><span class="hstep__n">Вариант 3</span><h3>Облачные сервисы с программой</h3>
      <p>Альтернативным вариантом является использование облачных сервисов для хранения и передачи данных (Яндекс Диск, Dropbox и других). Это удобный и простой метод.</p>
      <p>Для отправки результатов исследований необходимо скачать программу, которая создаст папку на компьютере для синхронизации с облачным хранилищем данных. На примере сервиса Яндекс:</p>
      <p>Задать в любом поисковике или верхней строчке браузера поисковое слово «яндекс диск».</p>
      {shot('search', 'Поиск «яндекс диск»', 1000, 233)}
      <p>Зарегистрироваться на сервисе и скачать программу-установщик:</p>
      {shot('install', 'Страница загрузки Яндекс Диска', 838, 864)}
      <p>Загрузить и установить программу:</p>
      {shot('install-btn', 'Кнопка «Установить Диск»', 458, 152)}
      <p>После установки программы, ввода логина и пароля на компьютере появится папка:</p>
      {shot('folder', 'Папка Яндекс Диска на компьютере', 226, 252)}
      <p>в которой можно создавать новые папки и переместить туда файлы с результатами исследований.</p>
      <p>Затем надо вновь вернуться к браузеру (Google Chrome, Opera, Internet Explorer), где открыта страница Яндекс Диска. Войти в свой аккаунт (ввести логин и пароль). Теперь у вас есть возможность отправить ссылку на результаты исследований врачу:</p>
      {shot('disk-folder', 'Папка с результатами исследований на Яндекс Диске', 1000, 567)}
      <p>Выберите нужную папку одним щелчком мыши. Появится окно с кнопкой «Поделиться»:</p>
      {shot('share-btn', 'Кнопка «Поделиться»', 288, 126)}
      <p>Затем можно скопировать ссылку на папку и отправить её по электронной почте:</p>
      <p><a class="mail" href="mailto:k.tumarec@nesutulsya.ru">k.tumarec@nesutulsya.ru</a></p>
      {shot('share-link', 'Окно со ссылкой на папку', 458, 850)}
    </article>
  </div>
  <div class="more-link"><a class="btn btn--lime btn--xl magnetic" href="{P}#zapis"><span>Записаться на приём</span></a></div>
</section>'''
    page('patients', 'patients', 'Как отправить результаты КТ, МРТ, рентгена врачу — «НеСутулься»',
         'Инструкция для пациентов «НеСутулься»: как скопировать DICOM с диска и отправить результаты КТ, МРТ или рентгена врачу через архив, Яндекс Диск или облако.',
         body)

# ---------------------------------------------------------------- МЕРЧ (/store)
def build_store():
    body = phero('МЕРЧ', 'Фирменный мерч «НеСутулься».', crumbs='Мерч', label='Мерч')
    body += f'''
<section class="sec sec--brick soon">
  <p class="soon__t reveal">СКОРО…</p>
  <div class="merch reveal"><img src="{P}assets/img/store/merch.webp" alt="Мерч «НеСутулься» — термокружки «Собака сутулая»" width="1600" height="900" loading="lazy" decoding="async"></div>
  <div class="more-link" style="gap:14px;flex-wrap:wrap"><a class="btn btn--lime btn--xl magnetic" href="{VK}" target="_blank" rel="noopener"><span>Следить в VK</span></a><a class="btn btn--ghost btn--xl magnetic" href="{P}shop/"><span>Услуги и цены</span></a></div>
</section>'''
    page('store', 'store', 'Мерч «НеСутулься» — скоро',
         'Фирменный мерч реабилитационного центра «НеСутулься» — скоро в продаже.', body)

# ---------------------------------------------------------------- ПРИЛОЖЕНИЕ (/application)
def build_app():
    body = f'''<section class="phero" id="top" style="min-height:100svh;display:grid;place-items:center">
  <div class="phero__wall" data-speed="0.2" aria-hidden="true"></div>
  <div class="phero__inner appstart">
    <h1 class="sr-only" style="position:absolute;left:-9999px">Приложение «НеСутулься»</h1>
    <img class="appstart__logo reveal" src="{P}assets/img/logo.webp" alt="НеСутулься" width="900" height="197">
    <div class="appstart__img reveal"><img src="{P}assets/img/app/start.webp" alt="Приложение «НеСутулься»" width="900" height="1125"></div>
    <a class="btn btn--lime btn--xl magnetic reveal" href="{OLD}/account-1" target="_blank" rel="noopener"><span>НАЧАТЬ</span></a>
    <p class="reveal" style="color:var(--mute);font-size:14px;max-width:420px;margin:0">Вход и регистрация в личном кабинете пока работают на основном сайте не-сутулься.рф.</p>
  </div>
</section>'''
    page('application', 'app', 'Приложение «НеСутулься»', 'Приложение и личный кабинет пациента «НеСутулься».', body)
# ---------------------------------------------------------------- ЮРИДИЧЕСКИЕ СТРАНИЦЫ
LEGAL = json.load(open(os.path.join(ROOT, 'tools', 'legal.json'), encoding='utf8'))
LEGAL_META = {
    'privacy': ('ПОЛИТИКА ПДн', 'Политика обработки персональных данных — «НеСутулься»', 'Политика ИП Тумарца К.М. («НеСутулься») в отношении обработки персональных данных пользователей сайта.'),
    'cookie': ('COOKIES', 'Политика в отношении файлов cookie — «НеСутулься»', 'Какие файлы cookie использует сайт «НеСутулься», зачем они нужны и как отозвать согласие.'),
    'ps': ('СОГЛАШЕНИЕ', 'Пользовательское соглашение — «НеСутулься»', 'Пользовательское соглашение сайта «НеСутулься»: условия использования сайта, личного кабинета и формы обратной связи.'),
    'oferta': ('ОФЕРТА', 'Публичная оферта на оказание услуг — «НеСутулься»', 'Публичная оферта ИП Тумарца К.М. («НеСутулься») на оказание услуг от 24.01.2026 и прейскурант услуг.'),
}
def fix_links(t):
    t = t.replace('https://несутулься.рф/privacy', P + 'privacy/').replace('http://несутулься.рф/privacy', P + 'privacy/')
    t = t.replace('https://несутулься.рф/cookie', P + 'cookie/').replace('http://несутулься.рф/cookie', P + 'cookie/')
    return t

def legal_html(slug):
    items = LEGAL[slug]['items']; out = []; ul = []
    def close_ul():
        if ul: out.append('<ul>' + ''.join(f'<li>{x}</li>' for x in ul) + '</ul>'); ul.clear()
    i = 0
    while i < len(items):
        k, v = items[i]; v = fix_links(v); plain = re.sub('<[^>]+>', '', v)
        # оферта: реквизиты и прейскурант — отдельной вёрсткой
        if slug == 'oferta' and plain.startswith('Подписи и реквизиты'):
            close_ul()
            rest = [re.sub('<[^>]+>', '', x[1]) for x in items[i+1:]]
            pi = rest.index('ПРЕЙСКУРАНТ УСЛУГ')
            sig = rest[:pi]; price = rest[pi+1:]
            isp = [x for x in sig if x.startswith(('Индивидуальный', 'ОГРНИП', 'ИНН', 'Юр.', 'Фактический', 'тел.', 'e-mail', 'Банковские', 'Тумарец'))]
            zak = [x for x in sig if x not in isp and not x.startswith('ИСПОЛНИТЕЛЬ')]
            out.append('<h2>Подписи и реквизиты Сторон</h2><div class="rekv"><div><p><b>ИСПОЛНИТЕЛЬ</b></p>' + ''.join(f'<p>{H.escape(x)}</p>' for x in isp) +
                       '</div><div><p><b>ЗАКАЗЧИК</b></p>' + ''.join(f'<p>{H.escape(x)}</p>' for x in zak) + '</div></div>')
            rows = []; notes = []
            for x in price:
                if x.startswith(('№ п/п', 'Наименование')): continue
                if x.startswith(('Итого', '___')): continue
                m = re.match(r'^(\d+(?:\.\d+)?)\s*-?\s*(.*?)\s*([\d ]{3,}|-)$', x)
                if m and not x.startswith(('*', '-', '1)', '2)')):
                    num, name, cost = m.groups(); name = name.rstrip('.* ').rstrip() if cost != '-' else name
                    name = name.rstrip('*')
                    rows.append(f'<tr><td>{num}</td><td>{H.escape(name)}</td><td>{cost.strip() if cost.strip()!="-" else "—"}</td></tr>')
                elif re.match(r'^\d+\s+[^\d].*:$', x):
                    num, name = x.split(None, 1)
                    rows.append(f'<tr class="grp"><td>{num}</td><td colspan="2">{H.escape(name)}</td></tr>')
                else:
                    notes.append(x)
            out.append('<h2 id="price">Прейскурант услуг</h2><table><thead><tr><th>№</th><th>Наименование, продолжительность</th><th>Стоимость, ₽</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table>')
            out.append('<p><b>' + H.escape(notes[0]) + '</b></p><ul>' + ''.join(f'<li>{H.escape(n.lstrip("- "))}</li>' for n in notes[1:]) + '</ul>')
            break
        if k == 'h' or (slug in ('privacy', 'ps') and re.match(r'^\d+\.\s?[А-ЯЁA-Z][^.]{2,90}\.?$', plain) and len(plain) < 100 and not re.match(r'^\d+\.\d', plain)) \
           or (slug == 'cookie' and len(plain) < 40 and not plain.endswith('.')) or (slug == 'ps' and plain in ('Порядок принятия Соглашения.', 'Дееспособность пользователя.', 'Термины и определения')):
            close_ul(); out.append(f'<h2>{plain}</h2>')
        elif re.match(r'^[—–-]\s', plain):
            ul.append(re.sub(r'^[—–-]\s*', '', v))
        else:
            close_ul(); out.append(f'<p>{v}</p>')
        i += 1
    close_ul()
    return '\n'.join(out)

def build_legal(slug):
    h1, title, desc = LEGAL_META[slug]
    doc_title = LEGAL[slug]['title']
    extra = ''
    if slug == 'oferta':
        extra = f'<a class="btn btn--lime magnetic" href="{P}assets/docs/oferta.docx" download><span>Скачать DOCX</span></a>'
    others = [('privacy', 'Политика ПДн'), ('cookie', 'Cookie'), ('ps', 'Пользовательское соглашение'), ('oferta', 'Публичная оферта')]
    nav = ''.join(f'<a class="btn {"btn--lime" if s==slug else "btn--ghost"} btn--sm" href="{P}{s}/"{" aria-current=\"page\"" if s==slug else ""}>{t}</a>' for s, t in others)
    body = phero(h1, doc_title, crumbs=doc_title, label='Документы')
    body += f'''
<section class="sec sec--concrete" style="padding-top:60px">
  <div class="legal-meta">{'<p>г. Москва · ИП Тумарец Кирилл Михайлович</p>' if slug=='oferta' else '<p>ИП Тумарец Кирилл Михайлович · ИНН 772086427984</p>'}{extra}</div>
  <article class="prose">
{legal_html(slug)}
  </article>
  <nav class="legal-nav" aria-label="Документы">{nav}</nav>
</section>'''
    page(slug, slug, title, desc, body)

# ---------------------------------------------------------------- ГЛАВНАЯ: шапка/подвал
def patch_index():
    p = os.path.join(ROOT, 'index.html'); s = open(p, encoding='utf8').read()
    hdr = header('', 'home', '#zapis', home=True)
    ftr = footer('', home=True).replace('{ZAPIS}', '#zapis')
    s = re.sub(r'<!-- @hdr -->.*?<!-- /@hdr -->', lambda m: '<!-- @hdr -->\n' + hdr + '\n<!-- /@hdr -->', s, flags=re.S)
    s = re.sub(r'<!-- @ftr -->.*?<!-- /@ftr -->', lambda m: '<!-- @ftr -->\n' + ftr + '\n<!-- /@ftr -->', s, flags=re.S)
    open(p, 'w', encoding='utf8').write(s); print('patched index.html')

PAGES = ['', 'shop', 'founder', 'friends', 'orto', 'store', 'patients', 'application', 'privacy', 'cookie', 'ps', 'oferta']
def sitemap():
    urls = ''.join(f'<url><loc>{BASE}{(s + "/") if s else ""}</loc></url>\n' for s in PAGES)
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf8').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    open(os.path.join(ROOT, 'robots.txt'), 'w', encoding='utf8').write(f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n')

if __name__ == '__main__':
    patch_index()
    build_shop(); build_orto(); build_founder(); build_friends(); build_patients(); build_store(); build_app()
    for s in ('privacy', 'cookie', 'ps', 'oferta'): build_legal(s)
    sitemap()
