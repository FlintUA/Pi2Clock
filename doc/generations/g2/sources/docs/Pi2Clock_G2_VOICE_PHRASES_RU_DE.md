# Pi2Clock G2 - тексты озвучивания (русский и немецкий)

**Статус:** редакторский сценарий, 23.11.2026. **Речевые файлы ещё не созданы.** Тексты ниже - предназначенные для записи/синтеза фразы, а не расшифровки старых MP3 с DFPlayer.

**Соглашение:** `ID` - постоянный идентификатор события прошивки; `[N]`, `[TIME]`, `[DURATION]`, `[DATE]`, `[NAME]`, `[TEMP]`, `[HUMIDITY]`, `[PRESSURE]`, `[PERCENT]`, `[VOICE]`, `[LEVEL]`, `[CONDITION]` - **переменные**, которые движок составляет из проверенных токенов. Нельзя озвучивать квадратные скобки и английские имена переменных. Столбец «Примечание» содержит условия воспроизведения.

**Режимы:** RU и DE - два целевых языка. Для каждого по **6 голосов**: `female_01`, `female_02`, `female_03`, `male_01`, `male_02`, `male_03`; всего 12 пакетов. На начальном этапе разрешается заполнить лишь один проверенный голос на язык и добавить оставшиеся как опциональные пакеты. Каждый объявленный *установленным* пакет обязан пройти полную валидацию. Файлы аудио у каждого голоса независимы; не смешивать голоса внутри предложения.

**Важная техническая граница:** текущий G1 поддерживает один таймер и пять будильников; три независимых таймера, полные голосовые пакеты и новый файловый формат - требования G2, не реализованная возможность. Голосовые объявления не должны задерживать сами события таймера/будильника.

## 1. Полный каталог семантических событий

| ID | Русский текст / образец | Deutscher Text / Muster | Примечание |
|---|---|---|---|
| `alarm.announced` | Будильник [N]. Сейчас [TIME]». | Wecker [N]. Es ist [TIME]. | Текущая V3 уже произносит время; добавить DE номера 1-5. |
| `alarm.disabled` | Будильник [N] выключен». | Wecker [N] deaktiviert. |  |
| `alarm.enabled` | Будильник [N] включён на [TIME]». | Wecker [N] ist für [TIME] aktiviert. | Настройка. |
| `alarm.next` | Следующий будильник в [TIME]». | Der nächste Wecker ist um [TIME] gestellt. | Запрос информации. |
| `alarm.next_slot` | Следующий будильник номер [N] в [TIME] | Der nächste Wecker ist Nummer [N] um [TIME] |  |
| `alarm.none` | Включённых будильников нет | Keine aktiven Wecker |  |
| `alarm.saved` | Будильник [N] сохранён». | Wecker [N] gespeichert. |  |
| `alarm.snooze_finished` | Время повтора будильника | Die Schlummerzeit ist vorbei |  |
| `alarm.snoozed` | Будильник отложен на [DURATION]». | Wecker um [DURATION] verschoben. | Только если функция Snooze будет реализована; пока не обязательна. |
| `alarm.stopped` | Будильник [N] остановлен». | Wecker [N] ausgeschaltet. | Обычно можно обойтись индикацией. |
| `birthday.age` | Исполняется [N] лет | Wird [N] Jahre alt | Только если указан год рождения |
| `birthday.today` | Сегодня день рождения [NAME] | Heute hat [NAME] Geburtstag | Не проговаривать произвольное имя без TTS |
| `birthday.tomorrow` | Завтра день рождения [NAME] | Morgen hat [NAME] Geburtstag |  |
| `bt.connected` | Bluetooth-колонка подключена». | Bluetooth-Lautsprecher verbunden. | Отображать сохранённое реальное имя на OLED. |
| `bt.connecting` | Подключение к Bluetooth-колонке». | Verbindung zum Bluetooth-Lautsprecher wird hergestellt. |  |
| `bt.connection_failed` | Не удалось подключиться к колонке». | Verbindung zum Lautsprecher fehlgeschlagen. |  |
| `bt.disconnected` | Bluetooth-колонка отключена». | Bluetooth-Lautsprecher getrennt. |  |
| `bt.found` | Найдено [N] устройств». | [N] Geräte gefunden. | Не озвучивать имя произвольного устройства без TTS. |
| `bt.no_devices` | Bluetooth-устройства не найдены | Keine Bluetooth-Geräte gefunden |  |
| `bt.output_local` | Звук через встроенный динамик | Ton über den eingebauten Lautsprecher |  |
| `bt.output_remote` | Звук через Bluetooth-колонку | Ton über den Bluetooth-Lautsprecher |  |
| `bt.preferred_saved` | Bluetooth-колонка сохранена | Bluetooth-Lautsprecher gespeichert |  |
| `bt.reconnecting` | Повторное подключение». | Verbindung wird wiederhergestellt. | Не произносить при каждом повторе. |
| `bt.searching` | Поиск Bluetooth-устройств». | Suche nach Bluetooth-Geräten. | По запросу. |
| `clock.chime` | бой часов / двойной полчасовой сигнал | Stundenschlag / Halbstundenton | `sounds/`; без речевого пакета. |
| `clock.current_date` | Сегодня [WEEKDAY], [DAY] [MONTH] [YEAR] года». | Heute ist [WEEKDAY], der [DAY]. [MONTH] [YEAR]. | Даты 2000-2099, грамматические падежи RU. |
| `clock.current_time` | Сейчас [TIME]». | Es ist [TIME]. | Вручную/по расписанию. |
| `clock.exact_hour` | Сейчас [HOUR] ровно». | Es ist genau [HOUR] Uhr. | Форму согласовать с готовыми аудиоклипами. |
| `clock.next_birthday` | Ближайший день рождения [NAME] [DATE] | Der nächste Geburtstag von [NAME] ist am [DATE] | С именами из словаря или только экран |
| `clock.sync_failed` | Не удалось синхронизировать время». | Uhrzeit konnte nicht synchronisiert werden. | Не блокировать RTC. |
| `clock.time_synced` | Время синхронизировано». | Uhrzeit synchronisiert. | NTP-статус, опционально. |
| `music.collection_empty` | Выбранная коллекция пуста | Die gewählte Musiksammlung ist leer |  |
| `music.empty` | Музыкальные файлы не найдены». | Keine Musikdateien gefunden. | Только при наличии голосового пакета. |
| `music.next` | Следующая композиция | Nächster Titel |  |
| `music.paused` | Пауза». | Pause. |  |
| `music.previous` | Предыдущая композиция | Vorheriger Titel |  |
| `music.shuffle_off` | Случайный порядок выключен | Zufallswiedergabe ausgeschaltet |  |
| `music.shuffle_on` | Случайный порядок включён | Zufallswiedergabe eingeschaltet |  |
| `music.sleep_timer` | Музыка будет остановлена через [DURATION] | Musik wird in [DURATION] gestoppt |  |
| `music.started` | Воспроизведение музыки». | Musikwiedergabe gestartet. | Опционально. |
| `music.stopped` | Воспроизведение остановлено». | Wiedergabe gestoppt. |  |
| `music.track_missing` | Выбранная мелодия недоступна». | Der ausgewählte Musiktitel ist nicht verfügbar. | При сломанной ссылке alarm track_id. |
| `network.no_internet` | Нет подключения к интернету | Keine Internetverbindung |  |
| `network.web_closed` | Веб-интерфейс отключён | Weboberfläche deaktiviert |  |
| `network.web_started` | Веб-интерфейс доступен | Weboberfläche verfügbar |  |
| `ota.available` | Доступно обновление». | Ein Update ist verfügbar. | Не обещать при отсутствии сервиса. |
| `ota.checking` | Проверка обновлений | Suche nach Updates |  |
| `ota.downloading` | Загрузка обновления | Update wird heruntergeladen |  |
| `ota.failed` | Не удалось установить обновление». | Update konnte nicht installiert werden. |  |
| `ota.installing` | Установка обновления | Update wird installiert |  |
| `ota.rollback` | Возврат к предыдущей версии | Vorherige Version wird wiederhergestellt |  |
| `ota.success` | Обновление установлено». | Update installiert. | После проверки. |
| `recording.failed` | Не удалось сохранить запись | Aufnahme konnte nicht gespeichert werden |  |
| `recording.start` | Начинается запись | Aufnahme beginnt | Только с микрофоном |
| `recording.stopped` | Запись сохранена | Aufnahme gespeichert |  |
| `sound.disabled` | Звук выключен». | Ton ausgeschaltet. | Существуют 07/009 и 17/009 по назначению. |
| `sound.enabled` | Звук включён». | Ton eingeschaltet. | Существуют 07/008 и 17/008 по назначению. |
| `sound.night_mode_off` | Ночной режим выключен». | Nachtmodus deaktiviert. |  |
| `sound.night_mode_on` | Ночной режим включён». | Nachtmodus aktiviert. | Раздельно с тихим режимом. |
| `sound.silent_mode_off` | Тихий режим выключен». | Lautloser Modus deaktiviert. | Без обрыва критичного таймера. |
| `sound.silent_mode_on` | Тихий режим включён». | Lautloser Modus aktiviert. | Текст подтверждения опционален. |
| `sound.volume` | Громкость [LEVEL] процентов». | Lautstärke [LEVEL] Prozent. | Возможен только экран/тон, чтобы не мешать. |
| `system.audio_unavailable` | Голосовые сообщения недоступны». | Sprachausgabe nicht verfügbar. | Если есть резервный встроенный сигнал. |
| `system.battery_critical` | Аккумулятор почти разряжен | Akku fast leer |  |
| `system.battery_low` | Низкий заряд аккумулятора | Akkustand niedrig | Только при установленном аккумуляторе |
| `system.battery_power` | Работа от аккумулятора | Akkubetrieb |  |
| `system.cancelled` | Отменено». | Abgebrochen. | Тихое подтверждение опционально. |
| `system.error` | Ошибка». | Fehler. | Резерв UI сигнал. |
| `system.external_power` | Внешнее питание подключено | Externe Stromversorgung angeschlossen |  |
| `system.first_setup` | Первоначальная настройка часов | Ersteinrichtung der Uhr | Офлайн первичная настройка |
| `system.language_selected` | Выбран русский язык | Russisch ausgewählt | Языковые альтернативы по факту выбранного языка |
| `system.no_valid_time` | Точное время не установлено | Die Uhrzeit ist noch nicht eingestellt | Критично после холодного пуска без NTP и RTC |
| `system.ready` | Часы готовы к работе». | Die Uhr ist betriebsbereit. | Не обязательно озвучивать при каждом старте. |
| `system.reset_confirm` | Подтвердите сброс настроек | Zurücksetzen der Einstellungen bestätigen |  |
| `system.sd_error` | Ошибка чтения карты памяти | Fehler beim Lesen der Speicherkarte | Отсутствие SD -> только экран и резервный beep из Flash |
| `system.sd_missing` | Карта памяти не найдена». | Speicherkarte nicht gefunden. | При отсутствии SD произнести невозможно: показать OLED/WS2812 и сигнал из встроенной flash. |
| `system.settings_saved` | Настройки сохранены». | Einstellungen gespeichert. | Не озвучивать каждое вращение энкодера. |
| `system.startup` | короткий стартовый сигнал | kurzer Startton | Отдельный `sounds/startup.wav`. |
| `system.storage_full` | Недостаточно места на карте памяти | Nicht genügend Speicherplatz auf der Speicherkarte |  |
| `system.time_manual` | Время установлено вручную | Uhrzeit manuell eingestellt |  |
| `timer.acknowledged` | [ORD] таймер подтверждён». | Timer [N] bestätigt. | Обычно лучше только короткий тон/индикация. |
| `timer.all_finished` | Все таймеры завершены». | Alle Timer sind abgelaufen. | Опционально; не вместо отдельных сообщений. |
| `timer.cancelled` | [ORD] таймер отменён». | Timer [N] abgebrochen. |  |
| `timer.finished` | **«[ORD] таймер на [DURATION] завершён».** | **„Timer [N] über [DURATION] ist abgelaufen.“** | Точное требование пользователя для RU. DE формулировку утвердить на прослушивании. |
| `timer.five_seconds_warning` | Таймер [N]: осталось пять секунд | Timer [N]: Noch fünf Sekunden |  |
| `timer.idle` | Таймер [N] не запущен | Timer [N] ist nicht gestartet |  |
| `timer.max_running` | Уже работают три таймера | Es laufen bereits drei Timer |  |
| `timer.one_minute_warning` | Таймер [N]: осталась одна минута | Timer [N]: Noch eine Minute | При включенном предупреждении |
| `timer.overlap` | Завершились несколько таймеров». | Mehrere Timer sind abgelaufen. | При одновременном событии, затем индивидуальные фразы. |
| `timer.paused` | [ORD] таймер приостановлен». | Timer [N] pausiert. |  |
| `timer.remaining` | [ORD] таймер - осталось [DURATION]». | Timer [N]: noch [DURATION]. | Только по запросу. |
| `timer.resumed` | [ORD] таймер продолжен». | Timer [N] fortgesetzt. |  |
| `timer.running` | Таймер [N] работает | Timer [N] läuft |  |
| `timer.setup` | Настройка [ORD] таймера». | [N]. Timer einstellen. | Открытие редактора, по настройке. |
| `timer.started` | [ORD] таймер установлен на [DURATION]». | Timer [N] auf [DURATION] eingestellt und gestartet. | После успешного запуска. |
| `timer.time_invalid` | Неверная продолжительность таймера». | Ungültige Timerdauer. | UI в приоритете. |
| `voice.preview` | Здравствуйте. Это образец моего голоса». | Hallo. Das ist eine Hörprobe meiner Stimme. | Одинаковый текст для всех голосов. |
| `voice.selected` | Выбран голос [VOICE]». | Stimme [VOICE] ausgewählt. | + фраза предпрослушивания. |
| `weather.condition.clear` | Ясно». | Klar. | Контекстная форма нужна в полноценном предложении. |
| `weather.condition.cloudy` | Облачно». | Bewölkt. |  |
| `weather.condition.fog` | Туман». | Nebel. |  |
| `weather.condition.part_cloudy` | Переменная облачность». | Teilweise bewölkt. |  |
| `weather.condition.rain` | Дождь». | Regen. |  |
| `weather.condition.snow` | Снег». | Schnee. |  |
| `weather.condition.thunderstorm` | Гроза». | Gewitter. |  |
| `weather.current` | На улице [TEMP] градусов». | Draußen sind es [TEMP] Grad. | Текущая температура, только если данные свежие. |
| `weather.data_age` | Последнее обновление [TIME]». | Zuletzt aktualisiert um [TIME]. | Для кэша. |
| `weather.feels_like` | Ощущается как [TEMP] градусов». | Gefühlt [TEMP] Grad. | Опционально. |
| `weather.indoor` | В помещении [TEMP] градусов, влажность [HUMIDITY] процентов | Im Raum [TEMP] Grad, Luftfeuchtigkeit [HUMIDITY] Prozent | BME280 опция |
| `weather.not_installed` | Датчик температуры не установлен | Temperatursensor nicht installiert |  |
| `weather.pressure` | Атмосферное давление [PRESSURE] гектопаскалей | Luftdruck [PRESSURE] Hektopascal | BME280 опция |
| `weather.rain_probability` | Вероятность осадков [PERCENT] процентов». | Niederschlagswahrscheinlichkeit [PERCENT] Prozent. |  |
| `weather.stale` | Данные о погоде устарели | Wetterdaten sind veraltet | Не говорить как текущие |
| `weather.temp_range` | Температура от [MIN] до [MAX] градусов». | Temperaturen zwischen [MIN] und [MAX] Grad. |  |
| `weather.today` | Сегодня ожидается [CONDITION]». | Heute wird [CONDITION] erwartet. | Согласовать немецкую грамматику по категориям. |
| `weather.tomorrow` | Завтра ожидается [CONDITION]». | Morgen wird [CONDITION] erwartet. |  |
| `weather.unavailable` | Нет актуальных данных о погоде». | Keine aktuellen Wetterdaten verfügbar. | Не выдавать старый прогноз за новый. |
| `wifi.ap_enabled` | Точка доступа включена | Zugangspunkt aktiviert |  |
| `wifi.connected` | Wi-Fi подключён». | WLAN verbunden. |  |
| `wifi.connecting` | Подключение к Wi-Fi | Verbindung mit WLAN wird hergestellt |  |
| `wifi.disconnected` | Wi-Fi недоступен. Часы работают автономно». | WLAN nicht verfügbar. Die Uhr arbeitet offline. | Обычно без звукового спама. |
| `wifi.ntp_pending` | Ожидание синхронизации времени | Warte auf Zeitsynchronisierung |  |

## 2. Фразы, которые нельзя собрать из одних «универсальных» слов

### Время - произношение и образцы

| Время | RU | DE (24-часовой официальный стиль) |
|---|---|---|
| 00:00 | Сейчас полночь. | Es ist Mitternacht. |
| 01:00 | Сейчас один час ровно. | Es ist ein Uhr. |
| 02:01 | Сейчас два часа одна минута. | Es ist zwei Uhr eins. |
| 05:02 | Сейчас пять часов две минуты. | Es ist fünf Uhr zwei. |
| 14:25 | Сейчас четырнадцать часов двадцать пять минут. | Es ist vierzehn Uhr fünfundzwanzig. |
| 23:59 | Сейчас двадцать три часа пятьдесят девять минут. | Es ist dreiundzwanzig Uhr neunundfünfzig. |

RU - согласование `час/часа/часов`, `минута/минуты/минут`; для *времени на часах* рекомендуется мужской «один час», «два часа», для длительности после `на` - «одну минуту». DE - `ein Uhr` для 01:00, остальное в стандартном 24-часовом произнесении; короткая разговорная форма *halb drei* необязательна. При озвучивании часов не добавлять «ноль минут», если минуты равны нулю.

### Три таймера: обязательные полные примеры

| Событие | RU | DE |
|---|---|---|
| T1, 14 минут, старт | Первый таймер установлен на четырнадцать минут. | Timer eins auf vierzehn Minuten eingestellt und gestartet. |
| T1, 14 минут, завершён | **Первый таймер на четырнадцать минут завершён.** | **Timer eins mit vierzehn Minuten Laufzeit ist abgelaufen.** |
| T2, 1 минута, завершён | Второй таймер на одну минуту завершён. | Timer zwei mit einer Minute Laufzeit ist abgelaufen. |
| T3, 1 ч 2 мин 3 сек, завершён | Третий таймер на один час две минуты три секунды завершён. | Timer drei mit einer Stunde, zwei Minuten und drei Sekunden Laufzeit ist abgelaufen. |
| T2, 5 секунд осталось | Второй таймер - осталось пять секунд. | Timer zwei: noch fünf Sekunden. |

При завершении озвучивается **исходная установленная длительность**, а не оставшиеся ноль секунд. При совпадающих событиях - очередь приоритетных уведомлений и отдельное подтверждение каждого. Исходную длительность хранить в состоянии таймера.

### Даты, дни недели, дни рождения

| Событие | RU | DE |
|---|---|---|
| 1 ноября 2026 | Сегодня воскресенье, первое ноября две тысячи двадцать шестого года. | Heute ist Sonntag, der erste November zweitausendsechsundzwanzig. |
| Будильник 4, 07:30 | Будильник номер четыре. Сейчас семь часов тридцать минут. | Wecker vier. Es ist sieben Uhr dreißig. |
| День рождения | Сегодня день рождения Михаила. | Heute hat Michail Geburtstag. |

**Предупреждение:** если имя не записано в голосовом словаре, объявлять нейтральное «Напоминание о дне рождения» / „Geburtstagserinnerung“ и показывать имя текстом на OLED; не подменять неизвестные имена произвольным файлом.

## 3. План обязательных токенов (записывать в каждом голосовом пакете)

1. `numbers/cardinal`: 0..59 (минимум), 60..100 и разряды/сотни для процентов, лет, давления, температур. Немецкие числительные должны быть проверены на составные формы `einundzwanzig`, `zweiundvierzig` и т.д.
2. `numbers/ordinal_timer`: RU первый/второй/третий, DE eins/zwei/drei или erste/zweite/dritte в согласованном синтаксисе.
3. `numbers/alarm`: 1..5; `numbers/birthday`: 1..15 (номер события), при необходимости возраст 0..120.
4. `units/duration`: RU `час/часа/часов`, `минуту/минуты/минут`, `секунду/секунды/секунд`, а для «осталось» `час/часа/часов`, `минута/минуты/минут`, `секунда/секунды/секунд`. DE `eine Stunde/Stunden`, `eine Minute/Minuten`, `eine Sekunde/Sekunden`.
5. `calendar/weekdays`: семь полных дней недели в обоих языках. `calendar/months`: 12 месяцев (RU родительный: января, февраля...), DE именительные January->Januar и т.д. `calendar/day_ordinal`: RU `первое...тридцать первое`, DE `erste...einunddreißigste` в контексте „der ...“; отдельные формы после `am` (ersten...) если используется такой шаблон.
6. `time`: `Uhr`, `ровно`, `полночь`, `сейчас`, `Es ist`, фиксированные фразы 00:00, 01:00; в RU 24-часовая форма времени.
7. `weather`: `минус`, `градус/градуса/градусов`, `Prozent`, `Hektopascal`, категория погоды, давность; погодные данные только если свежие.
8. `ui`: подключения Wi-Fi/BT, меню, ошибки SD, голос/звук, аккумулятор, резервные озвученные уведомления (если карта доступна).

**Грамматика - программное правило, не файловая магия.** Например RU после `на` для 1 -> `одну минуту`, для 2/3/4 -> `две/три/четыре минуты`, для 5/11/14/25 -> `пять/одиннадцать/четырнадцать/двадцать пять минут`. Проверить формы 1, 2, 5, 11, 12, 14, 21, 22, 25 и 101 для нескольких единиц. Если решение основано на заранее записанных числительных, нельзя произвольно склеивать несовместимые формы и падежи.

## 4. Аудиофайлы и формат

- Путь: `/PI2CLOCK/voices/<language>/<voice_id>/phrases/<event_id_as_filename>.wav` для целых сообщений без переменных; например `system.ready.wav`. Для событий с параметрами - `templates/<event_id>.json` плюс токены `tokens/...` по именам.
- **Не копировать** старые `01/001.mp3`, `17/013.mp3` наугад. Их соответствие тексту без прослушивания неизвестно.
- Рекомендуется одинаковый mono PCM WAV 16-bit 16 или 24 кГц для коротких фраз и токенов, если реальный тракт поддерживает это с минимальными паузами; MP3 допустим для музыки и длинных фраз. Решение о частоте проверить тестами I2S/BT.
- Все 12 голосов должны иметь единые идентификаторы событий, уровни громкости и нормализованную динамику; проверить лицензии на синтез и распространение готовых записей в наборах.
- `voice.json` и `manifest.json` описывают реально установленные пакеты, версию схемы, формат, контрольные суммы. При отсутствии аудиофайла - текст на OLED и резервный системный сигнал из Flash, не случайный трек.

## 5. Приоритеты оповещений

Будильник / истёкший таймер -> обязательная индикация и, если разрешено настройками, звуковое событие -> остальные речевые статусы -> музыка. Не включать сетевое озвучивание как обязательный источник. В тихом режиме OLED и WS2812 обязательны; политика звучания будильника задаётся отдельно. Невоспроизведённые сообщения очереди не должны теряться при занятости аудиотракта.

## 6. Тест-кейсы записи для звукорежиссёра

- RU/DE 00:00, 01:01, 02:02, 05:05, 14:14, 23:59; дата 1,2,5,21,31 и годы 2027,2030,2099.
- T1=14 минут, T2=1 минута, T3=01:02:03; одновременный финиш и подтверждение отдельного таймера.
- День рождения с именем в словаре и без него; 5 будильников; выбор голоса из 6 на язык.
- Wi-Fi нет, NTP давно не был, SD извлечена, потерян BT, низкий аккумулятор, нет ответа погодного API.
- Музыка играет и её прерывает речь; переключение стерео BT -> моно local; отсутствие перезапуска трека после уведомления.

## 7. Связанные файлы

- `Pi2Clock_G2_VOICE_PHRASES_RU_DE.csv` - машиночитаемый каталог всех событий RU/DE; удобен для генерации аудио.
- `Pi2Clock_G2_SD_LAYOUT.md` - спецификация папок и примеры манифестов.
- `Pi2Clock_G2_WIRING_AND_ASSEMBLY.md` - подключение модулей.
