# Virgilio benutzen — eine Anleitung für Nicht-Programmierer

> Sprache: [English](user-guide.md) · [Italiano](user-guide.it.md) · **Deutsch**

Virgilio ist eine Schicht über Claude Code (oder einem anderen KI-Coding-Assistenten), die dich Schritt für Schritt durch den Bau einer App führt — ohne vorauszusetzen, dass du programmieren kannst.

Diese Anleitung erklärt nicht, wie man Virgilio installiert (dafür siehe die Haupt-README). Sie erklärt, was du von einer Sitzung erwarten kannst, wie du Virgilios Fragen gut beantwortest, und was Virgilio tun oder ablehnen wird. Lesezeit: ~10 Minuten.

## Was Virgilio ist, in zwei Absätzen

Virgilio setzt eine einfache Regel durch: **zuerst entscheiden, was die App macht, dann schreiben**. Kein Code wird geschrieben, bevor ein Dokument namens `SPEC.md` existiert, das in einfacher Sprache beschreibt, was die App tut, für wen, und innerhalb welcher Grenzen. Dieses Dokument definierst du selbst, in einem strukturierten Gespräch mit dem Assistenten.

Sobald die Spezifikation existiert, baut Virgilio die App **ein vollständiges Stück nach dem anderen** — eine kleine Funktion pro Stück. Nach jedem Stück sagt dir Virgilio, wie du es manuell testen kannst, bestätigt mit dir, dass es funktioniert, und speichert einen Wiederherstellungspunkt. Wenn etwas kaputtgeht, kehrt man zum letzten guten Punkt zurück.

## Was in der ersten Sitzung passiert

Eine typische erste Sitzung dauert 30–90 Minuten und hat diesen Ablauf:

1. **Brain Dump.** Virgilio wird dich bitten, in deinen eigenen Worten alles aufzuschreiben, was du für die App im Kopf hast — was sie tut, wer sie benutzt, warum, wie du sie dir vorstellst, was sie NICHT tun soll. Je mehr du hier schreibst, desto weniger Fragen wirst du später hören.
2. **Gezielte Fragen, eine nach der anderen.** Ein Thema pro Runde (z. B. „auf welchem Gerät läuft sie hauptsächlich?", „wird es einen Login geben?"). Oft mit 3–4 A/B/C/D-Optionen und einer Empfehlung.
3. **Zusammenfassung der Spezifikation.** Wenn Virgilio genug verstanden hat, zeigt er dir eine Zusammenfassung und bittet um ausdrückliche Bestätigung, bevor sie als `SPEC.md` gespeichert wird.
4. **Grundlegende technische Entscheidungen.** Direkt danach, 2–3 Alternativen für den Ort, an dem die App leben wird (Vercel fürs Web, Supabase für die Daten, Expo für Mobile, …) mit der empfohlenen Standardeinstellung.
5. **Grundeinrichtung.** Wenn die App Daten speichert, lässt dich Virgilio einen Supabase-Account erstellen, bevor Code geschrieben wird (etwa fünf Minuten, nur einmal).
6. **Erstes Stück.** Virgilio implementiert eine erste kleine Funktion, sagt dir genau, wie du sie im Browser testest, und fragt, ob sie funktioniert.

## Wie du gut antwortest

### Beim Brain Dump
Je spezifischer, desto besser. Schließe auch Offensichtliches ein („offensichtlich braucht es einen Login") und Dinge, die du **nicht** willst („ich will keine Push-Benachrichtigungen"). Konkrete Beispiele und Situationen sind mehr wert als abstrakte Beschreibungen: „zwei Freunde teilen die Pizzeria-Rechnung" ist nützlicher als „Verwaltung gemeinsamer Ausgaben".

Wenn du keine Lust hast, einen langen Brain Dump zu schreiben, reicht auch ein kurzer — Virgilio gleicht es später mit mehr Fragen aus. Aber wenn du wenig Zeit hast, lohnt es sich, sie hier zu investieren.

### Bei A/B/C/D-Fragen
Du kannst:

- mit einem einzigen Buchstaben antworten (`B`)
- kombinieren („A plus eine Sache aus B")
- deine eigene Version vorschlagen („keine davon passt, ich hätte gern…")
- nach weiteren Optionen oder einer Meinung fragen („ich weiß nicht, was meinst du?")

Es gibt keine „falschen" Antworten, solange sie deinen Geschmack oder deine echten Bedürfnisse widerspiegeln. Es gibt eine falsche Antwort: zu erraten versuchen, was Virgilio „hören will". Antworte ehrlich.

### Wenn du es nicht weißt
**„Ich weiß es nicht, entscheide du"** zu sagen ist eine legitime Antwort. Virgilio hat Standardeinstellungen, die für Nicht-Programmierer gedacht sind, die die App allein warten — diese Standards sind für die meisten Fälle in Ordnung. Bestehe nur dann auf einer eigenen Entscheidung, wenn die Frage direkt das berührt, was du als Produkt willst.

## Was die wiederkehrenden Entscheidungen bedeuten

**Hauptgerät.** Du musst entscheiden, ob die App in erster Linie für Desktop, Mobile Web (Browser auf dem Handy) oder als echte installierbare Handy-App gedacht ist. Das beeinflusst fast jede weitere Designentscheidung.

**Login oder kein Login?** „Kein Login" ist eine echte Wahl — sie bedeutet, dass jeder, der die URL der App kennt, alles sehen und ändern kann. In Ordnung für kleine persönliche Tools, sonst nicht.

**Wer sieht was.** Wenn es Nutzer gibt, musst du entscheiden, ob jeder nur seine eigenen Daten sieht, ob es geteilte Gruppen gibt, oder ob es eine „Admin"-Rolle gibt.

**Use as main / preview / discard.** Am Ende jedes Stücks wird Virgilio dich fragen, was mit der neuen Version geschehen soll:

- **Use as main** — diese Version wird zur echten App; die neue Funktionalität wird Teil der normalen App.
- **Keep as preview** — die aktuelle Version bleibt, wie sie war, die neue wird als Entwurf beiseitegelegt. Nützlich, wenn du vergleichen möchtest oder noch nicht überzeugt bist.
- **Discard** — wirf das Stück weg und kehre zur letzten funktionierenden Version zurück.

Keine dieser Entscheidungen ist endgültig: Auch ein *discard* ist wiederherstellbar, solange du nichts anderes überschreibst.

**Pending external review.** Wenn die App Login, Zahlungen, persönliche Daten, Produktions-Deployment oder rechtliche Fragen berührt, fügt Virgilio eine Zeile in einer Tabelle innerhalb von `SPEC.md` hinzu. Diese Tabelle ist eine Erinnerung: Bevor du echte Nutzer hineinlässt, sollte jemand mit Erfahrung diese Punkte anschauen. Virgilio baut trotzdem weiter, erinnert dich aber daran, vor dem „Launch" einen Experten zu rufen.

## Was Virgilio immer tut

- Fragt nach einer Spezifikation, bevor Code geschrieben wird.
- Speichert einen Wiederherstellungspunkt nach jedem funktionierenden Stück.
- Sagt dir genau, wie du die neue Funktionalität im Browser testest — URL, wohin klicken, was zu erwarten ist.
- Hält an, wenn Git nicht initialisiert ist, oder wenn die App Daten speichert, aber die Datenbank nicht konfiguriert ist.
- Zerlegt eine große Anfrage („mach Login, Signup, Passwort-Reset und Logout") in mehrere Stücke und baut sie eines nach dem anderen.

## Was Virgilio ablehnen wird

- Code zu schreiben, bevor `SPEC.md` existiert.
- „Temporäre Lösungen" zu verwenden, die zwar zu funktionieren scheinen, aber später neu gemacht werden müssen (z. B. Daten im Browser speichern, wenn die App eigentlich eine Datenbank braucht).
- Dich um Zustimmung zu technischen Entscheidungen zu bitten, die du nicht angemessen bewerten kannst (interne Refactorings, Abhängigkeiten, Dateistruktur). Diese trifft Virgilio selbst mit einer sicheren Standardeinstellung.
- Den manuellen Test am Ende eines Stücks zu überspringen.
- Mehrere große Funktionen in derselben Sitzung zu implementieren, ohne jeden Übergang zu bestätigen.
- Sensible Dinge in Produktion zu bringen (Authentifizierung, Zahlungen, persönliche Daten), ohne dich daran zu erinnern, dass eine Expertenüberprüfung nötig ist.

## Wenn du das Gefühl hast, der Agent geht zu schnell

Virgilio hat bestimmte Momente, in denen er *anhalten muss*, um deine Bestätigung einzuholen:

- bevor Code geschrieben wird → `SPEC.md` muss existieren;
- bevor Bildschirme entworfen werden → er muss dir 2–3 Designoptionen zeigen und dein OK abwarten;
- bevor echte Daten gespeichert werden → das Backend (Supabase) muss konfiguriert sein;
- am Ende jedes Stücks → er muss dir manuelle Testanweisungen geben;
- direkt danach → er muss dich fragen, was mit dem Stück geschehen soll (use as main / preview / discard).

Wenn der Agent einen dieser Schritte überspringt, kannst du ihn stoppen:

```text
Warte, du hast das Design / das Backend-Setup / den manuellen Test übersprungen.
Lass uns zu diesem Schritt zurückgehen.
```

Virgilio wird Dateien NICHT automatisch zurücksetzen (Risiko, Arbeit zu verlieren). Er wird dir sagen, was bereits geschrieben ist, und dich fragen, ob du jetzt durch den übersprungenen Schritt gehen willst (möglicherweise mit Codeänderungen) oder den Skip als bekannte „Schuld" akzeptieren willst, die später zu bearbeiten ist. Du entscheidest.

Kurze Bestätigungen wie „los", „weiter", „ok", „mach du" sind normal. Sie bedeuten „gehe zum nächsten erforderlichen Schritt", nicht „überspringe die Gates". Wenn der Agent sie als Erlaubnis interpretiert, Design oder Test zu überspringen, stoppe ihn.

## Wann einen echten Programmierer rufen

Virgilio ist hervorragend, um **einen funktionierenden Prototyp zu bauen** und ihn mit Freunden und Familie zu testen. Er ersetzt KEINEN Programmierer, wenn folgende Dinge ins Spiel kommen:

- **Echte, unbekannte Nutzer** (Menschen, die du nicht persönlich kennst und die deiner Software vertrauen).
- **Echtes Geld** (Zahlungen, Abonnements, Rechnungen).
- **Sensible Daten** (Gesundheits-, Finanz-, persönliche Identifikatoren).
- **Compliance-Entscheidungen** (DSGVO, gesetzliche Archivierung, verbindliche Barrierefreiheit).
- **Komplexe Infrastruktur** (mehrere Server, Skalierung, hohe Verfügbarkeit).

Für all dies hilft dir Virgilio bis zum Prototyp, erinnert dich aber daran, vor dem Launch einen Experten zu rufen. Die *Pending external review*-Tabelle innerhalb von `SPEC.md` ist deine Erinnerung.

## Ehrliche Grenzen

- **Virgilio ist nicht deterministisch.** Derselbe Prompt kann in zwei Sitzungen leicht unterschiedliche Antworten produzieren. Es ist kein Bug, es ist die Natur von Sprachmodellen. Für wichtige Dinge: immer bestätigen.
- **Es ist kein No-Code-Tool.** Du musst Fragen beantworten, Zusammenfassungen lesen, manuelle Tests durchführen, Wiederherstellungspunkte bestätigen. Es ist nicht „auf einen Knopf drücken und die App erscheint".
- **Es funktioniert am besten für kleine bis mittlere Apps.** Eine geteilte To-do-Liste, ein kleines Tool für eine Gruppe, eine persönliche Verwaltungs-App — ja. Ein soziales Netzwerk oder ein Marktplatz mit tausenden Nutzern — nein, jenseits eines Prototyps brauchst du ein echtes Team.
- **Der KI-Assistent kann sich irren.** Wenn du siehst, dass er etwas vorschlägt, das dir seltsam vorkommt, stoppe ihn und frag nach einer Erklärung. Es ist immer in Ordnung zu sagen „warte, ich verstehe nicht, warum du es so machst".

## Wenn du dich festgefahren fühlst

- „Ich verstehe die Frage nicht" → frag nach einem Beispiel oder einer Umformulierung.
- „Ich weiß nicht, welche Option ich wählen soll" → sag „ich weiß es nicht, entscheide du".
- „Die App tut nicht, was ich erwarte" → beschreibe, was du gemacht hast, was du erwartet hast, und was du gesehen hast. Virgilio wechselt in den Troubleshooting-Modus.
- „Das ist zu groß, ich will weniger machen" → sag „machen wir nur X für jetzt, der Rest später".
- „Ich verliere den Faden" → sag „gib mir eine Zusammenfassung, wo wir stehen und was noch übrig ist".

---

*Diese Anleitung ist für die erste Stunde mit Virgilio gedacht. Für technische Details zur internen Funktionsweise (Skills, Hooks, Repo-Struktur) siehe die anderen Projektdokumente.*
