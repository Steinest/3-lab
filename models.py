from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class Pilot(SQLModel, table=True):
    __tablename__ = "pilots"
    
    pilot_id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str = Field(max_length=100)
    birth_date: Optional[datetime] = None
    license_number: str = Field(unique=True, max_length=30)
    med_clearance: bool = Field(default=True)
    team_name: Optional[str] = Field(default=None, max_length=100)
    avatar_url: Optional[str] = Field(default=None, max_length=255)
    
    # Связи
    vehicles: List["Vehicle"] = Relationship(back_populates="pilot")


class Vehicle(SQLModel, table=True):
    __tablename__ = "vehicles"
    
    vehicle_id: Optional[int] = Field(default=None, primary_key=True)
    pilot_id: int = Field(foreign_key="pilots.pilot_id")
    make: str = Field(max_length=50)
    model: str = Field(max_length=50)
    vehicle_class: str = Field(max_length=30)
    race_number: int
    hex_color_code: str = Field(max_length=7)
    
    # Связи
    pilot: Optional[Pilot] = Relationship(back_populates="vehicles")
    lap_results: List["LapResult"] = Relationship(back_populates="vehicle")
    telemetry_desks: List["TelemetryDesk"] = Relationship(back_populates="vehicle")


class Event(SQLModel, table=True):
    __tablename__ = "events"
    
    event_id: Optional[int] = Field(default=None, primary_key=True)
    event_name: str = Field(max_length=100)
    start_date: datetime
    end_date: datetime
    event_type: str = Field(max_length=50)
    event_logo_url: Optional[str] = Field(default=None, max_length=255)
    
    # Связи
    sessions: List["Session"] = Relationship(back_populates="event")


class TrackConfig(SQLModel, table=True):
    __tablename__ = "track_configs"
    
    config_id: Optional[int] = Field(default=None, primary_key=True)
    config_name: str = Field(max_length=50)
    length_meters: int
    turns_count: int
    track_map_svg: Optional[str] = None
    
    # Связи
    sessions: List["Session"] = Relationship(back_populates="config")


class Session(SQLModel, table=True):
    __tablename__ = "sessions"
    
    session_id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="events.event_id")
    config_id: int = Field(foreign_key="track_configs.config_id")
    session_type: str = Field(max_length=30)
    start_time: datetime
    status: str = Field(max_length=20)
    
    # Связи
    event: Optional[Event] = Relationship(back_populates="sessions")
    config: Optional[TrackConfig] = Relationship(back_populates="sessions")
    lap_results: List["LapResult"] = Relationship(back_populates="session")
    telemetry_desks: List["TelemetryDesk"] = Relationship(back_populates="session")
    viewer_interfaces: List["ViewerInterface"] = Relationship(back_populates="session")


class LapResult(SQLModel, table=True):
    __tablename__ = "lap_results"
    
    result_id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="sessions.session_id")
    vehicle_id: int = Field(foreign_key="vehicles.vehicle_id")
    lap_number: int
    lap_time_ms: int  # Время в миллисекундах для точности тайминга
    sector_1_ms: int
    sector_2_ms: int
    sector_3_ms: int
    max_speed: float
    is_fastest_lap: bool = Field(default=False)
    
    # Связи
    session: Optional[Session] = Relationship(back_populates="lap_results")
    vehicle: Optional[Vehicle] = Relationship(back_populates="lap_results")


class TelemetryDesk(SQLModel, table=True):
    __tablename__ = "telemetry_desks"
    
    desk_id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="sessions.session_id")
    vehicle_id: int = Field(foreign_key="vehicles.vehicle_id")
    layout_grid: str = Field(max_length=20)       # Например, "2x2", "3x3"
    active_widgets: str                           # Перечень виджетов (JSON / строка)
    alert_profile: str = Field(max_length=50)     # Профиль критических алертов
    contrast_mode: str = Field(max_length=20)     # "Day" / "Night"
    
    # Связи
    session: Optional[Session] = Relationship(back_populates="telemetry_desks")
    vehicle: Optional[Vehicle] = Relationship(back_populates="telemetry_desks")


class ViewerInterface(SQLModel, table=True):
    __tablename__ = "viewer_interfaces"
    
    interface_id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="sessions.session_id")
    display_mode: str = Field(max_length=50)      # "Full Leaderboard", "On-board"
    typography_pkg: str = Field(max_length=50)    # Набор шрифтов
    sector_colors: str                            # Цветовая кодировка секторов (JSON)
    active_widgets: str                           # Интерактивные элементы (JSON)
    
    # Связи
    session: Optional[Session] = Relationship(back_populates="viewer_interfaces")