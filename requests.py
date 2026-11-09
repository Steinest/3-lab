from sqlmodel import Session, select
from datetime import datetime
from models import (
    Pilot, Vehicle, Event, TrackConfig, 
    Session as RaceSession, LapResult, 
    TelemetryDesk, ViewerInterface
)

def init_db_sample_data(session: Session):
    """Наполнение базы данных минимальным набором данных для отладки (Пункт 2 хода работы №3)"""
    # Проверяем, есть ли уже данные
    if session.exec(select(Pilot)).first():
        return

    # 1. Создание пилотов
    pilot1 = Pilot(full_name="Артем Максимов", birth_date=datetime(1995, 4, 12), license_number="MSK-55421", med_clearance=True, team_name="Apex Velocity", avatar_url="/avatars/artem.png")
    pilot2 = Pilot(full_name="Елена Смирнова", birth_date=datetime(1998, 9, 23), license_number="SPB-77109", med_clearance=True, team_name="Storm Racing", avatar_url="/avatars/elena.png")
    session.add(pilot1)
    session.add(pilot2)
    session.commit()
    session.refresh(pilot1)
    session.refresh(pilot2)

    # 2. Создание транспорта
    vehicle1 = Vehicle(pilot_id=pilot1.pilot_id, make="Porsche", model="911 GT3 R", vehicle_class="GT3", race_number=13, hex_color_code="#FF3333")
    vehicle2 = Vehicle(pilot_id=pilot2.pilot_id, make="BMW", model="M4 GT3", vehicle_class="GT3", race_number=46, hex_color_code="#3366FF")
    session.add(vehicle1)
    session.add(vehicle2)

    # 3. Конфигурация трассы
    config = TrackConfig(config_name="Grand Prix Circuit", length_meters=4574, turns_count=15, track_map_svg="<svg>circuit_gp</svg>")
    session.add(config)

    # 4. Событие
    event = Event(event_name="Кубок Автодрома: Этап 1", start_date=datetime(2026, 6, 15, 10, 0), end_date=datetime(2026, 6, 15, 18, 0), event_type="Чемпионат", event_logo_url="/logos/cup1.png")
    session.add(event)
    session.commit()
    session.refresh(config)
    session.refresh(event)

    # 5. Заезд (Сессия)
    race_session = RaceSession(event_id=event.event_id, config_id=config.config_id, session_type="Квалификация", start_time=datetime(2026, 6, 15, 12, 0), status="Активен")
    session.add(race_session)
    session.commit()
    session.refresh(race_session)

    # 6. Результаты кругов (Телеметрия/Тайминг)
    lap1 = LapResult(session_id=race_session.session_id, vehicle_id=vehicle1.vehicle_id, lap_number=1, lap_time_ms=91250, sector_1_ms=29800, sector_2_ms=30500, sector_3_ms=30950, max_speed=252.4, is_fastest_lap=True)
    lap2 = LapResult(session_id=race_session.session_id, vehicle_id=vehicle2.vehicle_id, lap_number=1, lap_time_ms=92100, sector_1_ms=30100, sector_2_ms=30700, sector_3_ms=31300, max_speed=248.1, is_fastest_lap=False)
    session.add(lap1)
    session.add(lap2)

    # 7. Настройки пульта телеметриста (Инженерный контур)
    desk = TelemetryDesk(session_id=race_session.session_id, vehicle_id=vehicle1.vehicle_id, layout_grid="3x3", active_widgets="['tire_temps', 'brake_pressure', 'steering_angle']", alert_profile="Critical_High", contrast_mode="Night")
    session.add(desk)

    # 8. Настройки зрительского интерфейса (Публичный контур)
    viewer_ui = ViewerInterface(session_id=race_session.session_id, display_mode="Full Leaderboard + Onboard", typography_pkg="Inter-Bold", sector_colors="{'purple': 'absolute_best', 'green': 'personal_best', 'yellow': 'standard'}", active_widgets="['mini_map', 'gap_counter']")
    session.add(viewer_ui)

    session.commit()


# --- Реализация методов выборки данных (Пункт 3 хода работы №3) ---

def get_all_pilots(session: Session):
    """Выборка всех зарегистрированных пилотов"""
    return session.exec(select(Pilot)).all()


def get_session_leaderboard(session: Session, session_id: int):
    """Выборка результатов заезда (Leaderboard), отсортированная по времени круга (от меньшего к большему)"""
    statement = (
        select(LapResult, Vehicle, Pilot)
        .join(Vehicle, LapResult.vehicle_id == Vehicle.vehicle_id)
        .join(Pilot, Vehicle.pilot_id == Pilot.pilot_id)
        .where(LapResult.session_id == session_id)
        .order_by(LapResult.lap_time_ms.asc())
    )
    return session.exec(statement).all()


def get_telemetry_desk_settings(session: Session, session_id: int, vehicle_id: int):
    """Выборка конфигурации пульта телеметриста для конкретного авто в сессии"""
    statement = (
        select(TelemetryDesk)
        .where(TelemetryDesk.session_id == session_id)
        .where(TelemetryDesk.vehicle_id == vehicle_id)
    )
    return session.exec(statement).first()


def get_viewer_interface_config(session: Session, session_id: int):
    """Выборка параметров зрительского интерфейса и трансляционной графики для заезда"""
    statement = select(ViewerInterface).where(ViewerInterface.session_id == session_id)
    return session.exec(statement).first()