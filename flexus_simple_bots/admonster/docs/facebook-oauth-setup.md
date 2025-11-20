# Facebook OAuth Setup - Implementation Guide

## Обзор

Flexus уже имеет полную инфраструктуру для OAuth 2.0. Нам нужно:
1. Добавить Facebook в список провайдеров в `external_oauth_source_configs.py`
2. Создать Facebook App в Facebook Developer Console
3. Настроить переменные окружения
4. Протестировать OAuth flow

---

## Часть 1: Создание Facebook App

### Шаг 1.1: Регистрация приложения

1. Перейти на https://developers.facebook.com/
2. Нажать **My Apps** → **Create App**
3. Выбрать тип приложения: **Business**
4. Заполнить:
   - **App Name:** Flexus (или ваше название)
   - **App Contact Email:** ваш email
   - **Business Account:** выбрать или создать Business Manager

### Шаг 1.2: Добавить продукты

1. В левом меню **Add Products**
2. Добавить **Facebook Login**:
   - **Valid OAuth Redirect URIs:**
     ```
     https://your-domain.com/v1/tool-oauth/facebook/callback
     http://localhost:3000/v1/tool-oauth/facebook/callback (для dev)
     ```
   - **Client OAuth Login:** Yes
   - **Web OAuth Login:** Yes
   - **Enforce HTTPS:** Yes (в продакшене)

3. Добавить **Marketing API**:
   - Нажать **Get Started**
   - Принять Terms of Service

### Шаг 1.3: Настройка разрешений

В **App Review** → **Permissions and Features** запросить:
- `ads_management` - Required для создания/управления рекламой
- `ads_read` - Required для чтения данных
- `read_insights` - Required для аналитики
- `business_management` - Optional, для управления Business Manager

**Note:** Для разработки используются standard permissions, для продакшена нужно пройти App Review.

### Шаг 1.4: Получить креденшалы

1. **Settings** → **Basic**
2. Скопировать:
   - **App ID** → это будет `FACEBOOK_CLIENT_ID`
   - **App Secret** (Show) → это будет `FACEBOOK_CLIENT_SECRET`

---

## Часть 2: Добавить Facebook в Flexus

### Шаг 2.1: Обновить `external_oauth_source_configs.py`

**Файл:** `flexus/flexus_backend/flexus_v1/external_oauth_source_configs.py`

Добавить конфигурацию Facebook после LinkedIn (строка ~196):

```python
"facebook": OAuthProviderConfig(
    oap_provider_key="facebook",
    oap_display_name="Facebook",
    oap_service_provider="facebook",
    oap_client_id_env="FACEBOOK_CLIENT_ID",
    oap_client_secret_env="FACEBOOK_CLIENT_SECRET",
    oap_authorize_url="https://www.facebook.com/v19.0/dialog/oauth",
    oap_token_url="https://graph.facebook.com/v19.0/oauth/access_token",
    oap_scope="ads_management,ads_read,read_insights",
    oap_redirect_path="/v1/tool-oauth/facebook/callback",
    oap_token_request_auth="body",  # Facebook uses body, not basic auth
    oap_post_auth_redirect_path="/profile",
    oap_auth_type="oauth2",
    oap_extra_token_params={},
    oap_token_request_headers={},
    oap_supports_refresh=True,  # Facebook supports long-lived tokens
    oap_minimum_expiry_margin=120,
    oap_scope_delimiter=",",  # Facebook uses comma, not space
    oap_extra_authorize_params={
        "auth_type": "rerequest",  # Re-request declined permissions
    },
    oap_available_scopes=(
        HumanReadableScope("ads_management", "Create and manage ads"),
        HumanReadableScope("ads_read", "Read ads data"),
        HumanReadableScope("read_insights", "Access ads analytics"),
        HumanReadableScope("business_management", "Manage Business Manager accounts"),
        HumanReadableScope("pages_show_list", "Read list of Pages managed by a person"),
        HumanReadableScope("pages_read_engagement", "Read engagement data for Pages"),
        HumanReadableScope("pages_manage_ads", "Create and manage ads for Pages"),
    ),
),
```

**Важные детали:**
- `oap_token_request_auth="body"` - Facebook отправляет client_id/secret в теле, не в Basic Auth
- `oap_scope_delimiter=","` - Facebook разделяет scopes запятыми, не пробелами
- `oap_supports_refresh=True` - Facebook поддерживает refresh (exchange short-lived → long-lived token)

### Шаг 2.2: Добавить переменные окружения

**Файл:** `.env` или переменные окружения Docker/K8s

```bash
# Facebook OAuth
FACEBOOK_CLIENT_ID=your_facebook_app_id_here
FACEBOOK_CLIENT_SECRET=your_facebook_app_secret_here
```

**Production:** Использовать secrets management (K8s secrets, AWS Secrets Manager, etc)

### Шаг 2.3: Проверить callback endpoint

Callback endpoint уже существует в `v1_external_auth_ops.py`:

```python
@tool_oauth_router.get("/{provider}/callback")
async def generic_oauth_callback(provider: str, request: Request):
    # Этот endpoint автоматически обработает Facebook callback
    # Никаких изменений не требуется
```

Этот endpoint:
1. Принимает `code` и `state` от Facebook
2. Обменивает code на access_token
3. Сохраняет токен в БД (encrypted)
4. Редиректит пользователя

---

## Часть 3: Обновить fi_facebook.py (Bot Integration)

### Шаг 3.1: Текущая реализация

Текущий `fi_facebook.py` имеет свой костыльный OAuth в `called_by_model`:

```python
# Lines 123-153 в fi_facebook.py
if not self.is_fake and not self.access_token:
    auth_searchable = hashlib.md5((self.app_id + self.ad_account_id).encode()).hexdigest()[:30]
    # ... старый код с ckit_external_auth
```

**Проблема:** Этот код дублирует логику, которая уже есть в Flexus.

### Шаг 3.2: Рефакторинг fi_facebook.py

**Цель:** Использовать стандартный Flexus OAuth flow вместо кастомного.

**Новая логика:**

```python
# fi_facebook.py - ОБНОВЛЕННАЯ ВЕРСИЯ

async def called_by_model(self, toolcall, model_produced_args):
    if not model_produced_args:
        return HELP

    # Check if we have OAuth token via Flexus external_auth
    if not self.is_fake and not self.access_token:
        # Look for existing Facebook OAuth in external_auth table
        # This is managed by Flexus frontend /profile page
        auth_record = await self._get_facebook_oauth_record()
        
        if not auth_record:
            # No Facebook auth found, prompt user to connect via UI
            web_url = os.getenv("FLEXUS_WEB_URL", "http://localhost:3000")
            connect_url = f"{web_url}/profile?connect=facebook&redirect_path=/chat/{self.rcx.thread_id}"
            
            return f"""Facebook authorization required.

Please connect your Facebook account:
{connect_url}

After connecting, try your request again."""
        
        # Get access token from auth record
        self.access_token = await self._extract_access_token(auth_record)
    
    # Rest of the code stays the same
    ...

async def _get_facebook_oauth_record(self):
    """Get Facebook OAuth record from Flexus external_auth"""
    from flexus_backend.db_connections.dbconn_prisma import my_prisma
    
    record = await my_prisma.flexus_external_auth.find_first(
        where={
            "owner_fuser_id": self.rcx.fuser_id,
            "ws_id": self.rcx.ws_id,
            "auth_service_provider": "facebook",
            "auth_auth_type": "oauth2",
        }
    )
    return record

async def _extract_access_token(self, auth_record) -> str:
    """Extract access token from encrypted auth record"""
    from flexus_backend.flexus_utils.auth_token_encryption import decrypt_json
    
    auth_json = await decrypt_json(data=auth_record.auth_json_encrypted)
    token_block = auth_json.get("token", {})
    access_token = token_block.get("access_token", "")
    
    if not access_token:
        raise Exception("Facebook auth record exists but has no access token")
    
    return access_token
```

**Преимущества:**
- ✅ Единый OAuth flow для всех сервисов
- ✅ Токены автоматически refresh'ятся (через `refresh_and_get_token`)
- ✅ Централизованное управление в UI (/profile page)
- ✅ Безопасное хранение (encrypted)

---

## Часть 4: Frontend Integration

### Шаг 4.1: Profile Page

Frontend уже имеет `/profile` страницу с OAuth integrations.

**Файл:** `flexus/flexus_frontend/pages/profile.vue`

Эта страница уже показывает доступные OAuth провайдеры и позволяет подключить/отключить их.

После добавления Facebook в `external_oauth_source_configs.py`, он автоматически появится в списке доступных интеграций.

### Шаг 4.2: Callback Page

**Файл:** `flexus/flexus_frontend/pages/v1/tool-oauth/[provider]/callback.vue`

Эта страница уже обрабатывает OAuth callbacks. Ничего менять не нужно - Facebook будет работать автоматически.

---

## Часть 5: Testing

### Шаг 5.1: Local Development

1. **Запустить Flexus локально:**
```bash
cd flexus
docker-compose up
```

2. **Добавить в `.env`:**
```bash
FACEBOOK_CLIENT_ID=your_app_id
FACEBOOK_CLIENT_SECRET=your_app_secret
FLEXUS_WEB_URL=http://localhost:3000
```

3. **Перезапустить backend:**
```bash
docker-compose restart backend
```

### Шаг 5.2: Connect Facebook

1. Открыть http://localhost:3000/profile
2. Найти **Facebook** в списке integrations
3. Нажать **Connect**
4. Авторизоваться на Facebook
5. Принять запрошенные permissions
6. Редирект обратно на /profile
7. Facebook должен появиться как **Connected**

### Шаг 5.3: Test в Ad Monster

1. Открыть чат с Ad Monster ботом
2. Отправить команду: `facebook(op="status")`
3. Бот должен:
   - Найти OAuth токен
   - Сделать запрос к Facebook API
   - Вернуть статус ad accounts

**Если токен не найден:**
```
Facebook authorization required.
Please connect your Facebook account:
http://localhost:3000/profile?connect=facebook&redirect_path=/chat/thread_123
```

---

## Часть 6: Production Deployment

### Шаг 6.1: Facebook App Production Mode

1. В Facebook Developer Console:
   - **Settings** → **Basic**
   - Переключить **App Mode** с Development на Live
   - Добавить **Privacy Policy URL**
   - Добавить **Terms of Service URL**

2. **App Review:**
   - Если нужны advanced permissions (`business_management`), подать на review
   - Приложить скриншоты использования
   - Указать use case

### Шаг 6.2: Environment Variables

Production переменные (K8s secrets):

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: flexus-oauth-secrets
type: Opaque
stringData:
  FACEBOOK_CLIENT_ID: "actual_production_app_id"
  FACEBOOK_CLIENT_SECRET: "actual_production_secret"
  FLEXUS_WEB_URL: "https://your-production-domain.com"
```

### Шаг 6.3: Valid Redirect URIs

В Facebook App Settings добавить production URL:
```
https://your-production-domain.com/v1/tool-oauth/facebook/callback
```

---

## Часть 7: Token Refresh Strategy

### Facebook Token Lifecycle

1. **Short-lived token:** Живет ~2 часа после авторизации
2. **Long-lived token:** Можно обменять short-lived на long-lived (60 дней)
3. **Refresh:** Можно продлевать long-lived токены

### Flexus Auto-refresh

Flexus уже поддерживает auto-refresh через `refresh_and_get_token()` в `external_oauth_source_configs.py`:

```python
# Lines 636-688
async def refresh_and_get_token(record, config):
    # Проверяет expires_at
    # Если токен скоро истечет, автоматически refresh
    # Сохраняет новый токен в БД
```

**Для Facebook:** Нужно убедиться, что:
- `oap_supports_refresh=True` ✅
- Facebook возвращает `expires_in` в token response
- Refresh token сохраняется правильно

### Long-lived Token Exchange

Facebook не использует стандартный `refresh_token` grant. Вместо этого нужно exchange short → long:

```python
# Добавить в external_oauth_source_configs.py для Facebook

async def exchange_facebook_short_to_long_token(
    short_lived_token: str,
    client_id: str,
    client_secret: str,
) -> Dict[str, Any]:
    """Exchange short-lived Facebook token for long-lived one"""
    url = "https://graph.facebook.com/v19.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "fb_exchange_token": short_lived_token,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code != 200:
            logger.error(f"Facebook token exchange failed: {response.text}")
            raise HTTPException(status_code=502, detail="token exchange failed")
        return response.json()
```

**Интегрировать в callback:**

Модифицировать `generic_oauth_callback` в `v1_external_auth_ops.py` для Facebook:

```python
@tool_oauth_router.get("/{provider}/callback")
async def generic_oauth_callback(provider: str, request: Request):
    # ... existing code ...
    
    token_payload = await _exchange_code_for_token(config, code, redirect_uri)
    
    # Special handling for Facebook: exchange short → long token
    if provider == "facebook":
        access_token = token_payload.get("access_token")
        client_id = required_env(config.oap_client_id_env)
        client_secret = required_env(config.oap_client_secret_env)
        
        long_lived = await exchange_facebook_short_to_long_token(
            access_token,
            client_id,
            client_secret,
        )
        token_payload = long_lived  # Replace with long-lived token
    
    # ... continue with existing code ...
```

---

## Часть 8: Error Handling

### Common Errors

**1. "Invalid OAuth Redirect URI"**
- **Причина:** URL в Facebook App не совпадает с фактическим
- **Решение:** Проверить Settings → Facebook Login → Valid OAuth Redirect URIs

**2. "Permissions not granted"**
- **Причина:** Пользователь не дал нужные permissions или App не прошел review
- **Решение:** 
  - Development mode: Добавить пользователя в Test Users
  - Production: Пройти App Review для advanced permissions

**3. "Token expired"**
- **Причина:** Long-lived token истек (60 дней)
- **Решение:** Пользователь должен переавторизоваться через /profile

**4. "Ad account access denied"**
- **Причина:** У пользователя нет доступа к ad account
- **Решение:** Добавить пользователя в Business Manager с нужными правами

### Error Messages в Боте

Обновить error handling в `fi_facebook.py`:

```python
async def _get_facebook_oauth_record(self):
    try:
        record = await my_prisma.flexus_external_auth.find_first(...)
        return record
    except Exception as e:
        logger.error(f"Failed to get Facebook OAuth: {e}")
        return None

async def _extract_access_token(self, auth_record):
    try:
        auth_json = await decrypt_json(data=auth_record.auth_json_encrypted)
        token = auth_json.get("token", {}).get("access_token")
        
        if not token:
            raise ValueError("No access token in auth record")
        
        # Check if expired
        expires_at = auth_json.get("token", {}).get("expires_at", 0)
        if expires_at and expires_at < time.time():
            raise ValueError("Facebook token expired, please reconnect")
        
        return token
    except Exception as e:
        logger.error(f"Failed to extract Facebook token: {e}")
        raise
```

---

## Checklist

### Facebook App Setup
- [ ] Создан Facebook App
- [ ] Добавлен Facebook Login product
- [ ] Добавлен Marketing API product
- [ ] Настроены Valid OAuth Redirect URIs
- [ ] Получены App ID и App Secret
- [ ] Запрошены нужные permissions

### Flexus Backend
- [ ] Добавлен Facebook в `external_oauth_source_configs.py`
- [ ] Добавлены env variables (FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET)
- [ ] (Optional) Добавлена логика exchange short → long token
- [ ] Протестирован OAuth flow локально

### Bot Integration
- [ ] Обновлен `fi_facebook.py` для использования Flexus OAuth
- [ ] Убран старый костыльный OAuth код
- [ ] Добавлен error handling
- [ ] Протестирована интеграция в боте

### Frontend
- [ ] Facebook появился на /profile странице
- [ ] Работает Connect/Disconnect
- [ ] Callback page корректно редиректит

### Testing
- [ ] OAuth flow работает локально
- [ ] Токены сохраняются в БД
- [ ] Бот может использовать токены для API calls
- [ ] Error messages понятные

### Production
- [ ] Facebook App в Live mode
- [ ] Production redirect URIs добавлены
- [ ] Secrets настроены в K8s/production env
- [ ] (If needed) App Review пройден

---

## Next Steps After OAuth Setup

После того, как OAuth настроен и работает:

1. **Вернуться к имплементации Facebook Ads функциональности**
   - Использовать план из `facebook-ads-implementation-plan.md`
   - Начать с AGENT 7 (`fb_utils.py`)
   - Параллельно разрабатывать AGENT 1-4

2. **Тестирование с реальным токеном**
   - Создать Test Ad Account в Facebook Business Manager
   - Подключить через OAuth
   - Тестировать все операции (campaigns, ad sets, etc)

3. **Documentation для пользователей**
   - Как подключить Facebook
   - Как создать Business Manager
   - Как настроить ad account permissions

---

**Автор:** Claude  
**Дата:** 2025-11-19  
**Версия:** 1.0


