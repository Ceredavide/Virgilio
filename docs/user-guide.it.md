# Usare Virgilio — guida per non-programmatori

> Lingua: [English](user-guide.md) · **Italiano** · [Deutsch](user-guide.de.md)

Virgilio è uno strato sopra Claude Code (o un altro assistente AI di programmazione) che ti guida passo dopo passo nella costruzione di un'app, senza presupporre che tu sappia programmare.

Questa guida non spiega come installare Virgilio (per quello vedi il README principale). Spiega cosa aspettarti da una sessione, come rispondere bene alle domande, e cosa Virgilio farà o rifiuterà di fare. Tempo di lettura: ~10 minuti.

## Cosa è Virgilio, in due paragrafi

Virgilio impone una regola semplice: **prima si decide cosa fa l'app, poi si scrive**. Niente codice prima che esista un documento (chiamato `SPEC.md`) che descrive in linguaggio piano cosa l'app fa, per chi, e con quali limiti. Quel documento sei tu a definirlo, attraverso una conversazione strutturata con l'assistente.

Una volta che la specifica esiste, Virgilio implementa l'app **un pezzettino completo alla volta** — una piccola funzionalità per volta — e dopo ogni pezzettino ti dice come provarla manualmente, conferma con te che funziona, e salva un punto di ripristino. Se qualcosa si rompe, si torna all'ultimo punto buono.

## Cosa succede nella prima sessione

Una prima sessione tipica dura 30-90 minuti e ha questa forma:

1. **Brain dump.** Virgilio ti chiederà di scrivere, con le tue parole, tutto quello che hai in mente per l'app — cosa fa, chi la usa, perché, come la immagini, cosa NON deve fare. Più scrivi qui, meno domande sentirai dopo.
2. **Domande mirate, una alla volta.** Su un argomento per turno (es. "su che dispositivo gira principalmente?", "ci sarà un login?"). Spesso con 3-4 opzioni A/B/C/D e una raccomandazione.
3. **Riepilogo della specifica.** Quando ha capito abbastanza, ti mostra un riassunto e ti chiede conferma esplicita prima di salvarlo come `SPEC.md`.
4. **Scelte tecniche di base.** Subito dopo, 2-3 alternative per dove l'app vivrà (Vercel per il web, Supabase per i dati, Expo per il mobile, …) con il default consigliato.
5. **Setup di base.** Se l'app salva dei dati, Virgilio ti farà creare un account su Supabase prima di scrivere codice (cinque minuti, una sola volta).
6. **Primo pezzettino.** Implementa una prima piccola feature, ti dice esattamente come provarla nel browser, ti chiede se funziona.

## Come rispondere bene

### Al brain dump
Più sei specifico, meglio è. Includi anche cose ovvie ("ovviamente serve un login") e cose che **non** vuoi ("non voglio notifiche push"). Esempi e situazioni concrete valgono più di descrizioni astratte: "due amici si dividono il conto della pizzeria" è più utile di "gestione spese condivise".

Se non hai voglia di scrivere un brain dump lungo va bene anche poco — Virgilio compenserà con più domande dopo. Ma se sei a corto di tempo, conviene investire qui.

### Alle domande A/B/C/D
Puoi:

- rispondere con una lettera (`B`)
- combinare ("A più una cosa di B")
- proporre la tua versione ("non mi convince nessuna, io vorrei…")
- chiedere altre opzioni o un parere ("non lo so, secondo te?")

Non esistono risposte "sbagliate" se riflettono il tuo gusto o le tue esigenze. Esiste una risposta sbagliata: cercare di tirare a indovinare cosa Virgilio "vuole sentire". Rispondi onestamente.

### Quando non lo sai
Dire **"non lo so, consigliami tu"** è una risposta legittima. Virgilio ha dei default pensati per non-programmatori che mantengono l'app da soli — quei default vanno bene per la maggior parte dei casi. Insisti solo quando la cosa tocca direttamente cosa vuoi tu come prodotto.

## Cosa significano le scelte ricorrenti

**Dispositivo principale.** Devi decidere se l'app è pensata prima per desktop, per mobile web (browser sul telefono), o per essere un'app installabile sul telefono. Influenza quasi tutte le decisioni di design.

**Login o no?** Anche "nessun login" è una scelta — significa che chiunque conosce l'indirizzo dell'app può vedere e modificare tutto. Va bene per piccole utility personali, non per altro.

**Chi vede cosa.** Se ci sono utenti, devi pensare se ognuno vede solo i propri dati, se ci sono gruppi condivisi, o se c'è un ruolo "admin".

**Use as main / preview / discard.** A fine di ogni pezzettino, Virgilio ti chiederà cosa fare della nuova versione:

- **Use as main** — questa versione diventa l'app reale, la nuova funzionalità entra a far parte dell'app normale.
- **Keep as preview** — la versione corrente resta com'era, quella nuova è messa da parte come bozza. Utile se vuoi confrontare o non sei convinto.
- **Discard** — butta via il pezzettino, torna all'ultima versione funzionante.

Nessuna è definitiva: anche un *discard* è recuperabile finché non sovrascrivi altro.

**Pending external review.** Se l'app tocca login, pagamenti, dati personali, deployment di produzione, o questioni legali, Virgilio aggiungerà una riga in una tabella dentro `SPEC.md`. Quella tabella è un promemoria: prima di mandare l'app a utenti veri, qualcuno con esperienza dovrebbe guardare quei punti. Virgilio costruisce comunque, ma ti ricorderà di chiamare un esperto prima del "lancio".

## Cosa Virgilio farà sempre

- Chiede una specifica prima di scrivere codice.
- Salva un punto di ripristino dopo ogni pezzettino funzionante.
- Ti dice esattamente come provare la nuova funzionalità nel browser — URL, cosa cliccare, cosa aspettarti di vedere.
- Si ferma se Git non è inizializzato, o se l'app salva dati ma il database non è configurato.
- Spezza una richiesta grande ("fai login, signup, password reset e logout") in più pezzettini, costruendoli uno alla volta.

## Cosa Virgilio rifiuterà di fare

- Scrivere codice prima che `SPEC.md` esista.
- Usare "soluzioni temporanee" che sembrano funzionare ma vanno rifatte dopo (es. salvare dati nel browser invece che nel database vero quando l'app dovrà salvarli sul serio).
- Chiederti di approvare scelte tecniche che non puoi valutare (refactoring interni, dipendenze, struttura dei file). Quelle le fa da sé con un default sicuro.
- Saltare il test manuale alla fine di un pezzettino.
- Implementare più funzionalità grandi nella stessa sessione senza confermare ogni passaggio.
- Mandare in produzione cose sensibili (auth, pagamenti, dati personali) senza ricordarti che serve una review da un esperto.

## Se senti che l'agente sta andando troppo veloce

Virgilio ha dei momenti precisi in cui *deve* fermarsi a chiederti conferma:

- prima di scrivere codice → deve esserci `SPEC.md`;
- prima di disegnare schermate → deve mostrarti 2-3 opzioni di design e attendere il tuo OK;
- prima di salvare dati veri → deve aver configurato il backend (Supabase);
- alla fine di ogni pezzettino → deve darti istruzioni di test manuale;
- subito dopo → deve chiederti cosa farne (use as main / preview / discard).

Se l'agente salta uno di questi, puoi fermarlo:

```text
Aspetta, hai saltato il design / il setup backend / il test manuale.
Torniamo indietro a quel passaggio.
```

L'agente NON ribalterà i file in automatico (rischio di perdita di lavoro). Ti dirà cosa c'è di già scritto e ti chiederà se vuoi passare per il passaggio saltato adesso (forse con modifiche al codice) oppure accettare lo skip come "debito" da affrontare dopo. Decidi tu.

Frasi come "vai", "procedi", "ok", "fai tu" sono normali. Significano "continua al prossimo passaggio richiesto", non "salta i passaggi". Se l'agente le interpreta come un permesso a saltare design o test, fermalo.

## Quando chiamare un programmatore vero

Virgilio è ottimo per **costruire un prototipo funzionante** e per testarlo con amici e familiari. NON sostituisce un programmatore quando entrano in gioco:

- **Utenti veri non noti** (gente che non conosci che si fida del tuo software).
- **Soldi veri** (pagamenti, abbonamenti, fatture).
- **Dati sensibili** (sanitari, finanziari, identificativi personali).
- **Decisioni di compliance** (GDPR, archiviazione legale, accessibilità obbligatoria).
- **Infrastruttura complessa** (più server, scaling, alta affidabilità).

Per tutte queste cose Virgilio ti aiuta a fare un prototipo, ma ti ricorderà di chiamare un esperto prima del lancio. La tabella *Pending external review* dentro `SPEC.md` è il tuo promemoria.

## Limiti onesti

- **Virgilio non è deterministico.** Lo stesso prompt può produrre risposte leggermente diverse in due sessioni. Non è un bug, è la natura dei modelli di linguaggio. Per le cose importanti, conferma sempre.
- **Non è un no-code tool.** Devi rispondere a domande, leggere riassunti, fare test manuali, confermare punti di ripristino. Non è "premi un bottone e l'app appare".
- **Funziona meglio per app piccole-medie.** Una to-do list condivisa, una mini-utility per un gruppo, un'app di gestione personale — sì. Un social network o un marketplace con migliaia di utenti — no, oltre il prototipo serve un team vero.
- **L'assistente AI può sbagliare.** Se vedi che propone qualcosa che ti sembra strano, fermalo e chiedi spiegazioni. Va benissimo dire "aspetta, non ho capito perché lo stai facendo così".

## Se ti senti bloccato

- "Non capisco la domanda" → chiedi un esempio o una riformulazione.
- "Non so quale opzione scegliere" → di' "non lo so, consigliami tu".
- "L'app non fa quello che mi aspetto" → descrivi cosa hai fatto, cosa ti aspettavi, e cosa hai visto. Virgilio entrerà in modalità troubleshooting.
- "È troppo grande, voglio fare di meno" → di' "facciamo solo X per ora, il resto dopo".
- "Sto perdendo il filo" → di' "fammi un riassunto di dove siamo e cosa rimane".

---

*Questa guida è pensata per la prima ora con Virgilio. Per dettagli tecnici sul funzionamento interno (skill, hook, struttura del repo) vedi gli altri documenti del progetto.*
