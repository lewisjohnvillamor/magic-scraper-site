"""Pages for people scraping sites that are not in English: an English hub and
one page each in Japanese, German, Spanish and French, linked by hreflang.

Every site named here was run through the extension before the page was
written (see each page's "tried" section), and anything that arrives with an
update not yet in the stores is marked with a dagger and the update's name.
"""

HUB = "scrape-websites-in-other-languages"
JA = "scraper-japanese-websites"
DE = "web-scraper-deutsche-websites"
ES = "web-scraper-sitios-en-espanol"
FR = "web-scraper-sites-francais"
ALTERNATES = [("en", HUB), ("ja", JA), ("de", DE), ("es", ES), ("fr", FR)]

LANG_LINKS = (f'<a href="/{JA}" hreflang="ja" lang="ja">日本語</a> &middot; '
              f'<a href="/{DE}" hreflang="de" lang="de">Deutsch</a> &middot; '
              f'<a href="/{ES}" hreflang="es" lang="es">Español</a> &middot; '
              f'<a href="/{FR}" hreflang="fr" lang="fr">Français</a> &middot; '
              f'<a href="/{HUB}" hreflang="en" lang="en">English</a>')


def language_pages(sec, claim, table):
    def soon(label):
        return f'<span class="soon">{label}</span>'

    # table() heads the first column itself (empty), so a head naming every
    # column drops its first name
    def words(rows):
        head = rows[0][1:] if len(rows[0]) == len(rows[1]) else rows[0]
        return table(head, [[r[0]] + [("", c) for c in r[1:]] for r in rows[1:]])

    pages = []

    # ------------------------------------------------------------ English hub
    s = soon("next update")
    pages.append(dict(
        slug=HUB,
        crumb="Other languages",
        title="Scraping websites in other languages: Next, Load more, Excel",
        desc="Why a scraper stops on page one of a Japanese, German or Spanish site, why Excel garbles the accents, and how Magic Scraper reads pagers in over 80 languages.",
        h1="Scraping a site that isn't in <i>English</i>.",
        standfirst="A scraper that finds the Next button by looking for the word &ldquo;Next&rdquo; stops at page one of a site that says 次へ, Weiter or Siguiente. A CSV opened in Excel can turn ü and 日本語 into gibberish, and a German 1.234 can arrive as one point two three four. Here is what goes wrong on sites in other languages, and what Magic Scraper does about each.",
        aside="Free, with no account. In your language: " + LANG_LINKS,
        alternates=ALTERNATES,
        sections=[
            sec("pager", "Page two, in any language", "\n".join([
                claim("Most big sites mark their Next button in ways that do not depend on the language: a "
                      "<code>rel=\"next\"</code> link, an arrow, an <code>aria-label</code>, a numbered pager. "
                      "Magic Scraper reads all of those, which is why Amazon.co.jp, Kleinanzeigen and LDLC crawl "
                      "the same as an English shop. The word only matters on sites that write nothing else, and "
                      "there it reads the word, in more than 80 languages, and the Load more button too."),
                words([["Next", "Load more"],
                       ["Japanese", "次へ &middot; 次のページ &middot; 次の20件 &middot; 次&dagger;", "もっと見る&dagger; &middot; さらに表示&dagger;"],
                       ["Chinese", "下一页 &middot; 下一頁 &middot; 后页&dagger;", "加载更多&dagger; &middot; 查看更多&dagger;"],
                       ["Korean", "다음", "더보기&dagger;"],
                       ["German", "Weiter &middot; Nächste &middot; Nächste Seite&dagger;", "Mehr laden&dagger; &middot; Weitere anzeigen&dagger;"],
                       ["Spanish", "Siguiente &middot; Página siguiente&dagger;", "Cargar más&dagger; &middot; Ver más&dagger;"],
                       ["French", "Suivant &middot; Page suivante&dagger;", "Voir plus&dagger; &middot; Charger plus&dagger;"],
                       ["Portuguese", "Próxima &middot; Seguinte", "Carregar mais&dagger; &middot; Ver mais&dagger;"],
                       ["Italian", "Prossima &middot; Successiva&dagger; &middot; Avanti&dagger;", "Mostra altri&dagger; &middot; Carica altri&dagger;"],
                       ["Dutch", "Volgende", "Meer laden&dagger;"],
                       ["Polish", "Następna &middot; Dalej", "Pokaż więcej&dagger;"],
                       ["Russian", "Следующая&dagger; &middot; Далее&dagger;", "Показать ещё&dagger;"],
                       ["Turkish", "Sonraki &middot; Sonraki sayfa&dagger;", "Daha fazla göster&dagger;"],
                       ["Swedish", "Nästa&dagger; &middot; Nästa sida&dagger;", "Visa fler&dagger;"],
                       ["Indonesian", "Berikutnya &middot; Halaman berikutnya&dagger;", "Muat lebih banyak&dagger;"],
                       ["Vietnamese", "Tiếp &middot; Sau &middot; Trang sau&dagger;", "Xem thêm&dagger;"],
                       ["Thai", "ถัดไป &middot; หน้าถัดไป", "โหลดเพิ่มเติม&dagger;"],
                       ["Arabic", "التالي&dagger; &middot; الصفحة التالية&dagger;", "تحميل المزيد&dagger;"],
                       ["Hebrew", "הבא&dagger; &middot; העמוד הבא&dagger;", "טען עוד&dagger;"],
                       ["Hindi", "अगला&dagger; &middot; अगला पेज&dagger;", "और देखें&dagger;"]]),
                claim(f"&dagger; With the next update, 2.0.8 {s}. The rest is in the stores now. In all, Next and Previous are "
                      "read in 87 languages and Load more in about 68: every major European language, and Turkish, "
                      "Azerbaijani, Indonesian, Malay, Filipino, Vietnamese, Swahili, Arabic, Persian, Urdu, Hebrew, "
                      "the languages of India from Hindi and Bengali to Tamil and Malayalam, Sinhala, Thai, Lao, "
                      "Khmer, Burmese, Georgian, Armenian and Amharic. Previous-page words are read too, so Zurück, "
                      "Anterior or 前へ is never taken for Next. And outside Latin script the word has to come first, "
                      "so 目次 (&ldquo;contents&rdquo;), Читать далее (&ldquo;read more&rdquo;) and आगे पढ़ें (&ldquo;read "
                      "on&rdquo;) are never taken for it either."),
            ])),
            sec("excel", "Accents and kanji that turn to gibberish in Excel", claim(
                "Excel guesses a CSV file's encoding, and without a hint it guesses wrong: Müller becomes "
                "MÃ¼ller and 東京 becomes æ±äº¬. Magic Scraper's CSV starts with the byte-order mark that tells "
                "Excel the file is UTF-8, so the letters arrive as the page wrote them. The Excel (.xlsx) "
                "export avoids the question altogether, and Google Sheets reads either.",
                "A CSV from another tool that is already garbled can be rescued: in Excel, use "
                "<b>Data &rarr; From Text/CSV</b> and set File origin to <b>65001: Unicode (UTF-8)</b>.")),
            sec("numbers", "1.234 is not one point two three four", claim(
                "Most of Europe writes 1.234,56 where English writes 1,234.56, and France writes 1 234,56. A "
                "spreadsheet that reads the dot as a decimal point turns a German table's 1.234 (one thousand "
                "two hundred and thirty-four) into 1.234, a thousand times too small, with nothing to say so.",
                f"From the next update {s}, the Excel export looks at the whole column. When it shows European "
                "signs (83.200.000, 12,50, 1.234,56) every value is read that way, so the column sums. Thousands "
                "written apart with a space, the French way, are read in any column. A column of nothing but "
                "1.234-style values could be either, so it stays text: never wrong, only not summable. The CSV "
                "keeps every value exactly as the page wrote it.")),
            sec("columns", "Column names stay in the page's language", claim(
                "A table's own headers come through as written: 価格, Preis, Precio. Where a page has no "
                "headers, columns are named from the markup, and those names are English: Price, Link, Image. "
                "Double-click a header in the popup, or press F2, to rename it; the name is remembered for that "
                "site.",
                "The extension's own buttons and messages are in English. The data never is.")),
            sec("tried", "Tried on", claim(
                "Before this page was written, the extension ran on Amazon.co.jp search, 価格.com, Yahoo!ニュース "
                "and はてなブックマーク; Kleinanzeigen, Chefkoch, heise online and Gelbe Seiten; Allociné, Marmiton "
                "and LDLC; and the German, Spanish and French Wikipedias. Some sites showed a &ldquo;prove you're "
                "human&rdquo; check instead. On those it stops and hands you the tab, and never tries to get past "
                "the check.",
                "In your language: " + LANG_LINKS + ".")),
        ],
        faq=[
            ("Why does my scraper stop at page one on a Japanese or German site?",
             "Many scrapers find the next page by looking for the English word Next. Magic Scraper also reads rel=\"next\" links, arrows, aria-labels and numbered pagers, and the word for Next in more than 80 languages."),
            ("Why are the accents wrong when I open the CSV in Excel?",
             "Excel guessed the wrong encoding. Magic Scraper's CSV carries the byte-order mark that tells Excel it is UTF-8, and its .xlsx export avoids the problem altogether."),
            ("Does it work on right-to-left sites in Arabic or Hebrew?",
             "Yes. It reads the page's structure, not its direction, and from the next update it reads التالي and הבא as Next."),
            ("Is Magic Scraper available in my language?",
             "The extension's buttons are in English. The data it collects stays in the language of the page."),
        ],
    ))

    # ------------------------------------------------------------ Japanese
    s = soon("次回アップデート")
    pages.append(dict(
        slug=JA,
        crumb="日本語サイト",
        eyebrow="ガイド",
        title="日本語サイトのスクレイピング：「次へ」「もっと見る」と文字化け",
        desc="スクレイピングツールが日本語サイトの1ページ目で止まる理由、CSVをExcelで開くと文字化けする理由、そしてMagic Scraperが「次へ」や「もっと見る」をどう見つけるかを説明します。",
        h1="日本語のサイトも、<i>最後のページ</i>まで。",
        standfirst="英語の「Next」という文字でページ送りを探すツールは、「次へ」としか書かれていないサイトでは1ページ目で止まります。CSVをExcelで開くと、「東京」が「æ±äº¬」に化けることもあります。日本語のサイトで起きやすい問題と、Magic Scraperでの扱いをまとめました。",
        aside="無料、アカウント登録は不要です。",
        ui=dict(lang="ja", locale="ja_JP", skip="本文へスキップ", install="Chrome に追加（無料）",
                edge="Edge に追加", faq="よくある質問"),
        alternates=ALTERNATES,
        sections=[
            sec("pager", "2ページ目以降も取得する", "\n".join([
                claim("大きなサイトの多くは、言語に関係なく見分けられる形でページ送りを置いています。"
                      "<code>rel=\"next\"</code>、矢印のアイコン、<code>aria-label</code>、番号付きのページャーです。"
                      "Magic Scraperはそのすべてを読むので、Amazon.co.jpや価格.comでも英語のサイトと同じようにページをたどれます。"
                      "文字だけのボタンでは、その言葉を読みます。"),
                words([["種類", "認識する表記"],
                       ["次のページ", "次へ &middot; 次のページ &middot; 次の20件 &middot; 次&dagger;"],
                       ["続きを読み込む", "もっと見る&dagger; &middot; さらに表示&dagger; &middot; もっと読み込む&dagger;"],
                       ["前のページ（次と取り違えない）", "前へ &middot; 前のページ"],
                       ["ページ送りと見なさないもの", "目次 &middot; 画像スライダーの矢印&dagger; &middot; 注釈の番号&dagger;"]]),
                claim(f"&dagger; は次回アップデート（2.0.8）から {s}。そのほかは現在ストアで配信中の版で動作します。"
                      "中国語の「下一页」「后页」、韓国語の「다음」「더보기」も読み、全部で80以上の言語のページ送りに対応します&dagger;。"),
            ])),
            sec("excel", "Excelで開くと文字化けする", claim(
                "ExcelはCSVファイルの文字コードを推測し、手がかりがないと読み違えます。"
                "Magic ScraperのCSVはBOM付きのUTF-8で保存されるので、ダブルクリックで開いても日本語がそのまま表示されます。"
                "Excel形式（.xlsx）で書き出せば文字コードの問題自体が起きず、Googleスプレッドシートはどちらも正しく読みます。",
                "ほかのツールで化けてしまったCSVは、Excelの<b>［データ］&rarr;［テキストまたはCSVから］</b>で、"
                "元のファイルを<b>「65001: Unicode (UTF-8)」</b>にすると読み直せます。")),
            sec("columns", "列名と数値", claim(
                "表に見出しがあれば、「価格」「商品名」のようにそのまま列名になります。"
                "見出しのないリストでは、ページの構造から英語の列名（Price、Link、Image など）が付きます。"
                "ポップアップで見出しをダブルクリック（またはF2キー）すると名前を変えられ、サイトごとに記憶されます。",
                "「1,280」のような数字はExcel形式で書き出すと数値になり、合計できます。"
                "「¥1,280」や「2026年10月29日」のように記号や単位の付いた値は、ページの表記のまま文字として残ります。",
                "拡張機能のボタンや表示は英語です。取得するデータは、ページの言語のままです。")),
            sec("tried", "試したサイト", claim(
                "このページを書く前に、Amazon.co.jpの検索結果、価格.comの製品一覧、Yahoo!ニュースのアクセスランキング、"
                "はてなブックマークの人気エントリーで動作を確かめました。",
                "「ロボットではありません」などの確認が表示されたページでは処理を止め、タブをお返しします。確認を回避することはありません。"
                "サイトの利用規約で収集が認められているかは、ご自身でご確認ください。",
                "ほかの言語：" + LANG_LINKS)),
        ],
        faq=[
            ("スクレイピングツールが日本語サイトの1ページ目で止まるのはなぜですか？",
             "多くのツールは英語の「Next」という文字でページ送りを探します。Magic Scraperは「次へ」「次のページ」などの日本語に加え、矢印、rel=\"next\"、番号付きのページャーも読みます。"),
            ("CSVの文字化けを防ぐには？",
             "Magic ScraperのCSVはBOM付きのUTF-8なので、Excelでそのまま開けます。Excel形式（.xlsx）で書き出せば、文字コードの問題は起きません。"),
            ("日本語版はありますか？",
             "拡張機能の表示は英語のみです。データは日本語のまま取得できます。"),
            ("無料で使えますか？",
             "はい。表の検出、ページ数無制限のクロール、CSV・Excel・JSONの書き出しは無料です。各行のリンク先を開いて項目を追加する「ドリルダウン」は、無料版では3行まで、Pro（25ドルの買い切り）では全行に使えます。"),
        ],
    ))

    # ------------------------------------------------------------ German
    s = soon("nächstes Update")
    pages.append(dict(
        slug=DE,
        crumb="Deutsche Websites",
        eyebrow="Ratgeber",
        title="Web Scraper für deutsche Websites: Weiter, Mehr laden, Excel",
        desc="Warum Scraper auf deutschen Seiten nach Seite 1 aufhören, warum Umlaute in Excel kaputtgehen und warum 1.234 nicht 1,234 ist, und wie Magic Scraper das löst.",
        h1="Deutsche Seiten, <i>bis zur letzten</i>.",
        standfirst="Ein Scraper, der den Weiter-Link am englischen Wort &bdquo;Next&ldquo; erkennt, bleibt auf einer Seite mit &bdquo;Nächste Seite&ldquo; oder &bdquo;Mehr laden&ldquo; hängen. In Excel wird aus Müller schnell MÃ¼ller, und aus 1.234 die Zahl eins Komma zwei drei vier. Was auf deutschsprachigen Seiten schiefgeht, und was Magic Scraper dagegen tut.",
        aside="Kostenlos, ohne Konto.",
        ui=dict(lang="de", locale="de_DE", skip="Zum Inhalt springen", install="Für Chrome installieren &ndash; kostenlos",
                edge="Für Edge installieren", faq="Häufige Fragen"),
        alternates=ALTERNATES,
        sections=[
            sec("pager", "Seite 2, Seite 3, bis zum Ende", "\n".join([
                claim("Große Seiten kennzeichnen ihre Blätter-Links meist so, dass die Sprache keine Rolle spielt: "
                      "<code>rel=\"next\"</code>, ein Pfeil, ein <code>aria-label</code>, nummerierte Seiten. Magic Scraper "
                      "liest all das, deshalb blättert es bei Kleinanzeigen und Chefkoch genauso wie in einem englischen "
                      "Shop. Wo nur das Wort dasteht, liest es das Wort:"),
                words([["Art", "Erkannte Beschriftung"],
                       ["Nächste Seite", "Weiter &middot; Nächste &middot; Nächste Seite&dagger;"],
                       ["Nachladen", "Mehr laden&dagger; &middot; Mehr anzeigen&dagger; &middot; Weitere anzeigen&dagger; &middot; Weitere Ergebnisse&dagger;"],
                       ["Zurück (nie für Weiter gehalten)", "Zurück &middot; Vorherige"],
                       ["Kein Blättern", "Pfeile von Bildergalerien&dagger; &middot; Fußnotennummern&dagger;"]]),
                claim(f"&dagger; Ab dem nächsten Update, 2.0.8 {s}. Alles andere steckt schon in der Version, die "
                      "die Stores gerade ausliefern. Insgesamt erkennt es Blätter-Links in mehr als 80 Sprachen&dagger;."),
            ])),
            sec("excel", "Umlaute, die in Excel kaputtgehen", claim(
                "Excel rät die Kodierung einer CSV-Datei, und ohne Hinweis rät es falsch: aus Müller wird MÃ¼ller, "
                "aus Straße StraÃŸe. Die CSV von Magic Scraper beginnt mit der Byte-Order-Mark, an der Excel UTF-8 "
                "erkennt; Umlaute und ß kommen an, wie sie auf der Seite stehen. Der Excel-Export (.xlsx) kennt das "
                "Problem gar nicht, und Google Tabellen liest beides.",
                "Eine schon verdorbene CSV aus einem anderen Tool öffnen Sie über <b>Daten &rarr; Aus Text/CSV</b> "
                "mit dem Dateiursprung <b>65001: Unicode (UTF-8)</b>.")),
            sec("numbers", "1.234 ist nicht 1,234", claim(
                "Im Deutschen trennt der Punkt die Tausender und das Komma die Dezimalstellen. Wer 1.234 als "
                "Dezimalzahl liest, macht aus eintausendzweihundertvierunddreißig eins Komma zwei drei vier, "
                "ohne jede Warnung.",
                f"Ab dem nächsten Update {s} schaut der Excel-Export auf die ganze Spalte. Zeigt sie deutsche "
                "Schreibweise (83.200.000, 12,50, 1.234,56), wird jeder Wert so gelesen, und die Spalte lässt sich "
                "summieren. Eine Spalte nur aus Werten wie 1.234 könnte beides sein; sie bleibt Text: nie falsch, "
                "nur nicht summierbar. Die CSV behält jeden Wert genau so, wie die Seite ihn schreibt.")),
            sec("columns", "Spaltennamen", claim(
                "Hat eine Tabelle Überschriften, werden sie übernommen: Preis, Ort, Telefon. Ohne Überschriften "
                "benennt Magic Scraper die Spalten nach dem Seitenaufbau, und diese Namen sind englisch (Price, "
                "Link, Image). Ein Doppelklick auf die Überschrift im Popup, oder F2, benennt sie um; der Name wird "
                "für die Website gespeichert.",
                "Die Oberfläche der Erweiterung ist englisch. Die Daten bleiben deutsch.")),
            sec("tried", "Ausprobiert", claim(
                "Bevor diese Seite entstand, lief die Erweiterung auf Kleinanzeigen, Chefkoch, dem Newsticker von "
                "heise online, Gelbe Seiten und der deutschen Wikipedia.",
                "Fragt eine Seite, ob Sie ein Mensch sind, hält der Lauf an und gibt Ihnen den Tab; er versucht nie, "
                "die Prüfung zu umgehen. Ob eine Seite das Auslesen erlaubt, regeln ihre Nutzungsbedingungen, und "
                "bei personenbezogenen Daten gilt die DSGVO.",
                "Andere Sprachen: " + LANG_LINKS)),
        ],
        faq=[
            ("Warum hört mein Scraper auf deutschen Seiten nach Seite 1 auf?",
             "Viele Scraper suchen die nächste Seite am englischen Wort Next. Magic Scraper liest außerdem rel=\"next\", Pfeile, aria-labels und nummerierte Seiten, und Weiter, Nächste und, ab dem nächsten Update, Nächste Seite und Mehr laden."),
            ("Wie verhindere ich kaputte Umlaute in Excel?",
             "Die CSV von Magic Scraper trägt die Byte-Order-Mark, an der Excel UTF-8 erkennt. Der Excel-Export (.xlsx) hat das Problem gar nicht."),
            ("Warum stimmen die Zahlen in Excel nicht?",
             "Weil 1.234 als Dezimalzahl gelesen wurde. Ab dem nächsten Update liest der Excel-Export von Magic Scraper eine Spalte in deutscher Schreibweise auch so."),
            ("Ist das DSGVO-konform?",
             "Magic Scraper schickt die Daten nirgendwohin: Erkennung, Blättern und Export laufen in Ihrem Browser, und es gibt keinen Server von uns. Ob Sie personenbezogene Daten erheben und verwenden dürfen, hängt davon ab, was Sie damit tun, und bleibt Ihre Verantwortung."),
            ("Gibt es Magic Scraper auf Deutsch?",
             "Die Oberfläche ist englisch. Die gesammelten Daten bleiben in der Sprache der Seite."),
        ],
    ))

    # ------------------------------------------------------------ Spanish
    s = soon("próxima actualización")
    pages.append(dict(
        slug=ES,
        crumb="Sitios en español",
        eyebrow="Guía",
        title="Web scraper para sitios en español: Siguiente y Cargar más",
        desc="Por qué un scraper se queda en la página 1 de un sitio en español, por qué Excel estropea las tildes y la ñ, y cómo Magic Scraper halla Siguiente y Cargar más.",
        h1="Sitios en español, <i>hasta la última página</i>.",
        standfirst="Una herramienta que busca el botón de paginación por la palabra inglesa &laquo;Next&raquo; se detiene en la página 1 de un sitio que dice &laquo;Página siguiente&raquo; o &laquo;Cargar más&raquo;. Y al abrir el CSV en Excel, &laquo;España&raquo; puede convertirse en &laquo;EspaÃ±a&raquo;. Esto es lo que falla en los sitios en español, y lo que hace Magic Scraper en cada caso.",
        aside="Gratis, sin cuenta.",
        ui=dict(lang="es", locale="es_ES", skip="Saltar al contenido", install="Instalar en Chrome, gratis",
                edge="Instalar en Edge", faq="Preguntas frecuentes"),
        alternates=ALTERNATES,
        sections=[
            sec("pager", "La página 2, y la 3, hasta el final", "\n".join([
                claim("Los sitios grandes suelen marcar la paginación de una forma que no depende del idioma: "
                      "<code>rel=\"next\"</code>, una flecha, un <code>aria-label</code>, páginas numeradas. Magic Scraper "
                      "lee todo eso. Cuando el botón solo tiene texto, lee la palabra:"),
                words([["Tipo", "Texto que reconoce"],
                       ["Página siguiente", "Siguiente &middot; Página siguiente&dagger;"],
                       ["Cargar más resultados", "Cargar más&dagger; &middot; Ver más&dagger; &middot; Mostrar más&dagger; &middot; Más resultados&dagger;"],
                       ["Anterior (nunca se toma por Siguiente)", "Anterior"],
                       ["No es paginación", "Flechas de galerías de fotos&dagger; &middot; Números de notas&dagger;"]]),
                claim(f"&dagger; Con la próxima actualización, 2.0.8 {s}. Lo demás ya está en la versión que "
                      "distribuyen las tiendas. En total reconoce la paginación en más de 80 idiomas&dagger;."),
            ])),
            sec("excel", "Tildes y eñes que Excel estropea", claim(
                "Excel adivina la codificación de un CSV, y sin una pista se equivoca: &laquo;España&raquo; se convierte "
                "en &laquo;EspaÃ±a&raquo;. El CSV de Magic Scraper empieza con la marca de orden de bytes (BOM) que le "
                "indica a Excel que es UTF-8, así que las tildes y la ñ llegan como están en la página. La exportación "
                "a Excel (.xlsx) no tiene el problema, y Google Sheets lee ambos.",
                "Un CSV de otra herramienta que ya llegó estropeado se recupera en Excel con <b>Datos &rarr; Desde el "
                "texto/CSV</b>, eligiendo como origen del archivo <b>65001: Unicode (UTF-8)</b>.")),
            sec("numbers", "1.234 no es uno coma dos", claim(
                "En España y en buena parte de Sudamérica se escribe 1.234,56; en México y Centroamérica, 1,234.56. "
                "Una hoja de cálculo que toma el punto como decimal convierte 1.234 (mil doscientos treinta y "
                "cuatro) en 1,234, mil veces menos, sin avisar.",
                f"Desde la próxima actualización {s}, la exportación a Excel mira la columna entera. Si muestra el "
                "formato europeo (83.200.000, 12,50, 1.234,56), lee cada valor así y la columna se puede sumar. Una "
                "columna formada solo por valores como 1.234 podría ser cualquiera de los dos, así que se queda como "
                "texto: nunca incorrecta, solo no sumable. El CSV guarda cada valor tal como lo escribe la página.")),
            sec("columns", "Nombres de columna", claim(
                "Si la tabla tiene encabezados, se usan tal cual: Precio, Ciudad, Teléfono. Si no los tiene, Magic "
                "Scraper nombra las columnas según la estructura de la página, y esos nombres están en inglés "
                "(Price, Link, Image). Haz doble clic en el encabezado en la ventana de la extensión, o pulsa F2, "
                "para cambiarlo; el nombre se recuerda para ese sitio.",
                "Los botones de la extensión están en inglés. Los datos, en el idioma de la página.")),
            sec("tried", "Probado en", claim(
                "Antes de escribir esta página la probamos en la Wikipedia en español: sus 544 municipios en una "
                "sola tabla, con los encabezados de la página. Algunos sitios mostraron una comprobación de "
                "&laquo;¿eres humano?&raquo;: ahí la extensión se detiene y te devuelve la pestaña, sin intentar "
                "saltársela nunca.",
                "Otros idiomas: " + LANG_LINKS)),
        ],
        faq=[
            ("¿Por qué mi scraper se queda en la página 1 de un sitio en español?",
             "Muchas herramientas buscan la página siguiente por la palabra inglesa Next. Magic Scraper también lee rel=\"next\", flechas, aria-labels y páginas numeradas, además de Siguiente y, desde la próxima actualización, Página siguiente y Cargar más."),
            ("¿Cómo evito que Excel estropee las tildes?",
             "El CSV de Magic Scraper lleva la marca BOM que indica a Excel que es UTF-8. La exportación a Excel (.xlsx) no tiene el problema."),
            ("¿Por qué los números salen mal en Excel?",
             "Porque 1.234 se leyó como decimal. Desde la próxima actualización, la exportación a Excel de Magic Scraper lee una columna en formato europeo como tal."),
            ("¿Magic Scraper está en español?",
             "Los botones de la extensión están en inglés. Los datos se quedan en el idioma de la página."),
        ],
    ))

    # ------------------------------------------------------------ French
    s = soon("prochaine mise à jour")
    pages.append(dict(
        slug=FR,
        crumb="Sites en français",
        eyebrow="Guide",
        title="Web scraper pour sites en français : Suivant, Voir plus, Excel",
        desc="Pourquoi un scraper s’arrête à la page 1 d’un site français, pourquoi Excel abîme les accents, et comment Magic Scraper trouve Page suivante et Voir plus.",
        h1="Les sites français, <i>jusqu’à la dernière page</i>.",
        standfirst="Un outil qui cherche le bouton de pagination grâce au mot anglais &laquo;&nbsp;Next&nbsp;&raquo; s’arrête à la page 1 d’un site qui écrit &laquo;&nbsp;Page suivante&nbsp;&raquo; ou &laquo;&nbsp;Voir plus&nbsp;&raquo;. Et dans Excel, &laquo;&nbsp;Café&nbsp;&raquo; peut devenir &laquo;&nbsp;CafÃ©&nbsp;&raquo;. Voici ce qui coince sur les sites francophones, et ce que fait Magic Scraper à chaque fois.",
        aside="Gratuit, sans compte.",
        ui=dict(lang="fr", locale="fr_FR", skip="Aller au contenu", install="Installer pour Chrome, gratuit",
                edge="Installer pour Edge", faq="Questions fréquentes"),
        alternates=ALTERNATES,
        sections=[
            sec("pager", "La page 2, la 3, jusqu’au bout", "\n".join([
                claim("Les grands sites marquent le plus souvent leur pagination d’une façon qui ne dépend pas de la "
                      "langue&nbsp;: <code>rel=\"next\"</code>, une flèche, un <code>aria-label</code>, des pages numérotées. "
                      "Magic Scraper lit tout cela&nbsp;; c’est pourquoi il parcourt LDLC, Marmiton ou Allociné comme une "
                      "boutique anglaise. Quand le bouton n’a que du texte, il lit le mot&nbsp;:"),
                words([["Type", "Texte reconnu"],
                       ["Page suivante", "Suivant &middot; Page suivante&dagger;"],
                       ["Charger la suite", "Voir plus&dagger; &middot; Charger plus&dagger; &middot; Afficher plus&dagger; &middot; Plus de résultats&dagger;"],
                       ["Précédent (jamais pris pour Suivant)", "Précédent"],
                       ["Pas une pagination", "Flèches des galeries photo&dagger; &middot; Numéros de notes&dagger;"]]),
                claim(f"&dagger; Avec la prochaine mise à jour, 2.0.8 {s}. Le reste est déjà dans la version que "
                      "distribuent les boutiques d’extensions. Au total, il reconnaît la pagination dans plus de 80 langues&dagger;."),
            ])),
            sec("excel", "Les accents qu’Excel abîme", claim(
                "Excel devine l’encodage d’un fichier CSV, et sans indice il se trompe&nbsp;: &laquo;&nbsp;Café&nbsp;&raquo; "
                "devient &laquo;&nbsp;CafÃ©&nbsp;&raquo;. Le CSV de Magic Scraper commence par la marque d’ordre des octets "
                "(BOM) qui indique à Excel qu’il s’agit d’UTF-8&nbsp;: les accents arrivent tels qu’ils sont sur la page. "
                "L’export Excel (.xlsx) n’a pas ce problème, et Google Sheets lit les deux.",
                "Un CSV déjà abîmé par un autre outil se récupère dans Excel avec <b>Données &rarr; À partir d’un "
                "fichier texte/CSV</b>, en choisissant l’origine <b>65001&nbsp;: Unicode (UTF-8)</b>.")),
            sec("numbers", "1 234,56, pas 1.23456", claim(
                "En France on écrit 1 234,56, en Belgique et en Allemagne souvent 1.234,56, et en anglais 1,234.56. "
                "Un tableur qui prend le point pour la virgule décimale transforme 1.234 (mille deux cent trente-quatre) "
                "en un virgule deux trois quatre, sans prévenir.",
                f"À partir de la prochaine mise à jour {s}, l’export Excel regarde la colonne entière. Les milliers "
                "séparés par une espace, à la française, sont lus partout&nbsp;; une colonne écrite 1.234,56 ou 12,50 "
                "est lue à l’européenne, et elle s’additionne. Une colonne faite uniquement de valeurs comme 1.234 "
                "pourrait être l’un ou l’autre&nbsp;: elle reste du texte, jamais fausse, seulement pas additionnable. Le "
                "CSV garde chaque valeur exactement comme la page l’écrit.")),
            sec("columns", "Noms de colonnes", claim(
                "Si le tableau a des en-têtes, ils sont repris tels quels&nbsp;: Prix, Ville, Téléphone. Sans en-têtes, "
                "Magic Scraper nomme les colonnes d’après la structure de la page, et ces noms sont en anglais (Price, "
                "Link, Image). Double-cliquez sur l’en-tête dans la fenêtre de l’extension, ou appuyez sur F2, pour le "
                "renommer&nbsp;; le nom est retenu pour ce site.",
                "Les boutons de l’extension sont en anglais. Les données restent en français.")),
            sec("tried", "Essayé sur", claim(
                "Avant d’écrire cette page, nous l’avons fait tourner sur Allociné, Marmiton, LDLC et Wikipédia en "
                "français. Certains sites affichent une vérification &laquo;&nbsp;êtes-vous humain&nbsp;?&nbsp;&raquo;&nbsp;: "
                "l’extension s’arrête alors et vous rend l’onglet, sans jamais chercher à la contourner. Les conditions "
                "d’utilisation du site disent si la collecte est permise, et le RGPD s’applique aux données personnelles.",
                "Autres langues&nbsp;: " + LANG_LINKS)),
        ],
        faq=[
            ("Pourquoi mon scraper s’arrête-t-il à la page 1 d’un site français ?",
             "Beaucoup d’outils cherchent la page suivante grâce au mot anglais Next. Magic Scraper lit aussi rel=\"next\", les flèches, les aria-labels et les pages numérotées, ainsi que Suivant et, à partir de la prochaine mise à jour, Page suivante et Voir plus."),
            ("Comment éviter que les accents soient abîmés dans Excel ?",
             "Le CSV de Magic Scraper contient la marque BOM qui indique à Excel qu’il s’agit d’UTF-8. L’export Excel (.xlsx) n’a pas ce problème."),
            ("Pourquoi les nombres sont-ils faux dans Excel ?",
             "Parce que 1.234 a été lu comme un nombre décimal. À partir de la prochaine mise à jour, l’export Excel de Magic Scraper lit une colonne au format européen comme telle."),
            ("Magic Scraper existe-t-il en français ?",
             "Les boutons de l’extension sont en anglais. Les données restent dans la langue de la page."),
        ],
    ))

    return pages
