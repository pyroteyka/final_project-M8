
import json
from config import USER_SCHEDULE_FILE


def load_user_schedules() -> dict:
    """Загружает расписания всех пользователей."""
    try:
        with open(USER_SCHEDULE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_user_schedules(data: dict):
    """Сохраняет расписания пользователей."""
    with open(USER_SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def add_lesson(user_id: str, day: str, time: str, subject: str) -> str:
    """Добавляет урок пользователю."""
    data = load_user_schedules()
    user_schedule = data.get(user_id, {})

    user_schedule.setdefault(day, []).append(f"{time} — {subject}")
    data[user_id] = user_schedule
    save_user_schedules(data)

    return f"✅ Добавлен урок: *{day}*, {time} — {subject}"


def get_user_schedule(user_id: str) -> str:
    """Возвращает расписание пользователя."""
    data = load_user_schedules()
    schedule = data.get(user_id, {})

    if not schedule:
        return "📭 У тебя пока нет занятий. Добавь своё расписание через кнопку ниже!"

    lines = ["📅 *Твоё расписание:*", ""]
    for day, lessons in schedule.items():
        lines.append(f"*{day}:*\n" + "\n".join(lessons) + "\n")
    return "\n".join(lines)
