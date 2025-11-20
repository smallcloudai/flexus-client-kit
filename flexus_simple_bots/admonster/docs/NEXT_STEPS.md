# Facebook OAuth Setup - Next Steps

## ✅ Сделано

- [x] Добавлен Facebook provider в `external_oauth_source_configs.py`
- [x] Добавлена функция `exchange_facebook_short_to_long_token()` для получения long-lived tokens
- [x] Интегрирован Facebook token exchange в `generic_oauth_callback`
- [x] No linter errors

## 🔧 Что нужно сделать

### 1. Создать Facebook App (15 минут)

1. **Перейти на https://developers.facebook.com/**
2. **Create App → Business**
3. **App Name:** Flexus (или ваше название)
4. **Add Products:**
   - Facebook Login
   - Marketing API

5. **Settings → Basic:**
   - Скопировать **App ID** → `FACEBOOK_CLIENT_ID`
   - Скопировать **App Secret** → `FACEBOOK_CLIENT_SECRET`

6. **Facebook Login → Settings:**
   - **Valid OAuth Redirect URIs:** добавить:
     ```
     http://localhost:3000/v1/tool-oauth/facebook/callback
     https://your-domain.com/v1/tool-oauth/facebook/callback
     ```

### 2. Добавить Environment Variables

**Local Development (.env file):**
```bash
FACEBOOK_CLIENT_ID=your_app_id_here
FACEBOOK_CLIENT_SECRET=your_app_secret_here
```

**Production (K8s secrets / Docker Compose):**
```yaml
environment:
  - FACEBOOK_CLIENT_ID=your_app_id_here
  - FACEBOOK_CLIENT_SECRET=your_app_secret_here
```

### 3. Перезапустить Flexus Backend

```bash
# Docker Compose
cd flexus
docker-compose restart backend

# Or full rebuild if needed
docker-compose up --build backend
```

### 4. Тестирование OAuth Flow

1. Открыть http://localhost:3000/profile (или ваш URL)
2. Найти **Facebook** в списке OAuth integrations
3. Нажать **Connect**
4. Авторизоваться на Facebook
5. Принять запрошенные permissions:
   - ads_management
   - ads_read
   - read_insights
6. Проверить редирект обратно на /profile
7. Facebook должен показаться как **Connected** ✅

### 5. Тестирование в Ad Monster Bot

1. Открыть чат с Ad Monster ботом
2. Отправить команду: `facebook(op="status")`
3. Бот должен вернуть список ad accounts (или просить подключиться если токен не найден)

**Expected output:**
```
Facebook Ads Account: act_123456
Active Campaigns (2):
  📊 Summer Sale 2025 (ID: 123...)
     Status: ACTIVE, Objective: OUTCOME_TRAFFIC, Daily Budget: $50.00
  📊 Winter Promo (ID: 456...)
     Status: PAUSED, Objective: OUTCOME_AWARENESS, Lifetime Budget: $100.00
```

## 🔍 Проверка что всё работает

### Check 1: Provider появился в Flexus
```bash
# Query GraphQL или через frontend
# Должен показать Facebook в списке доступных providers
```

### Check 2: OAuth callback endpoint
```bash
curl http://localhost:8000/v1/tool-oauth/facebook/callback?code=test&state=test
# Should return redirect (не 404)
```

### Check 3: Database record
После успешного OAuth flow в БД должна появиться запись:
```sql
SELECT * FROM flexus_external_auth 
WHERE auth_service_provider = 'facebook' 
AND auth_auth_type = 'oauth2';
```

## 🐛 Troubleshooting

### Problem: "Invalid OAuth redirect URI"
**Solution:** Убедиться что URL в Facebook App Settings точно совпадает с `FLEXUS_WEB_URL` + redirect_path

### Problem: "Token exchange failed"
**Solution:**
- Проверить что App ID и Secret правильные
- Проверить что Marketing API продукт добавлен в App
- Посмотреть логи backend: `docker-compose logs backend | grep facebook`

### Problem: "Facebook не появляется в /profile"
**Solution:**
- Перезапустить frontend: `docker-compose restart frontend`
- Проверить что backend правильно загрузился с новым кодом
- Очистить кэш браузера

### Problem: "Permissions denied"
**Solution:**
- В Development mode: добавить пользователя в Test Users
- В Production: пройти App Review для advanced permissions

## 📝 Logs для мониторинга

```bash
# Backend logs
docker-compose logs -f backend | grep -E "facebook|oauth"

# Успешный OAuth должен показать:
# "Stored OAuth tokens provider=facebook auth_id=... expires_at=..."
# "Facebook token exchanged to long-lived, expires_in=5183999" (60 days)

# OAuth callback processed provider=facebook fuser=... ws=...
```

## 📊 Metrics to Track

После внедрения отслеживать:
- Сколько пользователей подключили Facebook
- Успешность OAuth flow (success vs errors)
- Token refresh rate (должны refresh'иться автоматически)
- API errors from Facebook

## 🚀 Next: Implement Bot Features

После того, как OAuth работает → переходить к:

1. **AGENT 7:** `fb_utils.py` - базовые утилиты
2. **AGENT 1:** `fb_ad_account.py` - управление ad accounts
3. **AGENT 2-4:** Параллельная разработка остальных модулей

См. `facebook-ads-implementation-plan.md` для деталей.

---

**Status:** OAuth setup complete, ready for testing!
**Date:** 2025-11-19


