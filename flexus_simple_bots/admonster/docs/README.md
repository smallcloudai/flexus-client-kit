# Facebook Ads Integration - Documentation

## 📚 Документация

Эта папка содержит полную документацию по интеграции Facebook Marketing API в Ad Monster бота.

### Файлы

1. **[facebook-oauth-setup.md](facebook-oauth-setup.md)** 🔐 START HERE (OAuth Setup)
   - Настройка Facebook App
   - Интеграция OAuth в Flexus
   - Рефакторинг fi_facebook.py
   - Token refresh strategy
   - Production deployment

2. **[QUICKSTART.md](QUICKSTART.md)** ⭐ START HERE (Development)
   - Быстрый старт для разработчиков
   - Структура проекта
   - Примеры кода для каждого агента
   - Checklist для разработки
   - Troubleshooting

3. **[facebook-ads-implementation-plan.md](facebook-ads-implementation-plan.md)** 📋 MAIN PLAN
   - Полный план имплементации
   - Разбивка по агентам (AGENT 1-7)
   - Roadmap по неделям
   - Архитектура решения
   - Риски и митигация

4. **[facebook-api-reference.md](facebook-api-reference.md)** 📖 API REFERENCE
   - Справочник по всем Facebook Marketing API endpoints
   - Примеры запросов и ответов
   - Параметры и типы данных
   - Error codes
   - Rate limits

## 🎯 Быстрая навигация

### Для setup (OAuth)
1. Начни с [OAuth Setup Guide](facebook-oauth-setup.md)
2. Создай Facebook App
3. Добавь конфигурацию в Flexus
4. Протестируй OAuth flow

### Для нового разработчика
1. После OAuth setup прочитай [QUICKSTART.md](QUICKSTART.md)
2. Выбери своего агента из [Implementation Plan](facebook-ads-implementation-plan.md#разбивка-по-агентам-parallel-development)
3. Используй [API Reference](facebook-api-reference.md) как справочник

### Для координатора проекта
1. [Implementation Plan](facebook-ads-implementation-plan.md) - полный обзор
2. [Roadmap](facebook-ads-implementation-plan.md#план-внедрения-roadmap) - временные рамки
3. [Метрики успеха](facebook-ads-implementation-plan.md#метрики-успеха) - KPI

### Для тестировщика
1. [Testing Strategy](QUICKSTART.md#5-testing-strategy) - подход к тестированию
2. [Common Issues](QUICKSTART.md#8-common-issues--solutions) - известные проблемы

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────┐
│                  admonster_bot.py                   │
│              (Main bot entry point)                 │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│              fi_facebook.py (existing)              │
│         (Base integration, OAuth, routing)          │
└────────────────────┬────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│   fb_utils.py    │    │  Existing ops    │
│  (Error, Rate,   │    │  (status, etc)   │
│   Validation)    │    └──────────────────┘
└────────┬─────────┘
         │ (used by all)
         │
    ┌────┴────┬────────┬────────┬──────────┬────────┐
    ▼         ▼        ▼        ▼          ▼        ▼
┌────────┐ ┌────────┐ ┌──────┐ ┌────────┐ ┌──────┐ ┌────────┐
│ Ad Acc │ │Campaign│ │AdSet │ │Creative│ │Insigh│ │Audienc │
│        │ │        │ │      │ │  & Ads │ │  ts  │ │   es   │
│ AGENT1 │ │ AGENT2 │ │AGENT3│ │ AGENT4 │ │AGENT5│ │ AGENT6 │
└────────┘ └────────┘ └──────┘ └────────┘ └──────┘ └────────┘
```

## 👥 Команда агентов

| Agent | Module | Responsibility | Priority | Complexity |
|-------|--------|---------------|----------|------------|
| **AGENT 7** | `fb_utils.py` | Shared utilities | ⭐ HIGH | Medium |
| **AGENT 1** | `fb_ad_account.py` | Ad account mgmt | ⭐ HIGH | Medium |
| **AGENT 2** | `fb_campaign.py` | Campaign extended | ⭐ HIGH | Low-Med |
| **AGENT 3** | `fb_adset.py` | Ad sets & targeting | ⭐ HIGH | High |
| **AGENT 4** | `fb_creative.py` | Creatives & ads | ⭐ HIGH | High |
| **AGENT 5** | `fb_insights.py` | Advanced analytics | Medium | Med-High |
| **AGENT 6** | `fb_audience.py` | Audiences & pixels | Medium | Med-High |

## 📅 Timeline

- **Week 1:** Setup + AGENT 7 (fb_utils)
- **Week 2-3:** AGENT 1-4 (core functionality) - **parallel**
- **Week 4:** AGENT 5-6 (advanced features) - **parallel**
- **Week 5:** Integration, testing, documentation

## ✅ Current Status

- [x] Documentation created
- [x] Architecture designed
- [x] Agent roles assigned
- [x] OAuth setup guide created
- [ ] **→ CREATE FACEBOOK APP (YOU ARE HERE)**
- [ ] **→ ADD FACEBOOK TO FLEXUS BACKEND**
- [ ] Test OAuth flow
- [ ] Development started (AGENT 7)
- [ ] Core functionality (AGENT 1-4)
- [ ] Advanced features (AGENT 5-6)
- [ ] Integration complete
- [ ] Testing complete
- [ ] Production ready

## 🔗 External Resources

- **Facebook Marketing API:** https://developers.facebook.com/docs/marketing-api
- **Graph API Explorer:** https://developers.facebook.com/tools/explorer
- **Business SDK (Python):** https://github.com/facebook/facebook-python-business-sdk
- **Ad Account Setup:** https://business.facebook.com/

## 💡 Key Concepts

### Facebook Ads Hierarchy
```
Business
  └─ Ad Account (act_123)
      └─ Campaign (objective, budget)
          └─ Ad Set (targeting, placement, schedule)
              └─ Ad (creative)
                  └─ Creative (images, text, CTA)
```

### Marketing API vs Graph API
- **Graph API:** General Facebook data (users, pages, posts)
- **Marketing API:** Advertising-specific (campaigns, ads, insights)
- **Same endpoint, different objects and permissions**

### OAuth & Permissions
Required scopes:
- `ads_management` - Create/edit ads
- `ads_read` - Read ad data
- `read_insights` - Access analytics
- `business_management` - Manage business accounts

## 🐛 Known Issues

See [Common Issues](QUICKSTART.md#8-common-issues--solutions) in QUICKSTART.md

## 📞 Getting Help

1. Check this documentation first
2. Search Facebook's official docs
3. Test in Graph API Explorer
4. Ask in team chat (specify your AGENT number)

---

**Last Updated:** 2025-11-19  
**Version:** 1.0  
**Status:** Planning Phase

