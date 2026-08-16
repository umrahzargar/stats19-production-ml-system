from pydantic import BaseModel


class PredictionInput(BaseModel):
    """The 42 raw features required by the STATS19 model."""

    # Casualty information
    casualty_class: int
    sex_of_casualty: float | None
    age_of_casualty: int | None
    casualty_type: float | None
    pedestrian_location: int
    pedestrian_movement: int

    # Vehicle information
    vehicle_type: float | None
    vehicle_manoeuvre: float | None
    skidding_and_overturning: float | None
    vehicle_leaving_carriageway: float | None
    first_point_of_impact: float | None
    journey_purpose_of_driver: int

    # Driver information
    sex_of_driver: float | None
    age_of_driver: int | None
    age_of_vehicle: int | None

    # Collision and road information
    speed_limit: int
    number_of_vehicles: int
    road_type: int
    first_road_class: int    
    junction_detail: float | None
    junction_control: float | None
    urban_or_rural_area: float | None
    trunk_road_flag: float | None
    light_conditions: int
    weather_conditions: float | None
    road_surface_conditions: float | None

    # Time-based features
    hour: int
    month: int
    is_weekend: int
    is_night: int
    is_rush_hour: int
    is_weekend_night: int

    # Collision-context features
    ctx_any_motorcycle: int
    ctx_any_cycle: int
    ctx_any_hgv: int
    ctx_any_skidding: int
    ctx_any_left_carriageway: int
    ctx_any_front_impact: int
    ctx_any_young_driver: int
    ctx_any_elderly_driver: int
    ctx_mean_driver_age: float | None
    ctx_mean_vehicle_age: float | None


class BatchPredictionRequest(BaseModel):
    source_filename: str | None = None
    records: list[PredictionInput]