# План обучения агента контентному продвижению на X

## Обзор

Этот документ описывает пошаговый план создания AI-агента для контентного продвижения SaaS/digital-продуктов на платформе X (Twitter). План разделён на базовую инфраструктурную часть и три стратегически специфичные части.

---

## Часть 0: Базовая инфраструктура

### 0.1 OAuth и авторизация

#### Задачи:
- [ ] Регистрация приложения на X Developer Platform
- [ ] Выбор тарифного плана (рекомендуется Basic $200/мес для старта)
- [ ] Настройка OAuth 2.0 Authorization Code with PKCE
- [ ] Реализация flow "Войти через X" в клиентском приложении

#### Требуемые scopes:
```
tweet.read
tweet.write
users.read
follows.read
follows.write
dm.read
dm.write
offline.access
media.write
```

#### Endpoints для авторизации:
- Authorization: `https://twitter.com/i/oauth2/authorize`
- Token: `https://api.twitter.com/2/oauth2/token`
- Token refresh: автоматическое обновление через `refresh_token`

#### Хранение токенов:
```
user_id -> {
  access_token: string,
  refresh_token: string,
  expires_at: timestamp,
  scopes: string[]
}
```

---

### 0.2 Базовые инфраструктурные тулы

#### Tool: `x_get_me`
**Описание:** Получение информации о текущем авторизованном пользователе
```
Endpoint: GET /2/users/me
Параметры: user.fields=id,name,username,description,public_metrics,profile_image_url
Использование: Идентификация аккаунта, получение базовых метрик
```

#### Tool: `x_get_user_tweets`
**Описание:** Получение последних твитов пользователя
```
Endpoint: GET /2/users/{id}/tweets
Параметры: max_results, tweet.fields, pagination_token
Использование: Анализ существующего контента, поиск успешных постов
```

#### Tool: `x_get_user_mentions`
**Описание:** Получение упоминаний пользователя
```
Endpoint: GET /2/users/{id}/mentions
Использование: Отслеживание реакций, ответ на mentions
```

#### Tool: `x_search_tweets`
**Описание:** Поиск твитов по ключевым словам
```
Endpoint: GET /2/tweets/search/recent
Параметры: query, max_results, tweet.fields, expansions
Использование: Мониторинг ниши, поиск opportunities для engagement
```

---

### 0.3 Базовые action-тулы

#### Tool: `x_post_tweet`
**Описание:** Публикация твита
```
Endpoint: POST /2/tweets
Body: { text: string, reply?: { in_reply_to_tweet_id }, quote_tweet_id?, media?: { media_ids } }
Rate limit: 200 запросов / 15 мин (user), 300 твитов / 3 часа (app)
```

#### Tool: `x_delete_tweet`
**Описание:** Удаление твита
```
Endpoint: DELETE /2/tweets/{id}
Rate limit: 50 запросов / 15 мин
```

#### Tool: `x_like_tweet`
**Описание:** Лайк твита
```
Endpoint: POST /2/users/{id}/likes
Body: { tweet_id: string }
```

#### Tool: `x_retweet`
**Описание:** Ретвит
```
Endpoint: POST /2/users/{id}/retweets
Body: { tweet_id: string }
```

#### Tool: `x_upload_media`
**Описание:** Загрузка медиа (изображение/видео)
```
Endpoint: POST /2/media/upload
Процесс: INIT -> APPEND (chunks) -> FINALIZE
Scope: media.write
```

---

### 0.4 Rate Limit Manager

#### Функция отслеживания лимитов:
```python
class RateLimitManager:
    """
    Отслеживает rate limits для каждого endpoint
    Возвращает информацию о доступных запросах
    Реализует backoff при приближении к лимитам
    """
    
    limits = {
        "post_tweet": {"requests": 200, "window": 900},  # 15 min
        "delete_tweet": {"requests": 50, "window": 900},
        "search": {"requests": 450, "window": 900},
        "like": {"requests": 200, "window": 900},
    }
    
    def can_execute(self, action: str) -> bool: ...
    def record_request(self, action: str): ...
    def get_wait_time(self, action: str) -> int: ...
```

---

### 0.5 Content Queue Manager

#### Очередь контента:
```python
class ContentQueue:
    """
    Управляет очередью запланированного контента
    Обеспечивает равномерное распределение постов
    Учитывает оптимальное время публикации
    """
    
    def schedule(self, content: Content, optimal_time: datetime): ...
    def get_next(self) -> Content: ...
    def reschedule_failed(self, content: Content): ...
```

---

## Часть 1: Стратегия "Build in Public"

### 1.1 Концепция

**Build in Public (BIP)** — открытое публичное документирование процесса создания продукта. Включает:
- Прогресс разработки
- Метрики и результаты
- Провалы и уроки
- Закулисье принятия решений

**Целевая аудитория:** Indie hackers, разработчики, предприниматели, потенциальные пользователи

**Ключевые метрики успеха:**
- Рост подписчиков
- Engagement rate на BIP-постах
- Конверсия подписчиков в пользователей продукта
- Количество feedback/suggestions от аудитории

---

### 1.2 Тулы для BIP

#### Tool: `bip_generate_update`
**Описание:** Генерация поста о прогрессе на основе данных

**Input:**
```json
{
  "update_type": "feature_shipped" | "milestone" | "learning" | "failure" | "metrics",
  "data": {
    "title": "string",
    "description": "string", 
    "metrics": {"mrr": 1234, "users": 567},
    "learnings": ["string"],
    "next_steps": ["string"]
  },
  "tone": "casual" | "professional" | "excited",
  "include_cta": boolean
}
```

**Output:**
```json
{
  "tweet_text": "string (max 280)",
  "thread": ["string"] | null,
  "suggested_media": "screenshot" | "chart" | "video" | null,
  "hashtags": ["#buildinpublic", "#indiehacker"]
}
```

#### Tool: `bip_schedule_weekly_recap`
**Описание:** Создание еженедельного recap-треда

**Input:**
```json
{
  "week_data": {
    "commits": 47,
    "features_shipped": ["Feature A", "Feature B"],
    "bugs_fixed": 12,
    "user_feedback": ["quote1", "quote2"],
    "metrics_delta": {"mrr": "+$234", "users": "+45"}
  }
}
```

**Output:**
```json
{
  "thread": [
    "Week 12 of building [Product] in public 🧵",
    "Shipped 2 features this week...",
    "User feedback highlight...",
    "Metrics update...",
    "Next week goals..."
  ]
}
```

#### Tool: `bip_analyze_audience_response`
**Описание:** Анализ реакции аудитории на BIP-контент

**Input:**
```json
{
  "tweet_ids": ["id1", "id2"],
  "period_days": 7
}
```

**Output:**
```json
{
  "best_performing_type": "milestone",
  "avg_engagement_rate": 4.5,
  "top_comments_themes": ["pricing", "feature_requests"],
  "suggested_topics": ["behind the scenes", "revenue breakdown"]
}
```

---

### 1.3 Стратегические функции для BIP

#### Function: `generate_bip_content_calendar`
```python
def generate_bip_content_calendar(
    product_info: ProductInfo,
    current_stage: str,  # "pre-launch" | "launched" | "scaling"
    posting_frequency: int,  # posts per week
    time_range_days: int
) -> ContentCalendar:
    """
    Генерирует контент-план для Build in Public
    
    Распределение контента:
    - 30% Progress updates (что сделано)
    - 20% Learnings/Failures (честные уроки)
    - 20% Metrics sharing (MRR, users, etc.)
    - 15% Behind the scenes (процесс, инструменты)
    - 15% Engagement posts (вопросы, polls)
    
    Returns: Календарь с датами, типами и шаблонами постов
    """
```

#### Function: `detect_milestone_opportunity`
```python
def detect_milestone_opportunity(
    current_metrics: Metrics,
    historical_metrics: List[Metrics]
) -> Optional[MilestonePost]:
    """
    Автоматически определяет значимые milestones:
    - Круглые числа (100, 500, 1000 users)
    - Процентный рост (2x, 10x)
    - Временные вехи (1 month, 1 year)
    - Первые события (first paying customer, first churn)
    
    Returns: Готовый пост о milestone или None
    """
```

#### Function: `craft_failure_post`
```python
def craft_failure_post(
    failure_description: str,
    impact: str,
    lessons_learned: List[str],
    next_actions: List[str]
) -> Tweet:
    """
    Создаёт пост о провале в конструктивном ключе
    
    Формула:
    1. Честное признание проблемы
    2. Контекст и последствия
    3. Извлечённые уроки
    4. Конкретные действия по исправлению
    5. Призыв к feedback
    
    Тон: Уязвимый, но не жалостливый. Конструктивный.
    """
```

---

### 1.4 Промпты для BIP

#### System Prompt: BIP Content Generator
```
Ты — опытный indie hacker, который успешно строит продукты публично на X (Twitter). 
Твоя задача — помогать создавать аутентичный Build in Public контент.

ПРИНЦИПЫ:
1. Аутентичность важнее полировки — люди ценят честность
2. Конкретика побеждает абстракции — числа, даты, факты
3. Уязвимость создаёт connection — делись провалами так же, как успехами
4. Каждый пост должен давать ценность — insight, урок, или вдохновение
5. Избегай хвастовства — фокус на journey, не на achievements

ФОРМАТЫ ПОСТОВ:
- Короткий update (1 твит): Конкретный факт + эмоция + контекст
- Milestone celebration: Числа + путь к ним + благодарность
- Weekly recap thread: 5-7 твитов, структурированный обзор
- Failure post: Проблема + урок + план действий
- Behind the scenes: Процесс + инструменты + tips

ГОЛОС:
- Первое лицо, разговорный стиль
- Эмодзи умеренно (1-3 на пост)
- Без корпоративного жаргона
- Как будто пишешь другу-разработчику

ЗАПРЕЩЕНО:
- Фейковые числа или преувеличения
- Чистое хвастовство без ценности
- Атаки на конкурентов
- Просьбы о подписке/лайках в каждом посте
```

#### User Prompt Template: Progress Update
```
Создай пост для Build in Public о прогрессе:

ПРОДУКТ: {product_name}
ОПИСАНИЕ: {product_description}
ЧТО СДЕЛАНО: {achievement}
КОНТЕКСТ: {context}
СЛЕДУЮЩИЙ ШАГ: {next_step}
ТОН: {casual/excited/reflective}

Требования:
- Максимум 280 символов (или укажи, что нужен thread)
- Конкретные детали вместо общих фраз
- Один clear takeaway для читателя
```

#### User Prompt Template: Weekly Recap Thread
```
Создай еженедельный recap thread для Build in Public:

ПРОДУКТ: {product_name}
НЕДЕЛЯ #: {week_number}

ДОСТИЖЕНИЯ:
{achievements_list}

ПРОВАЛЫ/СЛОЖНОСТИ:
{challenges_list}

МЕТРИКИ:
- Было: {metrics_before}
- Стало: {metrics_after}

УРОКИ НЕДЕЛИ:
{learnings}

ПЛАН НА СЛЕДУЮЩУЮ НЕДЕЛЮ:
{next_week_goals}

Требования:
- 5-7 твитов в треде
- Первый твит — hook с интригой
- Последний — call to action (вопрос к аудитории)
- Каждый твит самодостаточен, но связан с общей историей
```

---

## Часть 2: Стратегия "Reply Guy" (Strategic Engagement)

### 2.1 Концепция

**Reply Guy Strategy** — систематическое взаимодействие через комментарии к постам релевантных аккаунтов для повышения видимости и построения отношений.

**Ключевой принцип:** Давать ценность в каждом ответе, а не продавать

**Целевые аккаунты:**
- Influencers в нише продукта
- Потенциальные пользователи, обсуждающие релевантные проблемы
- Другие indie hackers / founders
- Популярные tech-аккаунты с high engagement

**Метрики успеха:**
- Profile visits с ответов
- Новые подписчики после engagement sessions
- Replies/mentions от target аккаунтов
- Конверсия в website traffic

---

### 2.2 Тулы для Reply Guy

#### Tool: `rg_find_engagement_opportunities`
**Описание:** Поиск постов для стратегического engagement

**Input:**
```json
{
  "keywords": ["saas", "indie hacker", "building"],
  "exclude_keywords": ["hiring", "job"],
  "min_engagement": 10,
  "max_replies": 50,
  "recency_hours": 24,
  "target_accounts": ["@account1", "@account2"],
  "language": "en"
}
```

**Output:**
```json
{
  "opportunities": [
    {
      "tweet_id": "123",
      "author": "@influencer",
      "author_followers": 50000,
      "text": "What's the hardest part of building a SaaS?",
      "engagement": {"likes": 234, "replies": 45, "retweets": 12},
      "opportunity_score": 8.5,
      "suggested_angle": "Share personal experience with specific challenge",
      "posted_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Tool: `rg_generate_reply`
**Описание:** Генерация ценного ответа на пост

**Input:**
```json
{
  "original_tweet": {
    "id": "123",
    "text": "What's the hardest part of building a SaaS?",
    "author": "@influencer",
    "context": "Founder asking community for input"
  },
  "my_product": {
    "name": "ProductX",
    "description": "...",
    "relevant_experience": "..."
  },
  "reply_goal": "provide_value" | "share_experience" | "ask_followup" | "soft_mention",
  "include_product_mention": false
}
```

**Output:**
```json
{
  "reply_text": "The hardest part for me was...",
  "confidence_score": 0.85,
  "value_type": "personal_experience",
  "follow_up_potential": true,
  "warning": null
}
```

#### Tool: `rg_track_engagement_session`
**Описание:** Отслеживание результатов engagement session

**Input:**
```json
{
  "session_id": "sess_123",
  "replies_sent": ["tweet_id1", "tweet_id2"],
  "session_duration_minutes": 30
}
```

**Output:**
```json
{
  "session_stats": {
    "replies_sent": 15,
    "likes_received": 23,
    "replies_received": 5,
    "profile_visits_estimated": 12,
    "new_followers": 3
  },
  "best_performing_reply": {
    "tweet_id": "456",
    "engagement": 15,
    "type": "personal_experience"
  },
  "recommendations": [
    "Replies with specific numbers perform 2x better",
    "Morning sessions (9-11am) show higher engagement"
  ]
}
```

#### Tool: `rg_manage_target_lists`
**Описание:** Управление списками целевых аккаунтов

**Input:**
```json
{
  "action": "add" | "remove" | "analyze",
  "list_name": "tier1_influencers",
  "accounts": ["@account1", "@account2"]
}
```

**Output:**
```json
{
  "list": {
    "name": "tier1_influencers",
    "accounts": [
      {
        "username": "@account1",
        "followers": 50000,
        "avg_engagement": 234,
        "posting_frequency": "3/day",
        "best_time_to_engage": "10:00-12:00 UTC",
        "topics": ["saas", "startups", "marketing"]
      }
    ]
  }
}
```

---

### 2.3 Стратегические функции для Reply Guy

#### Function: `score_engagement_opportunity`
```python
def score_engagement_opportunity(
    tweet: Tweet,
    my_profile: Profile,
    engagement_history: List[Engagement]
) -> OpportunityScore:
    """
    Оценивает пост как opportunity для engagement
    
    Факторы scoring:
    - Author reach (followers, avg engagement)
    - Tweet momentum (engagement velocity)
    - Topic relevance (match с моим продуктом/экспертизой)
    - Competition (количество уже существующих replies)
    - Timing (свежесть поста)
    - Historical success (как мои replies работали с этим автором)
    
    Score: 1-10, где 10 = идеальная opportunity
    """
```

#### Function: `generate_value_reply`
```python
def generate_value_reply(
    original_tweet: Tweet,
    reply_strategy: str,  # "experience" | "insight" | "resource" | "question"
    product_context: ProductContext,
    max_length: int = 280
) -> Reply:
    """
    Генерирует ответ, дающий реальную ценность
    
    Стратегии:
    - experience: Поделиться личным опытом, релевантным к теме
    - insight: Дать неочевидный инсайт или perspective
    - resource: Порекомендовать полезный ресурс (не свой продукт!)
    - question: Задать thoughtful follow-up вопрос
    
    Правила:
    - Никогда не начинать с продвижения продукта
    - Добавлять конкретику (числа, примеры)
    - Personality > generic advice
    - Длина: sweet spot 100-200 символов
    """
```

#### Function: `schedule_engagement_session`
```python
def schedule_engagement_session(
    target_lists: List[TargetList],
    session_duration_minutes: int,
    optimal_time: bool = True
) -> EngagementPlan:
    """
    Планирует engagement session
    
    Распределение времени:
    - 60% — ответы на посты tier-1 аккаунтов
    - 25% — ответы на посты с релевантными keywords
    - 15% — ответы на replies к моим постам
    
    Optimal timing:
    - Weekdays: 9-11am, 1-3pm (target timezone)
    - Avoid: weekends, late evenings
    
    Safeguards:
    - Max 30 replies per session
    - Min 2 min between replies
    - Variety in reply types
    """
```

---

### 2.4 Промпты для Reply Guy

#### System Prompt: Strategic Responder
```
Ты — эксперт по стратегическому engagement на X (Twitter).
Твоя задача — создавать ответы, которые дают реальную ценность и строят отношения.

ПРИНЦИПЫ:
1. Value First — каждый ответ должен быть полезен автору или другим читателям
2. Be Specific — общие советы игнорируются, конкретика запоминается
3. Be Human — personality важнее perfection
4. No Selling — продукт упоминается только если напрямую релевантен и полезен
5. Earn Attention — не проси подписку, заслужи её контентом

ТИПЫ ЦЕННЫХ ОТВЕТОВ:
1. Personal Experience: "Я сталкивался с этим когда строил X. Что помогло: ..."
2. Contrarian Insight: "Интересная мысль. Хотя я заметил, что в случае Y работает иначе..."
3. Tactical Addition: "Добавлю к этому: конкретный тактический совет..."
4. Thoughtful Question: "Интересно, а как это работает в случае когда...?"
5. Resource Share: "Недавно читал исследование на эту тему: [краткий инсайт]"

ЗАПРЕЩЕНО:
- "Great post!" и подобные пустые комплименты
- Немедленное продвижение своего продукта
- Копипаст одинаковых ответов
- Спор ради спора
- Ответы длиннее оригинального поста (обычно)

ФОРМАТ:
- 1-3 предложения (sweet spot)
- Можно использовать 1 emoji если уместно
- Начинать с сути, не с обращения
```

#### User Prompt Template: Generate Reply
```
Создай ценный ответ на этот твит:

ОРИГИНАЛЬНЫЙ ТВИТ:
Автор: {author} ({follower_count} подписчиков)
Текст: "{tweet_text}"
Контекст: {context}

МОЙ КОНТЕКСТ:
Продукт: {my_product}
Моя экспертиза: {my_expertise}
Релевантный опыт: {relevant_experience}

СТРАТЕГИЯ ОТВЕТА: {strategy}
УПОМИНАТЬ ПРОДУКТ: {yes/no}

Требования:
- Максимум 200 символов
- Дать конкретную ценность
- Быть memorable, не generic
- Соответствовать выбранной стратегии
```

#### User Prompt Template: Find Opportunities
```
Найди opportunities для engagement:

МОЯ НИША: {niche}
МОЙ ПРОДУКТ: {product_description}
ЦЕЛЕВЫЕ АККАУНТЫ: {target_accounts}
КЛЮЧЕВЫЕ ТЕМЫ: {topics}

Критерии хорошей opportunity:
- Автор с 5K+ подписчиков
- Пост не старше 6 часов
- Менее 30 ответов уже
- Тема, где я могу дать уникальную ценность

Выдай топ-5 opportunities с:
- Ссылка на твит
- Почему это хорошая opportunity
- Suggested angle для ответа
```

---

## Часть 3: Стратегия "Thread Marketing"

### 3.1 Концепция

**Thread Marketing** — создание и дистрибуция ценных Twitter threads как основного формата контента для привлечения аудитории и установления экспертности.

**Почему threads работают:**
- Больше screen time = больше engagement сигналов алгоритму
- Формат storytelling удерживает внимание
- Репосты тредов приносят больше exposure
- Evergreen threads можно переиспользовать

**Типы тредов:**
1. **Educational** — обучающий контент, how-to
2. **Story** — история успеха/провала/урока
3. **Curation** — подборка ресурсов/инструментов
4. **Analysis** — разбор кейса/продукта/стратегии
5. **Contrarian** — непопулярное мнение с аргументами

**Метрики успеха:**
- Thread impressions vs single tweet impressions
- Bookmark rate (показатель ценности)
- Profile visits с тредов
- Follower conversion rate

---

### 3.2 Тулы для Thread Marketing

#### Tool: `thread_generate`
**Описание:** Генерация полного thread на заданную тему

**Input:**
```json
{
  "topic": "How I grew my SaaS from 0 to $10K MRR",
  "thread_type": "story" | "educational" | "curation" | "analysis" | "contrarian",
  "target_length": 7,
  "key_points": [
    "Started with problem validation",
    "Built MVP in 2 weeks",
    "First 10 customers from Twitter",
    "Pricing mistakes",
    "What worked for growth"
  ],
  "include_cta": true,
  "cta_type": "follow" | "newsletter" | "product" | "reply"
}
```

**Output:**
```json
{
  "thread": [
    {
      "position": 1,
      "text": "I grew my SaaS from $0 to $10K MRR in 8 months.\n\nHere's everything I did (including the mistakes):\n\n🧵",
      "type": "hook",
      "media": null
    },
    {
      "position": 2,
      "text": "1/ Problem Validation\n\nBefore writing a single line of code, I spent 2 weeks talking to potential users.\n\nI reached out to 50 people. 23 responded. 8 had the exact problem I wanted to solve.\n\nThat was enough signal to start building.",
      "type": "content",
      "media": "screenshot_of_dm_outreach"
    }
  ],
  "estimated_read_time": "2 min",
  "suggested_hashtags": ["#buildinpublic", "#saas", "#indiehacker"],
  "best_posting_time": "Tuesday 10:00 AM UTC"
}
```

#### Tool: `thread_analyze`
**Описание:** Анализ performance существующих threads

**Input:**
```json
{
  "thread_first_tweet_id": "123",
  "include_comparison": true
}
```

**Output:**
```json
{
  "thread_stats": {
    "total_impressions": 45000,
    "total_engagements": 1234,
    "engagement_rate": 2.7,
    "bookmarks": 89,
    "profile_visits": 234,
    "new_followers_attributed": 45
  },
  "per_tweet_breakdown": [
    {"position": 1, "impressions": 45000, "drop_off": "0%"},
    {"position": 2, "impressions": 32000, "drop_off": "29%"},
    {"position": 3, "impressions": 28000, "drop_off": "12%"}
  ],
  "comparison_to_average": {
    "vs_my_threads": "+45%",
    "vs_single_tweets": "+320%"
  },
  "insights": [
    "Hook tweet performed exceptionally well",
    "Drop-off at tweet 5 suggests it was weakest",
    "CTA tweet had 2x average engagement"
  ]
}
```

#### Tool: `thread_repurpose`
**Описание:** Конвертация контента в thread

**Input:**
```json
{
  "source_type": "blog_post" | "video_transcript" | "podcast_notes" | "bullet_points",
  "source_content": "...",
  "target_thread_length": 7,
  "adapt_for_twitter": true
}
```

**Output:**
```json
{
  "thread": [...],
  "adaptation_notes": [
    "Removed jargon for Twitter audience",
    "Added hook based on most valuable insight",
    "Broke down complex section into 2 tweets"
  ],
  "source_link_placement": "final_tweet"
}
```

#### Tool: `thread_schedule_repost`
**Описание:** Планирование репостов evergreen threads

**Input:**
```json
{
  "thread_id": "123",
  "repost_strategy": "quote_with_update" | "simple_retweet" | "fresh_hook",
  "schedule": {
    "frequency_days": 30,
    "times_to_repost": 3,
    "vary_time": true
  }
}
```

**Output:**
```json
{
  "scheduled_reposts": [
    {
      "date": "2024-02-15",
      "time": "10:00 UTC",
      "format": "quote_with_update",
      "new_hook": "This thread from last month still getting saves. Here's why pricing your SaaS is harder than building it:"
    }
  ]
}
```

---

### 3.3 Стратегические функции для Thread Marketing

#### Function: `generate_thread_hook`
```python
def generate_thread_hook(
    thread_topic: str,
    thread_type: str,
    key_value_proposition: str,
    urgency_level: str = "medium"  # "low" | "medium" | "high"
) -> str:
    """
    Генерирует hook (первый твит) для thread
    
    Формулы hooks:
    - Story: "I [achievement]. Here's how: 🧵"
    - Educational: "[Number] [things] that [benefit]. A thread:"
    - Contrarian: "Unpopular opinion: [statement]. Here's why:"
    - Curation: "I spent [time] [doing X]. Here are the best [Y]:"
    - Analysis: "I studied [X]. Here's what I learned:"
    
    Правила:
    - Первая строка = scroll-stopper
    - Обещание конкретной ценности
    - Числа повышают CTR на 20%+
    - Emoji 🧵 сигнализирует thread
    """
```

#### Function: `structure_thread_content`
```python
def structure_thread_content(
    raw_content: str,
    target_length: int,
    thread_type: str
) -> List[Tweet]:
    """
    Структурирует контент в thread формат
    
    Структура thread:
    1. Hook (scroll-stopper + promise)
    2-N-1. Content tweets (value delivery)
    N. CTA (what to do next)
    
    Правила для content tweets:
    - Один ключевой поинт на твит
    - Каждый твит самодостаточен
    - Нумерация помогает (1/, 2/, ...)
    - Transition words между твитами
    - Variety: facts, stories, examples, quotes
    """
```

#### Function: `optimize_thread_for_engagement`
```python
def optimize_thread_for_engagement(
    thread: List[Tweet],
    historical_performance: ThreadPerformance
) -> List[Tweet]:
    """
    Оптимизирует thread на основе данных о performance
    
    Оптимизации:
    - Reorder tweets by predicted engagement
    - Add strategic whitespace
    - Insert "curiosity gaps" между твитами
    - Add media suggestions для key tweets
    - Optimize CTA based on past performance
    """
```

---

### 3.4 Промпты для Thread Marketing

#### System Prompt: Thread Creator
```
Ты — эксперт по созданию viral Twitter threads.
Твоя задача — превращать идеи в захватывающие threads, которые люди читают до конца и сохраняют.

АНАТОМИЯ УСПЕШНОГО THREAD:

1. HOOK (Tweet 1):
   - Первая строка = scroll-stopper
   - Конкретное обещание ценности
   - Числа когда уместно
   - Emoji 🧵 в конце
   - Примеры: 
     * "I made $50K from one tweet. Here's the exact formula:"
     * "10 tools I use daily that 90% of founders don't know about:"
     * "I failed at 3 startups before this one worked. The lessons:"

2. CONTENT TWEETS (2 to N-1):
   - Один ключевой поинт на твит
   - Начинать с номера: "1/", "2/", etc.
   - Конкретика > общие советы
   - Stories > statements
   - Каждый твит = mini-hook для следующего
   - Whitespace для читаемости

3. CTA (Last Tweet):
   - Резюме ценности
   - Конкретный next step
   - Не begging ("please follow")
   - Value exchange ("Follow for more X")

ПРАВИЛА ФОРМАТИРОВАНИЯ:
- 200-250 символов per tweet (оптимально)
- Переносы строк для читаемости
- 1-2 emoji per tweet (не больше)
- Bold statements в начале абзацев

ЗАПРЕЩЕНО:
- Пустые transition tweets
- Повторение одной мысли
- Клиффхэнгеры без payoff
- Слишком длинные threads (7-12 optimal)
- Selling в каждом твите
```

#### User Prompt Template: Create Educational Thread
```
Создай educational thread на тему:

ТЕМА: {topic}
ЦЕЛЕВАЯ АУДИТОРИЯ: {audience}
МОЯ ЭКСПЕРТИЗА: {expertise}

КЛЮЧЕВЫЕ ПОИНТЫ ДЛЯ РАСКРЫТИЯ:
{key_points}

УНИКАЛЬНЫЙ ANGLE/INSIGHT:
{unique_angle}

ЖЕЛАЕМАЯ ДЛИНА: {length} твитов
CTA: {cta_goal}

Требования:
- Hook должен создавать curiosity gap
- Каждый твит должен давать actionable value
- Включить хотя бы 1 personal story/example
- Финальный CTA должен быть natural, не pushy
```

#### User Prompt Template: Repurpose to Thread
```
Преобразуй этот контент в Twitter thread:

ИСХОДНЫЙ КОНТЕНТ:
{source_content}

ТИП КОНТЕНТА: {blog_post/video/podcast}
КЛЮЧЕВЫЕ TAKEAWAYS: {takeaways}

Требования:
- Адаптировать язык для Twitter (более casual)
- Выбрать самые ценные insights
- Добавить hook, которого не было в оригинале
- {length} твитов максимум
- В последнем твите — ссылка на оригинал
```

---

## Часть 4: Интеграция и оркестрация

### 4.1 Unified Content Strategy Engine

```python
class ContentStrategyEngine:
    """
    Оркестратор всех трёх стратегий
    """
    
    def __init__(self, user_profile, product_info, goals):
        self.bip = BuildInPublicStrategy(user_profile, product_info)
        self.reply_guy = ReplyGuyStrategy(user_profile, product_info)
        self.threads = ThreadMarketingStrategy(user_profile, product_info)
        self.goals = goals
    
    def generate_weekly_plan(self) -> WeeklyPlan:
        """
        Генерирует сбалансированный недельный план:
        - 2-3 threads
        - Daily BIP updates
        - 2 engagement sessions (30 min each)
        - 1 weekly recap thread
        """
        pass
    
    def adapt_strategy(self, performance_data: PerformanceData):
        """
        Адаптирует стратегию на основе performance:
        - Increase winning content types
        - Adjust posting times
        - Refine target accounts
        - Optimize thread lengths
        """
        pass
```

### 4.2 Recommended Weekly Schedule

| День | BIP | Reply Guy | Threads |
|------|-----|-----------|---------|
| Пн | Progress update | 30 min session | — |
| Вт | — | — | Educational thread |
| Ср | Behind the scenes | 30 min session | — |
| Чт | Metrics/milestone | — | — |
| Пт | — | — | Story thread |
| Сб | — | Light engagement | — |
| Вс | Weekly recap thread | — | — |

### 4.3 KPI Dashboard

```json
{
  "weekly_kpis": {
    "followers_gained": {"target": 100, "actual": 0},
    "profile_visits": {"target": 500, "actual": 0},
    "engagement_rate": {"target": 3.0, "actual": 0},
    "website_clicks": {"target": 50, "actual": 0},
    "thread_saves": {"target": 30, "actual": 0}
  },
  "strategy_breakdown": {
    "bip_contribution": "40%",
    "reply_guy_contribution": "35%",
    "threads_contribution": "25%"
  }
}
```

---

## Часть 5: Compliance и Safety

### 5.1 Rate Limit Compliance

| Action | Limit | Window | Safety Buffer |
|--------|-------|--------|---------------|
| Post tweet | 200 | 15 min | Use max 150 |
| Delete tweet | 50 | 15 min | Use max 40 |
| Like | 200 | 15 min | Use max 150 |
| Retweet | 200 | 15 min | Use max 150 |
| Follow | 400 | 24 hours | Use max 300 |
| DM | 500 | 24 hours | Use max 400 |

### 5.2 Anti-Spam Guidelines

**Разрешено:**
- Автоматическая публикация полезной информации
- Авто-ответы на engagement с нашим контентом
- Scheduled posting

**Запрещено:**
- Автоматические посты о trending topics
- Bulk unsolicited DMs
- Одинаковые ответы разным пользователям
- Aggressive follow/unfollow

### 5.3 Content Safety

```python
class ContentSafetyChecker:
    """
    Проверяет контент перед публикацией
    """
    
    def check(self, content: str) -> SafetyResult:
        """
        Проверки:
        - Нет spam patterns
        - Нет запрещённых keywords
        - Нет excessive self-promotion
        - Нет misleading claims
        - Rate limits OK
        """
        pass
```

---

## Приложения

### A. Полезные API Endpoints Reference

```yaml
Core:
  - GET /2/users/me
  - GET /2/users/{id}/tweets
  - GET /2/tweets/search/recent
  - POST /2/tweets
  - DELETE /2/tweets/{id}

Engagement:
  - POST /2/users/{id}/likes
  - DELETE /2/users/{id}/likes/{tweet_id}
  - POST /2/users/{id}/retweets
  - DELETE /2/users/{id}/retweets/{tweet_id}

Media:
  - POST /2/media/upload (INIT, APPEND, FINALIZE)

Analytics:
  - GET /2/tweets/{id} (with public_metrics)
  - GET /2/users/{id} (with public_metrics)
```

### B. Тарифные планы и лимиты (актуально на 2025)

| Plan | Цена | Reads/month | Writes/month | Key Features |
|------|------|-------------|--------------|--------------|
| Free | $0 | 100 | 500 | Basic endpoints, Login with X |
| Basic | $200 | 15,000 | 50,000 | Full v2 access |
| Pro | $5,000 | 1,000,000 | 300,000 | Full archive search, Filtered stream |

### C. Checklist для запуска

- [ ] Зарегистрировано приложение на developer.twitter.com
- [ ] Выбран и оплачен тарифный план
- [ ] Настроен OAuth 2.0 flow
- [ ] Реализованы базовые тулы
- [ ] Настроен rate limit manager
- [ ] Протестирована авторизация пользователя
- [ ] Реализована стратегия BIP
- [ ] Реализована стратегия Reply Guy
- [ ] Реализована стратегия Thread Marketing
- [ ] Настроен мониторинг и аналитика
- [ ] Проведено тестирование на тестовом аккаунте
