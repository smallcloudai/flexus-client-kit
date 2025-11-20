# Facebook Ads Complete Integration - Implementation Plan

## Общий обзор

**Цель:** Добавить в Ad Monster полноценную работу с Facebook Marketing API для создания и управления рекламными кабинетами, кампаниями, ad sets и креативами.

**Текущее состояние:**
- ✅ Базовая интеграция с Facebook Graph API (fi_facebook.py)
- ✅ Создание и просмотр кампаний
- ✅ Базовые insights
- ❌ Создание рекламных кабинетов
- ❌ Управление Ad Sets (таргетинг, расписание)
- ❌ Создание и управление креативами (Ads)
- ❌ Работа с пикселями, конверсиями
- ❌ Custom Audiences, Lookalike Audiences
- ❌ Расширенная аналитика и автоматизация

---

## Архитектура решения

### Структура файлов (новые)

```
flexus_simple_bots/admonster/
├── docs/
│   ├── facebook-ads-implementation-plan.md        (этот файл)
│   ├── facebook-api-reference.md                   (справочник по API endpoints)
│   └── testing-scenarios.md                        (тестовые сценарии)
├── integrations/
│   ├── __init__.py
│   ├── fb_ad_account.py       [AGENT 1]   # Ad Account management
│   ├── fb_campaign.py         [AGENT 2]   # Campaign management (расширение)
│   ├── fb_adset.py            [AGENT 3]   # Ad Set creation & targeting
│   ├── fb_creative.py         [AGENT 4]   # Creatives & Ads
│   ├── fb_insights.py         [AGENT 5]   # Advanced analytics & reporting
│   ├── fb_audience.py         [AGENT 6]   # Custom/Lookalike audiences
│   └── fb_utils.py            [AGENT 7]   # Shared utilities & error handling
└── admonster_bot.py                       # Updated integration points
```

**Важно:** Каждый модуль - независимый, может разрабатываться параллельно разными агентами.

---

## Разбивка по агентам (Parallel Development)

### AGENT 1: Ad Account Management (`fb_ad_account.py`)

**Зона ответственности:**
- Создание рекламных кабинетов (Ad Accounts)
- Просмотр списка кабинетов
- Настройка лимитов и бюджетов на уровне аккаунта
- Управление пользователями и правами доступа

**API Endpoints:**
- `GET /me/adaccounts` - список кабинетов
- `GET /{ad_account_id}` - детали кабинета
- `POST /{business_id}/adaccounts` - создание кабинета (требует Business Manager)
- `GET /{ad_account_id}/users` - пользователи
- `POST /{ad_account_id}/users` - добавить пользователя

**Операции для бота:**
```python
facebook(op="list_ad_accounts")
facebook(op="get_ad_account_info", args={"ad_account_id": "act_123"})
facebook(op="create_ad_account", args={
    "business_id": "123456",
    "name": "My Ad Account",
    "currency": "USD",
    "timezone_id": 1,
    "end_advertiser_id": "..."
})
facebook(op="update_ad_account_spending_limit", args={
    "ad_account_id": "act_123",
    "spending_limit": 10000
})
```

**Зависимости:** Только базовый Graph API клиент (httpx)

**Сложность:** Medium  
**Приоритет:** HIGH (нужно для всего остального)

---

### AGENT 2: Campaign Management Extended (`fb_campaign.py`)

**Зона ответственности:**
- Расширение существующей функциональности кампаний
- Добавление недостающих операций (update, pause, archive)
- Работа со специальными категориями (housing, credit, employment)
- Bulk operations (массовые операции)

**API Endpoints:**
- `POST /{ad_account_id}/campaigns` - создание (уже есть, расширяем)
- `POST /{campaign_id}` - обновление кампании
- `DELETE /{campaign_id}` - удаление
- `POST /{ad_account_id}/campaigns` (batch) - массовые операции

**Операции для бота:**
```python
facebook(op="update_campaign", args={
    "campaign_id": "123",
    "status": "PAUSED",
    "name": "New Name",
    "daily_budget": 7500
})
facebook(op="duplicate_campaign", args={
    "campaign_id": "123",
    "new_name": "Copy of Campaign"
})
facebook(op="archive_campaign", args={"campaign_id": "123"})
facebook(op="bulk_update_campaigns", args={
    "campaigns": [
        {"id": "123", "status": "PAUSED"},
        {"id": "456", "status": "ACTIVE"}
    ]
})
```

**Зависимости:** 
- Базовая интеграция `fi_facebook.py` (рефакторинг)
- `fb_utils.py` для error handling

**Сложность:** Low-Medium  
**Приоритет:** HIGH (дополняем базовую функциональность)

---

### AGENT 3: Ad Set Management (`fb_adset.py`)

**Зона ответственности:**
- Создание и управление Ad Sets
- Настройка таргетинга (geo, demo, interests, behaviors)
- Расписание показов (day parting)
- Placement (где показывать: Facebook, Instagram, Messenger, Audience Network)
- Оптимизация и стратегии ставок

**API Endpoints:**
- `POST /{ad_account_id}/adsets` - создание
- `GET /{campaign_id}/adsets` - список ad sets в кампании
- `GET /{adset_id}` - детали ad set
- `POST /{adset_id}` - обновление
- `GET /{ad_account_id}/targetingsentencelines` - валидация таргетинга

**Операции для бота:**
```python
facebook(op="create_adset", args={
    "campaign_id": "123",
    "name": "US 25-45 Tech Interests",
    "optimization_goal": "LINK_CLICKS",
    "billing_event": "IMPRESSIONS",
    "bid_amount": 150,  # cents
    "daily_budget": 5000,  # cents
    "targeting": {
        "geo_locations": {"countries": ["US"]},
        "age_min": 25,
        "age_max": 45,
        "interests": [{"id": "6003139266461", "name": "Technology"}],
        "device_platforms": ["mobile", "desktop"]
    },
    "start_time": "2025-01-01T00:00:00",
    "end_time": "2025-12-31T23:59:59"
})
facebook(op="list_adsets", args={"campaign_id": "123"})
facebook(op="update_adset", args={
    "adset_id": "456",
    "status": "PAUSED",
    "daily_budget": 7500
})
facebook(op="validate_targeting", args={
    "targeting_spec": {...}
})
```

**Зависимости:** 
- `fb_campaign.py` (ad sets принадлежат кампаниям)
- `fb_utils.py` для targeting validation

**Сложность:** HIGH (таргетинг очень сложный)  
**Приоритет:** HIGH (критично для запуска рекламы)

---

### AGENT 4: Creative & Ads Management (`fb_creative.py`)

**Зона ответственности:**
- Создание креативов (AdCreative)
- Создание объявлений (Ads)
- Работа с медиа (картинки, видео)
- Форматы объявлений (single image, carousel, video, collection)
- Preview URLs для проверки

**API Endpoints:**
- `POST /{ad_account_id}/adcreatives` - создание креатива
- `POST /{ad_account_id}/ads` - создание объявления
- `GET /{ad_id}` - детали объявления
- `POST /{ad_id}` - обновление
- `GET /{ad_id}/previews` - превью объявления
- `POST /{ad_account_id}/adimages` - загрузка картинок
- `POST /{ad_account_id}/advideos` - загрузка видео

**Операции для бота:**
```python
facebook(op="upload_image", args={
    "ad_account_id": "act_123",
    "image_path": "/path/to/image.jpg"
})
facebook(op="create_creative", args={
    "ad_account_id": "act_123",
    "name": "Summer Sale Creative",
    "object_story_spec": {
        "page_id": "123456",
        "link_data": {
            "image_hash": "abc123",
            "link": "https://example.com",
            "message": "Check out our summer sale!",
            "call_to_action": {"type": "SHOP_NOW"}
        }
    }
})
facebook(op="create_ad", args={
    "adset_id": "456",
    "creative_id": "789",
    "name": "Ad 1",
    "status": "PAUSED"
})
facebook(op="preview_ad", args={
    "ad_id": "999",
    "ad_format": "DESKTOP_FEED_STANDARD"
})
```

**Зависимости:**
- `fb_adset.py` (ads принадлежат ad sets)
- `fb_utils.py` для работы с медиа

**Сложность:** HIGH (много форматов, медиа)  
**Приоритет:** HIGH (без этого реклама не запустится)

---

### AGENT 5: Advanced Analytics (`fb_insights.py`)

**Зона ответственности:**
- Расширенные insights (больше метрик)
- Breakdown по различным измерениям (age, gender, placement, device)
- Отчеты за период
- Автоматические алерты (низкий CTR, высокий CPC, etc)
- Export в CSV/PDF через report system

**API Endpoints:**
- `GET /{object_id}/insights` - insights с breakdowns
- `POST /{ad_account_id}/insights` - async reporting
- `GET /{ad_account_id}/insights` - async report status

**Операции для бота:**
```python
facebook(op="get_detailed_insights", args={
    "campaign_id": "123",
    "date_preset": "last_7d",
    "level": "ad",  # campaign, adset, ad
    "breakdowns": ["age", "gender", "placement"],
    "fields": [
        "impressions", "clicks", "spend", "reach",
        "frequency", "ctr", "cpc", "cpm", "cpp",
        "actions", "conversions", "cost_per_action"
    ]
})
facebook(op="create_async_report", args={
    "ad_account_id": "act_123",
    "time_range": {"since": "2025-01-01", "until": "2025-01-31"},
    "level": "campaign",
    "filtering": [{"field": "spend", "operator": "GREATER_THAN", "value": "100"}]
})
facebook(op="export_insights_to_csv", args={
    "campaign_id": "123",
    "filename": "campaign_report.csv"
})
facebook(op="setup_performance_alert", args={
    "campaign_id": "123",
    "conditions": [
        {"metric": "ctr", "operator": "less_than", "value": 0.5},
        {"metric": "spend", "operator": "greater_than", "value": 1000}
    ],
    "action": "pause_campaign"  # or "notify"
})
```

**Зависимости:**
- Все модули кампаний/adsets/ads
- `ckit_schedule.py` для периодических проверок
- `fi_report.py` для экспорта отчетов

**Сложность:** MEDIUM-HIGH  
**Приоритет:** MEDIUM (после основного функционала)

---

### AGENT 6: Audience Management (`fb_audience.py`)

**Зона ответственности:**
- Custom Audiences (загрузка клиентов, посетителей сайта)
- Lookalike Audiences (похожие аудитории)
- Saved Audiences (сохраненные настройки таргетинга)
- Работа с Facebook Pixel
- Конверсии и custom conversions

**API Endpoints:**
- `POST /{ad_account_id}/customaudiences` - создание custom audience
- `POST /{custom_audience_id}/users` - добавление пользователей
- `POST /{ad_account_id}/customaudiences` (lookalike) - lookalike audience
- `GET /{ad_account_id}/savedaudiences` - список сохраненных
- `POST /{ad_account_id}/pixels` - создание пикселя
- `GET /{pixel_id}/stats` - статистика пикселя

**Операции для бота:**
```python
facebook(op="create_custom_audience", args={
    "ad_account_id": "act_123",
    "name": "Website Visitors",
    "subtype": "WEBSITE",
    "customer_file_source": "USER_PROVIDED_ONLY"
})
facebook(op="add_users_to_audience", args={
    "audience_id": "123",
    "schema": ["EMAIL", "PHONE"],
    "data": [
        ["email1@example.com", "+1234567890"],
        ["email2@example.com", "+0987654321"]
    ]
})
facebook(op="create_lookalike_audience", args={
    "ad_account_id": "act_123",
    "origin_audience_id": "123",
    "name": "Lookalike 1%",
    "target_countries": ["US"],
    "ratio": 0.01  # 1% similarity
})
facebook(op="create_pixel", args={
    "ad_account_id": "act_123",
    "name": "Website Pixel"
})
facebook(op="get_pixel_stats", args={"pixel_id": "456"})
```

**Зависимости:**
- `fb_ad_account.py` (audiences привязаны к аккаунту)
- `fb_utils.py` для хеширования данных (PII)

**Сложность:** MEDIUM-HIGH  
**Приоритет:** MEDIUM (важно, но можно после основного функционала)

---

### AGENT 7: Shared Utilities (`fb_utils.py`)

**Зона ответственности:**
- Error handling и retry logic
- Rate limiting management
- Валидация параметров
- Хеширование PII (email, phone) для audiences
- Форматирование данных для API
- Логирование и debugging
- Mock data для тестирования

**Функции:**
```python
# Error handling
async def handle_fb_api_error(response: httpx.Response) -> str
async def retry_with_backoff(func, max_retries=3)

# Validation
def validate_budget(budget: int, currency: str = "USD") -> bool
def validate_targeting_spec(spec: dict) -> tuple[bool, str]
def validate_ad_account_id(ad_account_id: str) -> str  # ensure "act_" prefix

# Data formatting
def format_currency(cents: int, currency: str = "USD") -> str
def parse_date_range(date_preset: str) -> dict
def normalize_insights_data(raw_data: dict) -> dict

# PII hashing (for Custom Audiences)
def hash_email(email: str) -> str
def hash_phone(phone: str) -> str

# Rate limiting
class RateLimiter:
    async def wait_if_needed()
    def update_from_headers(headers: dict)

# Mock для тестов
def generate_mock_campaign() -> dict
def generate_mock_insights() -> dict
```

**Зависимости:** Нет (используется всеми остальными)

**Сложность:** MEDIUM  
**Приоритет:** HIGH (начать первым, нужно всем)

---

## План внедрения (Roadmap)

### Фаза 0: Подготовка (Week 1)
- [ ] **AGENT 7** Создать `fb_utils.py` с базовыми утилитами
- [ ] Обновить `fi_facebook.py` с использованием `fb_utils.py`
- [ ] Настроить Facebook App в Facebook Developers
- [ ] Получить test ad account для разработки
- [ ] Создать тестовые сценарии

### Фаза 1: Core Functionality (Week 2-3)
**Параллельно:**
- [ ] **AGENT 1** Реализовать `fb_ad_account.py`
- [ ] **AGENT 2** Расширить `fb_campaign.py`
- [ ] **AGENT 3** Реализовать `fb_adset.py`
- [ ] **AGENT 4** Реализовать `fb_creative.py`

**Тестирование:** End-to-end тест создания полного потока (account → campaign → adset → ad)

### Фаза 2: Advanced Features (Week 4)
**Параллельно:**
- [ ] **AGENT 5** Реализовать `fb_insights.py`
- [ ] **AGENT 6** Реализовать `fb_audience.py`

**Интеграция с Flexus:**
- [ ] Подключить к ckit_schedule для автоматических проверок
- [ ] Интеграция с fi_report для экспорта отчетов
- [ ] Настроить алерты через Slack/Discord

### Фаза 3: Polish & Automation (Week 5)
- [ ] Автоматические A/B тесты
- [ ] Smart optimization (ML recommendations)
- [ ] Документация для пользователей
- [ ] Tutorial scenarios

---

## Интеграция с существующим кодом

### Обновление `admonster_bot.py`

```python
# Add new imports
from flexus_simple_bots.admonster.integrations import fb_ad_account
from flexus_simple_bots.admonster.integrations import fb_campaign
from flexus_simple_bots.admonster.integrations import fb_adset
from flexus_simple_bots.admonster.integrations import fb_creative
from flexus_simple_bots.admonster.integrations import fb_insights
from flexus_simple_bots.admonster.integrations import fb_audience

# Update tool registration
@rcx.on_tool_call(fi_facebook.FACEBOOK_TOOL.name)
async def toolcall_facebook(toolcall, model_produced_args):
    try:
        # Router to appropriate module based on operation
        op = model_produced_args.get("op", "")
        
        if op.startswith("ad_account_"):
            return await fb_ad_account.handle(facebook_integration, toolcall, model_produced_args)
        elif op.startswith("campaign_"):
            return await fb_campaign.handle(facebook_integration, toolcall, model_produced_args)
        elif op.startswith("adset_"):
            return await fb_adset.handle(facebook_integration, toolcall, model_produced_args)
        elif op.startswith("creative_") or op.startswith("ad_"):
            return await fb_creative.handle(facebook_integration, toolcall, model_produced_args)
        elif op.startswith("insights_") or op.startswith("report_"):
            return await fb_insights.handle(facebook_integration, toolcall, model_produced_args)
        elif op.startswith("audience_") or op.startswith("pixel_"):
            return await fb_audience.handle(facebook_integration, toolcall, model_produced_args)
        else:
            # Fallback to existing integration
            return await facebook_integration.called_by_model(toolcall, model_produced_args)
    except Exception as e:
        logger.error(f"Facebook tool error: {e}")
        return f"ERROR: {str(e)}"
```

### Обновление `admonster_prompts.py`

Добавить описание новых операций в промпт:

```python
admonster_prompt = f"""
You are Ad Monster, a Facebook/LinkedIn advertising campaign management assistant.

Facebook Ads Operations:

AD ACCOUNT MANAGEMENT:
- facebook(op="list_ad_accounts") - List all ad accounts
- facebook(op="get_ad_account_info", args={{"ad_account_id": "act_123"}}) - Get account details
- facebook(op="create_ad_account", ...) - Create new ad account (requires Business Manager)

CAMPAIGN MANAGEMENT:
- facebook(op="status") - Overview of all campaigns
- facebook(op="create_campaign", ...) - Create campaign
- facebook(op="update_campaign", ...) - Update campaign (budget, status, name)
- facebook(op="duplicate_campaign", ...) - Duplicate existing campaign

AD SET MANAGEMENT:
- facebook(op="create_adset", ...) - Create ad set with targeting
- facebook(op="list_adsets", args={{"campaign_id": "123"}}) - List ad sets
- facebook(op="update_adset", ...) - Update ad set
- facebook(op="validate_targeting", ...) - Validate targeting before creating

CREATIVE & ADS:
- facebook(op="upload_image", ...) - Upload image for ads
- facebook(op="create_creative", ...) - Create ad creative
- facebook(op="create_ad", ...) - Create ad from creative
- facebook(op="preview_ad", ...) - Preview how ad looks

ANALYTICS:
- facebook(op="get_detailed_insights", ...) - Advanced insights with breakdowns
- facebook(op="export_insights_to_csv", ...) - Export report to CSV

AUDIENCES:
- facebook(op="create_custom_audience", ...) - Create custom audience
- facebook(op="create_lookalike_audience", ...) - Create lookalike audience
- facebook(op="create_pixel", ...) - Create Facebook Pixel

Best practices:
- Always start campaigns in PAUSED status
- Use validate_targeting before creating ad sets
- Monitor insights regularly and optimize
- Use preview_ad before activating ads
...
"""
```

---

## Тестирование

### Unit Tests
Каждый модуль должен иметь:
- `tests/test_fb_ad_account.py`
- `tests/test_fb_campaign.py`
- etc.

### Integration Tests
- `tests/test_full_campaign_flow.py` - создание кампании от начала до конца
- `tests/test_error_handling.py` - проверка обработки ошибок

### Scenario Tests (через Flexus)
- `admonster_scenario_create_campaign.yaml`
- `admonster_scenario_optimize_campaign.yaml`

---

## Безопасность и лимиты

### Rate Limits (Facebook Marketing API)
- Graph API: 200 calls per hour per user (может варьироваться)
- Ads API: Different limits per endpoint
- Batch requests: до 50 операций за раз

**Решение:** Использовать `RateLimiter` из `fb_utils.py`

### Permissions (Scopes)
Требуемые разрешения:
- `ads_management` - создание и управление рекламой
- `ads_read` - чтение данных
- `read_insights` - доступ к insights
- `business_management` - управление Business Manager (для создания ad accounts)

### Error Handling
- Всегда оборачивать API calls в try-except
- Логировать ошибки с контекстом
- Возвращать понятные сообщения пользователю
- Retry с exponential backoff для transient errors

---

## Метрики успеха

После внедрения мы должны иметь возможность:

1. ✅ Создать полную рекламную кампанию в Facebook одной командой в чат
2. ✅ Автоматически останавливать неэффективные кампании (по заданным критериям)
3. ✅ Получать еженедельные отчеты по всем кампаниям
4. ✅ Создавать A/B тесты автоматически
5. ✅ Масштабировать успешные кампании
6. ✅ Создавать lookalike audiences на основе конверсий

---

## Риски и митигация

### Риск 1: Facebook API нестабилен / меняется
**Митигация:** Версионирование API (используем конкретную версию v19.0+), мониторинг changelog Facebook

### Риск 2: Rate limits
**Митигация:** RateLimiter, batch requests, кэширование данных

### Риск 3: Сложность таргетинга
**Митигация:** Валидация через `targetingsentencelines`, примеры и шаблоны в промптах

### Риск 4: Ошибки в production
**Митигация:** Always start campaigns in PAUSED, extensive testing, rollback procedures

---

## Следующие шаги

1. **Получить одобрение плана от пользователя** ⬅️ ВЫ ЗДЕСЬ
2. Настроить Facebook App и test ad account
3. Начать с AGENT 7 (fb_utils.py)
4. Параллельно запустить AGENT 1-4
5. Тестирование фазы 1
6. Запуск AGENT 5-6
7. Полное тестирование и документация

---

## Вопросы для обсуждения

1. Нужна ли поддержка Instagram (отдельные операции) или через общий Facebook API?
2. Какие автоматизации приоритетны (A/B тесты, автоостановка, масштабирование)?
3. Интеграция с другими ботами (например, Boss для отчетов, Karen для задач)?
4. Нужна ли работа с WhatsApp Business API через тот же бот?

---

**Автор:** Claude  
**Дата:** 2025-11-19  
**Версия:** 1.0

