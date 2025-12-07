# pzn999.github.io

📄 Documentazione: Trade Calculator – HTML Tool per Trading
Nome progetto: Trade Calculator
Versione: 1.0
Autore: Utente (con supporto AI)
Data: Dicembre 2025
Piattaforma: Web (HTML5 + JavaScript), eseguibile su qualsiasi browser moderno (Chrome, Edge, Firefox, Safari) su Android, Windows, macOS, iOS.

🎯 Scopo del progetto
Fornire uno strumento offline, leggero e immediato per:

Incollare un segnale di trading (da Telegram, WhatsApp, ecc.)
Calcolare automaticamente:
Lots (dimensione della posizione)
Pips per SL, TP1, TP2, TP3
Profit/Loss in USD per ogni livello
Visualizzare i risultati in un layout chiaro, colorato e professionale
✅ Nessuna connessione internet richiesta (se usato da file locale)
✅ Zero dipendenze esterne (nessuna libreria, solo JavaScript nativo)

📥 Input atteso
Il testo da incollare deve seguire questo formato (righe non necessariamente consecutive, ma obbligatorie):

123456
[Emoji] [BUY/SELL] [Ordine] [SIMBOLO]
📊 ENTRY: [valore]
💰TP1: [valore]
💰TP2: [valore]
💰TP3: [valore]     ← opzionale
✋ SL : [valore]
✅ Esempio valido:
123456789
✅ SELL LIMIT BTCUSD

📊 ENTRY: 47990

💰TP1: 47840
💰TP2: 47500
💰TP3: 47000

✋ SL : 48105
🔑 Regole di parsing:
Simbolo: estratto come ultima parola della prima riga oppure cercato tra i simboli noti (BTCUSD, ETHUSD, US500, ecc.)
ENTRY, SL, TP1, TP2: obbligatori
TP3: opzionale (appare solo se presente)
Numeri: supportano:
Punto (.) come separatore delle migliaia → 12.345 → 12345
Virgola (,) come separatore decimale → 1234,5 → 1234.5
📤 Output prodotto
Tabella con le seguenti righe:

Campo
Descrizione
Lots
Dimensione della posizione calcolata in base al rischio
Entry
Prezzo di entrata
TP1 pips
Distanza in pips + (profitto in $)
TP2 pips
Distanza in pips + (profitto in $)
TP3 pips
(solo se presente) Distanza in pips + (profitto in $)
SL pips
Distanza in pips + (perdita in $)
✅ Regole di calcolo:
Pips: sempre valore assoluto, arrotondato all’intero
PL (Profit/Loss):
SL: sempre negativo (perdita)
TP1/2/3: sempre positivo (profitto)
Arrotondato all’intero, senza segno +
Formula Lots:
1
⚙️ Configurazione: Simboli supportati
La tabella SYMBOL_CONFIG definisce, per ogni simbolo:

UnitsPerLot: dimensione del lotto (es. 100 per XAUUSD)
PipsPerPrezzo: quanti "pips" corrispondono a 1 punto di prezzo
Simbolo
UnitsPerLot
PipsPerPrezzo
Note
XAUUSD
100
100
Oro
EURUSD
100000
10000
Forex
BTCUSD
1
10
Bitcoin
ETHUSD
1
10
Ethereum
US500
1
1
S&P 500
US100
1
1
NASDAQ 100
US30
1
1
Dow Jones
🔧 Per aggiungere un nuovo simbolo, modificare SYMBOL_CONFIG:

js
1
"NUOVO_SIMBOLO": { UnitsPerLot: X, PipsPerPrezzo: Y }
🎨 Interfaccia utente
Elementi:
Campo "Rischio (USD)"
Precompilato a 1250
Modificabile (min: 1, step: 50)
Bottone "Incolla e Calcola"
Funziona su HTTPS o con permesso utente
Su Android da file: mostra istruzioni per incolla manuale
Bottone "Pulisci"
Svuota input e output
Textarea
Per incolla manuale (utile su desktop)
Tabella output
Colori soft:
Entry: verde chiaro (#e8f5e9)
TP: azzurro chiaro (#e3f2fd)
SL: arancio chiaro (#fff3e0)
🛠️ Manutenzione e personalizzazione
🔧 File principale:
Nome file: trade-calculator.html
Formato: HTML5 + inline CSS + JavaScript
Nessun file esterno: tutto incluso in un unico file
✏️ Come modificare:
Modifica desiderata
File da editare
Sezione
Cambiare rischio predefinito
HTML
<input id="risk" value="1250">
Aggiungere simbolo
JavaScript
SYMBOL_CONFIG
Cambiare colori
HTML/CSS
bgColorEntry, bgColorTP, bgColorSL
Modificare formula
JavaScript
processText()
Cambiare layout
HTML
struttura <table> in processText()
💡 Suggerimenti per evoluzione:
Aggiungere esportazione in clipboard del risultato
Salvare l’ultimo rischio usato in localStorage
Supporto per multi-simbolo in un unico file
Versione PWA con icona e installazione
⚠️ Limitazioni note
Piattaforma
Limitazione
Soluzione alternativa
Android + file://
navigator.clipboard non funziona
Incolla manualmente con "tocco lungo → Incolla"
iOS Safari
Clipboard API limitata
Incolla manuale
Numeri molto grandi
Potenziale overflow
Usare BigInt (non necessario per trading normale)
✅ Workaround universale: incolla manualmente nel campo di testo → clicca "Calcola dal testo"

📦 Distribuzione
Opzioni:
File locale (file://)
Salva come .html → apri con Chrome
✅ Offline, ✅ immediato, ❌ clipboard automatica non funziona su mobile
GitHub Pages (consigliato per Android)
Carica su repo pubblica → URL HTTPS
✅ Clipboard automatica funziona ovunque
Aggiungi a Home (PWA)
In Chrome: Menu → "Aggiungi alla home"
Si comporta come un’app
📜 Licenza
Questo strumento è open-source e può essere:

Usato liberamente
Modificato
Condiviso
Attribuzione apprezzata ma non obbligatoria.

📞 Supporto
In caso di:

Formato input non riconosciuto
Simbolo mancante
Calcoli errati
Verifica:

Che il simbolo sia in SYMBOL_CONFIG
Che ogni riga termini con un numero
Che non ci siano caratteri strani (es. spazi non breaking)
Per assistenza, controlla la console del browser (F12) o invia un esempio di input che non funziona.
