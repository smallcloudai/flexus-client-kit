# План рефакторинга Facebook интеграции

## Цель
Перенести файлы FB интеграции из бота admonster в client_kit с организацией "на выставку лучших практик".

## Текущая структура (AS-IS)

```
flexus_client_kit/integrations/
└── fi_facebook.py                    # Базовая интеграция (IntegrationFacebook)

flexus_simple_bots/admonster/integrations/
├── __init__.py                       # dispatch_facebook_operation()
├── fb_utils.py                       # Утилиты, ошибки, валидация
├── fb_ad_account.py                  # Операции с Ad Accounts
├── fb_campaign.py                    # Расширенные операции с кампаниями
├── fb_adset.py                       # Операции с Ad Sets
└── fb_creative.py                    # Креативы и Ads

flexus_simple_bots/admonster/docs/
├── FACEBOOK_TOOLS.md                 # Документация операций
└── facebook-api-reference.md         # Справка по API
```

## Целевая структура (TO-BE)

```
flexus_client_kit/integrations/facebook/
├── __init__.py                       # Публичный API, re-exports
├── client.py                         # FacebookAdsClient (HTTP клиент + auth)
├── models.py                         # Pydantic models (Campaign, AdSet, Ad, etc.)
├── exceptions.py                     # FacebookAPIError и обработка ошибок
├── utils.py                          # Валидация, форматирование, хелперы
├── operations/
│   ├── __init__.py                   # dispatch_operation()
│   ├── accounts.py                   # list_ad_accounts, get_account_info, update_spending_limit
│   ├── campaigns.py                  # CRUD + bulk operations
│   ├── adsets.py                     # CRUD + validate_targeting
│   └── ads.py                        # upload_image, create_creative, create_ad, preview_ad
└── testing/
    ├── __init__.py
    ├── mocks.py                      # Mock data generators
    └── fixtures.py                   # Pytest fixtures

flexus_client_kit/integrations/facebook/docs/
├── README.md                         # Обзор интеграции
├── operations.md                     # Документация операций (из FACEBOOK_TOOLS.md)
└── api-reference.md                  # Справка по Facebook API

flexus_client_kit/integrations/
└── fi_facebook.py                    # Удалить или оставить как thin re-export
```

## Задачи

### 1. Подготовка структуры
- [ ] Создать директорию `facebook/` в integrations
- [ ] Создать поддиректории `operations/`, `testing/`, `docs/`
- [ ] Создать `__init__.py` файлы

### 2. Pydantic Models (`models.py`)
- [ ] `Campaign` - модель кампании с валидацией
- [ ] `AdSet` - модель ad set с targeting валидацией
- [ ] `Ad` - модель объявления
- [ ] `Creative` - модель креатива
- [ ] `AdAccount` - модель ad account
- [ ] `Insights` - модель метрик
- [ ] `TargetingSpec` - модель таргетинга с вложенными типами
- [ ] `FacebookAPIResponse` - generic response wrapper

### 3. Exceptions (`exceptions.py`)
- [ ] `FacebookAPIError` - перенести из fb_utils.py
- [ ] `FacebookAuthError` - для ошибок аутентификации
- [ ] `FacebookValidationError` - для ошибок валидации
- [ ] `FacebookRateLimitError` - для rate limiting
- [ ] `handle_api_error()` - парсинг ошибок FB API

### 4. Utils (`utils.py`)
- [ ] `validate_ad_account_id()` - валидация act_ формата
- [ ] `validate_budget()` - валидация бюджета
- [ ] `validate_targeting_spec()` - валидация таргетинга
- [ ] `format_currency()` - форматирование валюты
- [ ] `parse_date_preset()` - валидация date presets
- [ ] `normalize_insights_data()` - нормализация метрик
- [ ] `hash_for_audience()` - хэширование PII

### 5. HTTP Client (`client.py`)
- [ ] `FacebookAdsClient` class:
  - `__init__(fclient, rcx, ad_account_id)` - инициализация
  - `async ensure_auth()` - получение токена
  - `async request(method, endpoint, ...)` - универсальный HTTP запрос
  - `async get(...)`, `async post(...)` - удобные методы
  - Rate limiting и retry logic
  - Поддержка test mode (is_fake)

### 6. Operations (`operations/`)

#### accounts.py
- [ ] `list_ad_accounts(client)` - список аккаунтов
- [ ] `get_ad_account_info(client, ad_account_id)` - детали аккаунта
- [ ] `update_spending_limit(client, ad_account_id, limit)` - обновление лимита

#### campaigns.py
- [ ] `list_campaigns(client, status_filter)` - список кампаний
- [ ] `create_campaign(client, campaign: Campaign)` - создание
- [ ] `update_campaign(client, campaign_id, updates)` - обновление
- [ ] `duplicate_campaign(client, campaign_id, new_name)` - дублирование
- [ ] `archive_campaign(client, campaign_id)` - архивация
- [ ] `bulk_update_campaigns(client, campaigns)` - массовое обновление
- [ ] `get_insights(client, campaign_id, days)` - метрики

#### adsets.py
- [ ] `list_adsets(client, campaign_id)` - список ad sets
- [ ] `create_adset(client, adset: AdSet)` - создание
- [ ] `update_adset(client, adset_id, updates)` - обновление
- [ ] `validate_targeting(client, targeting_spec)` - валидация

#### ads.py
- [ ] `upload_image(client, image_path_or_url)` - загрузка изображения
- [ ] `create_creative(client, creative: Creative)` - создание креатива
- [ ] `create_ad(client, ad: Ad)` - создание объявления
- [ ] `preview_ad(client, ad_id, format)` - превью

### 7. Dispatcher (`operations/__init__.py`)
- [ ] `dispatch_operation(client, op, args)` - маршрутизация операций
- [ ] Маппинг operation name → handler function

### 8. Testing (`testing/`)

#### mocks.py
- [ ] `MockFacebookClient` - мок клиента для тестов
- [ ] `generate_mock_campaign()` - генератор mock кампании
- [ ] `generate_mock_adset()` - генератор mock ad set
- [ ] `generate_mock_ad()` - генератор mock объявления
- [ ] `generate_mock_insights()` - генератор mock метрик
- [ ] `generate_mock_ad_account()` - генератор mock аккаунта

#### fixtures.py
- [ ] `@pytest.fixture facebook_client` - фикстура клиента
- [ ] `@pytest.fixture mock_campaign` - фикстура кампании
- [ ] `@pytest.fixture mock_adset` - фикстура ad set

### 9. Тесты (`test_facebook.py` в корне integrations)
- [ ] `test_models.py` - тесты Pydantic моделей
- [ ] `test_utils.py` - тесты утилит
- [ ] `test_operations_accounts.py` - тесты операций с аккаунтами
- [ ] `test_operations_campaigns.py` - тесты операций с кампаниями
- [ ] `test_operations_adsets.py` - тесты операций с ad sets
- [ ] `test_operations_ads.py` - тесты операций с объявлениями
- [ ] `test_client.py` - тесты HTTP клиента
- [ ] `test_integration.py` - интеграционные тесты (с моками)

### 10. Публичный API (`__init__.py`)
- [ ] Re-export основных классов и функций:
  ```python
  from .client import FacebookAdsClient
  from .models import Campaign, AdSet, Ad, Creative, Insights, TargetingSpec
  from .exceptions import FacebookAPIError
  from .operations import dispatch_operation

  # Tool definition for AI model
  FACEBOOK_TOOL = CloudTool(...)

  # Main integration class (wrapper for bot usage)
  class IntegrationFacebook:
      ...
  ```

### 11. Документация (`docs/`)
- [ ] `README.md` - обзор, quick start
- [ ] `operations.md` - перенести из FACEBOOK_TOOLS.md
- [ ] `api-reference.md` - перенести из facebook-api-reference.md

### 12. Обновление admonster бота
- [ ] Обновить импорты в `admonster_bot.py`
- [ ] Удалить `admonster/integrations/fb_*.py`
- [ ] Удалить `admonster/integrations/__init__.py` (dispatch)
- [ ] Удалить `admonster/docs/FACEBOOK_*.md`

### 13. Удаление старого кода
- [ ] Удалить `fi_facebook.py` из корня integrations (код переехал в пакет)
- [ ] Или оставить как thin re-export для обратной совместимости (если нужно)

## Архитектурные решения

### Pydantic Models
```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from enum import Enum

class CampaignObjective(str, Enum):
    TRAFFIC = "OUTCOME_TRAFFIC"
    SALES = "OUTCOME_SALES"
    ENGAGEMENT = "OUTCOME_ENGAGEMENT"
    AWARENESS = "OUTCOME_AWARENESS"
    LEADS = "OUTCOME_LEADS"
    APP_PROMOTION = "OUTCOME_APP_PROMOTION"

class CampaignStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    ARCHIVED = "ARCHIVED"

class Campaign(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=400)
    objective: CampaignObjective
    status: CampaignStatus = CampaignStatus.PAUSED
    daily_budget: Optional[int] = Field(None, ge=100)  # cents, min $1
    lifetime_budget: Optional[int] = Field(None, ge=100)
    special_ad_categories: List[str] = Field(default_factory=list)

    @field_validator('daily_budget', 'lifetime_budget')
    @classmethod
    def validate_budget(cls, v):
        if v is not None and v < 100:
            raise ValueError('Budget must be at least 100 cents ($1.00)')
        return v
```

### Client Pattern
```python
class FacebookAdsClient:
    def __init__(self, fclient, rcx, ad_account_id: str):
        self.fclient = fclient
        self.rcx = rcx
        self.ad_account_id = validate_ad_account_id(ad_account_id)
        self._access_token: Optional[str] = None
        self._headers: Dict[str, str] = {}

    @property
    def is_test_mode(self) -> bool:
        return self.rcx.running_test_scenario

    async def ensure_auth(self) -> None:
        if self.is_test_mode:
            return
        if not self._access_token:
            self._access_token = await self._fetch_token()
            self._headers = {"Authorization": f"Bearer {self._access_token}"}

    async def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        await self.ensure_auth()
        if self.is_test_mode:
            return self._mock_response(endpoint)
        return await self._make_request(method, endpoint, **kwargs)
```

### Operation Pattern
```python
# operations/campaigns.py
from ..client import FacebookAdsClient
from ..models import Campaign
from ..exceptions import FacebookValidationError

async def create_campaign(client: FacebookAdsClient, campaign: Campaign) -> Campaign:
    """Create a new campaign."""
    if client.is_test_mode:
        return Campaign(id="mock_123", **campaign.model_dump(exclude={'id'}))

    response = await client.post(
        f"{client.ad_account_id}/campaigns",
        data=campaign.model_dump(exclude_none=True, by_alias=True)
    )
    return Campaign(id=response["id"], **campaign.model_dump(exclude={'id'}))
```

## Порядок выполнения

1. **Фаза 1: Структура и модели** (первый PR)
   - Создать структуру папок
   - Написать Pydantic models
   - Написать exceptions
   - Написать utils

2. **Фаза 2: Клиент и операции** (второй PR)
   - Написать FacebookAdsClient
   - Перенести операции из fb_*.py
   - Написать dispatcher

3. **Фаза 3: Тесты** (третий PR)
   - Написать unit тесты для моделей
   - Написать unit тесты для utils
   - Написать integration тесты с моками

4. **Фаза 4: Интеграция и cleanup** (четвёртый PR)
   - Обновить admonster_bot.py
   - Удалить старые файлы
   - Перенести документацию

## Риски и митигации

| Риск | Митигация |
|------|-----------|
| Сломается admonster | Постепенный перенос, сначала работает старый код |
| Несовместимость API | Сохранить те же сигнатуры функций |
| Пропущенные edge cases | Покрыть тестами все текущие mock сценарии |

## Definition of Done
- [ ] Весь код из admonster/integrations/fb_*.py перенесён
- [ ] Pydantic models для всех сущностей
- [ ] Unit тесты с coverage > 80%
- [ ] Integration тесты проходят
- [ ] Документация актуальна
- [ ] admonster бот работает с новой интеграцией
- [ ] Старые файлы удалены
