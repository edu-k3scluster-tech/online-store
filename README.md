## How to run linters
```bash
make lint
```


## How to run tests

```bash
make test-order
```

## How to run project

```bash
make start
make stop
```

# 🧾 Тестовое задание: Event-driven Order System

## 📖 Описание

Нужно реализовать 3 микросервиса, которые взаимодействуют между собой через **Kafka** и моделируют полный цикл заказа — от создания до доставки.

**Главная идея:**
- **Order Service** создаёт заказ и публикует событие в Kafka.  
- **Payment Service** принимает заказы, моделирует оплату (успешно/ошибка), публикует событие в Kafka.  
- **Shipping Service** принимает события об успешных оплатах и создает отгрузки.  
- **Order Service** слушает все обратные события и обновляет статусы заказа в БД.  

Все взаимодействие между сервисами — только через Kafka. REST используется только для создания заказа и просмотра статуса.

---

## 🧩 Архитектура

```
                         +---------------------+
                         |      Order API      |
                         | (создание, статус)  |
                         +---------+-----------+
                                   |
                         kafka ↓   |   ↑ kafka
+---------------------+   +---------+-----------+   +---------------------+
|     Payment Service | ← |    Kafka Topics     | → |   Shipping Service  |
| (обработка платежей)|   | orders, payments,   |   | (создание отгрузки) |
|                     |   | shipments, cancels  |   |                     |
+---------------------+   +---------------------+   +---------------------+

- Order → публикует событие "OrderCreated" в `orders`
- Payment → слушает `orders`, публикует `payments` или `cancels`
- Shipping → слушает `payments`, публикует `shipments`
- Order → слушает все топики и обновляет статус заказа
```

---

## ⚙️ Задачи по сервисам

### 1. 🧾 Order Service
**Функциональность:**
- REST API:
  - `POST /orders` — создать заказ (в БД, статус `CREATED`)
  - `GET /orders/{id}` — получить текущий статус заказа
- После создания — публикует событие `OrderCreated` в Kafka (`orders`).
- Слушает Kafka-топики:
  - `payments` — если пришло `PAID`, обновить заказ в БД на `PAID`.
  - `shipments` — если пришло `SHIPPED`, обновить заказ в БД на `SHIPPED`.
  - `cancels` — если пришло `CANCELLED`, обновить заказ в БД на `CANCELLED`.
- Использует **Inbox Pattern**:
  - Все входящие Kafka-сообщения сначала сохраняются в таблицу `inbox` с `message_id`, чтобы обеспечить идемпотентность (одно сообщение обрабатывается только один раз).

---

### 2. 💳 Payment Service
**Функциональность:**
- Подписывается на Kafka-топик `orders`.
- При получении нового заказа:
  - Сохраняет событие в `inbox` (идемпотентность).
  - Проверяет условие:
    - Если `orderId % 2 == 0` → симулирует **ошибку оплаты**, публикует `PaymentFailed` в топик `cancels`:
      ```json
      { "orderId": 2, "status": "CANCELLED", "reason": "INSUFFICIENT_FUNDS" }
      ```
    - Если `orderId % 2 == 1` → симулирует успешную оплату, публикует `PaymentSuccess` в топик `payments`:
      ```json
      { "orderId": 1, "status": "PAID", "amount": 150.0 }
      ```
- (Опционально) Имеет REST `GET /payments` для просмотра истории платежей.

---

### 3. 📦 Shipping Service
**Функциональность:**
- Подписывается на Kafka-топик `payments`.
- При получении `PaymentSuccess`:
  - Сохраняет событие в `inbox` (идемпотентность).
  - Создает запись об отгрузке (в БД, статус `SHIPPED`, генерирует `trackingNumber`).
  - Публикует событие `OrderShipped` в топик `shipments`:
    ```json
    { "orderId": 1, "status": "SHIPPED", "trackingNumber": "SHIP-ABC123" }
    ```

---

## 🧱 Общие требования

### Kafka топики
| Топик | Отправитель | Получатель | Описание |
|-------|--------------|-------------|----------|
| `orders` | Order Service | Payment Service | События создания заказов |
| `payments` | Payment Service | Order & Shipping Service | Успешные оплаты |
| `shipments` | Shipping Service | Order Service | События об отгрузках |
| `cancels` | Payment Service | Order Service | Отменённые заказы |

---

### Inbox Pattern (Идемпотентность)
Каждый сервис обязан:
- Иметь таблицу `inbox` (например: `id`, `message_id`, `payload`, `processed_at`).
- При получении Kafka-сообщения:
  1. Проверить, есть ли `message_id` в `inbox`.
  2. Если нет — сохранить и обработать.
  3. Если есть — пропустить (сообщение уже обработано).

---

### Persistence
Каждый сервис должен иметь собственную БД в продакшене 
(для простоты можно использовать одну базу в докере, чтобы экономить ресурсы, 
только создавайте таблицы с префиксом сервиса):
- **Order Service** — таблицы `orders`, `inbox`
- **Payment Service** — таблицы `payments`, `inbox`
- **Shipping Service** — таблицы `shipments`, `inbox`

---

## 🚀 Как это всё должно работать

1. `POST /orders` → создаёт заказ `#1`
   - Order Service сохраняет заказ → публикует `OrderCreated`.
2. Payment Service получает `OrderCreated`:
   - Если `orderId % 2 == 1`: публикует `PaymentSuccess`.
   - Если `orderId % 2 == 0`: публикует `PaymentFailed`.
3. Order Service слушает события:
   - Обновляет статус `PAID` или `CANCELLED`.
4. Shipping Service слушает `payments`:
   - Создаёт отгрузку → публикует `OrderShipped`.
5. Order Service слушает `shipments`:
   - Обновляет статус заказа на `SHIPPED`.

Пример жизненного цикла:
```
Order #1 → CREATED → PAID → SHIPPED
Order #2 → CREATED → CANCELLED
```

---

