export const messages = {
  help: () => `
Virgilio installer.

Comandi:
  npx @ceredavide/virgilio init       Installa Virgilio nella cartella corrente.
  npx @ceredavide/virgilio update     Aggiorna l'installazione esistente di Virgilio.
  npx @ceredavide/virgilio --help     Mostra questo messaggio.

Opzioni di init:
  --only=claude                       Installa solo la configurazione per Claude Code.
  --only=codex                        Installa solo la configurazione per Codex.
  --dry-run                           Mostra cosa verrebbe fatto senza scrivere file.

Documentazione completa: https://github.com/Ceredavide/Virgilio
`,

  unknownCommand: (cmd) =>
    `Comando sconosciuto: "${cmd}".\nUsa: npx @ceredavide/virgilio --help per vedere i comandi disponibili.`,

  unexpectedError: (err) =>
    `Qualcosa è andato storto durante l'installazione. Ho salvato i dettagli tecnici in virgilio-install-error.log nella cartella corrente. Se vuoi, riportami il problema su https://github.com/Ceredavide/Virgilio/issues.\n\nDettaglio: ${err.message}`,

  errNodeVersion: (current) =>
    `Virgilio richiede Node.js versione 18 o superiore. Hai la ${current}. Installa la versione più recente da https://nodejs.org, poi riprova.`,

  errGitMissing: () =>
    `Virgilio richiede Git per funzionare. Sembra che non sia installato sul tuo computer. Installalo da https://git-scm.com, poi riprova.`,

  errInitOnExisting: () =>
    `Sembra che Virgilio sia già installato in questa cartella. Per aggiornarlo: npx @ceredavide/virgilio update.`,

  errUpdateOnFresh: () =>
    `Non vedo un'installazione di Virgilio in questa cartella. Per installare da zero: npx @ceredavide/virgilio init.`,

  errCopyFailed: () =>
    `Non sono riuscito a scrivere in questa cartella. Probabilmente è un problema di permessi. Prova a eseguire il comando in una cartella in cui hai i permessi di scrittura (es. la tua home directory).`,

  initSummary: (paths) =>
    `Virgilio installato.\n\nFile creati:\n${paths.map((p) => '  - ' + p).join('\n')}`,

  initNextStepsFresh: () =>
    `Prossimo passo: apri Claude Code o Codex in questa cartella e descrivi l'app che vuoi costruire. L'agente comincerà a scrivere insieme a te la specifica del progetto, prima ancora di toccare codice.`,

  initNextStepsExisting: () =>
    `Prossimo passo: apri Claude Code o Codex in questa cartella. L'agente leggerà il tuo progetto esistente per capirlo, poi ti chiederà cosa vuoi aggiungere o cambiare.`,

  superpowersReminder: () =>
    `Importante: Virgilio dipende da Superpowers. Se non l'hai ancora installato nel tuo tool AI, fallo prima di iniziare. Istruzioni: https://github.com/obra/superpowers`,

  updateSummary: (from, to) =>
    `Virgilio aggiornato da ${from} a ${to}.`,
};
