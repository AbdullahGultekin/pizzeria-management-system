# 🚀 Multi-Threading Optimalisatie Plan

## 📊 **HUIDIGE SITUATIE**

### ✅ **Wat al goed is:**
- **Backend (FastAPI)**: Gebruikt al async/await voor concurrent request handling
- **SQLite WAL Mode**: Enabled voor betere concurrency (`PRAGMA journal_mode=WAL`)
- **Database Timeout**: 20 seconden timeout om locking te voorkomen
- **Threading**: Al gebruikt in `online_bestellingen.py` voor polling

### ⚠️ **Verbeterpunten:**
- **Tkinter GUI**: Single-threaded (standaard, maar kan blocking operaties naar threads verplaatsen)
- **Database queries**: Sommige kunnen parallel worden uitgevoerd
- **File I/O**: JSON bestanden worden synchroon geladen
- **API calls**: Sommige kunnen parallel worden gedaan

---

## 🎯 **OPTIMALISATIE OPPORTUNITEITEN**

### 1. **Tkinter GUI - Background Threading** ⭐ HOGE PRIORITEIT

**Probleem:** Tkinter GUI blokkeert tijdens lange operaties (database queries, file I/O)

**Oplossing:** Gebruik `threading` voor blocking operaties

**Locaties:**
- `app.py`: Menu/Extras laden, database queries
- `modules/koeriers.py`: Order loading, API calls
- `modules/geschiedenis.py`: Order history loading
- `modules/klanten.py`: Customer search

**Implementatie:**
```python
import threading
from queue import Queue

def load_data_async(self):
    """Load data in background thread."""
    def worker():
        try:
            data = self._load_data_sync()  # Blocking operation
            # Use after() to update UI from main thread
            self.root.after(0, lambda: self._update_ui(data))
        except Exception as e:
            self.root.after(0, lambda: self._show_error(e))
    
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
```

**Impact:** Zeer hoog - voorkomt UI freezing

---

### 2. **Database Connection Pooling** ⭐ HOGE PRIORITEIT

**Probleem:** Elke database operatie maakt nieuwe connectie

**Oplossing:** Connection pool voor betere concurrency

**Implementatie:**
```python
from queue import Queue
import threading

class DatabasePool:
    def __init__(self, max_connections=5):
        self.pool = Queue(maxsize=max_connections)
        self.lock = threading.Lock()
        
        # Pre-create connections
        for _ in range(max_connections):
            conn = sqlite3.connect(DB_FILE, timeout=DB_TIMEOUT)
            conn.execute("PRAGMA journal_mode=WAL")
            self.pool.put(conn)
    
    def get_connection(self):
        return self.pool.get()
    
    def return_connection(self, conn):
        self.pool.put(conn)
```

**Impact:** Hoog - betere database performance bij concurrent access

---

### 3. **Parallel File I/O** ⭐ MIDDEL PRIORITEIT

**Probleem:** JSON bestanden worden sequentieel geladen

**Oplossing:** Load meerdere bestanden parallel

**Locaties:**
- `app.py`: `load_data()` - laadt menu.json, extras.json, settings.json
- `config.py`: JSON file operations

**Implementatie:**
```python
import concurrent.futures

def load_all_data_parallel(self):
    """Load all JSON files in parallel."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        menu_future = executor.submit(load_json_file, "menu.json")
        extras_future = executor.submit(load_json_file, "extras.json")
        settings_future = executor.submit(load_json_file, "settings.json")
        
        self.menu_data = menu_future.result()
        self.EXTRAS = extras_future.result()
        self.app_settings = settings_future.result()
```

**Impact:** Middel - snellere startup tijd

---

### 4. **Async API Calls in Tkinter** ⭐ HOGE PRIORITEIT

**Probleem:** API calls blokkeren de GUI

**Locaties:**
- `modules/koeriers.py`: `fetch_online_orders()` - kan lang duren
- `modules/online_bestellingen.py`: Polling (al geoptimaliseerd)

**Implementatie:**
```python
import threading
import requests

def fetch_online_orders_async(self, callback):
    """Fetch online orders in background thread."""
    def worker():
        try:
            orders = self._fetch_online_orders_sync()
            self.root.after(0, lambda: callback(orders))
        except Exception as e:
            self.root.after(0, lambda: self._show_error(e))
    
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
```

**Impact:** Zeer hoog - voorkomt UI freezing tijdens API calls

---

### 5. **Parallel Database Queries** ⭐ MIDDEL PRIORITEIT

**Probleem:** Meerdere queries worden sequentieel uitgevoerd

**Oplossing:** Parallel queries waar mogelijk

**Locaties:**
- `modules/koeriers.py`: `recalculate_courier_totals()` - meerdere queries
- `modules/geschiedenis.py`: Statistics + orders loading

**Implementatie:**
```python
import concurrent.futures

def load_orders_and_stats_parallel(self):
    """Load orders and statistics in parallel."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        orders_future = executor.submit(self._load_orders_sync)
        stats_future = executor.submit(self._calculate_stats_sync)
        
        orders = orders_future.result()
        stats = stats_future.result()
        
        self._update_ui(orders, stats)
```

**Impact:** Middel - snellere data loading

---

### 6. **Backend Async Improvements** ⭐ LAAG PRIORITEIT

**Probleem:** Sommige endpoints kunnen nog beter async zijn

**Oplossing:** Meer async database operations

**Locaties:**
- `pizzeria-web/backend/app/api/menu.py`: Menu queries
- `pizzeria-web/backend/app/api/orders.py`: Order queries

**Implementatie:**
```python
# Gebruik async database sessions
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

@router.get("/menu/public")
async def get_public_menu(db: AsyncSession = Depends(get_async_db)):
    # Async queries
    categories = await db.execute(select(MenuCategory))
    items = await db.execute(select(MenuItem).filter(MenuItem.beschikbaar == 1))
    ...
```

**Impact:** Laag - backend is al goed geoptimaliseerd

---

### 7. **Caching met Thread-Safe Locks** ⭐ MIDDEL PRIORITEIT

**Probleem:** Cache updates kunnen race conditions veroorzaken

**Oplossing:** Thread-safe caching

**Implementatie:**
```python
import threading
from functools import lru_cache

class ThreadSafeCache:
    def __init__(self):
        self._cache = {}
        self._lock = threading.RLock()
    
    def get(self, key):
        with self._lock:
            return self._cache.get(key)
    
    def set(self, key, value):
        with self._lock:
            self._cache[key] = value
    
    def clear(self):
        with self._lock:
            self._cache.clear()
```

**Impact:** Middel - voorkomt race conditions

---

## 📋 **IMPLEMENTATIE PRIORITEITEN**

### 🔴 **FASE 1: Kritieke UI Blocking (Direct implementeren)**
1. ✅ Background threading voor database queries in GUI
2. ✅ Async API calls in Tkinter modules
3. ✅ Loading indicators tijdens background operaties

**Verwachte impact:** UI blijft responsive, geen freezing meer

---

### 🟡 **FASE 2: Performance Verbeteringen (Later)**
4. ✅ Database connection pooling
5. ✅ Parallel file I/O
6. ✅ Parallel database queries waar mogelijk

**Verwachte impact:** 20-40% snellere data loading

---

### 🟢 **FASE 3: Advanced Optimizations (Nice to have)**
7. ✅ Thread-safe caching
8. ✅ Backend async improvements
9. ✅ Advanced connection pooling

**Verwachte impact:** Extra 10-20% performance boost

---

## ⚠️ **BELANGRIJKE WAARSCHUWINGEN**

### **Tkinter Thread Safety:**
- ❌ **NOOIT** UI updates vanuit background threads
- ✅ Gebruik altijd `root.after(0, callback)` voor UI updates
- ✅ Gebruik `Queue` voor thread-safe data passing

### **SQLite Concurrency:**
- ✅ WAL mode is al enabled (goed!)
- ✅ Timeout is al geconfigureerd (goed!)
- ⚠️ SQLite ondersteunt max 1 writer tegelijk
- ✅ Meerdere readers zijn mogelijk

### **Thread Management:**
- ✅ Gebruik `daemon=True` voor background threads
- ✅ Cleanup threads correct
- ✅ Gebruik `ThreadPoolExecutor` voor managed threads

---

## 🛠️ **IMPLEMENTATIE VOORBEELD**

### **Voorbeeld: Async Menu Loading**

```python
import threading
from queue import Queue

class PizzeriaApp:
    def __init__(self, ...):
        self.data_queue = Queue()
        self.loading = False
    
    def load_menu_async(self):
        """Load menu in background thread."""
        if self.loading:
            return
        
        self.loading = True
        self._show_loading_indicator()
        
        def worker():
            try:
                # Blocking operation
                menu_data = load_json_file("menu.json")
                self.data_queue.put(("menu", menu_data))
            except Exception as e:
                self.data_queue.put(("error", str(e)))
            finally:
                self.loading = False
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        
        # Check queue periodically
        self.root.after(100, self._check_data_queue)
    
    def _check_data_queue(self):
        """Check for data from background thread."""
        try:
            while True:
                data_type, data = self.data_queue.get_nowait()
                if data_type == "menu":
                    self.menu_data = data
                    self._update_menu_ui()
                elif data_type == "error":
                    self._show_error(data)
        except:
            pass  # Queue empty
        
        # Continue checking if still loading
        if self.loading:
            self.root.after(100, self._check_data_queue)
```

---

## 📊 **VERWACHTE RESULTATEN**

### **Voor Implementatie:**
- UI freezing tijdens database queries: ~2-5 seconden
- Menu loading: ~1-2 seconden (blocking)
- API calls: ~3-10 seconden (blocking)

### **Na Implementatie:**
- UI freezing: **0 seconden** (altijd responsive)
- Menu loading: **0.1-0.3 seconden** (background)
- API calls: **0 seconden blocking** (background)

### **Performance Verbetering:**
- **UI Responsiveness:** 100% verbetering (geen freezing meer)
- **Data Loading:** 30-50% sneller (parallel operations)
- **User Experience:** Significante verbetering

---

## 🎯 **AANBEVELING**

Begin met **FASE 1** (kritieke UI blocking):
1. Background threading voor alle database queries in GUI
2. Async API calls
3. Loading indicators

Dit geeft de grootste impact met minimale risico's!

