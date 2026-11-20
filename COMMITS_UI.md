# Blender iOS - Modifiche UI e Commit

Questo documento riassume i commit, le modifiche architetturali alla UI e al sistema di input, e le patch applicate per rendere Blender utilizzabile su iPad / iOS.

---

## 1. Sorgente Upstream e Branch Ufficiali

- **Repository Ufficiale:** [projects.blender.org/blender/blender](https://projects.blender.org/blender/blender)
- **Branch Ufficiale `ios`:**
  - Commit di riferimento: `a1de44dd54af75a4c8c4a29a5fed2a1334a87446` (Blender 5.1.2 Release)
  - Include la base per compilare Blender su architettura Apple Silicon iOS (librerie precompilate `ios_arm64`, patch per FFmpeg, OpenColorIO, OpenImageIO, Python 3.11/3.13, USD).
- **Branch Ufficiale Sperimentale `ios-workshop`:**
  - `97232b0f` — *WIP: Experimental editor dock #144945* (Docking modulare per schermi touch)
  - `922720b9` — *UI: Touch-Capable Area Maintenance #144591* (Gestione e ridimensionamento delle aree con dita/stilo)
  - `c6e8abfe` — *UI: Menu Behavior Preferences #144838* (Comportamento dei menu a discesa ottimizzato per tocco)

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
1. **`release/ios/Blender.app/Info.plist` & Icone:**
   - Display name: **Blender iPad**
   - Bundle Identifier: `com.unofficial.blenderipad`
   - Icone PNG a risoluzione nativa iPad (76x76, 152x152, 167x167) iniettate e Info.plist convertito in formato binario (`plutil -convert binary1`) per garantire la compatibilità con AltStore, Sideloadly e SideStore.

---

## 3. Ulteriori Sviluppi UI della Community (Shlok-Bhakta / 3D Modeling Thingy)

Per riferimento, nel fork `Shlok-Bhakta/3d-modeling-thingy-ios` sono presenti ulteriori commit dedicati alla UI touch:
- `5fea7ec0`: **iOS: add Shift/Ctrl/Alt keys belt**: barra mobile a schermo con tasti modificatori virtuali (Shift, Ctrl, Alt) attivabili con tocco singolo o doppio tocco (lock) per l'uso senza tastiera fisica; esposizione cartella impostazioni in iOS File app.
- `ed40c044`: **iOS: polish direct touch and software keyboard**: rifinitura del tocco diretto e richiamo tastiera virtuale iOS.
- `ce64f71d`: **iOS: link Blender runtime into UIKit frame loop**: sincronizzazione del rendering a 120 FPS ProMotion tramite `CADisplayLink`.
