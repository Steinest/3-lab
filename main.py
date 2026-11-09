from sqlmodel import create_engine, Session, select
from models import SQLModel, Session as RaceSession
from requests import (
    init_db_sample_data, 
    get_all_pilots, 
    get_session_leaderboard, 
    get_telemetry_desk_settings, 
    get_viewer_interface_config
)

# Конфигурация подключения к базе данных SQLite
sqlite_file_name = "racetrack.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Создание движка базы данных (echo=True включает вывод SQL-запросов в консоль для наглядности)
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    """Создание таблиц на основе моделей SQLModel"""
    SQLModel.metadata.create_all(engine)

def main():
    print("=== Инициализация системы 'Гоночная трасса' (Лабораторная работа №3) ===")
    
    # 1. Создание структуры БД
    create_db_and_tables()
    print("[OK] База данных и таблицы успешно созданы.\n")

    # 2. Открытие сессии для работы с данными
    with Session(engine) as session:
        # Наполнение базы данных минимальным набором данных для отладки
        init_db_sample_data(session)
        print("[OK] База данных успешно наполнена тестовыми данными.\n")

        # --- 3. Демонстрация методов выборки данных ---
        
        print("--- 1. Список всех зарегистрированных пилотов ---")
        pilots = get_all_pilots(session)
        for pilot in pilots:
            print(f"• ID: {pilot.pilot_id} | Имя: {pilot.full_name} | Команда: {pilot.team_name} | Лицензия: {pilot.license_number}")

        # Получаем ID первого доступного заезда для проверки связей
        first_session = session.exec(select(RaceSession)).first()
        if first_session:
            print(f"\n--- 2. Лидерборд заезда (ID сессии: {first_session.session_id}) ---")
            leaderboard = get_session_leaderboard(session, first_session.session_id)
            for lap, vehicle, pilot in leaderboard:
                print(f"• Круг №{lap.lap_number} | Пилот: {pilot.full_name} "
                      f"({vehicle.make} {vehicle.model}, №{vehicle.race_number}) | "
                      f"Время круга: {lap.lap_time_ms} мс | Макс. скорость: {lap.max_speed} км/ч")

            print("\n--- 3. Конфигурация пульта телеметриста (Инженерный контур) ---")
            desk = get_telemetry_desk_settings(session, first_session.session_id, vehicle_id=1)
            if desk:
                print(f"• Сетка экрана (Grid): {desk.layout_grid} | "
                      f"Профиль алертов: {desk.alert_profile} | "
                      f"Режим контрастности: {desk.contrast_mode} | "
                      f"Виджеты: {desk.active_widgets}")

            print("\n--- 4. Настройки интерфейса для зрителей (Публичный контур) ---")
            viewer_ui = get_viewer_interface_config(session, first_session.session_id)
            if viewer_ui:
                print(f"• Режим отображения: {viewer_ui.display_mode} | "
                      f"Типографика: {viewer_ui.typography_pkg} | "
                      f"Интерактивные виджеты: {viewer_ui.active_widgets}")


if __name__ == "__main__":
    main()