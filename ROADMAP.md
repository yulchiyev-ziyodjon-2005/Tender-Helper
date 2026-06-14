# TenderHelper — To'liq Amalga Oshirish Yo'l Xaritasi

**Versiya:** 1.0 (Audit 2026-06-15 asosida yaratildi)
**Asoslar:** `Plan.md v4.0` | `DESIGN.md v1.0` | Audit hisoboti
**Maqsad:** Backend va frontend orasidagi bo'shliqni yo'q qilib, loyihani 100% ishchi,
professional va bozorga tayyor holatga keltirish.

---

## Hozirgi Holat Xulosasi

| Qatlam | Tayyor | Yo'q |
|--------|--------|------|
| Backend xavfsizlik | ✅ P0 yopilgan | — |
| Backend modellari | ✅ Subscription, Analysis, Calculator, TenderLot | ❌ Adapter pattern, Chat endpoint, Payment, Telegram |
| Backend scraper | 🟡 `scraper.py` skeleti bor | ❌ Real xarid.uzex.uz integratsiya |
| Frontend routing | ✅ PrivateRoute/PublicRoute | ❌ 8+ sahifa yo'q |
| Frontend UI kutubxona | 🔴 Faqat 2 komponent | ❌ Button, Card, Modal, Toast, Skeleton, SubscriptionGate |
| Frontend layout | 🔴 Yo'q | ❌ AppLayout, Sidebar, Header |
| Frontend dizayn tizimi | ✅ CSS tokenlar (`index.css`) | ❌ Ulardan foydalanuvchi komponentlar yo'q |

---

## Ishlash Strategiyasi

Ish **6 ta fazaga** bo'linadi. Har bir faza avvalgi fazaning ustiga quriladi.

```
FAZA 1 → FAZA 2 → FAZA 3 → FAZA 4 → FAZA 5 → FAZA 6
Backend  Frontend  Frontend  Frontend  To'lov &  Test &
Yakunlash Poydevor  Sahifalar  AI Chat  Telegram  Monitoring
```

**Qoida:** Har bir faza "Exit Criteria" ga erishgandagina keyingisiga o'tiladi.

---

## FAZA 1 — Backend Yakunlash (2–3 kun)

### Maqsad
Backend'ni Plan.md §10.1 (Adapter Pattern) va §10.2 (Model taqsimoti) ga to'liq moslashtirish.

---

### 1.1. AI Provider Adapter Pattern (Plan.md §10.1)

**Yangi fayllar `backend/analysis/services/` da:**

#### `base.py` — Abstract interfeys
```
class AIProviderInterface(ABC):
  + analyze_tender(prompt: str, schema: dict) → dict
  + answer_question(context: str, question: str) → str
  + extract_structured_data(text: str, schema: dict) → dict
  + generate_embedding(text: str) → list[float]
```

#### `gemini_adapter.py` — Gemini 2.5 Flash
```
class GeminiAdapter(AIProviderInterface):
  - settings.GEMINI_MODEL_ANALYSIS
  - settings.GEMINI_MODEL_EMBEDDING
  - analyze_tender()       ← Mavjud _run_rule_based_analysis() ko'chiriladi
  - generate_embedding()  ← text-embedding-004
  - extract_structured_data()
  - answer_question()     ← Fallback (Groq ishlamasa)
```

#### `groq_adapter.py` — Groq Llama 3.3
```
class GroqAdapter(AIProviderInterface):
  - settings.GROQ_MODEL_CHAT
  - answer_question()     ← Asosiy chat funksiya (chunked streaming)
  - analyze_tender()      ← Gemini'ga yo'naltiradi (NotImplemented)
  - generate_embedding()  ← NotImplementedError
```

#### `gateway.py` — Markaziy kirish nuqtasi
```
get_analysis_provider()  → GeminiAdapter()
get_chat_provider()      → GroqAdapter()
get_embedding_provider() → GeminiAdapter()
```

**O'zgartiriladi:**
- `analysis/views.py`: `_run_rule_based_analysis()` → `gateway.get_analysis_provider().analyze_tender()`
- `requirements.txt`: `groq>=0.9,<1.0` qo'shiladi

---

### 1.2. Settings Nomlarini Tartibga Solish (Plan.md §10.2)

**`backend/core/settings.py`:**
```python
# ESKI                  → YANGI
GEMINI_MODEL            → GEMINI_MODEL_ANALYSIS = os.getenv('GEMINI_MODEL_ANALYSIS', 'gemini-2.5-flash')
(yo'q)                  → GEMINI_MODEL_EMBEDDING = os.getenv('GEMINI_MODEL_EMBEDDING', 'text-embedding-004')
(yo'q)                  → GROQ_MODEL_CHAT = os.getenv('GROQ_MODEL_CHAT', 'llama-3.3-70b-versatile')
(yo'q)                  → GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
```

---

### 1.3. AI Chat Endpoint (DESIGN.md §7.3)

**Yangi endpoint:** `POST /api/v1/analysis/{id}/chat/`

```
Request:  { "message": "Texnik topshiriqda qanday talablar bor?" }

Response: {
  "answer": "...",
  "sources": [
    { "file": "texnik_topshiriq.pdf", "page": 4, "excerpt": "Kamida 32GB RAM..." }
  ]
}

Logika:
  1. analysis.id → tender_lot → chunks → kontekst yig'ish (RAG)
  2. GroqAdapter.answer_question(context=chunks_text, question=message)
  3. Source citation qaysi chunk javob berdi)
  4. Faqat COMPLETED status bo'lgan analysis uchun ishlaydi
  5. IsAuthenticated + company ownership tekshiruvi majburiy
  6. UsageRecord: 'chat_message' metrik (kelajakda cheklash uchun)
```

---

### 1.4. SmartCalculator Mustaqil Endpoint (DESIGN.md §8)

**Model yangilanishlari:**
```python
class SmartCalculator(models.Model):
  analysis = OneToOneField(null=True, blank=True)  # null=True bo'ladi
  company  = ForeignKey('companies.CompanyProfile')  # YANGI
  target_margin = DecimalField(default=Decimal('0.15'))  # YANGI (hardcode emas)
  formula_version = CharField(default='v1.2')  # YANGI
```

**Yangi endpoint:** `POST /api/v1/calculator/`
```
Request: {
  "lot_id": "uuid (ixtiyoriy)",
  "start_price": 250000000,
  "raw_material_cost": 100000000,
  "logistics_cost": 15000000,
  "labor_cost": 10000000,
  "other_expenses": 5000000,
  "target_margin_percent": 15,
  "platform": "xarid_uzex",
  "has_vat": false
}
Response: Barcha hisoblangan qiymatlar + formula_version
```

---

### 1.5. `pg_trgm` va GIN Indeks Migratsiyasi (Plan.md §8.4)

**Yangi migration faylida:**
```sql
-- Faqat PostgreSQL da bajariladi
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX tender_lot_title_trgm_idx ON tender_lots USING gin (title gin_trgm_ops);
CREATE INDEX tender_lot_buyer_name_trgm_idx ON tender_lots USING gin (buyer_name gin_trgm_ops);
CREATE INDEX tender_lot_lot_number_trgm_idx ON tender_lots USING gin (lot_number gin_trgm_ops);
```

`RunSQL` ichida `IF connection.vendor == 'postgresql'` tekshiruvi bilan.

---

### 1.6. Real Scraper — xarid.uzex.uz (Plan.md §8.1)

`backend/tenders/services/scraper.py` to'ldiriladi:

```
class BaseSourceAdapter(ABC):
  + fetch_lots(since: datetime) → list[TenderLotData]
  + fetch_document_urls(lot_external_id: str) → list[str]

class XaridUzexAdapter(BaseSourceAdapter):
  - base_url: settings.TENDER_PORTALS['xarid_uzex']
  - BeautifulSoup4 orqali lot ro'yxatini olish
  - TenderLot upsert (source + external_id unique constraint ishlatiladi)
  - Retry logic: max 3 urinish, exponential backoff

Celery task: scrape_portal_task(source_code: str)
  - Schedule: har 30 daqiqada (SCRAPE_INTERVAL_MINUTES = 30)
  - Error monitoring: Celery Flower yoki Sentry orqali
```

---

### 1.7. `TenderListView` Ruxsat Yangilash

```python
# HOZIR: AllowAny (auth shart emas)
# YANGI:
class TenderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    # Kirganlar: to'liq ko'rinish + moslik balli
    # Kirmaganlar: ko'rish mumkin, cheklangan ma'lumot
```

---

### FAZA 1 Exit Criteria
- [ ] `GeminiAdapter.analyze_tender()` ishlaydi, mavjud test o'tadi
- [ ] `GroqAdapter.answer_question()` ishlaydi
- [ ] `POST /api/v1/analysis/{id}/chat/` 200 qaytaradi, citation bor
- [ ] `POST /api/v1/calculator/` mustaqil ishlaydi (lot bog'lamasdan)
- [ ] `requirements.txt` da `groq>=0.9` bor
- [ ] `GEMINI_MODEL_ANALYSIS`, `GEMINI_MODEL_EMBEDDING`, `GROQ_MODEL_CHAT`, `GROQ_API_KEY` settings da bor
- [ ] `pg_trgm` migration yozilgan (SQLite uchun skip)

---

## FAZA 2 — Frontend Poydevor: Dizayn Tizimi va Layout (2–3 kun)

### Maqsad
DESIGN.md §1–§3 da ko'rsatilgan barcha UI komponentlar va layout strukturasini qurish.
Bu barcha keyingi sahifalar uchun asos.

---

### 2.1. UI Komponent Kutubxonasi (`frontend/src/components/ui/`)

#### `Button.jsx`
```
variants: primary | secondary | ghost | danger
sizes: sm | md | lg
props: isLoading, leftIcon, rightIcon, disabled, onClick
animatsiya: hover scale(1.02) + shadow transition
Loading holat: spinner + "Yuklanmoqda..." matni
```

#### `Card.jsx`
```
variants: elevated | outlined | glass
props: hoverable (hover da Y-translate -2px animatsiya)
```

#### `Badge.jsx`
```
variants: free (kulrang) | pro (ko'k) | enterprise (binafsha)
          | active (yashil) | warning (sariq) | danger (qizil)
sizes: sm | md
```

#### `Modal.jsx`
```
props: isOpen, onClose, title, size (sm|md|lg|xl), preventClose
animatsiya: scale(0.95→1) + fade (200ms cubic-bezier)
backdrop: blur-sm, click to close (preventClose bo'lmasa)
Escape tugmasi bilan yopiladi
```

#### `Toast.jsx` + `useToastStore.js`
```
variants: success | error | warning | info
position: top-right (mobile: top-center)
auto-dismiss: 5 soniya, progress bar bilan
animatsiya: slide-in + fade-out
useToastStore (Zustand): addToast(), removeToast()
Maksimal 5 ta bir vaqtda ko'rsatiladi
```

#### `Skeleton.jsx`
```
variants: text | circle | card | table-row
Mavjud .skeleton CSS klassidan foydalanadi (shimmer effekt)
props: lines (text uchun), height, width
```

#### `Progress.jsx`
```
variants: linear | circular
props: value (0-100), color, size, showLabel, animated
```

#### `Stepper.jsx`
```
props: steps[] ({ id, label, description }), currentStep
holatlari: completed (✓ icon) | active (raqam) | upcoming (kulrang)
orientation: horizontal (desktop) | vertical (mobile)
```

#### `SubscriptionGate.jsx` — ENG MUHIM KOMPONENT
```jsx
props:
  feature: string  // masalan: 'export_pdf'
  requiredPlan: 'pro' | 'enterprise'
  children: ReactNode
  fallback?: ReactNode  // Custom bloklash UI (ixtiyoriy)

Logika:
  1. subscriptionStore.hasFeature(feature) tekshiradi
  2. true → children render qiladi
  3. false → UpgradePrompt ko'rsatadi

UpgradePrompt (inline yoki Modal):
  - Qaysi plan kerakligi
  - Shu planda nima beradi (feature ro'yxati)
  - [Hozircha emas] [⚡ Pro ga o'tish →] (→ /billing)
```

#### `UsageLimitBanner.jsx`
```
props: metric ('ai_analysis'), used, limit
75% band → warning banner (sariq, "X ta tahlil qoldi")
100% band → error banner (qizil, "Limit tugadi") + Upgrade CTA
```

#### `Tooltip.jsx`
```
props: content, position (top|bottom|left|right), children
Hover va focus trigger
```

#### `Tabs.jsx`
```
variants: underline | pill
props: tabs[] ({ id, label, icon }), activeTab, onChange
```

#### `DataTable.jsx`
```
props: columns[], data[], loading, emptyText
Sorting (ustun sarlavhaga bosib), Pagination integratsiya
```

---

### 2.2. Layout Komponentlar (`frontend/src/components/layout/`)

#### `AppLayout.jsx`
```jsx
// Tuzilma:
<div className="flex min-h-screen bg-surface-50 dark:bg-surface-950">
  <Sidebar />                    // Desktop: 270px fixed
  <div className="flex-1 flex flex-col overflow-hidden">
    <Header />                   // 64px sticky
    <main className="flex-1 overflow-y-auto p-6">
      {children}
    </main>
  </div>
  <BottomNav />                  // Mobile: fixed bottom
</div>
```

#### `Sidebar.jsx`
```
Navigatsiya (DESIGN.md §3.2):

  📊 Dashboard             /dashboard
  🔍 Tenderlar             /tenders
  📋 Tahlillarim           /analyses
  🧮 Kalkulyator           /calculator
  💾 Saqlangan             /saved
  🔔 Bildirishnomalar      /notifications

  ── PRO / BIZNES ──
  👥 Jamoa         [PRO🔒]  /team
  🏆 Raqobatchilar [BIZ🔒]  /competitors
  📤 Export        [PRO🔒]  (AnalysisPage action)

  ── SOZLAMALAR ──
  🏢 Kompaniya             /settings/company
  💳 Obuna                 /billing
  🤖 Telegram              /settings/telegram
  ⚙️  Sozlamalar            /settings

Pastki qism:
  [TARIF BADGE]           // BEPUL / PRO / BIZNES
  Progress bar            // "4 tahlildan 3 ta ishlatildi"
  [⚡ Pro ga o'tish]      // Free foydalanuvchilar uchun

Holat:
  Desktop: 270px fixed
  Tablet (768-1024px): Collapsible (hamburger icon bilan)
  Mobile (<768px): Yo'q, BottomNav ishlatiladi
```

#### `Header.jsx`
```
Desktop:
  [Logo] [Breadcrumb]                    [🔔 Badge] [👤 Avatar ▼]
                                                     ↳ Profil
                                                     ↳ Sozlamalar
                                                     ↳ Logout

Mobile:
  [≡] [Logo TenderHelper]                [🔔] [👤]

Avatar dropdown animatsiya: fade + slide down
```

#### `BottomNav.jsx` (Mobile only)
```
[🏠 Dashboard] [🔍 Tenderlar] [📋 Tahlillar] [👤 Profil]
Fixed bottom, backdrop blur
Active: primary rang + scale
```

---

### 2.3. State Management Yangilash

#### `store/subscriptionStore.js` — YANGI
```javascript
{
  state: {
    plan: 'free',           // 'free' | 'pro' | 'enterprise'
    planName: 'Bepul',
    subscription: null,
    usageRecords: {},       // { ai_analysis: { used: 3, limit: 4 }, ... }
  },
  actions: {
    fetchSubscription(),
    hasFeature(featureName): boolean,
    getRemainingUsage(metric): number | null,
    getUsagePercent(metric): number,
  }
}
```

#### `store/authStore.js` — YANGILASH
```javascript
// Qo'shimchalar:
{
  company: null,        // { id, name, industry, has_vat, ... }
  setCompany(company),
}
```

#### `utils/subscriptionHelpers.js` — YANGI
```javascript
export const PLAN_FEATURES = {
  free: {
    analysis_per_month: 4,
    saved_tenders: 10,
    telegram_notifications: false,
    export_pdf: false,
    export_excel: false,
    analysis_history: false,
    team_members: 0,
    competitor_analysis: false,
    advanced_filters: false,
    api_access: false,
    ai_chat: false,
  },
  pro: {
    analysis_per_month: null,       // cheksiz (fair-use: 100)
    saved_tenders: null,
    telegram_notifications: true,
    export_pdf: true,
    export_excel: true,
    analysis_history: true,
    team_members: 0,
    competitor_analysis: false,
    advanced_filters: true,
    api_access: false,
    ai_chat: true,
  },
  enterprise: {
    analysis_per_month: null,       // cheksiz (fair-use: 500)
    saved_tenders: null,
    telegram_notifications: true,
    export_pdf: true,
    export_excel: true,
    analysis_history: true,
    team_members: 5,
    competitor_analysis: true,
    advanced_filters: true,
    api_access: true,
    ai_chat: true,
  },
};

export function canAccess(plan, feature) { ... }
export function getUpgradePath(currentPlan, feature) { ... }
```

---

### 2.4. API Klientlar (`frontend/src/api/`)

Mavjud `api/client.js` (Axios) ustiga modullar:

#### `api/auth.js`
```javascript
login(email, password)             → POST /api/v1/auth/login/
register(data)                     → POST /api/v1/auth/register/
verifyPhone(phone, code)           → POST /api/v1/auth/verify-phone/
googleLogin(code)                  → POST /api/v1/auth/google/
logout()                           → POST /api/v1/auth/logout/
forgotPassword(email)              → POST /api/v1/auth/forgot-password/
resetPassword(token, newPassword)  → POST /api/v1/auth/reset-password/
```

#### `api/tenders.js`
```javascript
getTenders(params)        → GET  /api/v1/tenders/
getTenderById(id)         → GET  /api/v1/tenders/{id}/
createManualTender(data)  → POST /api/v1/tenders/manual/
saveTender(id)            → POST /api/v1/tenders/{id}/save/
unsaveTender(id)          → DEL  /api/v1/tenders/{id}/save/
```

#### `api/analysis.js`
```javascript
startAnalysis(lotId, text)       → POST /api/v1/analysis/start/
getAnalysis(id)                  → GET  /api/v1/analysis/{id}/result/
getAnalysisStatus(id)            → GET  /api/v1/analysis/{id}/status/
getAnalysisHistory()             → GET  /api/v1/analysis/history/
chatWithAnalysis(id, message)    → POST /api/v1/analysis/{id}/chat/
exportAnalysis(id, format)       → POST /api/v1/analysis/{id}/export/
```

#### `api/calculator.js`
```javascript
calculate(data)  → POST /api/v1/calculator/
```

#### `api/subscriptions.js`
```javascript
getMySubscription()                → GET  /api/v1/subscriptions/me/
getAvailablePlans()                → GET  /api/v1/subscriptions/plans/
getUsageRecords()                  → GET  /api/v1/subscriptions/usage/
initiatePayment(planId, provider)  → POST /api/v1/subscriptions/payment/initiate/
```

#### `api/companies.js`
```javascript
getMyCompany()       → GET  /api/v1/companies/me/
updateCompany(data)  → PATCH /api/v1/companies/me/
```

---

### FAZA 2 Exit Criteria
- [ ] Barcha 12+ UI komponent `components/ui/` da to'liq va ishlaydi
- [ ] `AppLayout` barcha sahifalarda ishlaydi
- [ ] `Sidebar` tarif badge, usage progress, navigation ni ko'rsatadi
- [ ] `SubscriptionGate` Pro funksiyani bloklaydi va UpgradeModal ko'rsatadi
- [ ] `subscriptionStore` plan va usage ma'lumotlarini API dan oladi
- [ ] `PLAN_FEATURES` to'liq va to'g'ri
- [ ] Barcha API metodlar `api/` da yozilgan

---

## FAZA 3 — Frontend: Asosiy Sahifalar (3–4 kun)

### Maqsad
DESIGN.md da ko'rsatilgan barcha sahifalarni `AppLayout` ichida qurish.

---

### 3.1. `DashboardPage.jsx` — QAYTA YOZISH

Hozirgi `DashboardPage.jsx` AppLayout siz, Sidebar siz yozilgan.

**Yangi tuzilma:**
```jsx
<AppLayout>
  <div className="space-y-6">
    <PageHeader greeting="Xayrli kun, [Ism]!" date={today} />

    {/* 4 ta Stat karta */}
    <StatsGrid>
      <StatCard icon="📋" label="Faol tenderlar" value={count} trend="+5%" />
      <StatCard icon="✅" label="Bugun yangi" value={newCount} />
      <StatCard icon="💰" label="O'rtacha moslik" value="78%" />
      <StatCard icon="⏰" label="Deadline" value="3 kun" color="danger" />
    </StatsGrid>

    {/* Sizga mos yangi tenderlar */}
    <Section title="Sizga mos yangi tenderlar">
      <TenderCard /> ← moslik balli bilan (company.industry asosida)
      <TenderCard />
    </Section>

    {/* So'nggi tahlillarim */}
    <Section title="So'nggi tahlillarim">
      <RecentAnalysisCard />
    </Section>

    {/* Yaqinlashayotgan deadline'lar */}
    <Section title="Deadline'lar">
      <DeadlineList />
    </Section>

    {/* Usage limit banner (agar kerak bo'lsa) */}
    <UsageLimitBanner metric="ai_analysis" />
  </div>
</AppLayout>
```

---

### 3.2. `TendersPage.jsx` — YANGI

```
URL: /tenders
DESIGN.md §5
```

```jsx
<AppLayout>
  <TendersPage>
    {/* Qidiruv */}
    <TenderSearch
      value={query}
      onChange={setQuery}
      debounce={300}
      placeholder="Tender yoki mahsulot nomini yozing..."
    />

    {/* Kengaytirilgan filtrlar */}
    <TenderFilters
      platform={platform} onPlatformChange={...}
      category={category} onCategoryChange={...}
      priceRange={[min, max]} onPriceChange={...}
      region={region} onRegionChange={...}
      deadline={deadline} onDeadlineChange={...}
      status={status} onStatusChange={...}
      onClear={clearFilters}
    />
    {/* Pro filtrlar SubscriptionGate bilan */}

    {/* Ko'rinish almashtirish */}
    <ViewToggle view={view} onChange={setView} />

    {/* Natijalar */}
    <div>{count} ta tender topildi</div>

    {/* Ro'yxat */}
    {view === 'list'
      ? <TenderList tenders={tenders} />
      : <TenderGrid tenders={tenders} />
    }

    {/* Pagination */}
    <Pagination current={page} total={totalPages} onChange={setPage} />
  </TendersPage>
</AppLayout>
```

**TenderCard komponenti (`components/tender/TenderCard.jsx`):**
```
Status badge | Platforma | Hudud
Sarlavha (hover: primary rang)
Buyurtmachi nomi
Narx | Deadline (kunlik taymer, qizil agar ≤3 kun)
Moslik: [████████░░ 82%] (company.industry asosida)
[🔬 AI Tahlil] [♥ Saqlash] [↗ Ochish]
```

---

### 3.3. `TenderDetailPage.jsx` — YANGI

```
URL: /tenders/:id
DESIGN.md §6
```

```jsx
<AppLayout>
  <Breadcrumb items={['Tenderlar', tender.lot_number]} />

  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
    {/* Asosiy ma'lumotlar (2/3 kenglik) */}
    <div className="lg:col-span-2">
      <TenderHeader tender={tender} />
      <Tabs>
        <Tab id="description"> Texnik topshiriq matni </Tab>
        <Tab id="documents">   Hujjatlar ro'yxati + yuklab olish </Tab>
        <Tab id="history">     Bu lot uchun o'tgan tahlillar </Tab>
      </Tabs>
    </div>

    {/* Action panel (1/3 kenglik) */}
    <div className="space-y-4">
      <MatchScoreCard company={company} tender={tender} />
      <DeadlineTimer deadline={tender.deadline} />
      <ActionButtons>
        <Button primary onClick={startAnalysis}> 🔬 AI Tahlil </Button>
        <Button secondary onClick={saveToggle}> ♥ Saqlash </Button>
        <Button ghost onClick={openExternal}> ↗ Asl saytda ochish </Button>
        <Button ghost onClick={gotoCalculator}> 🧮 Kalkulyator </Button>
      </ActionButtons>
    </div>
  </div>
</AppLayout>
```

---

### 3.4. `AnalysisPage.jsx` — QAYTA YOZISH

```
URL: /analyses/:id
DESIGN.md §7
```

**Progress holati (status ≠ COMPLETED va ≠ FAILED):**
```jsx
<AnalysisProgress>
  <StepList steps={[
    'Hujjatlarni yuklab olish',
    'Matnni ajratish',
    'AI tahlil qilmoqda',
    'Natijalarni formatlash',
  ]} currentStep={currentStep} />
  <LinearProgress value={progressPercent} animated />
  <InfoText> Bu jarayon 10–30 soniya davom etishi mumkin </InfoText>
  <AIDisclaimer />
</AnalysisProgress>
```

**Natija holati (COMPLETED):**
```jsx
<AnalysisResult>
  {/* Moslik balli */}
  <CircularProgress value={analysis.eligibility_score} size="xl" />
  <ScoreBreakdown items={['Soha', 'Hudud', 'Narx', 'Tajriba']} />

  {/* Tab navigatsiya */}
  <Tabs>
    <Tab id="summary">  AI Xulosa </Tab>
    <Tab id="redflags"> 🚩 Xatarlar ({redFlags.length}) </Tab>
    <Tab id="docs">     📄 Hujjatlar checklisti </Tab>
    <Tab id="reqs">     ✅ Talablar </Tab>
    <Tab id="stds">     📐 Standartlar </Tab>
    <Tab id="chat">
      <SubscriptionGate feature="ai_chat" requiredPlan="pro">
        <ChatPanel analysisId={id} />  {/* FAZA 4 */}
      </SubscriptionGate>
    </Tab>
  </Tabs>

  {/* Red flag karta */}
  <RedFlagCard
    level="blocker"          ← qizil
    title="Yetkazib berish muddati qisqa"
    reason="10 bank ish kuni ichida deyilgan"
    recommendation="Logistikani oldindan tayyorlang"
    source={{ file: 'texnik.pdf', page: 3, excerpt: '...' }}
    confidence={0.94}
  />

  {/* AI Tavsiya */}
  <AIRecommendation text={analysis.decision.recommendation} />
  <AIDisclaimer />

  {/* Action tugmalar */}
  <ActionBar>
    <Button onClick={gotoCalculator}> 🧮 Kalkulyator </Button>
    <SubscriptionGate feature="export_pdf">
      <Button onClick={exportPDF}> 📤 PDF yuklab olish </Button>
    </SubscriptionGate>
  </ActionBar>
</AnalysisResult>
```

**Xato holati (FAILED):**
```jsx
<ErrorState
  title="Tahlil muvaffaqiyatsiz"
  description="AI xizmatida vaqtinchalik muammo. Limit sarflanmadi."
  actions={[
    <Button onClick={retry}> 🔄 Qayta urinib ko'rish </Button>,
    <Button variant="ghost" onClick={goBack}> ← Orqaga </Button>,
  ]}
/>
```

---

### 3.5. `CalculatorPage.jsx` — YANGI

```
URL: /calculator
DESIGN.md §8
```

```jsx
<AppLayout>
  <PageHeader title="🧮 Aqlli Kalkulyator" />

  <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
    {/* Kirish paneli */}
    <Card>
      <TenderLinkInput />        {/* Lot bog'lash (ixtiyoriy) */}
      <NumberInput label="Xom ashyo tannarxi" />
      <NumberInput label="Logistika xarajatlari" />
      <NumberInput label="Ish haqi" />
      <NumberInput label="Boshqalar" />
      <VATToggle />
      <PlatformSelect options={platforms} />
      <SliderInput label="Maqsad foyda marjasi" min={5} max={50} step={1} />
      <NumberInput label="Zakalat foizi" />
      <Button
        secondary
        leftIcon={<Save />}
        onClick={saveToProfile}
      > Marjani profilga saqlash </Button>
      <Button primary onClick={calculate}> 🔄 Hisoblash </Button>
    </Card>

    {/* Natija paneli */}
    <Card>
      <ResultRow label="Tannarx jami" value={totalCost} />
      <Divider />
      <ResultRow label="QQS (12%)" value={vat} color="warning" />
      <ResultRow label="Komissiya (0.15%)" value={commission} color="warning" />
      <ResultRow label="Zakalat (3%)" value={zakalat} color="warning" />
      <Divider />
      <ResultRow label="Break-even narx" value={minSafe} bold />
      <ResultRow label="Tavsiya narx" value={recommended} bold />
      <ProfitDisplay value={netProfit} />  {/* yashil ≥0, qizil <0 */}
      <ResultRow label="Oldindan kerakli pul" value={cashRequired} />
      <FormulaVersion version="v1.2" link="/docs/formula" />

      <SubscriptionGate feature="export_excel">
        <Button leftIcon={<Download />}> Excel sifatida saqlash </Button>
      </SubscriptionGate>
    </Card>
  </div>
</AppLayout>
```

---

### 3.6. `SavedPage.jsx` — YANGI

```
URL: /saved
DESIGN.md §9
```

```jsx
<AppLayout>
  <Tabs>
    <Tab id="saved" label="💾 Saqlangan (12)">
      <SavedTenderList />
    </Tab>
    <Tab id="watching" label="👁 Kuzatish (5)">
      <WatchList />
      <NotificationSettings metric="deadline" />
    </Tab>
    <Tab id="searches" label="🔍 Qidiruvlar (3)">
      <SavedSearchList />
    </Tab>
  </Tabs>
</AppLayout>
```

---

### 3.7. `NotificationsPage.jsx` — YANGI

```
URL: /notifications
DESIGN.md §10
```

```jsx
<AppLayout>
  <div className="flex justify-between">
    <h1>🔔 Bildirishnomalar</h1>
    <Button ghost onClick={markAllRead}> Barchasini o'qilgan deb belgilash </Button>
  </div>

  <NotificationList notifications={notifications} />

  <Section title="Sozlamalar">
    <ChannelToggles />      {/* Telegram, Email, Push */}
    <ThresholdSlider />     {/* Moslik % chegarasi */}
  </Section>
</AppLayout>
```

---

### 3.8. Ro'yxatdan O'tish — 4 Bosqichli Qayta Yozish

```
URL: /register
DESIGN.md §2.2
```

`RegisterPage.jsx` va `OnboardingPage.jsx` ni birlashtirish:

```jsx
<AuthShell>
  <Stepper steps={steps} currentStep={step} />

  {step === 1 && <AccountStep onNext={handleAccount} />}
  {step === 2 && <VerifyStep phone={phone} onNext={handleVerify} />}
  {step === 3 && <CompanyStep onNext={handleCompany} onSkip={skipCompany} />}
  {step === 4 && <PlanStep onSelect={handlePlan} />}
  {step === 5 && <WelcomeStep company={company} />}
</AuthShell>
```

**AccountStep:** Ism, Email, Telefon (+998 prefix), Parol (kuch ko'rsatkichi), Parol tasdiqlash, Shartlar checkbox  
**VerifyStep:** `OTPVerification.jsx` (mavjud komponent ishlatiladi) + qayta yuborish  
**CompanyStep:** Kompaniya nomi, STIR, Tashkiliy shakl, Soha, Viloyat, QQS holati, [⏭ O'tkazib yuborish]  
**PlanStep:** 3 ta plan karta (Free/Pro/Enterprise) — DESIGN.md §4 ko'rinishida  
**WelcomeStep:** Confetti animatsiya + Keyingi qadamlar

---

### 3.9. `BillingPage.jsx` — YANGI

```
URL: /billing
DESIGN.md §11
```

```jsx
<AppLayout>
  {/* Hozirgi tarif holati */}
  <CurrentPlanCard plan={subscription} usage={usageRecords} />

  {/* Tarif solishtirish jadvali */}
  <BillingToggle period={period} onChange={setPeriod} />  {/* Oylik/Yillik */}
  <PricingTable plans={plans} currentPlan={plan} onSelect={openPayment} />

  {/* To'lov tarixi */}
  <PaymentHistory payments={paymentHistory} />
</AppLayout>
```

---

### FAZA 3 Exit Criteria
- [ ] `/tenders` real API dan tender ko'rsatadi + filtr + qidiruv ishlaydi
- [ ] `/tenders/:id` batafsil ko'rinish va Deadline taymer ishlaydi
- [ ] `/analyses/:id` progress, natija va xato holatlari ishlaydi
- [ ] `/calculator` mustaqil hisoblaydi + natija to'g'ri
- [ ] `/register` 4 bosqichli, OTP va CompanyStep ishlaydi
- [ ] `/billing` tarif ko'rsatadi, `SubscriptionGate` ishlaydi
- [ ] `/saved` va `/notifications` asosiy funksiya ishlaydi
- [ ] **`AppLayout` + `Sidebar` barcha sahifalarda ishlatiladi** (eng muhim!)

---

## FAZA 4 — Frontend: AI Chat va Kengaytirilgan (2 kun)

### Maqsad
Faza 1 da yaratilgan AI Chat endpointini frontendga ulash va Pro funksiyalarni to'liq qurish.

---

### 4.1. Chat Komponenti (`components/analysis/ChatPanel.jsx`)

```jsx
<ChatPanel analysisId={id}>
  <MessageList>
    {messages.map(msg => (
      msg.role === 'ai'
        ? <AIMessage text={msg.content} sources={msg.sources} />
        : <UserMessage text={msg.content} />
    ))}
    {isTyping && <TypingIndicator />}
  </MessageList>

  <QuickQuestions questions={[
    'Jarimalar bormi?',
    'QQS qanday to\'lanadi?',
    'Kerakli hujjatlar ro\'yxati?',
    'Eng katta xatarlar nima?',
  ]} onSelect={sendMessage} />

  <ChatInput
    value={input}
    onChange={setInput}
    onSend={sendMessage}
    disabled={isTyping}
    placeholder="Savolingizni yozing..."
  />
</ChatPanel>
```

**CitationBlock komponenti:**
```jsx
<CitationBlock source={{ file: 'texnik.pdf', page: 4, excerpt: '...' }} />
```

---

### 4.2. Fayl Yuklash (Upload) — `TenderUploadPage.jsx` — YANGI

```
URL: /tenders/new
DESIGN.md §9.5
```

```jsx
<AppLayout>
  <PageHeader title="📤 Yangi tender qo'shish" />
  <Card>
    {/* Tender ma'lumotlari */}
    <TextInput label="Tender nomi *" />
    <TextInput label="Buyurtmachi" />
    <NumberInput label="Boshlang'ich narx" />

    {/* Fayl yuklash */}
    <DropZone
      accept={{ 'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] }}
      maxSize={50 * 1024 * 1024}  // 50MB
      onDrop={handleFileDrop}
    />
    <FileList files={files} onRemove={removeFile} />

    <Button primary onClick={submitAndAnalyze}> Tahlilni boshlash 🚀 </Button>
  </Card>
</AppLayout>
```

---

### 4.3. `AnalysesPage.jsx` — YANGI

```
URL: /analyses
DESIGN.md §3.2 (Sidebar: "Tahlillarim")
```

```jsx
<AppLayout>
  <PageHeader title="📋 Tahlillarim" />
  {analyses.length === 0
    ? <EmptyState
        icon="📊"
        title="Hali hech qanday tahlil yo'q"
        description="Tenderlar sahifasidan 'AI Tahlil' tugmasini bosing"
        action={<Button onClick={() => navigate('/tenders')}>Tenderlar</Button>}
      />
    : <AnalysisHistory analyses={analyses} />
  }
</AppLayout>
```

---

### 4.4. Sozlamalar Sahifalari — `SettingsPage.jsx` QAYTA YOZISH

```
URL: /settings
DESIGN.md §16
```

```jsx
<AppLayout>
  <Tabs variant="pill">
    <Tab id="company">  🏢 Kompaniya </Tab>
    <Tab id="security"> 🔐 Xavfsizlik </Tab>
    <Tab id="telegram"> 🤖 Telegram </Tab>
    <Tab id="ui">       🌐 Interfeys </Tab>
  </Tabs>

  {activeTab === 'company'  && <CompanySettings />}
  {activeTab === 'security' && <SecuritySettings />}
  {activeTab === 'telegram' && <TelegramSettings />}
  {activeTab === 'ui'       && <InterfaceSettings />}
</AppLayout>
```

**TelegramSettings (DESIGN.md §15):**
```jsx
{user.telegram_connected
  ? <ConnectedState username="@username" onDisconnect={disconnect} />
  : <ConnectionFlow>
      <CodeDisplay code={linkCode} expiresIn={600} onRefresh={refreshCode} />
      <ExternalLink href="https://t.me/TenderHelperBot">
        📲 @TenderHelperBot ni ochish
      </ExternalLink>
    </ConnectionFlow>
}
<NotificationPreferences />
```

---

### FAZA 4 Exit Criteria
- [ ] AI Chat `/analyses/:id` sahifasida ishlaydi, citation bilan
- [ ] Fayl yuklash va tahlil boshlash ishlaydi
- [ ] `/analyses` tarixi sahifasi ishlaydi
- [ ] Sozlamalar Tabs bilan to'liq ishlaydi
- [ ] Telegram ulash UI ishlaydi

---

## FAZA 5 — To'lov va Telegram Integratsiya (3–4 kun)

### Maqsad
Daromad tizimi va Telegram bot notification'larni ishga tushirish.

---

### 5.1. To'lov Integratsiyasi Backend (Plan.md §14)

```
backend/subscriptions/services/payments/
  __init__.py
  base.py           ← PaymentProviderInterface
  click_adapter.py  ← prepare(), complete(), verify_signature(), ip_whitelist()
  payme_adapter.py  ← CreateTransaction, PerformTransaction, CancelTransaction

Yangi views:
  POST /api/v1/subscriptions/payment/initiate/
    → { redirect_url, merchant_trans_id }
  POST /api/v1/subscriptions/payment/click/webhook/
    → CLICK server tomonian chaqiriladi
  POST /api/v1/subscriptions/payment/payme/webhook/
    → Payme server tomonian chaqiriladi

WebhookEvent modeli:
  provider, event_type, raw_payload, processed_at, status, error_message

Payment State Machine:
  PENDING → PROCESSING → COMPLETED → [Subscription aktivatsiya]
                       ↓
                    FAILED → [Foydalanuvchiga xato xabari]

Idempotency:
  merchant_trans_id unique constraint
  Webhook ikki marta kelsa — ikkinchisi e'tiborga olinmaydi
```

---

### 5.2. Telegram Bot Backend (Plan.md §13)

```
requirements.txt: aiogram>=3.4,<4.0

backend/telegram/ (YANGI APP)
  __init__.py
  apps.py
  bot.py           ← Aiogram 3 dispatcher + Webhook setup
  handlers.py      ← /start, deep link parsing
  notifications.py ← send_lot_notification(user, lot), send_deadline_alert(user, lot)
  tasks.py         ← Celery tasks

Deep link format:
  t.me/TenderHelperBot?start=TH-{base62(lot_id)}

Celery tasks:
  send_deadline_notifications_task
    ← Har kuni 09:00 da (deadline 1 va 3 kun qolganlar)
  send_new_lot_notifications_task
    ← Har yangi lot qo'shilganda (moslik ≥ user.notification_threshold%)

initData verification:
  TELEGRAM_BOT_TOKEN → HMAC-SHA256
```

---

### 5.3. PDF/Excel Export Backend (Plan.md §11.3)

```
POST /api/v1/analysis/{id}/export/
  body: { format: 'pdf' | 'excel' }
  response: { download_url, expires_at (5 daqiqa) }

PDF (reportlab):
  - Sarlavha: TenderHelper AI Tahlili
  - Kompaniya va Tender ma'lumotlari
  - Moslik balli va breakdown
  - Red Flaglar ro'yxati
  - Hujjatlar checklisti
  - AI Tavsiya + Disclaimer

Excel (openpyxl):
  - SmartCalculator natijalari jadvali
  - Narx komponentlari breakdown
  - Formula versiyasi

SubscriptionGate: Pro va Enterprise
```

---

### FAZA 5 Exit Criteria
- [ ] CLICK to'lov oqimi test muhitida ishlaydi (redirect + webhook + subscription aktivatsiya)
- [ ] Payme oqimi test muhitida ishlaydi
- [ ] Telegram bot `/start` va deep link bilan tender ma'lumotini yuboradi
- [ ] Deadline notification Celery task ishlaydi
- [ ] PDF export yuklab olinadi, format to'g'ri
- [ ] Excel export yuklab olinadi

---

## FAZA 6 — Enterprise, Test va MVP Tayyor (2 kun)

---

### 6.1. Enterprise: Jamoa Boshqaruvi (DESIGN.md §13)

`TeamWorkspacePage.jsx` (mavjud) Plan.md §7 bilan to'liq moslashtiriladi:

```
Backend:
  POST /api/v1/teams/invite/       ← email orqali taklif
  PATCH /api/v1/teams/{id}/role/   ← rol o'zgartirish
  DELETE /api/v1/teams/{id}/       ← a'zo chiqarish

Frontend:
  MemberCard (rol, holat: Faol / ⏳ Kutilmoqda)
  RoleMatrix jadvali (kim nimani qila oladi)
  TaskBoard (lot bo'yicha vazifalar)
```

Rollar: Owner | Manager | Analyst | Viewer — DESIGN.md §13 matritsasiga ko'ra.

---

### 6.2. Enterprise: Raqobatchilar — `CompetitorsPage.jsx` — YANGI

```
URL: /competitors
DESIGN.md §14
```

`competitors/` moduli va `views.py` mavjud — frontendga ulash:

```jsx
<AppLayout>
  <SubscriptionGate feature="competitor_analysis" requiredPlan="enterprise">
    <CompetitorsPage>
      <CompetitorSearch />         ← STIR bo'yicha qidirish
      <CompetitorList />           ← Qo'shilgan raqobatchilar
      <CompetitorDetail>
        <WinRateChart />           ← G'alaba statistikasi
        <CategoryBreakdown />      ← Kategoriya bo'yicha
        <PriceTrend />             ← Narx trend
      </CompetitorDetail>
    </CompetitorsPage>
  </SubscriptionGate>
</AppLayout>
```

---

### 6.3. Performance va Monitoring

```
Backend:
  - EXPLAIN ANALYZE: TenderLot ILIKE qidiruv ≤ 300ms (Plan.md SLO)
  - AI tahlil p95 ≤ 15 soniya
  - Error logging: JSON formatter, rotating file handler
  - Celery task failure: admin email alert

Frontend:
  - React ErrorBoundary komponenti
  - Lighthouse: Performance ≥ 90 (lazy loading allaqachon bor)
  - apiClient interceptor: 5xx → Toast xabari + Sentry (ixtiyoriy)
```

---

### 6.4. Docker Compose

```yaml
version: '3.9'
services:
  postgres:
    image: pgvector/pgvector:pg16
    volumes: [postgres_data:/var/lib/postgresql/data]
    environment: {POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD}

  redis:
    image: redis:7-alpine

  backend:
    build: ./backend
    command: gunicorn core.wsgi -b 0.0.0.0:8000
    depends_on: [postgres, redis]
    env_file: .env

  worker:
    build: ./backend
    command: celery -A core worker -l info
    depends_on: [backend, redis]

  beat:
    build: ./backend
    command: celery -A core beat -l info
    depends_on: [backend, redis]

  telegram:
    build: ./backend
    command: python -m telegram.bot
    depends_on: [backend, redis]

  frontend:
    build: ./frontend
    ports: ["3000:80"]
```

---

### FAZA 6 Exit Criteria
- [ ] `docker compose up` bir buyruq bilan barcha servislar ishlaydi
- [ ] Demo foydalanuvchi: Register → OTP → Kompaniya → Tarif → Dashboard → Tender → Tahlil
- [ ] Pro foydalanuvchi: Yuqoridagi + Chat + Export
- [ ] Enterprise: Yuqoridagi + Jamoa + Raqobatchilar
- [ ] Plan.md §23 SLO tekshiruvi o'tdi
- [ ] Error holatlari uchun to'g'ri xabar va recovery ko'rsatiladi

---

## Muhim Qoidalar (Barcha Fazalar Uchun)

### Kod Sifati
```
✅ Har bir komponent DESIGN.md §1.3 ga mos
✅ AppLayout barcha private sahifalarda ishlatiladi
✅ SubscriptionGate Pro/Enterprise funksiyalarda ishlatiladi
✅ API xatosi → Toast + error state (soxta natija emas)
✅ Bo'sh holat (Empty State) har bir ro'yxatda bor
```

### Taqiqlar
```
❌ AllowAny — faqat IsAuthenticated yoki IsAuthenticatedOrReadOnly
❌ Mock fallback — AI xatosi → FAILED status
❌ print() — faqat logging
❌ Hardcode model nomi — faqat settings.GEMINI_MODEL_ANALYSIS
❌ Hardcode narx formulasi — faqat settings.VAT_RATE, OPERATOR_FEE_RATE
```

### Git Commit Qoidalari
```
feat(scope): yangi funksiya
fix(scope): xato tuzatish
refactor(scope): kod qayta tuzish
style(scope): vizual o'zgarish
test(scope): test qo'shish
docs: hujjat yangilash
```

### Tarif ↔ Funksiya Moslik
```
Funksiya                  Free    Pro    Enterprise
─────────────────────────────────────────────────
AI tahlil                 4/oy   ♾      ♾
Tenderlarni ko'rish       ✅     ✅     ✅
Kengaytirilgan filtrlar   🔴     ✅     ✅
AI Chat                   🔴     ✅     ✅
Telegram bildirish        🔴     ✅     ✅
PDF/Excel export          🔴     ✅     ✅
Tahlil tarixi             🔴     ✅     ✅
Jamoa (5 nafar)           🔴     🔴     ✅
Raqobat tahlili           🔴     🔴     ✅
API kirish                🔴     🔴     ✅
```

---

## Umumiy Progress Jadvali

| Faza | Davomiyligi | Maqsad | Exit Status |
|------|-------------|--------|-------------|
| **FAZA 1** | 2–3 kun | Backend Adapter + Chat + Kalkulyator | ⬜ |
| **FAZA 2** | 2–3 kun | UI Kutubxona + AppLayout + API Klientlar | ⬜ |
| **FAZA 3** | 3–4 kun | Asosiy 9+ Sahifa | ⬜ |
| **FAZA 4** | 2 kun | AI Chat UI + Upload + Sozlamalar | ⬜ |
| **FAZA 5** | 3–4 kun | To'lov + Telegram + Export | ⬜ |
| **FAZA 6** | 2 kun | Enterprise + Test + Monitoring | ⬜ |
| **JAMI** | **~14–18 kun** | **MVP Production Ready** | |

---

*Bu hujjat — `ROADMAP.md` — loyihaning yagona yo'l xaritasi.*
*Plan.md strategiya, DESIGN.md dizayn, ROADMAP.md ish tartibi.*
*Ziddiyat bo'lsa → ROADMAP.md ni yangilang, Plan.md bilan muvofiqlang.*
