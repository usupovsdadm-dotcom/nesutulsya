# «НеСутулься» — новая версия сайта (граффити / стрит-арт)

Многостраничный статичный сайт: HTML + CSS + чистый JavaScript.
Сборки нет, зависимостей нет, внешних CDN нет: шрифты, картинки и видео лежат локально.
Все пути относительные, поэтому сайт работает и в корне домена, и в подпапке (например, `/nesutulsya/` на GitHub Pages).

## Страницы

Адреса «чистые» (папка + `index.html`), все ссылки между страницами относительные.

| Страница | Файл | Адрес на GitHub Pages | Заменяет на старом сайте |
|---|---|---|---|
| Главная | `index.html` | https://usupovsdadm-dotcom.github.io/nesutulsya/ | https://не-сутулься.рф/ |
| Услуги и цены | `shop/index.html` | https://usupovsdadm-dotcom.github.io/nesutulsya/shop/ | /shop (якоря `#cons #sess #vyezd #zal #stelki #online #fitness #massage #cert`; «Онлайн» из меню → `shop/#online`) |
| Основатель | `founder/index.html` | https://usupovsdadm-dotcom.github.io/nesutulsya/founder/ | /Founder |
| Нам доверяют | `friends/index.html` | https://usupovsdadm-dotcom.github.io/nesutulsya/friends/ | /friends |
| Стельки | `orto/index.html` | https://usupovsdadm-dotcom.github.io/nesutulsya/orto/ | /orto |
| Мерч | `store/index.html` | https://usupovsdadm-dotcom.github.io/nesutulsya/store/ | /store |
| Результаты исследований | `patients/index.html` | https://usupovsdadm-dotcom.github.io/nesutulsya/patients/ | /patients |
| Приложение | `application/index.html` | https://usupovsdadm-dotcom.github.io/nesutulsya/application/ | /application |
| Политика ПДн | `privacy/index.html` | https://usupovsdadm-dotcom.github.io/nesutulsya/privacy/ | /privacy |
| Политика cookie | `cookie/index.html` | https://usupovsdadm-dotcom.github.io/nesutulsya/cookie/ | /cookie |
| Пользовательское соглашение | `ps/index.html` | https://usupovsdadm-dotcom.github.io/nesutulsya/ps/ | /ps |
| Публичная оферта | `oferta/index.html` | https://usupovsdadm-dotcom.github.io/nesutulsya/oferta/ | /oferta (+ DOCX в `assets/docs/oferta.docx`) |

«Команда» и «Контакты» — разделы главной (`#team`, `#contacts`), как и на старом сайте (там команда была всплывающим окном).
Не перенесены (нужен сервер): личный кабинет, вход/регистрация и курсы (`/Chat`, `/ointments`, `/cc/*`, `/hv/*`, `/account-1`),
онлайн-оплата «Приобрести» (корзина Creatium). Кнопка «НАЧАТЬ» на странице «Приложение» ведёт в кабинет на старом сайте.
`/online` на старом сайте не опубликована.

### Как править страницы
Внутренние страницы собираются скриптом (Python 3, без зависимостей):
```
python3 tools/build.py
```
- `tools/build.py` — тексты, цены и разметка внутренних страниц, `sitemap.xml`, `robots.txt`;
- `tools/partials.py` — общие шапка, мобильное меню, подвал, нижняя панель, cookie-баннер, `<head>` с SEO-тегами;
- `tools/legal.json` — тексты юридических документов (выгружены со старого сайта).
Шапку и подвал главной скрипт обновляет между маркерами `<!-- @hdr -->` и `<!-- @ftr -->`; остальной `index.html` правится руками.
Если правите HTML внутренних страниц вручную — следующий запуск скрипта их перезапишет.

## Структура

```
index.html              — главная (первый экран, «Что болит», подход, запись, основатель, команда, «Нам доверяют», FAQ, контакты)
<slug>/index.html       — внутренние страницы (см. таблицу выше), генерируются tools/build.py
sitemap.xml, robots.txt — карта сайта с адресами github.io
css/style.css           — стили, анимации, адаптив, prefers-reduced-motion
js/main.js              — прелоадер, эффекты, форма (FORM_ENDPOINT), статус «открыто/закрыто» по МСК
assets/fonts/           — Rubik Spray Paint, Rubik Wet Paint, Rubik Glitch, Rubik Mono One, Caveat, Unbounded, Manrope
                          (woff2, кириллица + латиница; все шрифты под лицензией SIL OFL)
assets/img/             — фото основателя, команды, гостей («Нам доверяют»), дипломы, зал, логотип, видео с тейпированием;
                          shop/ (услуги, сертификат), orto/ (стельки, документы соответствия), store/, patients/, app/, founder/
assets/docs/oferta.docx — публичная оферта для скачивания
assets/tex/             — сгенерированные текстуры (бетон, кирпич, брызги краски)
assets/og-image.jpg     — картинка для превью ссылки в соцсетях и мессенджерах
assets/favicon.ico, favicon-32.png, apple-touch-icon.png, icon-512.png
.nojekyll               — нужен для GitHub Pages
```

Все фото, тексты и цены взяты с текущего сайта не-сутулься.рф (все страницы из sitemap.xml и меню).

## Что подключить программисту

### 1. Форма заявки (обязательно)
В `js/main.js`, в самом начале:
```js
var FORM_ENDPOINT = '';
```
Укажите URL обработчика. Форма отправляет `POST` с `Content-Type: application/json`:
```json
{ "name": "Иван", "phone": "+7 (999) 123-45-67", "page": "https://…", "service": "Блок 6 сессий — 45 900 ₽" }
```
Поле `service` есть только у форм на страницах «Услуги» (выбор из списка; кнопки «Записаться» у карточек подставляют услугу) и «Стельки».
Формы — все `form.lead` на странице (главная, услуги, стельки).
Ответ 2xx — показываем «Заявка у нас!»; ошибка — показываем просьбу позвонить.
Пока `FORM_ENDPOINT` пустой, форма **ничего не отправляет**, а просто показывает успешное состояние и номер телефона.
Обработчиком может быть свой бэкенд, Telegram-бот, amoCRM/Bitrix24 webhook, Formspree и т. п.
Для обработчика на другом домене нужен CORS (`Access-Control-Allow-Origin`). Есть скрытое поле-ловушка `website` от ботов.

### 2. Яндекс.Метрика
Вставьте код счётчика перед `</head>` в `index.html` и в функцию `head()` в `tools/partials.py` (потом `python3 tools/build.py`). Цели удобно повесить на:
- отправку формы: в `js/main.js`, функция `done()` внутри обработчика формы, например `ym(XXXXXX,'reachGoal','lead')`;
- клики по `a[href^="tel:"]`, по ссылкам VK и MAX, по кнопкам «Записаться» (`a[href="#zapis"]`).
Если Метрика ставит cookie, добавьте cookie-баннер (на старом сайте он был).

### 3. Домен
Сейчас canonical и OG-теги указывают на `https://usupovsdadm-dotcom.github.io/nesutulsya/`.
При переезде на не-сутулься.рф замените `BASE` в `tools/partials.py` и адрес в `index.html` (`<link rel="canonical">`, `og:url`, `og:image`), затем `python3 tools/build.py`.
- Своя площадка: залейте содержимое папки в корень сайта, включите HTTPS и gzip/brotli, задайте долгий кэш для `assets/`.
- GitHub Pages с доменом: Settings → Pages → Custom domain = `xn----itbtfwbfhb5g8a.xn--p1ai` (punycode), в DNS — A-записи GitHub Pages.

### 4. Юридические страницы и cookie
Политика ПДн, cookie, пользовательское соглашение и оферта — свои страницы (`privacy/`, `cookie/`, `ps/`, `oferta/`).
В текстах документов остался адрес `https://несутулься.рф/` — это сам документ, его меняет юрист/владелец.
Cookie-баннер (текст со старого сайта) показывается один раз, выбор хранится в `localStorage` (`ns_cookie`).

## Настройки в коде
- Часы работы для статуса «Сейчас открыто / закрыто» — `WORK_FROM`, `WORK_TO` в `js/main.js` (время МСК).
- Слова для печатающейся строки на первом экране — массив `words` в `js/main.js`.
- Цвета — переменные в начале `css/style.css` (`--lime`, `--pink`, `--yellow`, `--cyan`).

## Эффекты
Прелоадер «логотип рисуется баллончиком» (только на главной и только при первом заходе за сессию) (SVG-маска + частицы на canvas), заголовки с «набрызгом» по буквам и рисуемой линией,
glitch, курсор-баллончик с брызгами (только мышь, не мобильные), параллакс, ленты-оградительные «Осторожно», стикеры
с физикой (их можно таскать и бросать), magnetic-кнопки, 3D-наклон карточек, рваные края между секциями, заливка секции записи краской,
линия «баллончиком» по скроллу в блоке «Как мы работаем», счётчики (только реальные числа с сайта), лайтбокс дипломов.
При `prefers-reduced-motion: reduce` анимации отключаются, контент виден сразу.

## Локальная проверка
```
python3 -m http.server 8080
```
и откройте http://localhost:8080
