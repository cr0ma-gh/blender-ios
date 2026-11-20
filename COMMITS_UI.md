# Blender iOS - Modifiche UI e Commit

Questo documento riassume i commit, le modifiche architetturali alla UI e al sistema di input, e le patch applicate per rendere Blender utilizzabile su iPad / iOS.

---

## 1. Sorgente Upstream e Branch Ufficiali

- **Repository Ufficiale:** [projects.blender.org/blender/blender](https://projects.blender.org/blender/blender)
- **Branch Ufficiale `ios`:**
  - Commit usato: `d9b6fe34ddce527d93b97c0bf42ad92cebac4e4e` (Blender 5.0) — ultimo commit compilabile con le librerie precompilate `lib-ios_arm64`.
  - La punta attuale `a1de44dd` (Blender 5.1.2, luglio 2026) richiede di compilare da sorgente le dipendenze iOS (`make deps`): non esiste un `lib-ios_arm64` per la 5.1. Patch WIP in `patches/wip-5.1/`.
- **Branch Ufficiale Sperimentale `ios-workshop`** (nuove UI tablet):
  - `97232b0f` — *WIP: Experimental editor dock #144945* (Docking modulare per schermi touch) — **incluso** nella build `tablet`
  - `c6e8abfe` — *UI: Menu Behavior Preferences #144838* (Comportamento dei menu a discesa ottimizzato per tocco) — **incluso** nella build `tablet`
  - `922720b9` — *UI: Touch-Capable Area Maintenance #144591* (Gestione e ridimensionamento delle aree con dita/stilo) — già presente nel branch `ios` tramite main

### Build prodotte dalla CI
- **`tablet`**: `ios@d9b6fe34` + `patches/tablet-ui.patch` (commit originali di `ios-workshop`) + `patches/tablet-ui-backports.patch` (commit di `main` riportati sulla 5.0) + `patches/blender-ipad.patch`
- **`legacy`**: `ios@d9b6fe34` + `patches/blender-ipad.patch`

---

## 2. Modifiche UI e Input Incluse in Questa Build (`patches/blender-ipad.patch`)

Il branch upstream ufficiale `ios` si avviava su iOS ma era incompleto per l'input: mouse, trackpad, tastiera esterna e Apple Pencil non rispondevano ai controlli desktop standard. Questa patch risolve l'integrazione UI:

### A. Backend Finestra e Input (`intern/ghost/intern/GHOST_WindowIOS.mm`)
1. **Tastiera Hardware Completa (`GCKeyboard` & `UIKey`):**
   - Supporto per tutte le scorciatoie da tastiera Blender (Cmd, Ctrl, Alt, Shift).
   - Inserimento valori numerici durante le trasformazioni (es. premere `G` poi `X` poi `2` poi `Enter` per traslare esattamente di 2 unità sull'asse X).
   - Mappatura layout corretta (QWERTY, QWERTZ, AZERTY).
2. **Mouse Esterno e Trackpad (`GCMouse` & `UIPanGestureRecognizer`):**
   - Click sinistro, destro e centrale con drag.
   - Rotella del mouse mappata direttamente sullo Zoom del viewport.
   - Navigazione Orbit a 2 dita sul trackpad della Magic Keyboard.
   - Pan a 2 dita con Shift per spostare la vista mantenendo il corretto punto di ancoraggio.
   - Gesture pinch-to-zoom fluida.
   - Risoluzione del drift nella selezione a riquadro (box-select).
3. **Apple Pencil (Pressione e Inclinazione):**
   - Dati di pressione e tilt inoltrati direttamente al motore di scultura e disegno di Blender (GHOST tablet data).
   - Soppressione dell'hover non intenzionale durante il contatto dello stilo, evitando che il tratto torni all'origine al rilascio.
4. **Gestione Finestre Secondarie (Render / Popup):**
   - Chiusura della finestra di rendering premendo `Esc` o tramite tocco esterno, riattivando la finestra principale.

### B. Navigazione 2D e 3D (`source/blender/editors/`)
1. **`source/blender/editors/interface/view2d/view2d_ops.cc`:**
   - Abilitato il pan a due dita nei viewport 2D (UV Editor, Image Editor, Timeline, Graph Editor, Asset Shelf).
2. **`source/blender/editors/space_view3d/view3d_navigate_view_move.cc`:**
   - Il click centrale (`MIDDLEMOUSE`) del mouse esterno avvia l'operatore modale nativo di spostamento vista (depth/zoom correct grab-pan).

### C. Branding e Configurazione iOS
1. **Branding originale di Blender:** nome **Blender**, Bundle Identifier `org.blenderfoundation.blender` e icona ufficiale (`blender_icon.icns`) restano quelli upstream.
2. **`build/prepare_ios_bundle.sh` (post-build):** icone PNG iPad (76x76, 152x152, 167x167) generate dall'icona ufficiale, integrazione con l'app File, e Info.plist convertito in formato binario (`plutil -convert binary1`) per la compatibilità con AltStore, Sideloadly e SideStore.

---

## 2a. UX tablet dal piano upstream (solo build `tablet`, `patches/tablet-ux.patch`)
Implementazione nostra di voci del post *"Blender on Tablet: Path to Release"* (code.blender.org, novembre 2026). Upstream questi punti sono ancora task aperti senza codice (#165897–#165902, #166024, #166529):
- **Barra modificatori** (≈ *Modifier Wheel* #165901): barra flottante e trascinabile con Ctrl / Shift / Alt / Cmd. Tocco = one-shot (si rilascia dopo il click successivo), secondo tocco = blocco, terzo = spento. Il pulsante in alto la comprime.
- **Conferma / Annulla + X / Y / Z** sulla stessa barra (≈ status bar cliccabile #165900): Invio/Esc e assi per trasformazioni e altri operatori modali.
- **Ricerca** (≈ *Top Level Search* #165902), **pie Vista**, **pie Shading**, **Focus/nascondi UI** nell'header della Vista 3D (*Portfolio Review* #166024).
- **Annulla / Ripeti** e **Apri / Salva** nella topbar (*Scene Assembly* #166529).

Non ancora fattibili sulla 5.0 senza codice upstream: UI responsive/"Compact UI", tastiera a schermo dedicata, modifica delle gesture, hand-off desktop.

## 2b. Backport da `main` (solo build `tablet`, `patches/tablet-ui-backports.patch`)
- `b5fd02b5` — *UI: Quad View Resizing*: ridimensionamento dei quadranti della Quad View trascinando il punto centrale (comodo con dito/Pencil).
- `728c8624` — *UI: Fine adjusting values with arrows on number button*: frecce dei campi numerici con passo fine (Shift) e snapping (Ctrl).
- `2d186b8c` — *UI: Support holding a shortcut to temporarily switch tools*: tenendo premuto un tasto si passa temporaneamente a uno strumento (Magic Keyboard).

Valutati ma non inclusi (conflitti troppo ampi con la 5.0, da riprendere con la 5.1+): *Navigation Gizmo Toolbar* (`2e62d75b`), *custom pressure curves* per hardness/auto-smooth/spacing (`8f909f9a`), *Preferences Search* (`0add7e5c`), *popup a lato del bottone* (`6dfe6f34`), *scroll normale nei menu* (`77cb9a66`), *soft snapping nel ridimensionamento aree* (`521293cb`). Dal branch `android` nessuna modifica UI è applicabile all'iPad (sono specifiche SDL/Android).

---

## 3. Ulteriori Sviluppi UI della Community (Shlok-Bhakta / 3D Modeling Thingy)

Per riferimento, nel fork `Shlok-Bhakta/3d-modeling-thingy-ios` sono presenti ulteriori commit dedicati alla UI touch:
- `5fea7ec0`: **iOS: add Shift/Ctrl/Alt keys belt**: barra mobile a schermo con tasti modificatori virtuali (Shift, Ctrl, Alt) attivabili con tocco singolo o doppio tocco (lock) per l'uso senza tastiera fisica; esposizione cartella impostazioni in iOS File app.
- `ed40c044`: **iOS: polish direct touch and software keyboard**: rifinitura del tocco diretto e richiamo tastiera virtuale iOS.
- `ce64f71d`: **iOS: link Blender runtime into UIKit frame loop**: sincronizzazione del rendering a 120 FPS ProMotion tramite `CADisplayLink`.
